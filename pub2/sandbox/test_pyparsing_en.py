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

Noun = MkSemWord(noun_list, 'Noun') # Noun
Verb = MkSemWord(verb_list, 'Verb') # Verb

        # Straightforward PUB stuff. I believe "Noun" used to be called
        # "BaseThing" though.  Of course, these are the *words* that
        # represent those game objects -- de-referencing will occur
        # after the basic parsing step, and is highly context-dependent.

Prep = MkSemWord(prep_list, 'Prep') # Preposition (strictly topological)
Decl = MkSemWord(decl_list, 'Decl') # Declension markers

        # In traditional English grammar we don't use this term, but it
        # applies to a subset of English prepositions which express what
        # declension does in inflected language.  A Russian, for example,
        # would decline a noun to the "Instrumental" declension in order
        # to express what an English speaker means by prepositions "with"
        # or "using"

        # The other use of prepositions is to express topological containment
        # relationships. Currently PUB is pretty simplistic about this
        # ("in" always equals "on"), but I want to extend this idea a bit
        # to allow more than just "containment". It may not be essential,
        # but I don't yet see any reason why it should be hard.
        
Artl = MkSemWord(artl_list, 'Artl') # Articles: "a", "an", "the" in English
Conj = MkSemWord(conj_list, 'Conj') # Conjunctions

        # Note that as far as this parser is concerned, conjunctions are
        # just delimiters for clauses -- no understanding of their subtler
        # meanings is done.
        
Adje = MkSemWord(adje_list, 'Adje') # Adjectives, modify nouns

        # The function of adjectives in PUB will be disambiguation. If
        # there is a "red button" and a "green button", then noun
        # de-referencing will have to figure out which is meant by
        # examining adjectives.  We want adjectives to always be considered,
        # though, because if you specify "push the red button" and there
        # is only a green button, then the command should fail, not
        # push the wrong button!  (But of course, if the command was
        # simply "push the button", it needs to be de-referenced to
        # the only button visible).

Advb = MkSemWord(advb_list, 'Advb') # Adverbs, modify the verb

        # Adverbs serve no function in PUB as it is, but I am planning for
        # extensions which do make use of them.

NounPhrase = Group(Optional(Decl | Prep) + Optional(Artl) + ZeroOrMore(Adje) + Noun)
NounPhrase.setParseAction(lambda s,l,t: NounPhraseClass(t[0]))

Clause     = Group(ZeroOrMore(Advb) + Verb + ZeroOrMore(Advb | NounPhrase))
Clause.setParseAction(lambda s,l,t: ClauseClass(t[0]))

Sentence   = Group(Clause) + ZeroOrMore( OneOrMore(Conj) + Group(Clause) ) 

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

