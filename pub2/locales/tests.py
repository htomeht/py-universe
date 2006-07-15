# (C) 2006 Terry Hancock
#-----------------------------------------
# tests
"""
Tests for locales.

Provides test cases for tell and parse consistency tests.
"""
#-----------------------------------------
# GPLv2+
#-----------------------------------------
import protocols
import textwrap

import l10n

from concept import *
from interfaces import *


# Dummy fixtures for testing:

class TestNP(object):
    """
    Minimal test-rig version of NounPhrase object.

    Here we have just enough to test localized 'tell' functionality.
    We're leaving out the dereferencing mechanism.
    """
    protocols.advise(instancesProvide=[INounPhrase])
    dereferenced = 'labels'
    def __init__(self, *args, **kw):
        self.set(*args, **kw)
    
    def set(self, noun, adjs=(), decl=None, prep=None, artl=None, plur=None):
        self.Noun = noun
        self.Adjs = adjs
        self.Decl = decl
        self.Prep = prep
        self.Artl = artl
        self.Plur = plur
        if self.Decl != sym.PRP:
            self.Prep = None
            
    def __repr__(self):
        return "<NounPhrase: N=%s, a=%s,\n\t\t\t(%s/%s %s #%s)>" % (
                        self.Noun, repr(self.Adjs), self.Decl, self.Prep or '-', self.Artl, self.Plur or '-')

class TestVP(object):
    """
    Minimal test-rig version of VerbPhrase object.

    Here we have just enough to test localized 'tell' functionality.
    We're leaving out the dereferencing mechanism.
    """
    protocols.advise(instancesProvide=[IVerbPhrase])
    dereferenced = 'labels'
    def __init__(self, *args, **kw):
        self.set(*args, **kw)
    
    def set(self, verb, advs=(), tense=sym.IMP, negative=False, person=sym.SECOND, number=sym.SING):
        self.Verb = verb
        self.Advs = advs
        self.Tense = tense
        self.Negative = negative
        self.Person = person
        self.Number = number

    def __repr__(self):
        return "<VerbPhrase: V=%s, A=%s,\n\t\t(%3.3s%1.1s %s person %s)>" % (
                        self.Verb, repr(self.Advs), str(self.Tense), 
                        '-+'[not self.Negative], str(self.Person), str(self.Number) )
                        

class TestClause(object):
    protocols.advise(instancesProvide=[IClause])
    dereferenced = 'labels'
    def __init__(self, VP, NPs):
        self.Verb = VP
        self.Nouns = NPs
        self.Negative = False
        
        # Convenient declension references to the Nouns:
        for decl in sym.lookup(domain=sym.DECL):
            decl_s = str(decl).lower().capitalize()
            setattr(self, decl_s, [N for N in self.Nouns if N.Decl==decl])

    def __repr__(self):
        rep_s = "\n<Clause: %s\n\tVP = %s,\n\tNPs =\n" % ('-+'[not self.Negative], repr(self.Verb))
        nouns = "".join(["\t\t%s\n" % repr(N) for N in self.Nouns])
        tail  = "\t>"
        return rep_s + nouns + tail

        
# Now define specific test sentences:

Vocabulary(sym.NOUN,
    {
    'HAMMER': "Tool for hitting things.",
    'NAIL':   "Nail as used to connect wood.",
    'BROOM_CLOSET': "Storage closet for brooms."
    })

Vocabulary(sym.ADJE,
    {
    'RED':   "Color red.",
    'RUSTY': "Oxidized ferrous metal.",
    'SHINY': "Reflective.",
    'DULL':  "Not very reflective."
    })

Vocabulary(sym.VERB,
    {
    'HIT':  "Strike, hit, or pound.",
    'MOVE': "Relocate an object from place to place.",
    'PUT':  "Relocate an object from inventory.",
    'GET':  "Relocate object to inventory.",
    'EXIST': "Implicit verb in 'there are'."
    })

test_hammer1_s = "Hit the nail with the hammer."
test_hammer1 = [TestClause(TestVP(sym.HIT, tense=sym.IMP), 
                    (   TestNP(sym.NAIL,    decl=sym.ACC,   artl=sym.DEFIN), 
                        TestNP(sym.HAMMER,  decl=sym.INS,   artl=sym.DEFIN) ))]

test_nails1_s = "There are 3 nails in the broom closet."
test_nails1 = [TestClause(TestVP(sym.EXIST, tense=sym.EXS, number=sym.PLUR, person=sym.THIRD),
                    (   TestNP(sym.NAIL, decl=sym.NOM, artl=sym.INDEF, plur=3),
                        TestNP(sym.BROOM_CLOSET, decl=sym.PRP, prep=sym.IN, 
                            artl=sym.DEFIN, plur=sym.SING)))]

