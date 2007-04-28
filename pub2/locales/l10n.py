# (C) 2006 Terry Hancock
#--------------------------------
# l10n
"""
Localization module.

Creates the locale object from locale files (xx.py, xx.xml, xx.po, where 'xx' is the locale).
For example:

"""
#--------------------------------------------------------------------
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#--------------------------------------------------------------------
# Prerequisites/utilities for Locale modules
# Every locale module should import this module
# and will be subsequently imported by it

import os, sys
import re
import gettext

locales_dir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
pub_dir     = os.path.abspath(os.path.join(locales_dir, '..'))

if os.path.abspath(sys.path[1]) != pub_dir:
    sys.path.insert(1, pub_dir)

# Note this will fail if the above path mechanics don't work
import config

#print "LOCALE = %s" % config.LOCALE

import interfaces
import semantics
from semantics import sym, AdjectiveVocabulary
from symbol import Symbol
from vague import Vague, SparseVector, table_lookup

from elementtree import ElementTree

import pyparsing

locales = {}

class PUB_InvalidVocabulary(ValueError):
    pass

class PoS:
    """
    Table of names for parts of speech.

    We use different abbreviations in different places, hopefully
    for greater clarity, but we need to be able to translate freely.

    This class contains the original table, tuples for each column,
    and dictionaries mapping each column to each other column.
    """
    #                Ltr  Grp               Abr     Sym
    Table = [       ('a', 'adjectives',     'adje', sym.ADJE),
                    ('A', 'adverbs',        'advb', sym.ADVB),
                    ('N', 'nouns',          'noun', sym.NOUN),
                    ('V', 'verbs',          'verb', sym.VERB),
                    ('t', 'articles',       'artl', sym.ARTL),
                    ('d', 'declensions',    'decl', sym.DECL),
                    ('p', 'prepositions',   'prep', sym.PREP),
                    ('c', 'conjunctions',   'conj', sym.CONJ),
                    ('P', 'punctuation',    'punc', sym.PUNC),
                    ('Q', 'quantifiers',    'number', sym.G_NUMBER)]
                    
    Ltrs, Grps, Abrs, Syms = zip(*Table)

for i in 'Ltr', 'Grp', 'Abr', 'Sym':
  for j in 'Ltr', 'Grp', 'Abr', 'Sym':
    if i!=j:
        setattr(PoS, '%s2%s' % (i,j),
            dict(zip(getattr(PoS,'%ss'%i), getattr(PoS,'%ss'%j))) )

def _update_multimap(d, e):
    """
    Update a multimap dictionary.
    Similar to .update() method of dictionary, but instead of replacing
    elements with the same keys, combine them into a single tuple.
    """
    for key in e:
        if not hasattr(e[key], '__iter__'):
            e_values = (e[key],)
        else:
            e_values = tuple(e[key])
        if key in d:
            if not hasattr(d[key], '__iter__'):
                d[key] = (d[key],)
            d[key] = tuple(d[key]) + e_values
        else:
            d[key] = e_values
    

def flatten_parse_results(tree):
    """
    Convenience function to generate a flattened list of tokens
    from a pyparsing.ParseResults object.
    """
    collection = []
    if hasattr(tree, '__iter__') and not (type(tree)==type(()) and len(tree)==2):
        for subtree in tree:
            addendum = flatten_parse_results(subtree)
            collection.extend(addendum)
    elif tree=='':
        pass
    else:
        collection.append(tree)
    return collection


def annotated(expression, **kw):
    """
    Convenience function to attach implicit information to parse expressions that will appear in results.
    This is the preferred method to mark positional grammatical information.

    Note that we use the pyparsing "results name" attribute to do this, and we actually load it with
    a tuple representing a dictionary (because it must be hashable).
    """
    implicit = tuple([(getattr(sym,k),v) for (k,v) in kw.items()])
    return expression.setResultsName(implicit)

# The LocaleVocabulary object will store all of the vocabulary lookup info
# for the locale.

class Gloss(object):
    wd = 'NO GLOSS'
    cl = None

    def __init__(self, attrib, posname):
        for key in attrib.keys():
            setattr(self, key, attrib[key])
        if not hasattr(self, 'wd'):
            raise PUB_InvalidVocabulary("PUB vocab: word must have a 'wd' attribute")
        self.attrib = attrib

        if posname=='verbs':
            if attrib.has_key('adv'):
                # Special handling of implicit adverbial content
                self.adv = self.parse_adv(attrib['adv'])
            else:
                self.adv = SparseVector({}, default=Vague(0.0))

        elif posname=='adverbs':
            if attrib.has_key('val'):
                self.val = Vague(float(attrib['val']))
            else:
                raise PUB_InvalidVocabulary("PUB vocab: adverb glosses must have a 'val' attribute")

    def __unicode__(self):
        return u"<GLOSS: %s, cl=%s, %s>" % (unicode(self.wd), unicode(self.cl), unicode(self.attrib))

    def __repr__(self):
        return u"<GLOSS: %s, cl=%s, %s>" % (repr(self.wd), repr(self.cl), repr(self.attrib))

    def parse_adv(self, adv_s):
        """
        Parse implicit adverb vector to SparseVector of Vague representation
        """
        adv_ds = dict([[n.strip() for n in m.split(':')][:2] for m in adv_s.split(',')])
        adv = {}
        for key, val in adv_ds.items():
            if not hasattr(sym, key):
                Symbol(key, domain=sym.ADVB)
            new_key = getattr(sym, key)
            if not new_key.domain == sym.ADVB:
                raise PUB_InvalidVocabulary("PUB vocab: symbol redefinition: %s", key_strip)
            adv[new_key] = Vague(val)
        return SparseVector(adv, default=Vague(0.0)) 

class LocaleGrammar(object):
    """
    Definition of grammar rules for the language.

    This object wraps the grammar module provided as "core PUB localization" for
    the language. All calls are actually passed through to the appropriate function
    in that module.
    """
    def load_grammar(self, grammar):
        """
        Load the grammar (.py) file.
        """
        self.grammar = __import__(grammar[:-len(".py")])

        # Guaranteed grokking interface:
        for abr in PoS.Abrs:
            grok_fn_name = 'grok_%s' % abr
            if not hasattr(self.grammar, grok_fn_name):
                setattr(self.grammar, grok_fn_name, lambda l,t,pos=PoS.Abr2Sym[abr]: self._default_grok(l,t, pos))
    
    def tell(self, sentence):
        """
        Tell a sentence to the user in correct locale.

        sentence - PUB sentence object in concept language

        Returns unicode text.
        """
        return self.grammar.tell_sentence(sentence)

    def parse(self, text):
        """
        Parse unicode text

        Returns PUB sentence object
        """
        return self.SentenceParser.parseString(text)

    def dir_grammar(self):
        return dir(self.grammar)

    def _default_grok(self, loc, tokens, pos):
        if not tokens:
            return {}
        tokens = tokens[:]
        for i in range(len(tokens)):
            if type(tokens[i]) in (str, unicode):
                tokens[i] = getattr(loc, PoS.Sym2Grp[pos]).get(tokens[i])
        return {pos:tokens}
        

class LocaleVocabulary(object):
    """
    Vocabulary of words for a given localization.

    Calls to load_vocabulary accumulate new concepts and words from XML source files.
    This is also the most convenient place to acquire top-level identification information,
    such as language variant, etc.
    """
    name = 'xx_XX'                  # filestem of locale files (and internal PUB name)
    lang = 'xx'                     # language code ISO-639 2, 3, or named language
    region = 'XX'                   # capitalized ISO-3166 country or other recognized region code
    variant = ''                    # special named variants (can say anything you like here)
    encoding = 'utf-8'              # Unicode encoding to use
    direction = 'LRTB'              # Text direction, e.g. "LRTB" means "Left-to-Right, Top-to-Bottom"
    language = 'Unknown Language'   # Full name of language, in the language (used in menus, etc)
    concepts = None

    pos_match = None                 # Will be a table of pyparsing expression for each part-of-speech

    def load_vocabulary(self, vocabulary):
        """
        Load the vocabulary (.xml) file.
        """
        # word-to-concept mappings
        for key in PoS.Grps:
            setattr(self, key, {})

        # concept-to-word mappings
        self.concepts = {}
        for key in PoS.Grp2Abr:
            self.concepts[key] = {}
            
        if type(vocabulary)==str and len(vocabulary) < 32:
            data = open(vocabulary, 'rt').read()    # short names are read as filenames
        elif type(vocabulary)==file:
            data = vocabulary.read()                # file handle
        else:
            data = vocabulary                       # data buffer

        self.xml = ElementTree.XML(data)
        if self.xml.tag != 'locale':
            raise PUB_InvalidVocabulary("Main element is not 'locale'")

        for attrib in ('name', 'lang', 'region', 'encoding', 'direction', 'language', 'variant'):
            if self.xml.attrib.has_key(attrib):
                setattr(self, attrib, self.xml.attrib[attrib])
            else:
                setattr(self, attrib, '')

        for child in self.xml.getchildren():
            if child.tag in PoS.Grps:
                for concept in [c for c in child.getchildren() 
                                if c.tag==PoS.Grp2Abr[child.tag]]:
                    self._load_concept(concept, child.tag)

    def _load_concept(self, concept, posname):
        """
        Load a word from vocabulary elementtree word element.

        concept - elementtree element object for the concept language symbol
        
        pos     - name of the part-of-speech dictionary to append this word
        """
        pos = getattr(self, posname)    # Get the correct dictionary by part-of-speech           
        if not concept.attrib.has_key('sym'):
            raise PUB_InvalidVocabulary("PUB vocab: concept must have 'sym' attribute")
        concept_symbol  = self._deref_concept(concept, posname)
        concept_glosses = self.concepts[posname][concept_symbol] = []        
        for gloss in [c for c in concept.getchildren() if c.tag in ('g', 'gloss')]:               
            concept_glosses.append(Gloss(gloss.attrib, posname)) # concept-to-language mapping
            pos[gloss.attrib['wd']] = concept_symbol    # language-to-concept mapping

    def _deref_concept(self, concept, posname):
        """
        Check sym for symbol matching a concept, and check that it is consistent.

        If it doesn't exist in sym, then add it.
        """
        concept_sym = concept.attrib['sym']
        
        # Special adjective concept handling -- get sense
        if concept.attrib.has_key('sense'):
            concept_sense_s = concept.attrib['sense']
            concept_sense = AdjectiveVocabulary.sense_inv[concept_sense_s]

        # "sym" = global PUB symbol table, "concept_sym" = "sym" attribute of concept XML element
        if hasattr(sym, concept_sym):
            domain = getattr(sym, concept_sym).domain
            if not domain == PoS.Grp2Sym[posname]:
                raise PUB_InvalidVocabulary(
                    "Concept symbol conflict: %s, wrong part of speech, %s." % (concept,  posname))
        elif posname == 'adjectives':
            AdjectiveVocabulary(concept_sense, [concept_sym])
        else:
            Symbol(concept_sym, domain=PoS.Grp2Sym[posname])            
        return getattr(sym, concept_sym)

    def save_vocabulary(self, filename):
        """
        Save XML representation of vocabulary.
        """
        ElementTree.ElementTree(self.xml).write(filename, "utf-8")

    def __unicode__(self):
        """
        Generate a report representing the locale.
        """
        if not self.concepts:
            return u"<PUB LocaleVocabulary: Not Initialized>"

        if self.variant:
            language_variant = ", ".join([self.language, self.variant])
        else:
            language_variant = self.language

        hdr = "'%s' %s_%s %s %s (%s)" % (self.name, self.lang, self.region, 
                                            self.encoding, self.direction, language_variant)
        counts = {}
        for k,v in PoS.Ltr2Grp.items():
            counts[k] = len(self.concepts[v])

        wds = ' '.join(["#%1.1s=%d" % (k,v) for (k,v) in counts.items() if v>0])

        return u"<PUB LocaleVocabulary: %s | %s >" % (hdr, wds)

    def __repr__(self):
        """
        Generate a report representing the locale.
        """
        return repr(unicode(self))

    def show(self):
        print unicode(self)

    def show_concepts(self):
        """
        Report concepts defined.
        """
        keys = self.concepts.keys()
        keys.sort()
        for key in keys:
            syms = self.concepts[key].keys()
            if len(syms):
                syms.sort()
                print '%s:\n\t' % key,
                for sym in syms:
                    print sym,
                print
        return

    def show_words(self):
        """
        Show word glosses available in vocabularies.
        """
        words = self.get_words()
        for pair in words:
            print u"%s \u2192 %s" % pair

    def get_words(self):
        """
        Get list of words defined in locale vocabulary.
        """
        words = []
        for key in PoS.Grps:
            vocab = getattr(self, key)
            for word, concept in vocab.items():
                words.append((word, concept))
        words.sort()
        return words

    def dereference_concepts(self, sym):
        """
        Convert string concepts in vocabulary to PUB Symbol objects

        When we read the XML file, we just get strings, but we need
        to convert those to Symbols for use within PUB.

        This is also where we catch a lot of possible errors (conflicting
        part of speech, dangling concepts, etc).
        """
        for posname, concepts in self.concepts.items():
            for concept, glosses in concepts.items():
                if type(concept)==type(''):
                    concept_symbol = self._deref_concept(concept, posname)
                    self.concepts[posname][concept_symbol] = self.concepts[posname][concept]
                    del self.concepts[posname][concept]

    def get_missing_concepts(self):
        """
        Report the concepts which do not yet have any glosses.
        This is principally meant as a debugging tool for localizers.
        """
        report = {}
        for pos in PoS.Grps:
            report[pos] = []
            for symbol, glosses in self.concepts[pos].items():
                if not glosses:
                    report[pos].append(symbol)
        return report

    def resolve_adverb(self, adverb, implicit=SparseVector(), tolerance=0.200):
        """
        Resolve a VagueConcept adverb object into best-fit adverb gloss.

        adverb    - adverbial value in concept language clause (SparseVector of Vague)

        implicit  - adverbial value implied by selected verb gloss (SparseVector of Vague)

        tolerance - match tolerance

        Returns a dictionary of adverbial glosses, arranged as tuples of
        the forms (), (A), or (A,C) where A is a domain adverb, and C is a
        combining adverb (both optional). The keys to the dictionary are the
        adverbial domains (a locale module author may wish to follow some convention
        about the ordering of the adverbs, or they may just loop through the keys
        in hash order).
        """
        combining_advs = self.concepts['adverbs'][sym.COMBINING]

        advs    = {}
        errors  = {}
        for adv_domain, adv_glosses in self.concepts['adverbs'].items():
            if not adv_domain == sym.COMBINING:
                target_value = adverb[adv_domain] - implicit[adv_domain]

                # If near enough to 0, just return an empty expression
                explicit_adv_expr = ()
                explicit_value = Vague(0.0)
                
                # If out of tolerance, try a bare adverb
                if abs(target_value) > tolerance:
                    adv_table = ([(g.val, (g,)) for g in adv_glosses] + 
                                [(explicit_value, explicit_adv_expr)])
                    explicit_value, explicit_adv_expr = table_lookup(target_value, adv_table)
                    
                    # If still out of tolerance, try adverb * combining
                    if abs(target_value - explicit_value) > tolerance:
                        for combining in self.concepts['adverbs'][sym.COMBINING]:
                            for gloss in adv_glosses:
                                adv_table.append( (gloss.val*combining.val, (gloss, combining)) )
                        
                        explicit_value, explicit_adv_expr = table_lookup(target_value, adv_table)
                        if abs(target_value - explicit_value) > tolerance:
                            # Punt --   if we're still out of tolerance, we currently
                            #           just give up (but we could log it or something)
                            #           A failure probably means the locale vocabulary
                            #           is not sufficiently expressive.
                            pass
                advs[adv_domain] = explicit_adv_expr
                errors[adv_domain] = target_value - explicit_value
        return advs, SparseVector(errors, default=Vague(0.0))

        
    def resolve_verb(self, verb_concept, adverbs):
        """
        Resolve concept language verb+adverbs to best-fit verb from glosses.

        Returns best-fit verb gloss and adverbial remainder as a tuple.
        """  
        verbs = self.concepts['verbs'][verb_concept]
        chisq = float(len(adverbs)) # i.e. maximum possible
        best  = verbs[0]
        for verb in verbs:
            new_chisq = (verb.adv.applied(float) - adverbs.applied(float))**2
            if new_chisq < chisq:
                chisq = new_chisq
                best = verb               
        return best, adverbs.applied(float) - best.adv.applied(float)

    # FIXME: the following methods might make more sense if moved into "Parser"
    #        (no actual difference in function should result from doing so, though)

    def get_pos_classifiers(self):
        """
        Generates a dictionary of part-of-speech classifier expressions for pyparsing
        based on the locale vocabulary tables.
        """
        # TODO: in the future, we may need contextual recognition using perturbational
        #       elements for words which can appear in several parts of speech. This may
        #       be necessary in highly analytic languages (e.g. Chinese).
        #
        #       The idea would be to vary the recognition for each word matched, and
        #       try multiple parses on a sentence until a good match is made.
        #
        #       However, in very small vocabularies, collisions are unlikely, and this
        #       is a pretty complicated idea, so I'm not going to try it until it's
        #       needed.

        # Two main problems:
        #   1) Find all the words of a given PoS and create a big "OR" expression
        #   2) For each element of the "OR", tolerate inflections as minimally as possibly

        # FIXME: should load using define_classifiers first, then overload.
        self.pos_match = {}
        pos_initial = self.grammar.define_classifiers()
        for i,pos in enumerate(PoS.Syms):
            self.pos_match[pos] = pos_initial[i]
            
        for pos in PoS.Syms:
            vocabulary_glosses = []
            for concept in self.concepts[PoS.Sym2Grp[pos]].values():
                vocabulary_glosses.extend(concept)
            # print vocabulary_glosses
            gloss_expressions = []
            for gloss in vocabulary_glosses:
                gloss_expressions.append(
                    self._adapt_match_expression(
                         self.grammar.define_inflections(pos, gloss)))
                         
            inflected_match = pyparsing.Or(gloss_expressions)

            if not self.pos_match[pos]:
                full_match = inflected_match
            elif not inflected_match:
                full_match = self.pos_match[pos]
            else:
                full_match = self.pos_match[pos] ^ inflected_match

            #print PoS.Sym2Abr[pos], full_match

            full_match.setName(PoS.Sym2Abr[pos].capitalize())

            self.pos_match[pos] = full_match
        
    def _adapt_match_expression(self, match_expression):
        """
        Convenience method to wrap pyparsing, regex, string, or unicode expression as pyparsing.
        """
        # One might argue that we shouldn't do this kind of type-checking in
        # Python, but this is the simplest way I know to do this (this is effectively
        # an ad-hoc "adapter" for string, unicode, regex, and pyparsing to pyparsing)
        if type(match_expression) in (str, unicode):
            return pyparsing.CaselessLiteral(match_expression)
        elif type(match_expression) == type(re.compile('')):
            return pyparsing.Regex(match_expression.pattern + '$')
        elif isinstance(match_expression, pyparsing.ParserElement):
            return match_expression
        else:
            raise TypeError("Match object must be string, unicode, "
                            "regular expression or pyparsing parse expression"
                            "(not %s)" % repr(type(match_expression)))

class LocaleMessages(object):
    """
    The dull, but necessary standard gettext messages required for the game.

    These are probably going to be mostly the standard stuff like the default
    answers to certain types of questions (e.g. "You see nothing here", help
    messages, file I/O feedback messages, etc.)
    """
    gettext_domain = 'pubcore'
    
    def load_messages(self, messages):
        """
        Load the messages (configure gettext).
        """
        # Locale directory is the same:
        gettext.bindtextdomain(self.gettext_domain, locales_dir)

    def gettext(self, text, plural=None, n=None):
        """
        Replacement for _() function from gettext.
        """
        if n:
            return gettext.dngettext(self.gettext_domain, text, plural, n)
        else:
            return gettext.dgettext(self.gettext_domain, text)

class TokenFactory(object):
    """
    Returns a tuple representing a classified word token.
    """
    def __init__(self, pos):
        self.pos = pos

    def __call__(self, text, location, tokens):
        if len(tokens)==1:
            return (self.pos, tokens[0])
        else:
            return (self.pos, tokens)

class Parser(object):
    """
    Oversees final conversion of localized information to concept language
    """
    def load_parser(self, C, NP, VP):
        """
        Loads the concept language representation classes.

        Note that these are the *classes*,  not instances.  They will
        be used to construct the parsed input from text.
        """
        #
        # We  load  these as  a separate action  in order to  provide a
        # separation of concerns between the parser and deeper parts of
        # the engine  (in particular, the de-referencing of language to
        # game objects). This allows us to build working unit test rigs
        # for the parser  which do not rely on  a functioning IF engine
        # core.
        #
        # Because of this, we can use a separate set of "Test" language
        # classes,  which  represent  only  the  aspects  needed by the
        # parser and tests.
        #

        # load ParseElement objects from locale grammar:
        (
        NounPhraseParsers,
        VerbPhraseParsers,
        ClauseParsers,
        SentenceParsers
        ) = self.grammar.define_sentence_parsers(
                *[self.pos_match[pos] for pos in PoS.Syms] )    # LocaleVocabulary.pos_match dictionary
                
        # load concept language classes from caller
        self.Clause = C
        self.NounPhrase = NP
        self.VerbPhrase = VP

        # attach parser hooks to ParserElements:
        self.set_hooks(SentenceParsers, ClauseParsers, NounPhraseParsers, VerbPhraseParsers)
        self.SentenceParser = SentenceParsers[0]    # Must be at least one sentence parser

    def parse_sentence(self, text, location, sentence_results):
        """
        Parse a sentence.

        Assembles a series of parsed concept language clauses.

        "Grokking"  is used here to refer to the process of identifying
        all of the non-localized grammatical information available from
        a language element. If successful, the outcome is a correct and
        dispatchable sequence of commands to the IF engine.

        So,  for example,  grokking  of a clause ensures that its tense
        and mood are defined,  and that all  the elements of all of the
        contained noun and verb phrases are also defined.  The point is
        to remove any ambiguities remaining from earlier steps.

        This is made  necessary  by  the fact that  different languages
        represent such information at different levels (for example, in
        the word inflection  or in the word order or word choice within
        a  phrase).   Thus,  parsing  Russian  relies  heavily  on  the
        functions  which grok individual noun and verb words,   whereas
        parsing English or Chinese relies heavily on phrase structure.

        So,  neither phrase nor word  parsers can,  in general,  assume
        responsibility for resolution.  Thus  we  need  a final pass to
        take  that  responsibility,    using  information  provided  by
        incomplete parsers. This is it.

        Note that grokking does not include *de-referencing*:  we still
        don't know *which object*  a given concept language  NounPhrase
        refers to in the game universe.  That's because,  at the parser
        level,  we don't have  any  information about the IF universe's
        model. We only know that we have collected all information that
        we know how  to extract from  the  input language.  The core IF
        engine will  be  responsible for figuring out which actual game
        objects are meant  (it is still possible for that to fail,  but
        it is not the responsibility of the parser).

        Returns: list of self.Clause instances
        """
        implicit = sentence_results.getName()
        if implicit:
            implicit = dict(implicit)
        else:
            implicit = {}
        
        sentence_tokens = sentence_results
        S = []
        for clause in sentence_tokens:
            S.append(self.parse_clause('', 0, clause))

        return S
        

    def parse_clause(self, text, location, clause_results):
        """
        Parse a clause

        Grokking  of  a  clause ensures  that  its  tense and mood  are
        defined, and that all the elements of all of the contained noun
        and verb phrases are also defined.

        Returns: fully grokked self.Clause instance
        """
        implicit = clause_results.getName()
        if implicit:
            implicit = dict(implicit)
        else:
            implicit = {}
        
        # First - extract any verb phrase words and create a verb phrase
        # token list

        # FIXME: need to link quantifiers to nounphrases
        # is this possible in general? Can we use a "grok_quantifier" to
        # figure out the assignment? How about implicit quantifier info
        # (e.g. an "nom_quant" variant for modifying the nominative?)

        # FIXME: what about quotations and other literals?

        clause_tokens = flatten_parse_results(clause_results)

        NPs = [t for t in clause_tokens if type(t)==self.NounPhrase]

        NP_map={}
        for decl in sym.lookup(sym.DECL):
            NP_map[decl] = [NP for NP in NPs if NP.decl == decl]

        NP_dangling = [NP for NP in NPs if not NP.decl]
        
        verb_phrase = []
        for item in clause_tokens:
            if type(item) == tuple:
                pos, word = item
                if pos in (sym.VERB, sym.ADVB):
                    verb_phrase.append( (pos,word) )

        VP = self.parse_verb_phrase('', 0, verb_phrase, implicit=implicit)

        for decl in VP.agreements:
            NP_map[decl] = self._imply_nounphrase(decl, NP_map[decl], NP_dangling, VP.agreement[decl])

        # Drop dangling NPs if remaining
        NPs = []
        for val in NP_map.values():
            NPs.extend(val)

        #if not [NP for NP in NPs if NP.decl==sym.NOM]:
            # If we still don't have a nominative case nounphrase,
            # then "singular you" (i.e. the player character) is implied:
        #    NPs.append(self.NounPhrase(sym.SECOND, number=sym.SING))
        
        C = self.Clause(VP, NPs)

        return C

    def _imply_nounphrase(declension, explicit_nouns, dangling_nouns, verb_agreement):
        """
        Discover nounphrases which are implied by the form of the verb.

        This allows us to get the subject of sentences in languages like
        Spanish, where there the noun may only be implied by the conjugation
        of the verb. In that case, the grok_verb function should've provided
        an "agreeements" dictionary which identifies the grammatical person
        and grammatical number of the subject (nominative case nounphrase).
        """
        imply_new_noun = False

        # FIXME: we may want number/person matching rules to be defined in other
        #       parts of PUB -- consider re-expressing them as __eq__ or
        #       as a special function in semantics
        #
        def person_matches(nounphrase, agreement):
            "Condition to tell if grammatical persons match"
            return ( 
                   agreement.get(sym.G_PERSON, None) and
                     ( 
                     (np.noun in sym.lookup(sym.G_PERSON))
                       or
                     (agreement[sym.G_PERSON] in (sym.THIRD, sym.FOURTH))
                     )
                   )

        def number_matches(nounphrase, agreement):
            "Condition to tell if grammatical numbers match"
            # FIXME: this shouldn't be an equality test, we need a
            #        special matching function, possibly part of the locale
            #        grammar?  Because, e.g. DUAL should match PLURAL in
            #        languages that don't have a DUAL
            return (
                   (not verb_agreement.get(sym.G_NUMBER, None)) or 
                   nounphrase.number == verb_agreement[sym.G_NUMBER]
                   )
            
        if explicit_nouns:
            for nounphrase in explicit_nouns:
                if person_matches(nounphrase, verb_agreement):
                    if number_matches(nounphrase, verb_agreement):
                        # agreed noun was explicit anyway, no implication necessary
                        break
                    elif not nounphrase.number and verb_agreement.get(sym.G_NUMBER, None):
                        # only imply missing grammatical number
                        nounphrase.number = verb_agreement[sym.G_NUMBER]
                        break
            else:
                # No nounphrase with matching number and person exists,
                # but there is a noun of the right declension.
                #
                # This could mean there is an implied noun, but it could
                # also mean the clause was grammatically incorrect (typo?)
                # We assume the latter is more likely and don't imply anything
                pass

        elif dangling_nouns:
            # No explicit nouns, but some nouns exist which aren't mapped
            # to a declension -- perhaps one of these is referred to by
            # the verb, which will in turn imply the correct declension
            for nounphrase in explicit_nouns:
                if ( person_matches(nounphrase, verb_agreement) and
                     number_matches(nounphrase, verb_agreement) ):
                    # Yatta! We have a winner...
                    nounphrase.decl = declension
                    break
            else:
                # no dangling nouns match, so we should imply a new noun phrase from the
                # verb (if not caught by another pass, the dangling nouns will be ignored)
                imply_new_noun = True

        if imply_new_noun or ((not explicit_nouns) and (not dangling_nouns)):
            # No likely nounphrases exist, so we'll create a new one
            explicit_nouns.append(self.NounPhrase(verb_agreement.get(sym.G_PERSON, sym.SECOND),
                        number=verb_agreement.get(sym.G_NUMBER, sym.SING), artl=sym.UNDEF ))

        # sloppy mutability semantics, we're both mutating and returning here
        # hopefully this causes no bugs
        return explicit_nouns

                
    def parse_noun_phrase(self, text, location, phrase_results):
        """
        'Grok' a noun phrase.

        Grokking  of  a  noun phrase ensures that  declension,  number,
        definiteness, and any prepositions are understood.

        Returns: fully grokked self.NounPhrase instance
        """
        implicit = phrase_results.getName()
        if implicit:
            implicit = dict(implicit)
        else:
            implicit = {}
        
        phrase_tokens = flatten_parse_results(phrase_results)
        
        phrase = dict([(pos, []) for pos in PoS.Syms])
        phrase[sym.G_NUMBER] = []       

        for pos in phrase:
            if pos in implicit:
                phrase[pos].append(implicit[pos])

        for pos, word in phrase_tokens:
            phrase[pos].append(word)
            #print "%s: %s" % (pos, word)

        phrase_parts = {}
        _update_multimap(phrase_parts, self.grammar.grok_noun(self, phrase.get(sym.NOUN,None) ))
        _update_multimap(phrase_parts, self.grammar.grok_adje(self, phrase.get(sym.ADJE,None) ))
        _update_multimap(phrase_parts, self.grammar.grok_decl(self, phrase.get(sym.DECL,None) ))
        _update_multimap(phrase_parts, self.grammar.grok_prep(self, phrase.get(sym.PREP,None) ))
        _update_multimap(phrase_parts, self.grammar.grok_artl(self, phrase.get(sym.ARTL,None) ))
        _update_multimap(phrase_parts, self.grammar.grok_number(self, phrase.get(sym.G_NUMBER,None) ))
      
        # noun, adjs, decl, prep, artl, plur
        NP = self.NounPhrase(phrase_parts.get(sym.NOUN,(None,))[0])
        NP.set( phrase_parts.get(sym.NOUN,(None,))[0], phrase_parts.get(sym.ADJE,()),
                phrase_parts.get(sym.DECL,(None,))[0], phrase_parts.get(sym.PREP,(None,))[0])

        NP.artl   = NP._specific_article(phrase_parts.get( sym.ARTL, () ) + (sym.UNDEF,) )
        NP.number = NP._specific_number(phrase_parts.get(sym.G_NUMBER,(None,)))

        return NP
        
    def parse_verb_phrase(self, text, location, phrase_results, implicit=None):
        """
        'Grok' a verb phrase.

        Grokking of a verb phrase ensures that tense, mood, valence,
        and noun phrase antecedants are understood.
        
        Returns: fully grokked self.VerbPhrase instance
        """
        if hasattr(phrase_results, 'getName'):
            implicit = phrase_results.getName()
            try:
                implicit = dict(implicit)
            except:
                implicit = {}
        elif not implicit:
            implicit = {}

        phrase_tokens = flatten_parse_results(phrase_results)
        
        phrase = dict([(pos, []) for pos in 
            (sym.VERB, sym.ADVB, sym.VERB_MOOD)]) 
       
        # FIXME: this is where the extra list layer is coming from
        for pos in phrase:
            if pos in implicit:
                phrase[pos].extend(list(implicit[pos]))

        #phrase[sym.VERB_MOOD] = list(phrase.get(sym.VERB_MOOD,())) + list(implicit.get(sym.VERB_MOOD,()))

        for pos, word in phrase_tokens:
            phrase[pos].append(word)
       
        phrase_parts = {}
        _update_multimap(phrase_parts, self.grammar.grok_verb(self, phrase.get(sym.VERB,None) ))
        _update_multimap(phrase_parts, self.grammar.grok_advb(self, phrase.get(sym.ADVB,None) ))
        _update_multimap(phrase_parts, {sym.VERB_MOOD:phrase.get(sym.VERB_MOOD, None)} )

        VP = self.VerbPhrase(phrase_parts.get(sym.VERB,(None,))[0],
                             advs = phrase_parts.get(sym.ADVB,()),
                             moods = phrase_parts.get(sym.VERB_MOOD,()))

        VP.agreements = dict([(k,v) for (k,v) in phrase_parts.items() if k in sym.lookup(sym.DECL)])

        return VP

        

    def set_hooks(self, SentenceParsers, ClauseParsers, NounPhraseParsers, VerbPhraseParsers):
        """
        Set grokking hooks on compound and part-of-speech ParserElements

        Uses the pyparsing.ParserElement.setParseAction method to
        attach the parser methods used to replace pyparsing generated
        string tokens with concept language data objects and use
        grokking functions to fill them in with locale-independant
        information garnered from locale-dependent cues.
        """
        for SentenceParser in SentenceParsers:
            SentenceParser.addParseAction(self.parse_sentence)

        for ClauseParser in ClauseParsers:
            ClauseParser.addParseAction(self.parse_clause)

        for NounPhraseParser in NounPhraseParsers:
            NounPhraseParser.addParseAction(self.parse_noun_phrase)

        for VerbPhraseParser in VerbPhraseParsers:
            VerbPhraseParser.addParseAction(self.parse_verb_phrase)

        for pos in PoS.Syms:
            self.pos_match[pos].addParseAction(TokenFactory(pos))
            self.pos_match[pos].setName(PoS.Sym2Abr[pos].capitalize())


class Locale(LocaleVocabulary, LocaleGrammar, LocaleMessages, Parser):
    """
    This module wraps all of the locale resources for the core engine.

    Doctest for unit testing:

    >>> locale = l10n.Locale('xx')
    >>> locale.show()
<PUB LocaleVocabulary: 'xx' en_US utf-8 LRTB (Test Locale) | #a=10 #A=3 #d=3 #p=2 #N=4 #V=2 >
    >>> from semantics import sym
    >>> locale.concepts['verbs'][sym.HIT]
[<GLOSS: 'hit', cl=None, {'wd': 'hit'}>, <GLOSS: 'tap', cl=None, {'adv': 'INTENSITY:-0.500', 'wd': 'tap'}>, <GLOSS: 'pound', cl=None, {'adv': 'INTENSITY:+0.500', 'wd': 'pound'}>, <GLOSS: 'bash', cl=None, {'adv': 'INTENSITY:+0.600', 'wd': 'bash'}>]

    These test the proper parsing of verb implicit adverb information:

    >>> locale.concepts['verbs'][sym.HIT][0].adv
    SparseVector({}, default=Vague(0.0))
    >>> locale.concepts['verbs'][sym.HIT][1].adv
    SparseVector({<!/PoS/ADVB: INTENSITY>: Vague(-0.5)}, default=Vague(0.0))
    >>> locale.concepts['verbs'][sym.HIT][2].adv
    SparseVector({<!/PoS/ADVB: INTENSITY>: Vague(0.5)}, default=Vague(0.0))
    >>> locale.concepts['verbs'][sym.HIT][3].adv
    SparseVector({<!/PoS/ADVB: INTENSITY>: Vague(0.59999999999999998)}, default=Vague(0.0))
    """
    name = 'xx_XX'
    lang = 'xx'
    region = 'XX'
    encoding = 'utf8'
    direction = 'LRTB'
    language = 'Unknown Language'

    def __init__(self, stem=None, grammar=None, vocabulary=None, messages=None,
                        concept_language_classes=(None, None, None)):
        if not stem:
            stem = config.LOCALE
        
        grammar = stem + ".py"
        vocabulary = stem + ".xml"
        messages_dir = stem

        # Get the core localization (i.e. for the PUB engine itself):
        if os.path.exists(vocabulary):
            self.load_vocabulary(vocabulary)
        else:
            vocab2 = stem.split('_')[0] + '.xml'
            print "File %s does not exist, trying %s." % (vocabulary, vocab2)
            if os.path.exists(vocab2):
                self.load_vocabulary(vocab2)
            else:
                print "No core vocabulary found!"

        if os.path.exists(grammar):
            self.load_grammar(grammar)
        else:
            gramm2 = stem.split('_')[0] + '.py'
            print "File %s does not exist, trying %s." % (grammar, gramm2)
            if os.path.exists(gramm2):
                self.load_grammar(gramm2)
            else:
                print "No core grammar found!"
        
        for msgdir in (messages_dir, stem.split('_')[0]):
            if os.path.exists(msgdir) and os.path.isdir(msgdir):
                self.load_messages(msgdir)
                break
        else:
            # Note that we don't check for actual .mo/.po files
            # just for the directory. Any further checking is
            # left up to gettext
            print "No core messages directory!"

        # Register a copy with the locales dictionary
        locales[stem] = self

        # Interactions between vocabulary, grammar, and/or messages:
        self.get_pos_classifiers()
        self.load_parser(*concept_language_classes)
            

        # FIXME: this is where we should implement the search for game localization files

        # FIXME: fallback behavior for partial locale matchups (e.g. "en.py" is okay for
        #        for use with "en_UK.xml" or "en_US.xml" or "en_US_slang1.xml" etc)


# FIXME: we're going to need unit tests that run the hammer and broom tests


# Unit test:
# (just run the module to test, with "-v" if you want a report even if it passes)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()


