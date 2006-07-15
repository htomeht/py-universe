#   (C) 1996 Joe Strout
#   verb
"""
Definition of basic verb behavior. Specific verbs are in verbs/*.
"""
#    pubverbs.py                                            8/27/96 JJS
#
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
#
#   Derived from:
#    pubverbs.py                                            8/27/96 JJS
#
#--------------------------------------------------------------------
# CHANGELOG
#
#   2006-01/23: Terry Hancock
#       Put core verb code in this module, moved basic verb vocabulary
#       to verbs/coreverbs.py
#
#       Changed interpolation to Python dict style.
#
#       Starting localization.
#
#   2004-22/10: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
Defines the basic classes of verbs understood by the game. More
verbs are interpreted via synonyms to these.
"""
#standard imports
import string

#pub imports
import types 
import pub

from concept import *
#from pubcore import *

#protcols imports

#----------------------------------------------------------------------
# NEW 2006: verb req's
#
#	- identified label (objects react to the label)
#
#	- subscription to adverbial domains
#
#	- identification of listener interface (doc-only or code?)
#
#	- scope rules. How large is an action?
#		SUBJ_SELF:	the subject
#		THIS_ROOM: 	current room
#		INVENTORY: 	current inventory
#		CHARACTER: 	set of agents in room
#		ALL_AGENT:	every agent in game
#		ABSTRACTS: 	set of abstracts
#		PUB_WORLD:	whole game (could be expensive!)
#	  determines how far we must search for referents.
#
#	- scheduling and duration events
#
class IVerb(Interface):
    """
    Verb Interface

    All verbs provide this interface for PUB.
    """
    label = Attribute("""
                Label uniquely identifying verb in semantic vocabulary
                (Label class instance)
                """)
		
    adverb_domains = Attribute("""
                Which adverbial domains make sense for this verb.

		Verb must subscribe to an adverbial domain in order
		for adverbs from that domain to be applied to it.
		If no adverbs make sense with the verb (or are not
		to be supported), this can be an empty sequence.

		Otherwise, it is a sequence of AdverbDomain class
		instances.
		""")

    listener_iface = Attribute("""
                Interface specification of listeners which understand
		this verb (i.e. Nouns which can be an object of this
		verb must implement this interface.
		""")

    
    scope = Attribute("""
                Scope determines to which nouns the verb action will
		be broadcast. It may be None, in which case the scope
		will be determined by the declension, it may be a single
		scope Enum, in which case that scope will be considered
		first, then the scopes determined by declension, or it
		may be a sequence of scopes, in which case, only those
		scopes will be considered.
		""")

    duration = Attribute("""
                How long will it take to complete the action?

		None,<0 = Statelike (permanent)
		0, 0.0 = instantaneous
		other int n = takes n turns (turn-based event)
		float f = takes f minutes (real-time event)
		""")
		 
   


#----------------------------------------------------------------------
# Verb -- base class of any Verb object
#
class Verb:
    """
    Verb:
            base class of any Verb object
            Verbs have various methods which are involved in
            executing them -- checking possibilities, etc.
    """

    symbol = sym.VERB

    def __init__(self, name, pNames='', doc=''):
        self.symbol = Concept(name, domain=sym.VERB, doc=doc)
        self.synonyms = string.split(string.lower(pNames),',')
        self.duration = 1        # time (in minutes) to execute
        self.succ = 'You ' + self.synonyms[0] + '.'
        self.osucc = '%(TheSubj)s ' + self.synonyms[0] + 's.'
        AddVerb(self.synonyms)
        for i in self.synonyms:
            pub.verbdict[i] = self

    def __str__(self):
        """
        returns a string containing Verb: 
        followed by a verbs primary name

        called with str(self)
        """
        return '< Verb: ' + self.synonyms[0] + ' >'

    def GetDuration(self, cmd):
        return self.duration

    def DoPrechecks(self, cmd):        # return OK or CANCEL
        """
        check that everything is ok, calls all relevant PreChecks
        PreWitness, PreObj, PreAct
        """
        # call room hierarchy's PreWitness method, if any
        obj = cmd.actor.container
        while obj:
            if hasattr(obj, 'PreWitness'):
                if not obj.PreWitness(cmd): return CANCEL
            obj = obj.container

        # call objects' PreObj methods, if any
        for obj in (cmd.dirobj, cmd.toobj, cmd.atobj, cmd.withobj, cmd.inobj):
            if isInstance(obj) and hasattr(obj, 'PreObj'):
                if not obj.PreObj(cmd): return CANCEL

        # call actor's PreAct method, if any
        if isInstance(cmd.actor) and hasattr(cmd.actor, 'PreAct'):
            if not cmd.actor.PreAct(cmd): return CANCEL

        # if all checks have passed, return OK
        return OK

    def DoPostchecks(self,cmd):        # return OK or CANCEL
        """
        finish up
        calls all relevant PostChecks
        PostWitness, PostObj, PostAct
        """
        # call room hierarchy's PostWitness method, if any
        obj = cmd.actor.container
        while obj:
            if hasattr(obj, 'PostWitness'):
                if not obj.PostWitness(cmd): return CANCEL
            obj = obj.container

        # call objects' PostObj methods, if any
        for obj in (cmd.dirobj, cmd.toobj, cmd.atobj, cmd.withobj, cmd.inobj):
            if isInstance(obj) and hasattr(obj, 'PostObj'):
                if not obj.PostObj(cmd): return CANCEL

        # call actor's PostAct method, if any
        if isInstance(cmd.actor) and hasattr(cmd.actor, 'PostAct'):
            if not cmd.actor.PostAct(cmd): return CANCEL

        # if all checks have passed, return OK
        return OK

    def Do(self,cmd):
        """
        schedule command for execution, if actor isn't busy
        initiate immediatly
        """ 
        if cmd.actor.busytill > pub.scheduler.minutes:
            pub.scheduler.AddAbsEvent(cmd.actor.busytill, \
                                      Event(self,'object.Begin(cmd)',cmd) )
            return
        # if actor is not busy, then begin command immediately
        self.Begin(cmd)

    def Begin(self,cmd):
        """
        handle the command
        """
        # do pre-checks; see if the command will even work
        if self.DoPrechecks(cmd) == CANCEL: return CANCEL
        
        # finish executing the command
        self.Finish(cmd)
        
        # make the actor pause appropriately before next comman
        delay = self.GetDuration(cmd)
        
        if cmd.actor.busytill > pub.scheduler.minutes:
            cmd.actor.busytill = cmd.actor.busytill + delay
        else: cmd.actor.busytill = pub.scheduler.minutes + delay
        
        return OK

    def Finish(self,cmd):
        """
        execute and output the even
        
        do the actual action, i.e. changes to the game objects
        
        do post-processing to provide alternate output
        return OK in either case her, since command executed
        """
        if self.DoPostchecks(cmd) == OK:
            cmd.Tell( self.succ, self.osucc )
        return OK


#----------------------------------------------------------------------
# Verb registry

verbs = ['drop', 'get', 'go', 'inv', 'look', 'eat', 'give', 'put', 'use']


#----------------------------------------------------------------------
# add a verb or list of verbs, singly, as a list, or separated with commas
def AddVerb( *pVerbs ):
    """
    AddVerb:
            add a verb or list of verbs, singly, as a list, or 
            separated with commas
    """
    for item in pVerbs:
        if type(item) == types.StringType:
            if item not in verbs: verbs.append(item)
        else:
            for subitem in item:
                if subitem not in verbs: verbs.append(subitem)
    verbs.sort()
            

