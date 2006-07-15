# (C)2006 Terry Hancock
#------
# en.py
"""
English locale grammar for PUB

It's also the first one written, so I hope it will also serve
as the prototype for others.
"""

from semantics import sym

#------
# GPLv2+
#------
#-------------------------------------------------------------------
# If you want to write a grammar file for your language, please
# read ../doc/developer/l10n.html which will be much more useful
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
#                    from words during parsing
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
#     __str__ method of various objects and thus they determine
#     how the objects serialize.
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
# DECLARE
#   The declare_* functions declare structural information about the
#   language to the parsing and semantics modules. This is used to
#   define the overall behavior of the module.
#
#   So far only one -- which defines the pyparsing expression used

#   to parse sentences in terms of the word elements (which the
#   parser figures out for itself from the vocabulary XML file.
#-------------------------------------------------------------------

def define_sentence_parsers(Verb,Advb,Noun,Adje,Artl,Decl,Prep,Conj,Punc):
    """
    Defines language's grammar for parsing -- note the calling order above should be left as is.

    This isn't really used as a function -- it's a declaration of the basic structure of
    sentences to the parser module.
    """
    # These are pyparsing expressions. They are very similar to EBNF, except that
    # the order of statements is reversed (you must work from bottom-to-top level):
    
    NounPhrase = Group(Optional(Decl | Prep) + Optional(Artl) + ZeroOrMore(Adje) + Noun)
    
    #VerbPhrase -- you may define this if VerbPhrases are contiguous in the target
    #               language (they aren't in English, where adverbs can occur anywhere
    #               in the sentence).
    
    Clause     = Group(ZeroOrMore(Advb) + Verb + ZeroOrMore(Advb | NounPhrase))
    
    Sentence   = Group(Clause) + ZeroOrMore( OneOrMore(Conj) + Group(Clause) )
    
    return NounPhrase, Clause, Sentence


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
    #address_s = str(Sentence.address)
    clauses_s = ', '.join([tell_clause(c) for c in S])
    tense = S[-1].Verb.Tense
    if tense == sym.INT:
        p = '?'
    else:
        p = '.'
     
    return clauses_s + p
    #return ', '.join(address_s, clauses_s) + p
    
def tell_clause(C):
    """
    Generate a clause (a simple sentence).
    """
    VP = C.Verb
    NPs = C.Nouns
    
    if VP.Tense == sym.INT:
        # Interrogative -- generate a question clause:
        sVP = ' '.join([tell_verb_phrase(VP)] + [tell_noun_phrase(n[0]) for n in 
                                [C.Nom, C.Acc, C.Prp, C.Dat, C.Gen, C.Ins] if n])

    elif VP.Tense == sym.EXS:
        # Existential -- there is/there are sentences
        if C.Nom[0].Plur in (sym.SING, sym.ABST, sym.MASS, 1):
            vb = 'is'
            quantifier = 'one'
        elif isinstance(C.Nom[0].Plur, int):
            vb = 'are'
            quantifier = '%d' % C.Nom[0].Plur
        elif C.Nom[0].Plur == sym.DUAL:
            vb = 'are'
            quantifier = 'two'
        else:
            vb = 'are'
            quantifier = ''

        if C.Prp:
            localizer = tell_noun_phrase(C.Prp[0])
        sVP = ' '.join([str(s) for s in ['There', vb, quantifier, tell_noun_phrase(C.Nom[0]), localizer]])
        
    elif VP.Tense == sym.COP:
        # Copula -- sentences specifying equation or description
        if C.Nom[0].number in (sym.SING, sym.ABST, sym.MASS, 1):
            if C.Nom[0].person == sym.FIRST:
                vb = 'am'
            elif C.Nom[0].person == sym.SECOND:
                vb = 'are'
            else:
                vb = 'is'
        else:
            vb = 'are'
        # This is the only use of double nominative case:
        sVP = ' '.join([str(s) for s in [C.Nom[0], vb, C.Nom[1] ]])

    elif VP.Tense in (sym.PPF, sym.PIM):
        # Present perfect or "plain present tense" statements
        sVP = ' '.join([str(s) for s in [C.Nom[0], _conjugate_verb(VP, C.Nom[0])] + NPs[1:]])
        
    elif VP.Tense == sym.IMP:
        # Imperative (command) clause
        sVP = ' '.join([tell_verb_phrase(VP)] + [tell_noun_phrase(N) for N in NPs])
    else:
        sVP = 'CLAUSE(TENSE=?): verb=%s, noun=' % str(VP) + ', '.join([str(s) for s in NPs])

    return sVP

def tell_noun_phrase(NP):
    # Expand a noun phrase
    
    # BTW, this builds the phrase up in reverse, then flips it,
    # to take advantage of appending semantics, and the fact that
    # noun phrases are "strongly left branching" in English

    words = []
    words.append(str(NP.Noun))

    adjs = [str(a) for a in NP.Adjs]
    adjs.reverse()

    words += adjs
    
    if NP.Artl == sym.DEFIN:
        words.append('the')
    elif NP.Artl == sym.INDEF and NP.Plur==sym.SING:
        if words[0][0] in 'aeiouAEIOU':
            words.append('an')
        else:
            words.append('a')

    if NP.Decl == sym.PRP:
        # Prepositional phrase, so look for preposition:
        words.append(str(NP.Prep))
    elif NP.Decl in (sym.NOM, sym.ACC):
        pass
    elif NP.Decl == sym.GEN:
        words.append('from')
    elif NP.Decl == sym.DAT:
        words.append('to')
    elif NP.Decl == sym.INS:
        words.append('with')

    words.reverse()
    return ' '.join(words)
    

def tell_verb_phrase(VP):
    """
    Expand a verb phrase.

    Unit test:
    >>> VP = DummyVP(verb='hit', advs=('very', 'gently'))
    """
    # Expand a verb phrase
    return ' '.join([tell_adverb(A) for A in VP.Advs] + [tell_verb(VP.Verb)])

def tell_adverb(A, clause=None):
    """
    Expand adverb expression to nearest match to adverbial value.
    """
    # FIXME: this assumes we have some stuff I haven't defined yet,
    #       including 'Adverb_Vocabulary' (locale-specific)
    #
    #       It also treats adverbs as Concepts (VagueConcepts), which
    #       I'm not certain is right
    domain_adverbs = [B for B in Adverb_Vocabulary if B.domain==A.domain]
    nearest    = domain_adverbs[0]
    prev_delta = abs(A._data - nearest._data)
    for adverb in domain_adverbs:
        delta = abs(A._data - adverb._data)
        if delta < prev_delta:
            delta = prev_delta
            nearest = adverb
    return str(adverb)

def tell_verb(V, context=()):
    """
    Expand verb word (calls conjugation).
    """
    return '%s(?)' % V.name

def tell_noun(N, context=()):
    """
    Expand noun word (calls declension if needed).
    """
    if context:
        NP, C, S = context
        decl = NP.Decl
    else:
        decl = sym.NOM
        
    if N in Pronoun_Vocabulary:
        s = _decline_noun(N, decl)
    else:
        s = N.name

    return s

#-------------------------------------------------------------------
# UTILITIES
#   You can of course define whatever extra functions you want to
#   use within the module:
#-------------------------------------------------------------------

def _conjugate_verb(V, S):
    if S.Plur != sym.SING and V.Person in (sym.THIRD, sym.FOURTH):
        return V.name
    else:
        return V.name + 's'

def _decline_noun(NP):
    return str(NP.noun)

#-------------------------------------------------------------------
# GROK
#   The grok_* functions define the interpretations of various types
#   of words and grammatical structures from strings. They recognize
#   meanings from words.
#
#   They are not aware of structure above what they are given, so
#   they may return inconclusive in many cases.
#-------------------------------------------------------------------

def grok_sentence():
    # Understand an entire sentence
    # Do we need this?
    pass

def grok_noun_phrase():
    pass

def grok_noun():
    # Identify 
    pass

def grok_verb_phrase():
    # Get various information from a verb phrase
    pass

def grok_verb():
    # info from the verb word itself
    pass

def grok_adjective():
    pass

def grok_adverb():
    pass

def grok_article():
    pass

def grok_declension():
    pass

def grok_preposition():
    pass

#---------------------------------------------------------------------
# Quality Assurance
#---------------------------------------------------------------------

