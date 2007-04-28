#(C)2006 Terry Hancock
#--------------------------------------------------------------------
# Semantics
"""
The NEW, IMPROVED 2006 pyparsing-based localizable parser for
Python Universe Builder.

Used to be called 'parser', until I realized that shadows the stdlib
module. It's also slightly more accurate since this module includes
both parsing and generating of sentences to/from semantic forms.

This is pretty much a complete rewrite of the old parser, and is based
on pyparsing.  It is much more conceptual and high-level than the old
parser (pyparsing does the "heavy-lifting" now), and this aides in
designing for internationalization, increases the flexibility of expression,
and eases integration of PUB as a logic engine for graphical games
as well as for interactive fiction games.

Like the new locale system, this module derives somewhat from a study
of the basic grammar of a range of world-languages, and I will occasionally
make reference to these to explain why certain features are needed, or
where the idea comes from.

The module uses "stateful grammar objects" which move from "lexical" to
"syntactical" to "semantic" during successive de-referencing operations.
(We could've created new objects at each layer, but our chosen approach
requires less confusing nomenclature -- e.g. a "NounPhrase" is
initially:

  - a string
  - then a series of lexical tokens
  - then a syntax object with attributes based on the tokenization,  
  - then a semantic object, with attributes de-referenced to PUB world-objects

Once a complete clause has been de-referenced to the semantic state,
it has succeeded as a "meaningful sentence or command". At that point,
it can be "dispatched" -- passed into pub for execution, depending on
how the world-model objects respond to it.

This module also includes a language *generator*, and in fact, the same
semantic objects are all designed to be reversible -- they can be re-referenced

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
# Most common types of part-of-speech values

import textwrap
from symbol import *
from vague import SparseVector
import random
from noun import Noun, Adjective
#from verb import Verb, AdverbDomain, Adver
import vocabulary
import protocols
from interfaces import *

# Symbolic vocabularies

Symbol('PoS',       doc="Part of Speech")
Symbol('SCOPE',     doc="Extent and place of search among program objects.")
Symbol('VERB_MOOD', doc="Tense (including aspect and mood) of a sentence or phrase.")
Symbol('G_NUMBER',  doc="Grammatical number of a noun.")
Symbol('G_PERSON',  doc="Grammatical 'person' 1st - 4th.")
Symbol('SENSES',    doc="Senses to which adjectives apply.")

part_of_speech = Enum(sym.PoS, {
        'NOUN':'Noun',
        'VERB':'Verb',
        'ADVB':'Adverb - modifies Verb',
        'ADJE':'Adjective - specifies Noun',
        'DECL':'Declension particle or marker (certain prepositions in English)',
        'PREP':'Preposition - Topological only, specify location relative to Noun',
        'ARTL':'Article - specifies definiteness of Noun (most Indo-European languages)',
        'CONJ':'Conjunction - solely used as a delimiter in PUB',
        'PUNC':'Punctuation symbols' })

scope = Enum(sym.SCOPE, {
        'SUBJ_SELF':'Contains only the subject character or actor.',
        'THIS_ROOM':'Objects within the room of the context character.',
        'INVENTORY':'Objects contained by the character.',
        'ABSTRACTS':'Abstract objects (no in-model object referrant).',
        'CHARACTER':'Only people (characters) in THIS_ROOM.',
        'EVERYBODY':'Every agent (character) in the game.',
        'UNIVERSE' :'All objects in game universe.' })

decl_cases = Enum(sym.DECL, {
        'NOM':'Nominative or Subject Case of Noun',
        'ACC':'Accusative or Direct Object Case of Noun',
        'DAT':'Dative or "to" Indirect Object.',
        'GEN':'Genitive or "from" Indirect Object.',
        'INS':'Instrumental or "with"/"using" Indirect Object.',
        'PRP':'Prepositional case, used with "topological" prepositions, e.g. "in", "on"' })

decl_order = [sym.NOM, sym.ACC, sym.DAT, sym.GEN, sym.INS, sym.PRP, None]

tense = Enum(sym.VERB_MOOD, {
        'VM_IMP':'Imperative = Command',      
        'VM_PPF':'Present Perfective = Report completed action',       
        'VM_PIM':'Present Imperfective = Report ongoing action',
        'VM_COP':'Copular = Report equality, membership, or properties',
        'VM_EXS':'Existential = Report existance "there are..."',
        'VM_LOC':'Locative = Report location',
        'VM_NEG':'Negative modifier',
        'VM_POS':'Positive modifier',
        'VM_INT':'Interrogative modifier'})
        
article = Enum(sym.ARTL, {
        'UNDEF':'Undefined - definiteness not known, unclear, or unspecified.',
        'INDEF':'Indefinite - "a", any available object identified with noun.',
        'DEFIN':'Definite - "the", particular instance of a noun.',
        'QUANT':'Quantity - "some", quantity of a mass noun.',
        'ABSTR':'Abstract - abstract, therefore uncountable noun.' })

number  = Enum(sym.G_NUMBER, {
        'SING':'Singular - same as 1',
        'DUAL':'Dual - same as 2',
        'PLND':'Plural + Non-Dual (3 or more)',
        'PLUR':'Plural (2 or more)',
        'MASS':'Mass noun (uncountable except with units)',
        'ABST':'Abstract noun (uncountable in principle)' })
        # Plurals may also be expressed by explicit number, but that's just an int type

person  = Enum(sym.G_PERSON, {
        'FIRST':  "First person, 'I' or 'we'",
        'SECOND': "Second person, 'you'",
        'THIRD':  "Third person, 'he/she/it/they'. 'Proximate' when appropriate.",
        'FOURTH': "Fourth person or 'obviative', when appropriate.",
        'YOUandI':"Inclusive 1st+2nd 'you and I'" })

topopreps = Vocabulary(sym.PREP, {
        'IN': "Inside of, contained within.",
        'ON': "On top of. Supported by.",
        'ABOVE': "Above the object, not necessarily supported by it.",
        'BELOW': "Below. Underneath.",
        })

senses = Vocabulary(sym.SENSES, {
        'VISIBLE':  "Responds to 'LOOK' sense verb.",
        'AUDIBLE':  "Responds to 'LISTEN' sense verb.",
        'FEELABLE': "Responds to 'FEEL' sense verb (implied by TOUCH).",
        'SMELLABLE':"Responds to 'SMELL' sense verb.",
        'TASTABLE': "Responds to 'TASTE' sense verb (implied by EAT or DRINK)."
        })

class AdjectiveVocabulary(Vocabulary):
    """
    Adjective vocabulary factory. Creates adjective symbols and constructs Adjective
    objects as well.
    
    Takes into account sense domains and prefixes overlapping meanings accordingly.
    """
    # Domains are associated with sense-verbs:
    sense = {sym.VISIBLE:'V', sym.AUDIBLE:'A', sym.FEELABLE:'F', sym.SMELLABLE:'S', sym.TASTABLE:'T'}
    sense_inv = dict([(v,k) for k,v in sense.items()])

    def update(self, names, doc=None):
        """
        Update the list of names.
        """
        if self.domain not in self.sense.keys():
            raise ValueError, "Adjective domain must be a sense: %s" % repr([s.name for s in self.sense.keys()])

        # This is a little bit ugly, but it allows us to reuse the code better. The
        # domain passed to AdjectiveVocabulary is the SENSE to which the adjective
        # will respond. The actual adjective symbols domain is always PoS/ADJE. The
        # sense domain is a property of the PUB Adjective object, which we create
        # as a side-effect of create the adjective symbol.
        
        sense = self.domain
        self.domain = sym.ADJE
            
        if self._lock: raise TypeError, "Immutable"

        if not doc:
            doc = self.doc
        
        data = []
        if type(names)==dict:
            for n in names:
                try:
                    data.append(Symbol(n, self.domain, names[n] + doc))
                except AttributeError:
                    data.append(Symbol(self.sense[sense]+'_'+n, self.domain, names[n] + doc))               
        elif hasattr(names, '__iter__'):
            for n in names:
                try:
                    data.append(Symbol(n, self.domain, doc))
                except AttributeError:
                    data.append(Symbol(self.sense[sense]+'_'+n, self.domain, doc))
        else:
            raise ValueError, "Vocabulary words must be in a collection object."

        for adj in data:
            vocabulary.All_Adjectives[adj] = Adjective(adj, sense=sense)

        self._data = {}
        if data is not None:
            self._update(data)


class SemanticNounPhrase(object):
    """
    Noun Phrase

    Semantic representation of a grammatical object specifying a
    noun and its relationship to a clause of a sentence.
 
    @ivar noun: None | unicode | Vocabulary PoS/NOUN | Noun | [Noun,...]
    @ivar plur:	None | unicode | Enum NUMBER 
    @ivar decl:	None | unicdoe | Enum PoS/DECL
    @ivar prep:	None | unicode | Vocabulary PoS/PREP
    @ivar artl:	None | unicode | Enum PoS/ARTL
    @ivar adjs:	None | [unicode,...] | [Vocabulary PoS/ADJE,...] 
    """
    noun = None
    decl = None
    prep = None
    artl = None
    adjs = ()
    number = None
    
    protocols.advise(instancesProvide=[INounPhrase])
    dereferenced = 'labels'
    def __init__(self, *args, **kw):
        self.set(*args, **kw)
    
    def set(self, noun, adjs=(), decl=None, prep=None, artl=sym.UNDEF, number=None):
        if not number:
            number = sym.SING

        self.noun = noun
        self.adjs = adjs
        self.decl = decl
        self.prep = prep
        self.artl = artl
        self.number = number
        if self.decl != sym.PRP:
            self.prep = None
            
    def __repr__(self):
        return "<NounPhrase: N=%s, a=%s,\t(%s/%s %s #%s)>" % (
                        self.noun, repr(self.adjs), self.decl,
                        self.prep or '-', self.artl, self.number or '-')

    def __eq__(self, other):
        """
        Value-based comparison of phrases.
        """
        if isinstance(other, SemanticNounPhrase):
            return  (   self.noun == other.noun and
                        self.decl == other.decl and
                        self.prep == other.prep and
                        self.adjs == other.adjs and
                        self._match_article(self.artl, other.artl) and
                        self._match_number(self.number, other.number) )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _cmp_article(self, j, k):
        for a,b,more_general in ((j,k,-1),(k,j,1)):
            if a==b:
                return 0
            if a in (sym.UNDEF, None):
                return more_general
        raise ValueError("Articles %s and %s conflict." % (j,k) )

    def _match_article(self, j, k):
        """
        Determine whether two definiteness articles match.
        """
        try:
            v = self._cmp_article(j,k)
            if v==1:
                return 2
            else:
                return 1
        except ValueError:
            return 0
    
    def _general_article(self, articles):
        """
        Select more general of two articles.
        """
        if articles:
            articles = list(articles[:])
            articles.sort(self._cmp_article)
            return articles[0]
        else:
            return None

    def _specific_article(self, articles):
        """
        Select more specific of two articles.
        """
        if articles:
            articles = list(articles[:])
            articles.sort(self._cmp_article)
            return articles[-1]
        else:
            return None

    def _cmp_number(self, j, k):
        for a,b,more_general in ((j,k,-1),(k,j,1)):
            if a==b:
                return 0
            elif a==None:
                return more_general
            elif a==sym.PLUR and (b in (sym.PLUR, sym.PLND, sym.DUAL) or (type(b)==int and b > 1)):
                return more_general
            elif a==sym.PLND and (b==sym.PLND or (type(b)==int and b > 2)):
                return more_general
            elif a==sym.DUAL and b in (sym.DUAL, 2):
                return more_general
            elif a==sym.SING and b in (sym.SING, 1):
                return more_general
        raise ValueError("Grammatical numbers %s and %s conflict." % (j,k) )

    def _match_number(self, j, k):
        """
        Determine whether two grammatical numbers are equivalent.

        returns 0, 1, or 2
        0 - means the two numbers conflict
        1 - means the two numbers are compatible, j implies k (or j iff k)
        2 - means the two numbers are compatible, k implies j (and not the reverse)
        """
        try:
            v = self._cmp_number(j,k)
            if v==1:
                return 2
            else:
                return 1
        except ValueError:
            return 0

    def _general_number(self, numbers):
        """
        Select more general of two grammatical numbers.
        """
        if numbers:
            numbers = list(numbers[:])
            numbers.sort(self._cmp_number)
            return numbers[0]
        else:
            return None

    def _specific_number(self, numbers):
        """
        Select the more exact of two grammatical numbers.
        """
        if numbers:
            numbers = list(numbers[:])
            numbers.sort(self._cmp_number)
            return numbers[-1]
        else:
            return None 

    def addAdje(self, adje):
    	"""
        Add an adjective to the noun phrase.
        """
    	self.adjs.append(adje)
                
                    
class SemanticVerbPhrase(object):
    """
    Verb Phrase or Predicate of sentence, includes verb and adverb(s).

    @ivar verb: None | unicode | symbol
    @ivar advs: () | tuple of unicode
    @ivar adverbs: dict of Adverb instances
    @ivar mood: mood or tense of verb
    @ivar negative: Boolean, is verb negated?
    @ivar question: Boolean, is verb interrogative?
    @ivar dereferenced: dereferencing state
    @ivar agreements: noun agreements (used during parsing)
    """
    verb = None
    advs = SparseVector()
    adverbs=None    # FIXME: role of "advs" vs "adverbs"?
    mood = None
    negative = False
    question = False
    dereferenced = 'labels'
    
    agreements = None

    protocols.advise(instancesProvide=[IVerbPhrase])

    def __init__(self, *args, **kw):
        self.set(*args, **kw)
    
    def set(self, verb, advs=None, moods=(sym.VM_IMP, sym.VM_POS)):
        if not advs:
            advs = SparseVector()
            
        self.verb = verb
        self.advs = advs
        for mood in moods:
            if mood in (sym.VM_IMP, sym.VM_PPF, sym.VM_PIM, sym.VM_COP, sym.VM_LOC, sym.VM_EXS):
                self.mood = mood
                break
        else:
            self.mood = sym.VM_IMP
        
        for mood in (sym.VM_COP, sym.VM_LOC, sym.VM_EXS):
            if mood in moods:
                self.verb = mood
                break

        if sym.VM_NEG in moods:
            self.negative = True
        else:
            self.negative = False

        if sym.VM_INT in moods:
            self.question = True
        else:
            self.question = False
            
        self.advb_remainders = {}
            

    def __repr__(self):
        return "<VerbPhrase: V=%s, A=%s,\t(%3.3s%1.1s%1.1s)>" % (
                        self.verb, repr(self.advs), str(self.mood)[3:], 
                        '-+'[not self.negative], '.?'[self.question] )
                        
    def __eq__(self, other):
        """
        Value-based comparison of phrases.
        """
        if isinstance(other, SemanticVerbPhrase):
            return  (   self.verb == other.verb and
                        self.advs == other.advs and
                        self.mood == other.mood and
                        self.negative == other.negative and
                        self.question == other.question )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
    
    def _dereference_adverbs(self):
        if not adverbs:
            # First we consider the adverbs in runs
            # We don't deal with multiple adverbial phrases (yet),
            # additional words are assumed to modify the adverb's value.
            adverb_words = ' '.join(self.advs)
            domain, value = locale.grok_adverb(adverb_words)
            self.adverbs[domain] =  value

    def _dereference_verb(self):
        if type(verb) in (str, unicode):
            # Consider synonym impact on adverbial value
            verb, domain, value = locale.grok_verb(verb)
            self.verb = verb
            self.adverbs[domain] =  value


class SemanticClause(object):
    """
    Independent clause. A complete simple sentence with a verb phrase and one or more nounphrases.
    """
    # implements IClause
    protocols.advise(instancesProvide=[IClause])

    dereferenced = 'labels'
    def __init__(self, VP, NPs):
        self.verb_phrase = VP
        self.noun_phrases = list(NPs)
        
        # Convenient declension references to the Nouns:
        for decl in sym.lookup(domain=sym.DECL):
            decl_s = str(decl).lower()
            setattr(self, decl_s, [N for N in self.noun_phrases if N.decl==decl])
        
        if not self.nom:
            self.noun_phrases.append(SemanticNounPhrase(sym.SECOND, number=sym.SING, decl=sym.NOM))
            self.nom = self.noun_phrases[-1]

        self.noun_phrases.sort(lambda a,b: cmp(decl_order.index(a.decl), decl_order.index(b.decl)) )

    def __repr__(self):
        rep_s = "\n<Clause: %s\n\tVP = %s,\n\tNPs =\n" % ('-+'[not self.verb_phrase.negative],
            repr(self.verb_phrase))
        nouns = "".join(["\t\t%s\n" % repr(N) for N in self.noun_phrases])
        tail  = "\t>"
        return rep_s + nouns + tail

    def __eq__(self, other):
        if isinstance(other, SemanticClause):
            return  (   self.verb_phrase == other.verb_phrase and
                        self.noun_phrases == other.noun_phrases)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class Sentence(list):
    """
    A Sentence is an optional Address followed by a list of one or more clauses.
    """
    protocols.advise(instancesProvide=[ISentence])
    



