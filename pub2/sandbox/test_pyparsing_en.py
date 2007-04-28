#!/usr/bin/env python

from textwrap import dedent
from pyparsing import *

noun_list  = ['broom', 'closet', 'hammer', 'nail', 'broom closet']
verb_list  = ['look at', 'view', 'observe', 'put', 'get', 'drop', 'use', 'hit']
prep_list  = ['in', 'on', 'out of', 'into', 'under', 'over', 'in front of', 'behind', 'to left of', 'to the left of', 'to right of', 'to the right of']
decl_list  = ['from', 'to', 'using', 'with']
artl_list  = ['a', 'an', 'the']
conj_list  = [',', ';', ':', '.', 'and', 'but', 'then', 'next']
adje_list  = ['red', 'green', 'blue', 'brown', 'black', 'white', 'shiny', 'rusty', 'dull']
advb_list  = ['gently', 'firmly', 'quickly', 'slowly', 'very', 'extremely']

class declension(dict):
    """
    Simple 6-part noun declension codes. English has no formal declension, but the
    ideas are still sound (we use special prepositions to mark declension).
    """
    NOM, ACC, DAT, GEN, INS, PRP = range(6)
    def __init__(self):
        for i,val in enumerate(('<subj>', '<dobj>', 'to', 'from', 'with', '<prep>')):
            self[i] = val
        self[None] = '?'

            
declension = declension()
    
decl_map = {'from': declension.GEN,
            'to': declension.DAT,
            'using':declension.INS,
            'with':declension.INS}

class WordClassifier(object):
    """
    This wrapper currently just identifies the part of speech of a word,
    mainly so that output of this script will show you that it has indeed
    figured this information out.
    """
    def __init__(self, wc, w):
        self.classname = wc
        if type(w)==type(''):
            self.name = w
        else:
            self.name = ' '.join(w)
    def __repr__(self):
        return '<%s: %s>' % (self.classname, repr(self.name))

class NounPhraseClass(object):
    """
    Represents a noun phrase in a clause of a sentence, and
    classifies its components.  Does not de-reference the
    noun to a game object, but should make that easier.
    Knows how to extract *explicit* declension, but leaves
    word-order based declension to the Clause handler.
    """
    def __init__(self, phrase):
        self.prep = None
        self.decl = None
        self.artl = None
        self.adje = ()
        self.noun = None
        for word in phrase:
            if word.classname == 'Artl':
                self.artl = word
            elif word.classname == 'Decl':
                self.decl = decl_map[str(word.name)]
            elif word.classname == 'Prep':
                self.prep = word
                if not self.decl:   # Probably unnecessary check?
                    self.decl = declension.PRP
            elif word.classname == 'Adje':
                self.adje += (word,)
            elif word.classname == 'Noun':
                self.noun = word
    def __str__(self):
        return ' '.join( (declension[self.decl], self.prep.name, self.artl.name)
                        + self.adje + (self.noun,))
    def __repr__(self):
        return ("<NounPhrase:decl %s, prep %s, artl %s, adjs(%s), %s>" %
                    (   declension[self.decl],
                        self.prep or 'NONE',
                        self.artl or 'NONE',
                        repr(self.adje),
                        self.noun)) 

def VerbPhraseClass(object):
    """
    Collects the verb phrase information (verb and adverb) in a sentence.
    """
    def __init__(self, verb, adverbs):
        self.adverbs = adverbs
        self.verb = verb
    def __str__(self):
        return ' '.join([a.name for a in self.adverbs] + (verb.name,))
    def __repr__(self):
        return ("<VerbPhrase: verb %s, adverbs %s>" % 
                        (self.verb, repr(self.adverbs)))

def ClauseClass(object):
    """
    Extract phrase description of one clause in a sentence.
    """
    noun_phrases = ()
    def __init__(self, phrases):
        print "WRAPPING CLAUSE OBJECT"
        adverbs = []
        verb = None
        self.noun_phrases = []
        for phrase in phrases:
            if isinstance(phrase, WordClassifier):
                if phrase.classname == 'Advb':
                    adverbs.append(phrase)
                elif phrase.classname == 'Verb':
                    verb = phrase
            elif isinstance(phrase, NounPhraseClass):
                self.noun_phrases.append(phrase)
        self.verb_phrase = VerbPhraseClass(verb, adverbs)
        if self.noun_phrases[0].decl == None:
            self.noun_phrases[0].decl = declension.ACC # implicit direct object
        self.noun_phrases = tuple(self.noun_phrases)
    def __str__(self):
        return (str(self.verb_phrase) + 
                    ' '.join([str(NP) for NP in self.noun_phrases]))
    def __repr__(self):
        return ("<CLAUSE: VP(%s)" % self.verb_phrase +
                    ' '.join(["NP(%s)" % repr(NP) for NP in self.noun_phrases]) +
                        ">")

def MkSemWord(wordlist, word_class):
    """
    Make a semantic 'word' -- i.e. recognize words as belonging to this part 
    of speech by whether they are in the vocabularly list. This allows us
    to classify words.
    """
    SW = Or([Group(And([Keyword(s) for s in w.split()]))
                    for w in wordlist if ' ' in w] +
                        [Keyword(w) for w in wordlist if ' ' not in w])
    SW.setParseAction(lambda s,l,t: WordClassifier(word_class, t[0]))
    return SW

# pre-constructed part-of-speech recognizers -- work on regex-matching of
# vocabularies
Noun = MkSemWord(noun_list, 'Noun') # Noun
Verb = MkSemWord(verb_list, 'Verb') # Verb
Prep = MkSemWord(prep_list, 'Prep') # Preposition (strictly topological)
Decl = MkSemWord(decl_list, 'Decl') # Declension markers
Artl = MkSemWord(artl_list, 'Artl') # Articles: "a", "an", "the" in English
Conj = MkSemWord(conj_list, 'Conj') # Conjunctions
Adje = MkSemWord(adje_list, 'Adje') # Adjectives, modify nouns
Advb = MkSemWord(advb_list, 'Advb') # Adverbs, modify the verb

# These rules are locale-specific & must be provided by locale grammar file
NounPhrase = Group(Optional(Decl | Prep) + Optional(Artl) + ZeroOrMore(Adje) + Noun)
Clause     = Group(ZeroOrMore(Advb) + Verb + ZeroOrMore(Advb | NounPhrase))
Sentence   = Group(Clause) + ZeroOrMore( OneOrMore(Conj) + Group(Clause) )

# These parts are patched on after defining the terms from the locale module
NounPhrase.setParseAction(lambda s,l,t: NounPhraseClass(t[0]))
Clause.setParseAction(lambda s,l,t: ClauseClass(t[0]))
#print Clause.parseString("put the red broom in the blue broom closet")

#print Sentence.parseString("put the red broom in the blue broom closet")

#print Sentence.parseString("""
#hit the hammer with the rusty nail very gently,
#then put the nail in the broom closet 
#and put the hammer in front of the broom closet
#""")

if __name__=='__main__':
    while 1:
        s = raw_input("PUBPARSE>")
        s = s.lower()
        if s[-1]=='.':
            s = s[:-1]
        if s:
            print Sentence.parseString(s)
        else:
            break

