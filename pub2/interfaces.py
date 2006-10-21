#   interfaces.py    contains interfaces for PUB         04/03/24  GJ
#
#   Copyright (C) 2004 Gabriel Jagenstedt
#
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
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# CHANGELOG
#
#   2006-06/26: Terry Hancock
#       Interfaces for semantics objects.
#
#   2004-10/22: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#---------------------------------------------------------------------
"""
This module should contain all interfaces for pub. An interface is a class
which documents how other classes or class instances should work. 
For instance the interface IOpenL documents functions that must be 
supported by objects like doors and books to be funtional. 
The interfaces are in alphabetical order.

We use interfaces by using advise to make an object support the protocol.
like so:

class Test(pub.core.Component):
    advise(instancesProvide=[IOpenL])

This makes a component which we can add as a part of gameobjects.


Interfaces have a very basic set of methods, these MUST be provided in 
components. They don't have to do anything more than just calling 
chain.next(). You can also have methods raising specific errors depending on
what you want to do.


Other methods are component specific. 
All methods that a component provides on behalf of an interface must be 
callable with the minimum of (chain). This ensures that invoke works with all
these methods.
"""

# system imports 

# pub imports

# protocols imports

from protocols import Interface, Attribute, advise


#--------------------------------------------------------------------#
# Language interfaces.
#


class ILangMod(Interface):
    """
    ILangMod documents what a language module needs to be accepted as such

    english.py should provide ILangMod like: 

    advise(moduleProvides=[ILangMod])

    as should all other language modules.

    This is to ensure that the module is really a language.
    """
    
#---------------------------------------------------------------------
#
class IDynamicComponentRack(Interface):
    """
    Interface for Symbol and classes that need to provide component handling.
    """

    def addComponents(com):
        """
        Method that adds components listed in com if of the right type.
        """

    def __iadd__(com):
        """
        Synonym for addComponents, allows algebraic notation.
        """

    def delComponents(com):
        """
        Method that removes components listed in com if it can be found.
        """

    def __isub__(com):
        """
        Synonym for delComponents, allows algebraic notation
        """

#---------------------------------------------------------------------
#
class INoun(Interface):
    """
    INoun is a marker interface mainly.
    It is used to adapt to Noun Interfaces.
    """

class INounPhrase(Interface):
    """
    Logical form of Noun Phrase.

    This is the internal 'concept language' interface of a Noun Phrase.
    """
    dereferenced = Attribute("""How de-referenced is this phrase?: 'text', 'partial', 'labels', 'object'""")

    Noun = Attribute("""The Noun (string, Symbol, or PUB Noun object) REQUIRED.""")
    Adjs = Attribute("""Sequence of adjectives (strings or Symbols) (may be empty sequence).""")
    Plur = Attribute("""Grammatical number of noun (string, int, Symbol, or None).""")
    Artl = Attribute("""Definite-ness of noun (article used) as (string, Symbol, or None).""")
    Decl = Attribute("""Declension of noun (its grammatical role in the sentence), (string, Symbol, or None).""")
    Prep = Attribute(
        """
        Topological preposition indicating spatial relationship of action to noun.

        Defined only if Decl==sym.PRP
        Otherwise None
        """)  
    
    def __repr__():
        """
        Symbolic representation of Noun Phrase.
        Primarily for locale and game testing.

        Should display all components with dereference states.
        """

    def set(noun, adjs, decl, prep, artl, plur):
        """
        Convenience method to set noun values all at once:

        'noun' the basic noun
        'adjs' a sequence of adjectives used
        'decl' declension of the noun phrase
        'prep' preposition used if in prepositional declension
        'artl' article (or definite-ness)
        'plur' grammatical number or plurality
        """

class IVerbPhrase(Interface):
    """
    Internal 'concept language' behavior of VerbPhrase.
    """
    dereferenced = Attribute("""How de-referenced is this phrase?: 'text', 'mixed', 'labels', 'object'""")

    Verb = Attribute("""The basic verb. (strings, concept, or PUB verb object) (REQUIRED).""")
    Advs = Attribute("""Sequence of adverbs. (strings or VagueConcepts).""")
    Tense  = Attribute("""Tense, Mood, Aspect of the verb. (None or Symbol or collection of Symbols).""")
    Negative = Attribute("""Negation of sense of verb. Boolean.""")
    Person = Attribute("""Person of verb. (possibly empty mapping of Declension Symbols to Person Symbols).""")
    Number = Attribute("""Number of person of verb. (possibly empty mapping of Declension Symbols to Number Symbols).""")

    # Most commonly Person and Number determine verb conjugation.
    #   In Romance languages, they will take forms like {sym.NOM: sym.FIRST}, {sym.NOM: sym.SING}
    #   Some language, e.g. Swahili, will conjugate for more than one noun, e.g.:
    #       {sym.NOM: sym.FIRST, sym.ACC: sym.SECOND}, ...
    #

    def set(verb, advs, tense, negative, person, number):
        """
        Set a verb's values directly.
        
        'verb' the basic verb
        'advs' sequence of adverbs used.
        """

    def __repr__(self):
        """
        Representation of VerbPhrase for debugging.
        """

NP_types = '''(None or NounPhrase or sequence of NounPhrases)'''
class IClause(Interface):
    """
    Internal 'concept language' behavior of a Clause (simple sentence).
    """
    dereferenced = Attribute("""How de-referenced is this phrase?: 'text', 'mixed', 'labels', 'object'""")
    
    Verb = Attribute("""The verb phrase (VerbPhrase).""")
    
    Nouns = Attribute("""All noun phrases in clause (sequence of NounPhrases).""")

    Negative = Attribute("""I.e. NOT or negative form of statement. Boolean.""")
    
    # Convenience references into Nouns:
    Nom = Attribute("""Nominative (= Subject) noun phrase.%s.""" % NP_types)
    Acc = Attribute("""Accusative (= Direct Object) noun phrase.%s.""" % NP_types)
    Dat = Attribute("""Dative (= 'to' Object) noun phrase.%s.""" % NP_types)
    Gem = Attribute("""Genitive (= 'from' Object) noun phrase.%s.""" % NP_types)
    Ins = Attribute("""Instrumental (= 'with'/'using' Object) I noun phrase.%s.""" % NP_types)
    Prp = Attribute("""Prepositional (= Object with spec'd preposition).%s.""" % NP_types)

    def __repr__(self):
        """
        Representation of Clause for debugging.
        """

class ISentence(Interface):
    """
    Possibly compound sentence, composed of one or more Clauses.

    This is a marker interface for a standard Python sequence object (should inherit correct interface).
    """


# The following are only provided by L10N adaptors

class ITellNounPhrase(Interface):
    """
    'Tell' interface of a NounPhrase.

    Provides methods needed to generate text or speech from a Noun.
    """
    def tell():
        """
        Tell in default form.
        """

class IParseNounPhrase(Interface):
    """
    'Parse' interface of a NounPhrase.

    Methods for creating a Noun Phrase from input text or other data.
    """
    def parse(data):
        """
        Parse a noun phrase from input 'data' (typically a string).
        """

def ITellVerbPhrase(Interface):
    """
    'Tell' interface of a verb phrase.
    """
    def tell():
        """
        Basic localized rendering of the verb.
        """

def IParseVerbPhrase(Interface):
    """
    'Parse' for verb phrases.
    """
    def parse(data):
        """
        Parse the 'data' to get the verb phrase information.
        """


#---------------------------------------------------------------------
#
class IVerb(Interface):
    """
    Documents what a verb has to do in PUB.
    """

    def do(cmd):
        """
        Initiates the command.
        Generally just calls begin.
        """

    def begin(cmd):
        """
        Does the invoking.
        ie 
        try: 
            cmd.obj.open(cmd)
        except RandomError:
            cmd.tell(pub.error['RandomError'])
        """

    def finish(cmd):
        """
        Calls cmd.tell() to let the player and all who see 
        know what has happened
        """

#-----------------------# NOUN INTERFACES #-------------------------#
#
# This Section contains interfaces that might be added to Nouns, like
# IDescribable and ILocatable.
#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# IDescribable
#
class IDescribable(Interface):
    """
    Classes that provide IDescribable can be given descriptions and have 
    methods for evaluating them. IDescribable is language specific. 
    IDescribable components also provide the syntax for an object like 
    gender and case.
    """

    def getDesc():
        """
        method to aquire a normal description of an item.
        """

    def getXDesc():
        """
        method to aquire a detailed description of an item if it exists.
        otherwise call getDesc
        """

#--------------------------------------------------------------------
#ILocatable
#
class ILocatable(Interface):
    """
    Classes that provide ILocatable are used to show where an item is situated
    and if any items are contained within the obj it's a part of.
    In short it's used to localize objects.
    """


#--------------------------------------------------------------------
#ITangible
#
class ITangible(Interface):
    """
    Classes that provide ITangible have size and weight and ways to deal with
    these attributes. It is a bit uncertain that this is a Thing Interface but
    since it's fully possible to have objects without this attribute I will
    leave it in.
    """

#----------------------Interface Packages---------------------------#        
# This section contains interfaces who in some way provide several
# listeners and other methods.
# Interfaces like IContainer.
#
# We will use advise to tell the framework that these packages are subclasses
# of others.
# advise(protocolExtends = [IOpenL, ICloseL] for some openable package.

class IContainer(Interface):
    """
    IContainer is an interface package. It sets some extra methods that should
    be requitered by all containers.
    """
    
    advise(protocolExtends = [IPutL])

    
    def containNoCheck(chain,*pThing):
        """Method that moves the object into the container."""


    def visibleContents(chain):
        """returns a list of contents"""

    def put(chain,cmd):
        """the put listener method"""

#--------------------------------------------------------------------
# ITest -- Used to test adaption in different places.
#
#  Amonst others used inside language modules for adapters.
#  Should also be used heavily by the testing framework.
#
class ITest(Interface):
    """A Test Interface Facility, use where you deem fit."""

    def test(obj,proto):
        """should just print out that everything worked out."""
        print 'aok'
