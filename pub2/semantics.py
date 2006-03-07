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
from concept import *

# First we define a limited set of vocabularies to express semantic concepts.

Concept('PoS',      doc="Part of Speech")
Concept('SCOPE',    doc="Extent and place of search among program objects.")
Concept('TENSE',    doc="Tense (including aspect and mood) of a sentence or phrase.")
Concept('G_NUMBER', doc="Grammatical number of a noun.")
Concept('G_PERSON', doc="Grammatical 'person' 1st - 4th.")

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
        'ALL_AGENT':'Every agent (character) in the game.',
        'PUB_WORLD':'All objects in game universe.' })

decl_cases = Enum(sym.DECL, {
        'NOM':'Nominative or Subject Case of Noun',
        'ACC':'Accusative or Direct Object Case of Noun',
        'DAT':'Dative or "to" Indirect Object.',
        'GEN':'Genitive or "from" Indirect Object.',
        'INS':'Instrumental or "with"/"using" Indirect Object.',
        'PRP':'Prepositional case, used with "topological" prepositions, e.g. "in", "on"' })

tense = Enum(sym.TENSE, {
        'IMP':'Imperative = Command',
        'INT':'Interrogative = Question',
        'PRP':'Present Perfective = Statement of Completed Action',
        'PRI':'Present Imperfective = Statement of Ongoing Action',
        'COP':'Copular = Statement of Equality Between Subject and Object  "A is B"',
        'EXS':'Existance = Statement of Existance "there are..."' })
        
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
        'P_1ST': "First person, 'I' or 'we'",
        'P_YAI': "Inclusive 1st+2nd 'you and I'",
        'P_2ND': "Second person, 'you'",
        'P_3RD': "Third person, 'he/she/it/they'. 'Proximate' when appropriate.",
        'P_4TH': "Fourth person or 'obviative', when appropriate." })

# FIXME: this module is very incomplete below this point.

class Grokable(object):
    """
    Can 'grok' or dereference a localized string value to its semantic equivalent.

    Makes class act like a typecast or type-converter factory function.
    """
    _part_of_speech = None
    def __call__(self, value):
    	# We pass the 
        return locale.grok(self._part_of_speech, value)   

class Declension(Enum, Grokable):
    """
    Declension or "case" of nouns (i.e. their role in the sentence):
    """
    scopes = {	NOM: (SUBJ_SELF, CHARACTER, ALL_AGENT),
                ACC: (THIS_ROOM, INVENTORY, ABSTRACTS, CHARACTER, ALL_AGENT),
		DAT: (ABSTRACTS, THIS_ROOM, INVENTORY),
		GEN: (ABSTRACTS, THIS_ROOM, INVENTORY),
		INS: (INVENTORY, THIS_ROOM, PUB_WORLD),
		PRP: (ABSTRACTS, THIS_ROOM, INVENTORY)  }
    _part_of_speech = DECL

Decl = Declension()


class Preposition(Grokable):
    """
    Open class of preposition words.
    """
    _part_of_speech = PREP
    pass


Prep = Preposition()


class NounPhrase(object):
    """
    Noun Phrase

    Semantic representation of a grammatical object specifying a
    noun and its relationship to a clause of a sentence.
 
    @ivar noun:	L{Noun} C{(string|label|PUB Noun instance)}
    @ivar plur:	int|Enumerated(SING|DUAL|PLUR|PLND|MASS|ABST)
    @ivar decl:	None|Enumerated(NOM|ACC|DAT|GEN|INS|PRP)
    @ivar prep:	None|label
    @ivar artl:	None|Enumerated(INDEF|DEFIN|QUANT|ABSTR|UNDEF)
    @ivar adjs:	list of string|label	
    """
    noun = None
    plur = 0
    decl = None
    prep = None
    artl = None
    adjs = ()
	
    def __init__(self, noun=None, plural=0, declension=None, preposition=None, 
    			article=None, adjectives=()):
        self.noun = noun
	self.plur = plural
	self.decl = declension
	self.prep = preposition
	self.artl = article
	self.adjs = list(adjectives)

    def addAdje(self, adje):
    	"""
	Add an adjective to the noun phrase.
	"""
    	self.adjs.append(adje)

    def _match(self, noun):
    	"""
	Is this noun phrase consistent with being the noun?

	@param noun: noun to match to (noun is assumed to be in scope, no checks made).
	"""
	# Not sure how this should check yet.
	pass
	

    def dereference(self, subject, scopes):
    	"""
	Attempt to resolve the identity of the noun
	from game scoping rules and available information in Noun Phrase.

	@param subject: subject (agent action originates from).
	@param scopes: sequence of scopes for the verb.
	"""
	# If words are still strings, then we need to ask the locale
	# module to translate them into semantic symbols:
	self.artl = Artl(self.artl)
	self.decl = Decl(self.decl)
	self.prep = Prep(self.prep)
	
	for scope in scopes:
            if scope==SUBJ_SELF:
	    	if self._match(subject):
		    self.noun = subject
		    
                container = subject
                contents  = subject.visibleContents()
                for noun in contents:
                    if self._match(noun):
		    	pass
	
