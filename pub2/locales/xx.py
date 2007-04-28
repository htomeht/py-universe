# (C)2006 Terry Hancock
#------
# xx.py
"""
Test grammar (based on English).

It's also the first one written, so I hope it will also serve
as the prototype for others.

Tests:


"""

from l10n import *
from vague import SparseVector
from semantics import sym
from pyparsing import *

NAME = 'xx'

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
#-------------------------------------------------------------------
# If you want to write a grammar file for your language, please
# read ../doc/developer/l10n.html which will be much more complete
# than this comment!
#
# Briefly:
#
#   * This file contains only functions (no OOP)
#
#   * Functions are grouped:
#
#       o 'define_*' single-call factory functions that provide
#                    basic structures to the parser 
#
#       o 'tell_*'   callbacks for output of words & objects
#
#       o 'grok_*'   callbacks to collect grammatical information 
#                    from words or phrases during parsing
#
#       o 'regex_*'  callbacks to get regular expressions to match
#                    words, based on stems provided in vocabulary
#
#       o '_*'       functions used only within this module
#
#   * In practical terms, the grok functions are called by various
#     objects which are themselves "parseActions" of pyparsing
#     expressions. You shouldn't need to know this, but that's how
#     they are used. They do not, however, have a single calling
#     profile, because they extract different kinds of information.
#
#   * The tell functions, on the other hand, are called by the
#     __str__ or __unicode__ methods of various objects and thus 
#     they determine how the objects serialize.
#
#   * Most functions take a keyword argument, "context", which is
#     expected to be a sequence representing the sentence context
#     for the object, e.g.: for an adverb argument, the context
#     is:
#       (the verb phrase, the clause, the sentence)
#
#     while, for an adjective, the context is:
#       (the noun phrase, the clause, the sentence)
#
#     (If you're still confused, there's a diagram in l10n.html)
#
#     The context can be used to provide grammatical "agreements",
#     such as number, person, gender, etc.  It also can be used
#     to tell which inflections should be used for words that
#     need them. This doesn't get used that much in English -- I
#     plan to write a Spanish module that shows it off a bit more.
#-------------------------------------------------------------------
#-------------------------------------------------------------------
# DEFINE
#   The define_* functions define structural information about the
#   language to the parsing and semantics modules. This is used to
#   define the overall behavior of the module.
#
#   So far only one -- which defines the pyparsing expression used
#   to parse sentences in terms of the word elements (which the
#   parser figures out for itself from the vocabulary XML file.
#-------------------------------------------------------------------


_grok_pronouns={'i':    {sym.NOUN:sym.FIRST,  sym.G_NUMBER:sym.SING},
                'we':   {sym.NOUN:sym.FIRST,  sym.G_NUMBER:sym.PLUR},
                'you':  {sym.NOUN:sym.SECOND, sym.G_NUMBER:sym.SING}, # plural you is unused
                'he':   {sym.NOUN:sym.THIRD,  sym.G_NUMBER:sym.SING}, # might need animate and gender
                'she':  {sym.NOUN:sym.THIRD,  sym.G_NUMBER:sym.SING}, # to resolve nouns?
                'it':   {sym.NOUN:sym.THIRD,  sym.G_NUMBER:sym.SING},
                'they': {sym.NOUN:sym.THIRD,  sym.G_NUMBER:sym.PLUR}
                }

_tell_pronouns={(sym.FIRST,sym.SING):   'I',
                (sym.FIRST,sym.PLUR):   'we',
                (sym.YOUandI,sym.PLUR): 'we two',
                (sym.SECOND,sym.SING):  'you',
                (sym.THIRD,sym.SING):   's/he',
                (sym.THIRD,sym.PLUR):   'they',
                (sym.FOURTH,sym.SING):  's/he',
                (sym.FOURTH,sym.PLUR):  'they'}

def define_sentence_parsers(Adje,Advb,Noun,Verb,Artl,Decl,Prep,Conj,Punc,Number):
    """
    Defines language's grammar for parsing -- note the calling order above should be left as is.

    Here we declare the phrase, clause, and sentence level structure of the subset
    of English that our parser will understand.

    Note that our IF parser uses several distinct kinds of 'sentences':
    
    "Imperative"/IMP are really just "commands" to the IF interpreter -
        "Hit the nail with the hammer?"
        
    "Perfective"/PPF are reports of actions -
        "You hit the nail with the hammer."
    
    "Existential"/EXS are reports of existence (e.g. results from "look")
        "There are three nails here."
    
    "Copular"/COP are reports of equality or description
        "The nails are rusty."

    "Locative"/LOC:
        "The nails are in the broom closet."

    All have interrogative (Q) forms:

    "Interrogative Imperative" (Confirmation) / QMP
        "Hit the nail with the hammer?"

    "Interrogative Perfective"/QPF
        "Did you hit the nail with the hammer?"
        "Hit you the nail with the hammer?" (archaic form)

    "Interrogative Existential"/QXS
        "Are there nails here?"
        "Where are the nails?"

    # Note these are really rather different, and might be
    # broken into "Existential" and "Locative" queries --
    # do I want to know if X exists, or the location of
    # X (assuming it exists)?

    "Interrogative Copular"/QCP
        "Are the nails rusty?"
        "Is the nail a ten-penny nail?"

    "Interrogative Locative"/QLC
        "Where are the nails?"

    and negative (N) forms:

    "Negative Imperative" (Don't) / NMP
        "Don't hit the nail."

    "Negative Perfective"/NPF
        "You did not hit the nail."

    "Negative Existential"/NXS
        "There are no nails here."

    "Negative Copular"/NCP
        "The nails are not rusty."

    "Negative Locative"/NLC
        "The nails are not in the broom closet."

    You may notice that some of these forms are infrequent in an IF context, and
    still more generally are only used in parsing or telling (not both). However,
    generality and the fact that agent characters and players are not distinguished
    by the world model, and the need to accurately translate character/player
    interactions is likely to exercise some of the edge cases.

    Nevertheless, we do not attempt to escape the present tense!

    While it is probably possible to do that, it would be extraordinarily
    complex because very different (and complex) schemes of temporal
    tenses exist in different natural languages.
    """
    # These are pyparsing expressions. They are very similar to EBNF, except that
    # the order of statements is reversed (you must work from bottom-to-top level):

    # FORMULAIC / GRAMMATICAL WORDS
    # These are words which are only understood as delimiters for certain types
    # of clauses:
    Did = Or([CaselessKeyword(w) for w in ('did', 'do', 'does')])
    Not = Or([CaselessKeyword(w) for w in ('not', 'no')])
    Dont = (Did + Not) ^ CaselessLiteral("don't")

    #Number = Regex(r'[0-9]*') ^ Or([CaselessLiteral(_spell_number(n)) for n in range(12)])

    There = CaselessKeyword('there')
    Is    = Or([CaselessKeyword(w) for w in ('am', 'is', 'are')])
    Locative = Or([CaselessKeyword(w) for w in ('here', 'there')])
    Where = CaselessKeyword('where')
    
    #VagueQuantifier = Or([CaselessKeyword(w) for w in ('single', 'pair', 'brace', 'couple', 'some', 'several', 'many', 'any')])
    #Quantifier = Number ^ VagueQuantifier
    #Quantifier.setName('G_NUMBER')

    Isnt = (Is + Not) ^ CaselessLiteral("isn't") ^ CaselessLiteral("aren't")
   
    # Isolated noun phrases and declensions other than nominative and accusative,
    # which are indicated by declension-marking prepositions:
    NounPhrase = Group(Optional(Decl ^ Prep) + Optional(Artl) + Optional(Number) + ZeroOrMore(Adje) + Noun)
    
    #VerbPhrase -- you may define this if VerbPhrases are contiguous in the target
    #               language (they aren't in English, where adverbs can occur anywhere
    #               in the sentence).

    # Decorated noun phrases -- used to determine positional declension, used for
    # nominative ("subject") and accusative ("direct object"):
    NP_Nom = annotated(Group(Optional(Artl) + Optional(Number) + ZeroOrMore(Adje) + Noun), DECL=sym.NOM)
    
    NP_Acc = annotated(NP_Nom, DECL=sym.ACC)
    
    NP_Prp = annotated(Group(Prep + Optional(Artl) + Optional(Number) + ZeroOrMore(Adje) + Noun), DECL=sym.PRP)  

    # NOTE on annotated elements
    #
    # In analytic languages (like English), we need the parser to apply annotations
    # to elements to inform the appropriate grok function (of things like
    # the implied declension)
    #
    # The 'annotated(expression, **kw)' function is provided by the l10n module

    # Imperative
    C_IMP = annotated(Group(ZeroOrMore(Advb) + Verb + NP_Acc + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_IMP, sym.VM_POS))

    C_QMP = annotated(Group(ZeroOrMore(Advb) + Verb + NP_Acc + ZeroOrMore(Advb ^ NounPhrase) 
                        + FollowedBy('?')),
        VERB_MOOD=(sym.VM_IMP, sym.VM_INT))

    C_NMP = annotated(Group(Dont + ZeroOrMore(Advb) + Verb + NP_Acc + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_IMP, sym.VM_NEG))
    
    # Perfective
    C_PPF = annotated(Group(NP_Nom + ZeroOrMore(Advb) + Verb + 
                        Optional(NP_Acc) + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_PPF, sym.VM_POS))
                        
    C_NPF = annotated(Group(NP_Nom + ZeroOrMore(Advb) + Did + Not + Verb + 
                        Optional(NP_Acc) + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_PPF, sym.VM_NEG))
                                        
    C_QPF = annotated(Group(Did + NP_Nom + ZeroOrMore(Advb) + Verb + 
                        Optional(NP_Acc) + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_PPF, sym.VM_INT))

    # Imperfective
    C_PIM = annotated(Group(NP_Nom + ZeroOrMore(Advb) + Is + Verb +
                        Optional(NP_Acc) + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_PIM, sym.VM_POS))

                        
    C_QIM = annotated(Group(Is + NP_Nom + ZeroOrMore(Advb) + Verb +
                        Optional(NP_Acc) + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_PIM, sym.VM_INT))


    C_NIM = annotated(Group(Is + NP_Nom + Not + ZeroOrMore(Advb) + Verb +
                        Optional(NP_Acc) + ZeroOrMore(Advb ^ NounPhrase)),
        VERB_MOOD=(sym.VM_PIM, sym.VM_NEG))

                        
    # Existential
    C_EXS = annotated(Group(There + Is + NP_Nom +
                        Optional(Locative) + Optional(NP_Prp)),
        VERB_MOOD=(sym.VM_EXS, sym.VM_POS))

    C_QXS =annotated( Group(Is + There + NP_Nom +
                        Optional(Locative) + Optional(NP_Prp)),
        VERB_MOOD=(sym.VM_EXS, sym.VM_INT))

    C_NXS = annotated(Group(There + Is + Not + NP_Nom +
                        Optional(Locative) + Optional(NP_Prp)),
        VERB_MOOD=(sym.VM_EXS, sym.VM_NEG))


    # Copular
    C_COP = annotated(Group(NP_Nom + Is + (OneOrMore(Adje) ^ NP_Nom)),
        VERB_MOOD=(sym.VM_COP, sym.VM_POS))
    
    C_QCP = annotated(Group(Is + NP_Nom + (OneOrMore(Adje) ^ NP_Nom)),
        VERB_MOOD=(sym.VM_COP, sym.VM_INT))
                        
    C_NCP = annotated(Group(NP_Nom + Isnt + (OneOrMore(Adje) ^ NP_Nom)),
        VERB_MOOD=(sym.VM_COP, sym.VM_NEG))


    # Locative
    C_LOC = annotated(Group(NP_Nom + Is   + (Locative ^ NP_Prp ^ (Locative + NP_Prp)) ),
        VERB_MOOD=(sym.VM_LOC, sym.VM_POS))
        
    C_QLC = annotated(Group(Where + Is   +  (Locative ^ NP_Prp ^ (Locative + NP_Prp)) ),
        VERB_MOOD=(sym.VM_LOC, sym.VM_INT))
        
    C_NLC = annotated(Group(NP_Nom + Isnt + (Locative ^ NP_Prp ^ (Locative + NP_Prp)) ),
        VERB_MOOD=(sym.VM_LOC, sym.VM_NEG))

    # An isolated clause may be of any one of the above types (or 'moods')

    Moods =[C_IMP, C_PPF, C_PIM, C_EXS, C_COP, C_LOC,
            C_QMP, C_QPF, C_QIM, C_QXS, C_QCP, C_QLC,
            C_NMP, C_NPF, C_NIM, C_NXS, C_NCP, C_NLC]

    Clause = Or(Moods)

    # Sentences may be made of any of the above kinds of clauses, but all clauses
    # in a sentence must be of the same kind:
    
    Sentence   = Or([C + ZeroOrMore(OneOrMore(Conj) + C)
                        for C in (Moods)])
    
    return [NounPhrase, NP_Nom, NP_Acc, NP_Prp], [], [Clause], [Sentence]

def define_classifiers():
    """
    Define the basic part-of-speech classifiers.

    This will be ORed with a set based on the locale vocabulary.
    """
    Artl = Or([CaselessKeyword(w) for w in ('a','an','the')])
    Adje = None
    Advb = None
    Noun = Or([CaselessKeyword(w) for w in ('I', 'you', 'he', 'she', 'it', 
                                            'him', 'her', 'me',
                                            'we', 'they',
                                            'us', 'them')])
    Verb = Or([CaselessKeyword(w) for w in ('is', 'are', 'am', 'be',
                                            'do', 'does')])
    Decl = Or([CaselessKeyword(w) for w in ('to', 'using', 'with', 'toward', 'towards', 'from')])
    Prep = None
    Conj = Or([CaselessKeyword(w) for w in ('and', 'but', 'or', 'then')])
    Punc = Regex(r'.,;:?!-')
    
    ExplicitNumber = Regex(r'[0-9]*') ^ Or([CaselessKeyword(_spell_number(n)) for n in range(12)])

    VagueQuantifier = Or([CaselessKeyword(w) for w in ('single', 'pair', 'brace', 'couple', 'some', 'several', 'many', 'any')])
    Number = ExplicitNumber ^ VagueQuantifier
    
    return Adje,Advb,Noun,Verb,Artl,Decl,Prep,Conj,Punc,Number

def define_inflections(pos, gloss):
    """
    For a given word stem and part-of-speech, return a string or pyparsing/regex expression
    that matches all recognized forms of the word (i.e. inflections).

    Return value will be wrapped to make it a pyparsing expression if it is a regex or a string.
    """
    if _isregular(gloss):
        stem = gloss.wd
        if pos in (sym.VERB, sym.NOUN):
            return Or([CaselessLiteral(w) for w in (stem, stem+'s')])
        #elif pos in (sym.ARTL,):
        #    return None
        else:
            return stem
    else:
        # no irregular glosses at this time
        pass
    return None

def _isregular(gloss):
    """
    Return false for glosses with special forms that need to be recognized.
    """
    return True

# It will be a PUB error for a sentence to contain clauses with different tenses,
# so there's no need to worry about this case -- checking the tense of the last
# clause in the Clauses list tells the tense of all.

#-------------------------------------------------------------------
# TELL
#
#   The 'tell_*' functions define locale-specific str() callbacks
#   for their respective objects. At the highest levels, these
#   result in more str() calls for lower elements, which in turn
#   call additional tell functions until we get to linguistic atoms.
#-------------------------------------------------------------------

def tell_sentence(S):
    #address_s = str(S.address)
    clauses_s = ', '.join([tell_clause(C, (S,)) for C in S])
    if S[-1].verb_phrase.question:
        p = '?'
    else:
        p = '.'

    sentence = clauses_s + p
    sentence = sentence[0].capitalize() + sentence[1:]
    return sentence


def tell_clause(C, context=()):
    """
    Generate a clause (a simple sentence).
    """
    VP = C.verb_phrase
    NPs = C.noun_phrases
    cx = (C,)+context
    
    if VP.question:
        # print "tell_clause, INT"
        # Interrogative -- generate a question clause:
        sVP = ' '.join(['Did'] + [tell_noun_phrase(C.nom[0], cx)] +
                    [tell_verb_phrase(VP, cx)] +
                            [tell_noun_phrase(n[0], cx) for n in 
                                [C.acc, C.prp, C.dat, C.gen, C.ins] if n])

    elif VP.mood == sym.VM_EXS:
        # print "tell_clause, EXS"
        # Existential -- there is/there are sentences
        if C.nom[0].number in (sym.SING, sym.ABST, sym.MASS, 1):
            vb = 'is'
            quantifier = 'one'
        elif isinstance(C.nom[0].number, int):
            vb = 'are'
            quantifier = _spell_number(C.nom[0].number)
        elif C.nom[0].number == sym.DUAL:
            vb = 'are'
            quantifier = 'two'
        else:
            vb = 'are'
            quantifier = ''

        if C.prp:
            localizer = tell_noun_phrase(C.prp[0], cx)
        sVP = ' '.join([str(s) for s in ['There', vb, quantifier, tell_noun_phrase(C.nom[0], cx), localizer]])
        
    elif VP.mood == sym.VM_COP:
        # print "tell_clause, COP"
        # Copula -- sentences specifying equation or description
        if C.nom[0].number in (sym.SING, sym.ABST, sym.MASS, 1):
            if C.nom[0].person == sym.FIRST:
                vb = 'am'
            elif C.nom[0].person == sym.SECOND:
                vb = 'are'
            else:
                vb = 'is'
        else:
            vb = 'are'
        # This is the only use of double nominative case:
        sVP = ' '.join(tell_noun(s, cx) for s in [C.nom[0], vb, C.nom[1]])

    elif VP.mood in (sym.VM_PPF, sym.VM_PIM):
        # print "tell_clause, PPF/PIM"
        # Present perfect or "plain present tense" statements
        sVP = ' '.join( [tell_noun_phrase(C.nom[0], cx)] +
                        [tell_verb_phrase(VP,cx)] +
                        [tell_noun_phrase(n, cx) for n in NPs[1:]])
        
    elif VP.mood == sym.VM_IMP:
        # print "tell_clause, IMP"
        # Imperative (command) clause
        sVP = ' '.join([tell_verb_phrase(VP, cx)] + [tell_noun_phrase(N, cx) for N in NPs if N.decl!=sym.NOM])
    else:
        # print "tell_clause, default"
        sVP = 'CLAUSE(TENSE=?): verb=%s, noun=' % str(VP) + ', '.join([str(s) for s in NPs])

    return sVP


def tell_noun_phrase(NP, context=()):
    # Expand a noun phrase
    
    # BTW, this builds the phrase up in reverse, then flips it,
    # to take advantage of appending semantics, and the fact that
    # noun phrases are "strongly left branching" in English

    cx = (NP,) + context

    words = []
    words.append(tell_noun(NP.noun, cx)[0])

    adjs = [str(a) for a in NP.adjs]
    adjs.reverse()

    words += adjs
    
    if NP.artl == sym.DEFIN:
        words.append('the')
    elif NP.artl == sym.INDEF and NP.number==sym.SING:
        if words[0][0] in 'aeiouAEIOU':
            words.append('an')
        else:
            words.append('a')

    if NP.decl == sym.PRP:
        # Prepositional phrase, so look for preposition:
        words.append(_tell_prep(NP.prep))
    elif NP.decl in (sym.NOM, sym.ACC):
        pass
    elif NP.decl == sym.GEN:
        words.append('from')
    elif NP.decl == sym.DAT:
        words.append('to')
    elif NP.decl == sym.INS:
        words.append('with')

    words.reverse()
    return ' '.join(words)
    

def tell_verb_phrase(VP, context=()):
    """
    Expand a verb phrase.

    Unit test:
    >>> VP = DummyVP(verb='hit', advs=('very', 'gently'))
    """
    # Expand a verb phrase
    cx = (VP,) + context
    return ' '.join([tell_adverb(A, cx) for A in VP.advs] + [tell_verb(VP.verb, cx)[0]])

def tell_adverb(A, context=()):
    """
    Expand adverb expression to nearest match to adverbial value.

    A - adverb (symbol.VagueConcept instance)
    """
    locale = locales[NAME]
    #adverbial_phrase = locale.resolve_adverb(A, tolerance=tolerance)
    adverbial_phrase = A
    phrases = []
    for domain_phrase in adverbial_phrase.values():
        domain_phrase = list(domain_phrase)
        domain_phrase.reverse()
        phrases.append(' '.join([g.wd for g in domain_phrase]))

    return ', '.join([p for p in phrases if p])


def tell_verb(V, context=()):
    """
    Expand verb word (calls conjugation).
    """
    if context:
        VP, C, S = context
        adverbs = VP.advs
        mood   = VP.mood

        # FIXME: need to fix person/number collection
        # verb forms depend on the person and number of the subject
        # of the sentence (the nominative case noun)
        #person  = VP.person[sym.NOM]
        #number  = VP.number[sym.NOM]
        person  = sym.SECOND
        number  = sym.SING       
    else:
        adverbs = SparseVector()
        mood    = sym.VM_PPF
        person  = sym.SECOND
        number  = sym.SING
        
    verb_gloss, remainders = locales[NAME].resolve_verb(V, adverbs)

    return _conjugate_verb(verb_gloss, mood, person, number), remainders


def tell_noun(N, context=()):
    """
    Expand noun word (calls declension if needed).
    """
    if context:
        NP, C, S = context
        number   = NP.number
    else:
        number   = sym.SING

    if (N,number) in _tell_pronouns:
        return _tell_pronouns[(N,number)], {}
    
    # print locales[NAME].concepts['nouns'][N][0]
    
    gloss = locales[NAME].concepts['nouns'][N][0]
    wd    = gloss.wd
    
    if not hasattr(gloss, 'pl'):
        # regular plurals
        if wd[-1]=='s':
            pl = wd + 'es'
        else:
            pl = wd + 's'
    else:
        # irregular plurals
        pl = gloss.pl

    if number != sym.SING:
        return pl, {}
    else:
        return wd, {}


def tell_adjective(a, context=()):
    """
    Expand adjective.

    English has no adjective inflections, so this is just a look-up.
    """
    return locales[NAME].adjectives[a][0].wd
    

#-------------------------------------------------------------------
# UTILITIES
#   You can of course define whatever extra functions you want to
#   use within the module:
#-------------------------------------------------------------------

def _conjugate_verb(V, tense, person, number):
    if not V.cl:    # Regular conjugation
        if number == sym.SING and person in (sym.THIRD, sym.FOURTH):
            return V.wd + 's'
        else:
            return V.wd
    else:
        print "FIXME: no irregular verb handling yet"

def _spell_number(n):
    if n > 1000:
        m = n
        thous = []
        while m > 1000:
            thous.append(m % 1000)
            m /= 1000
        return str(m) + ',' + ','.join(["%3.3d" % t for t in thous])
    elif n > 12:
        return str(n)
    else:
        return ('zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                'eight', 'nine', 'ten', 'eleven', 'twelve')[n]

def _read_number(s):
    # strip commas
    s = ''.join(s.split(','))
    try:
        n = int(s)
    except ValueError:
        try:
            n = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
                'eight', 'nine', 'ten', 'eleven', 'twelve'].index(s)
        except ValueError:
                n = None
    return n

def _read_quantifier(s):
    # first see if it's a number
    n = _read_number(s)
    if not n:
        # now try vague quantifiers
        if s in ('some', 'several', 'many', 'any'):
            n = sym.PLUR
        elif s in ('single',):
            n = sym.SING
        elif s in ('pair', 'brace', 'couple'):
            n = sym.DUAL
    return n
    
            
def _tell_prep(prep):
    return str(prep).lower()

#-------------------------------------------------------------------
# GROK
#   The grok_* functions define the interpretations of various types
#   of words and grammatical structures from strings. They recognize
#   meanings from words.
#
#   They are not aware of structure above what they are given, so
#   they may return inconclusive in many cases.
#
#   The first argument is always the locale object, which can be used
#   to access vocabulary information.
#-------------------------------------------------------------------

def grok_sentence(loc, tokens):
    # Understand an entire sentence
    # Do we need this?
    pass

def grok_noun_phrase(loc, tokens):
    pass

def grok_verb_phrase(loc, tokens):
    # Get various information from a verb phrase
    pass

def grok_number(loc, tokens):
    result = {}
    for i in range(len(tokens)):
        if type(tokens[i]) in (str, unicode):
            try:
                result[sym.G_NUMBER] = _read_quantifier(tokens[i])
            except KeyError:
                pass
    #print "grok_number: result=", result
    return result

def grok_noun(loc, tokens):
    result = {}
    for i in range(len(tokens)):
        if type(tokens[i]) in (str, unicode):
            if tokens[i].lower() in _grok_pronouns:
                return _grok_pronouns[tokens[i]]
            try:
                result[sym.NOUN] = (loc.nouns[tokens[i]],)
                result[sym.G_NUMBER] = sym.SING
            except KeyError:
                if tokens[i][-3:] == 'ses':
                    result[sym.NOUN] = (loc.nouns[tokens[i][:-2]],)
                    result[sym.G_NUMBER] = sym.PLUR
                elif tokens[i][-1] == 's':  
                    result[sym.NOUN] = (loc.nouns[tokens[i][:-1]],)
                    result[sym.G_NUMBER] = sym.PLUR 
    return result

    
##
##def grok_verb():
##    # info from the verb word itself
##    pass
##
##def grok_adje():
##    pass
##
##def grok_advb():
##    pass
##
##def grok_artl():
##    pass


def grok_decl(loc, tokens):
    for i in range(len(tokens)):
        if type(tokens[i]) in (str, unicode):
            tokens[i] = loc.declensions.get(tokens[i], sym.PRP)
    return {sym.DECL:tokens}
    
##
##def grok_prep():
##    pass
##
#---------------------------------------------------------------------
# Quality Assurance
#---------------------------------------------------------------------

