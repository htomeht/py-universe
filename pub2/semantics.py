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
import random
from noun import Noun
from verb import Verb, AdverbDomain, Adverb

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
        'EVERYBODY':'Every agent (character) in the game.',
        'UNIVERSE' :'All objects in game universe.' })

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
        'FIRST':  "First person, 'I' or 'we'",
        'SECOND': "Second person, 'you'",
        'THIRD':  "Third person, 'he/she/it/they'. 'Proximate' when appropriate.",
        'FOURTH': "Fourth person or 'obviative', when appropriate.",
        'YOUandI':"Inclusive 1st+2nd 'you and I'" })

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
    scopes = {	sym.NOM: (sym.SUBJ_SELF, sym.CHARACTER, sym.EVERYBODY),
                sym.ACC: (sym.THIS_ROOM, sym.INVENTORY, sym.ABSTRACTS, sym.CHARACTER, sym.EVERYBODY),
		        sym.DAT: (sym.ABSTRACTS, sym.THIS_ROOM, sym.INVENTORY),
		        sym.GEN: (sym.ABSTRACTS, sym.THIS_ROOM, sym.INVENTORY),
		        sym.INS: (sym.INVENTORY, sym.THIS_ROOM, sym.UNIVERSE ),
		        sym.PRP: (sym.ABSTRACTS, sym.THIS_ROOM, sym.INVENTORY)  }
    _part_of_speech = sym.DECL

Decl = Declension() 

class NounPhrase(object):
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
    plur = None
    decl = None
    prep = None
    artl = None
    adjs = ()
	
    def __init__(self, noun=None, plural=None, declension=None, preposition=None, 
    			article=None, adjectives=()):
        self.noun = noun
        self.plur = plural
        self.decl = declension
        self.prep = preposition
        self.artl = article
        self.adjs = list(adjectives)

        # build a dictionary mapping e.g. sym.SUBJ_SELF to self._match_scope_SUBJ_SELF
        # gotcha: we want the instance *method* not the class *function*!
        self.dereference_by_scope = dict([(c.name, getattr(self, '_match_scope_'+c.name))
                                                    for c in sym.SCOPES.vocabulary])

    def addAdje(self, adje):
    	"""
        Add an adjective to the noun phrase.
        """
    	self.adjs.append(adje)
        
    def _match(self, noun):
    	"""
        Is this noun phrase consistent with being the noun?

        This is essentially an equality test, but we don't want to imply a 1:1 relationship.
        There may be many nouns that this phrase could match.
        
        @param noun: noun to match to (noun is assumed to be in scope, no checks made).
        """
        # NOTE: decl, plur, and artl do not affect individual matches, they
        #       determine search sequence and multiple-matching rules.
        #
        match = False
        # First the name must match -- most matches end here
        if isinstance(self.noun, Concept) and self.noun==noun.name:
            match = True
        else:
            return False
        
        # interpretation of prepositions is going to depend on the target noun object
        #  (if prep doesn't make sense for that noun, it probably can't match?)
        if self.prep and (self.prep in noun.preps):
            match = True
        else:
            return False
        
        # adjectives act as filters -- noun target should know if adjective matches
        for adje in self.adjs:
            if not noun.describedBy(adje):
                return False
        else:
            match = True

        return match

    def _match_multiple(self, items):
        matches = []
        for item in items:
            if self._match(item):
                matches.append(item)
        if len(matches)==1:
            # If exactly one match, we have a winner
            self.noun = matches[0]
            return True
        if len(matches)>1:
            if self.plur in (sym.SING, sym.MASS, sym.ABST, 1):
                # Ambiguous reference violates singular grammatical number
                # user probably didn't mean all of them
                raise SemanticAmbiguityError
            elif self.artl==sym.INDEF:
                # Indefinite -- just pick one at random:
                # e.g. "push a button" -- pick a random button and push it... ;-)
                self.noun = random.choice(matches)
            elif isinstance(sym.plur, int):
                # Pick N of the objects, where N is given by the number --
                # only works for literal number
                random.shuffle(matches)
                self.noun = matches[:sym.plur]
            else:
                self.noun = matches
                return True
        else:
            return False

    def _match_scope_SUBJ_SELF(self, subject):
        if self._match(subject):
            self.noun = subject
            return True
        else:
            return False

    def _match_scope_INVENTORY(self, subject):
        return self._match_multiple(subject.visibleContents())

    def _match_scope_THIS_ROOM(self, subject):
        # Actually any container holding the player,
        # but that's usually the room
        return self._match_multiple(subject.parent.visibleContents())

    def _match_scope_CHARACTER(self, subject):
        contents = subject.parent.visibleContents()
        return self._match_multiple([s for s in contents if s.implements(IAgent)])

    def _match_scope_UNIVERSE(self, subject):
        # FIXME: we have no way to scan entire PUB universe for an object (?)
        return False
	
    def _match_scope_EVERYBODY(self, subject):
        # FIXME: Same as universe, except only consider agents.
        return False

    def _match_scope_ABSTRACTS(self, subject):
        return self._match_multiple(sym.ABSTRACTS.vocabulary)

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

        if self.decl:
            scopes = Declension.scopes[self.decl]

        for scope in scopes:
            if self.dereference_by_scope[scope](subject):
                break
        else:
            # Didn't find any possible reference
            raise SemanticError

        # The important thing is the side-effect of setting self.noun 
        # but we also return that:
        return self.noun
                
                    
class VerbPhrase(object):
    """
    Verb Phrase or Predicate of sentence, includes verb and adverb(s).
    """
    verb = None
    advs = None
    adverbs=None

    def __init__(self, verb=None, advs=(), adverbs=None):
        self.verb = verb
        self.advs = advs
        self.adverbs = {}
        if adverbs and type(adverbs)==dict:
            self.adverbs.update(adverbs)
    
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
            self.noun = verb
            self.adverbs[domain] = fuzzy.combine(

