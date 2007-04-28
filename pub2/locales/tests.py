# (C) 2006 Terry Hancock
#-----------------------------------------
# tests
"""
Tests for locales.

Provides test cases for tell and parse consistency tests.
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
import sys, traceback

import protocols
import textwrap

import l10n

from symbol import *
from vague import SparseVector
from interfaces import *

import pyparsing

from semantics import *

Symbol.verbosity = 0
        
# specific test sentences:

Vocabulary(sym.NOUN,
    {
    'HAMMER': "Tool for hitting things.",
    'NAIL':   "Nail as used to connect wood.",
    'BROOM_CLOSET': "Storage closet for brooms.",
    #'YOU': "2nd person pronoun"
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
    #'EXIST': "Implicit verb in 'there are'."
    })

tell_tests =    {
    'hammer1': ("Hit the nail with the hammer.",
                [SemanticClause(SemanticVerbPhrase(sym.HIT, moods=(sym.VM_IMP,)), 
                    (   SemanticNounPhrase(sym.NAIL,    decl=sym.ACC,   artl=sym.DEFIN), 
                        SemanticNounPhrase(sym.HAMMER,  decl=sym.INS,   artl=sym.DEFIN) ))]
                ),

    'nails1':  ("There are three nails in the broom closet.",
                [SemanticClause(SemanticVerbPhrase(sym.VM_EXS, moods=(sym.VM_EXS,)),
                    (   SemanticNounPhrase(sym.NAIL, decl=sym.NOM, artl=sym.INDEF, number=3),
                        SemanticNounPhrase(sym.BROOM_CLOSET, decl=sym.PRP, prep=sym.IN, 
                            artl=sym.DEFIN, number=sym.SING)))]
                ),

    'hammer2': ("Did the hammer hit the nail?",
                [SemanticClause(SemanticVerbPhrase(sym.HIT, moods=(sym.VM_PPF, sym.VM_INT)), 
                    (   SemanticNounPhrase(sym.NAIL,    decl=sym.ACC,   artl=sym.DEFIN), 
                        SemanticNounPhrase(sym.HAMMER,  decl=sym.NOM,   artl=sym.DEFIN) ))]
                ),
    'hammer3': ("You hit the nail with the hammer.",
                [SemanticClause(SemanticVerbPhrase(sym.HIT, moods=(sym.VM_PPF,)),
                    (   SemanticNounPhrase(sym.SECOND,  decl=sym.NOM,   artl=sym.UNDEF),
                        SemanticNounPhrase(sym.NAIL,    decl=sym.ACC,   artl=sym.DEFIN), 
                        SemanticNounPhrase(sym.HAMMER,  decl=sym.INS,   artl=sym.DEFIN) ))]
                ),
    'nails2':   ("The nails are in the broom closet.",
                [SemanticClause(SemanticVerbPhrase(sym.VM_LOC, moods=(sym.VM_LOC,)),
                    (   SemanticNounPhrase(sym.NAIL,    decl=sym.NOM,   artl=sym.DEFIN, number=sym.PLUR),
                        SemanticNounPhrase(sym.BROOM_CLOSET, decl=sym.PRP, prep=sym.IN,
                           artl=sym.DEFIN, number=sym.SING)))]
                ),
                }

# FIXME:    "The nail is rusty"
#   We have no CL for adjectives worked out yet



parse_tests = dict([(k,(v,e)) for (k,(e,v)) in tell_tests.items()])


def run_tests():

    # TODO:
    # This is sort of dumb, because it's an ad-hoc test runner. I probably should make
    # something that works with pyunit/doctest
    
    # however, this was easier and more fun at the time ;-)

    # Test code:
    failed = 0
    passed = 0
    errors = 0
    
    loc = l10n.Locale('xx', concept_language_classes=(SemanticClause, SemanticNounPhrase, SemanticVerbPhrase))

    print "tell tests..."
    for key, (expected, meaning) in tell_tests.items():
        print "TEST: %s" % key
        print "-"*40
        try:
            actual =  loc.grammar.tell_sentence(meaning)
        
            if not actual == expected:
                print "Failed test %s - Should read:" % repr(key)
                print expected
                print "not:"
                failed += 1
                print "FAIL"
            else:
                passed += 1
                print "PASS"
            print actual
        except:
            errors += 1
            print "Error occured during test:"
            t,e,tb = sys.exc_info()
            print t
            print e
            traceback.print_tb(tb)
        print "-"*40

    print "parse tests..."
    
    for key, (expected, text) in parse_tests.items():
        print "TEST: %s" % key
        print "-"*40
        try:
            actual =  loc.SentenceParser.parseString(text).asList()
        
            if not actual == expected:
                print "Failed test %s - Should read:" % repr(key)
                print expected
                print "not:"
                failed += 1
                print "FAIL"
            else:
                passed += 1
                print "PASS"
            print actual
        except:
            errors += 1
            print "Error occured during test:"
            t,e,tb = sys.exc_info()
            print t
            print e
            traceback.print_tb(tb) 
        print "-"*40
        
    print "%d failed, %d passed, %d errors" % (failed, passed, errors)

if __name__ == '__main__':
    run_tests()
