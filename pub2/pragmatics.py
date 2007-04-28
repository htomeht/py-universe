#(C)2006 Terry Hancock
#--------------------------------------------------------------------
# pragmatics
"""
Pragmatics converts symbolic objects defined in the semantics module
and (during parsing) de-references them to actual game Noun and Verb
objects, and/or re-references them (during telling) to generate symbolic
sentences.

Thus pragmatics is the final stage in parsing and the initial stage
in telling.

It represents the "situated meaning" of game information streams.

Its primary use is to communicate with the player, but it is also
capable of being used to communicated between non-player characters
(in which case, semantic objects may not need to be generated,
although they may be for the purposes of recording them).

The PragmaticNounPhrase, PragmaticVerbPhrase, and PragmaticClause
classes are mixins which are combined with the SemanticNounPhrase,
SemanticVerbPhrase, and SemanticClause classes to create the 
NounPhrase, VerbPhrase, and Clause objects that we actually use in
the game engine. The separation is primarily to simplify testing,
since semantics relies heavily on pyparsing, communications channels,
and locale-specific information, while pragmatics relies heavily on
the internal context of the game's topological world model. Thus
pragmatics is primarily concerned with searching "scopes" of objects
within the game world model in order to find the referents of symbols
provided from the semantics processing layer.

As such, it should generally be appreciated that pragmatic sentences
generally lack a hashable form (they are not self-contained), as
they contain references directly to the world model objects they
"describe". At the pragmatic level, they must be understood as
database operations on the model world.

Also as such, it can be seen that imperative pragmatic sentences
are directly dispatchable: they are completely unambiguous. As
statements or queries, they are directly evaluatable. In the
same way, they can be directly generated in response to queries
(as reports).

The contact point between pragmatic and semantic representations
are the symbol objects. Semantic methods operate in the space
between localized textual representations and symbolic representations,
while pragmatic methods operate in the space between symbolic
representations and the game model objects (including actions)
that the symbols refer to.
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
import random
from noun import Noun, Adjective
#from verb import Verb, AdverbDomain, Adver
import vocabulary
import protocols
from interfaces import *

from semantics import *

class PragmaticNounPhrase(object):
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

    protocols.advise(instancesProvide=[INounPhrase, IPragmaticNounPhrase])
	
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
        if isinstance(self.noun, Symbol) and self.noun==noun.name:
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
                
                    
class PragmaticVerbPhrase(object):
    """
    Verb Phrase or Predicate of sentence, includes verb and adverb(s).
    """
    verb = None
    advs = None
    adverbs=None
    mood = None
    negative = False
    question = False
    dereferenced = False
    agreements = None

    protocols.advise(instancesProvide=[IVerbPhrase, IPragmaticVerbPhrase])

    def __init__(self, *args, **kw):
        self._pragmatic_init(*args, **kw)

    def _pragmatic_init(self, verb=None, context=None):
        """
        Construct a pragmatic VerbPhrase based on a particular game action.
        """
        pass    # FIXME: how the hell do we do this?
        # I think this is a listener which generates a report based on
        # an action which takes place during a turn
           
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

class PragmaticClause(object):
    """
    Independent clause. A complete simple sentence with a verb phrase and one or more nounphrases.
    """
    # implements IClause
    protocols.advise(instancesProvide=[IClause])

class Sentence(list):
    """
    A Sentence is an optional Address followed by a list of one or more clauses.
    """
    protocols.advise(instancesProvide=[ISentence])
    pass


