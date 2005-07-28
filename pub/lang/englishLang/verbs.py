#    pub/lang/englishLang/objs.py                           1/11/04 GJ
#
#   Copyright (C) 1998 Joe Strout 
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
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# CHANGELOG
#
#   2004-11-01
#    Gabriel J
#       Baseline -- English verbs
#       
#--------------------------------------------------------------------
"""
This module contains english verbs.

Normally these will be instantiated into a verb dictionary on an actor.
"""
#--------------------------------------------------------------------

# system imports


# pub imports

import pub
from pub.constants import *
from pub.interfaces import *

# protocols imports

from protocols import advise

#--------------------------------------------------------------------

verblist = []

class EnglishVerb:
    """
    EnglishVerb:
      Base class of all english verbs.
    """

    advise(instancesProvide=[IVerb])

    def __init__(self, pNames=''):
        self.synonyms = pNames.split(',').lower()
        self.duration = 1    # time (in minutes) to execute
        self.succ = 'You ' + self.synonyms[0] + '.'
        self.osucc = '<The actor> ' + self.synonyms[0] + 's.'
        

    def __str__(self):
        """
        returns a string containing Verb: 
        followed by a verbs primary name

        called with str(self)
        """
        return '< Verb: ' + self.synonyms[0] + ' >'
                           
    def getDuration(self, cmd):
        return self.duration

    
    def doPreChecks(self, cmd):  # return OK or CANCEL
        """
        Check that everythings is ok, calls all relevant preChecks
        preWitness, preObj, preAct
        """
        
        #call romm hierarchy's preWitness method if any
        obj = cmd.actor.container
        
        while obj:
            if adapt(obj, IPreWitness, None) != None:
                if not obj.preWitness(cmd): return CANCEL
            obj = obj.container
        
        #call objects' preObj methods, if any
        for obj in cmd.objects: # should be a list of relevant cmd objects
            if adapt(obj, IPreObj, None):
                if not obj.preObj(cmd): return CANCEL
        
        #call actors preAct method, if any
        if adapt(cmd.actor, IPreAct, None) != None:
            if not cmd.actor.preAct(cmd): return CANCEL

        #if all checks have passed, return OK
        return OK

    def doPostChecks(self, cmd):    # return OK or CANCEL
        """
        finish up
        calls all relevant postChecks
        postWitness, postObj, postAct
        """
        #call romm hierarchy's postWitness method if any
        obj = cmd.actor.container
        
        while obj:
            if adapt(obj, IPostWitness, None) != None:
                if not obj.postWitness(cmd): return CANCEL
            obj = obj.container
        
        #call objects' postObj methods, if any
        for obj in cmd.objects: # should be a list of relevant cmd objects
            if adapt(obj, IPostObj, None):
                if not obj.postObj(cmd): return CANCEL
        
        #call actors postAct method, if any
        if adapt(cmd.actor, IPostAct, None) != None:
            if not cmd.actor.postAct(cmd): return CANCEL

        #if all checks have passed, return OK
        return OK

    #XXX: Write interfaces that show how preChecks and postChecks should work. 

    def do(self, cmd):
        """
        schedule command for execution, if actor isn't busy
        initiate immediatly
        """

        if cmd.actor.busytill > pub.scheduler.minutes:
            pub.scheduler.AddAbsEvent(cmd.actor.busytill, \
                                      pub.Event(self, 'object.begin(cmd)',cmd) )
            return
        # if actor is not busy, then begin command immediatly
        if self.begin(cmd): cmd.tell()

    def begin(self, cmd):
        """
        handle the command
        """
       
        #XXX: This is where prechecks would be handled
        # might be something like invoke(cmd.actor, IPreAct, 'preAct' cmd)
        
        if self.doPreChecks(cmd) == CANCEL: return CANCEL
        
        self.finish(cmd)

        delay = self.getDuration(cmd)

        if cmd.actor.busytill > pub.scheduler.minutes:
            cmd.actor.busytill = cmd.actor.busytill + delay
        else: cmd.actor.busytill = pub.scheduler.minutes + delay

       return OK

    def finish(self, cmd):
        """
        execute and output the event

        do the actual action i.e changes to the game objects
        """
        
        #XXX: handle postchecks
       
        if self.doPostChecks(cmd) == OK:
            cmd.tell()
        return OK
                
#--------------------------------------------------------------------
# BEGIN VERBS
#

#----------------------------------------------------------------------
# Transitive verbs -- require a direct object

class Transitive(Verb):
    """
    Transitive verbs -- require direct objects.
    """

    def __init__(self, pNames=''):
        Verb.__init(self, pNames)
        x = self.synonyms[0]
        self.succ = 'You '+x+' <the dirobj>.'
        self.osucc = '<The actor> '+x+'s <a dirobj>.'
        self.fail = cap(x)+' what?!?'
        self.seefail = "You can't see that here."
        self.seesucc = "It takes a bit of groping, but you manage it..."


    def begin(self,cmd):
        if not cmd.dirobj or not isInstance(cmd.dirobj):
            cmd.actor.tell(self.fail)
            return CANCEL
        if not cmd.actor.canSee(cmd.dirobj):
            if cmd.dirobj.container == cmd.actor:
                cmd.tell(self.seesucc)
            else:
                cmd.tell(self.seefail)
                return CANCEL
        return Verb.begin(self,cmd)

    def finish(self,cmd): return Verb.finish(self,cmd)

#--------------------------------------------------------------------
# Social verb class: verbs which do very little, and may either
# have no objects, or one object (which we'll call dirobj).

class Social(Verb):
    """
    Social verb class -- little effect on topology
        verbs which do very little, and may either
        have no objects, or one object (which we'll
        call dirobj).

        Note that Social verbs may take on a whole new
        meaning with emotive characters. These may become
        every bit as meaningful as action verbs. The
        distinction then will be that social verbs affect
        the agent state of other characters while action
        verbs affect the topological world.

        (But since agents emit action verbs based on
        emotive state, social verbs may indirectly affect
        the topo world. This makes for a new dimension in
        game play involving complex persuasion tasks).
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        x = self.synonyms[0]
        self.succ = 'You ' + x + '.'
        self.osucc = '<The actor> ' + x + 's.'
        self.atsucc = 'You ' + x + ' at <the dirobj>.'
        self.atosucc = '<The actor> ' + x + 's at <the dirobj>.'
        self.atobjsucc = '<The actor> ' + x + 's at you.'

    def finish(self,cmd):        # execute and output the event
        atwhom = cmd.dirobj
        if not atwhom: atwhom = cmd.atobj
        if not atwhom: atwhom = cmd.withobj
        if not atwhom: atwhom = cmd.toobj
        if not atwhom:
            cmd.Tell( self.succ, self.osucc )
        else:
            cmd.dirobj = atwhom        # necessary for correct substitution
            cmd.Tell( self.atsucc, self.atosucc, self.atobjsucc, atwhom )

