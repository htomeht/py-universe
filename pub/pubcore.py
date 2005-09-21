#    pubcore.py                                           6/01/98 JJS
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
#   2002-5/10:
#    Terry Hancock
#       Added doc strings based on comments/code.
#
#   2004-21/01
#    Gabriel J
#       Went through the code adding more doc strings
#       Most based on curent comments but some on own experience
#
#   2004-22/10: 
#    Gabriel J
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
NOTE: Don't mess with this module unless you know what you're doing!

Includes Scheduler, Event, Command, Parser, Verb, and BaseThing (=Noun?)

Also a number of utility functions. I'm a little
disturbed by things like "cap" which simply call
Python library functions -- not sure that we need
such a wrapper, as it likely increases the learning
curve for working with the code. (?)  On the other
hand, if used frequently enough, it might clarify
the code. If so, we need to add comments to define
what these things do.
"""
#----------------------------------------------------------------------

# system imports

import string
import types
import copy
import random
import re

# pub imports

import pub
from interfaces import ISymbol, ILangMod 
import adapters
from constants import *


# protocols imports

from protocols import adapt, advise

#--------------------------------------------------------------------

cap = string.capitalize # function to capitalize a string

def isString(x):
    """
    function to determine whether something is a string
    """
    return type(x) == type('')

def isInstance(x):
    """
    function to determine whether it's an Instance
    """
    return type(x) == types.InstanceType

def isInt(x):
    """
    function to determine whether it's a number, or interpretable as one
    """
    try:
       string.atoi(x)
       return TRUE
    except: return type(x) == type(1)

def toInt(x):
    """
    function to force it to be a number
    """
    if isInt(x): return x
    try: return string.atoi(x)
    except: return 0


def stripPunctuation(str):
    """
    function to strip commas and periods from a string
    """
    for char in ",.!?": 
        str = str.replace(char, '')
    return str

def savegame(filename='pub.dat', quiet=FALSE):
    """
    Save the game.
    """
    import sys
    import os
    import pub
    import pubverbs
    import picklemod

    pub.lastroom = None    # (to prevent auto-placement of objects)
    if not quiet and os.path.isfile(filename): 
        answer = raw_input('  File exists, do you wish to overwrite it?\
                              Y/y/N/n : ')
        if answer in 'Yy': pass
        else:
            print '  Aborting!'
            return CANCEL
    f = open(filename, 'w')
    picklemod.save(f, pubverbs, pub, sys.modules['__main__'])
    f.close()
    if not quiet: print '  Game saved as', filename 
    

def restoregame(filename='pub.dat', quiet=FALSE):
    """
    Restore a game.
    """
    import sys
    import pub
    import pubverbs
    import picklemod

    pub.lastroom = None    # (to prevent auto-placement of objects)
    try: 
        f = open(filename, 'r') 
    except:
        if not quiet:
            print '  Error:', filename, "doesn't exist or is not readable."
            print '  Aborting!'
        return CANCEL
    picklemod.restore(f, pubverbs, pub, sys.modules['__main__'])
    f.close()
    if not quiet: print '  Game', filename, 'restored'

#--------------------------------------------------------------------
# chainLinker -- Used by the component driven object system
#
def chainLinker(obj, proto, default=None):
    """
    A function that generates a chain
    used by, for instance invoke to get at all verb methods in an object.
    We can add more functionality here but it's probably best to keep it to 
    a minimum.
    """

    # First loop through the obj to see if it has any components
    adapted = adapt(obj, ISymbol, None)  
    if adapted is not None:
        for com in adapted.components:
            for adapted in chainLinker(com, proto):
                yield adapted

    # Second try to adapt those components to the relevant protocol
    # This is the function that builds the chain even though it get's 
    # passed through the above.
    adapted = adapt(obj, proto, None)
    if adapted is not None:
        yield adapted

    # Third add a default method.
    if default is not None:
        yield default

#--------------------------------------------------------------------
# check -- used to run object checks
#
def check(obj, proto, meth, args = [], default = None):
    """
    check special functions on objects that should return True or False
    depending on circumstances.
    In most cases a default should be supplied. 
    Ie if you want to check if something can contain water you do
    
    from pub import defaults as d
    if not check(glass, IContainer, 'canContain', d.NoLiquid, [waterI]):
        raise ContainError
    
    """
    chain = chainLinker(obj, proto, default) # chain of methods in components 
    try: first = chain.next()
    except StopIteration: 
        # The method can't be found on the object, return an error
        raise pub.errors.ComponentError, "No such component can be found"
    
    try: getattr(first, meth)(chain, obj)
    except StopIteration:
        return True # If we get this far nothing has stopped us.

#--------------------------------------------------------------------
# invoke -- used by the component driven object system
#
def invoke(obj, proto, meth, cmd=None, output=True):
    """
    invoke is used to run methods in an objects components that can be adapted
    to a interface of choice. It can also be used to generate output based on
    cmd, or to suppress it.

    Note: invoke is only used for verb methods. If you want to access other
    methods in other ways use chainLinker or other functions that might be
    provided.

    calling invoke without a cmd gives different responses depending on the
    actuall method called. All methods should be able to handle None as value.
    Mostly it will result in either an error or immediate execution.
    like: invoke(door, IOpen, 'open') will try to set the doors isOpen=True
    """
    chain = chainLinker(obj, proto) # link a chain of methods in components 
    try: first = chain.next()
    except StopIteration: 
        # The method can't be found on the object, return an error
        raise pub.errors.ComponentError, "No such component can be found"
    
    try: getattr(first,meth)(chain,cmd)
    except StopIteration: # Check for the end of the chain.
                          # This means that the command was successful
                          
        if not output: raise pub.errors.NoOutput
        else: 
            return True # Tells the caller it has finished processing
                        # and that it was succesfull.
    

#--------------------------------------------------------------------
# find -- used by the component driven object system
#
#def find(obj,proto,default=None):
#    """
#    minimal interface to chainLinker that simply finds out if an object has a
#    component that matches the protocol and returns it. If there are more or
#    less than one an error is raised.
#    """
#
#    out = chainLinker(obj, proto, default)
#    test = len(list(out))
#
#    if test < 1: raise pub.errors.ComponentError, "No such component"
#    if test > 1: raise pub.errors.ComponentError, "Too many components match"
#
#    else: return out.next()
#
#--------------------------------------------------------------------
# lingo -- a language finder
#
def lingo(lang, cls, args = []):
    """
    method to access a couple of dictionaries and dig out a language
    and subsequently a specific class.

    lang should be a string like 'english' or 'swedish'
    cls should be a string containing something like 'parser' 
    """

    try: temp = pub.lang.mods[lang.lower()] # a language module
    except KeyError: raise pub.errors.PubError, "Language doesn't exist."

    if adapt(temp, ILangMod, None) != None: 
        try: out = temp.get[cls.lower()] # get the named class
        except KeyError: raise pub.errors.PubError, "Can't find class"
    
        return out(*args) # if args is not empty args will be passed. 
                           # else temp will be called without args.
    
#def lingo(obj,proto):
#    """
#    lingo is used for instances when we want to find the right language.
#    """
#
#    adapted = adapt(obj, ILang, None)
#    if adapted != None:
#        adapted = adapted.initiate()
#        if pub.debugging: print adapted
#
#    if pub.debugging: print obj, proto
#
#    return adapt(adapted, proto, None)
#
#----------------------------------------------------------------------
# event -- a class which keeps something to be executed in the future
#
class Event:
    """
    Event:
        a class which keeps something to be executed in the future

        Basically you load code into it. If 'Perform'ed, it
        executes the code.
    """

    def __init__(self,pObject=None,pCode=None,pCmd=None):
        if not pObject: return    # must be unpickling
        self.object = pObject
        self.cmd = copy.copy(pCmd)
        self.code = pCode
#       print "Event created: " + str(self)

    def __str__(self):
        """
        prints an Event and code to be executed, called with str(self)
        """
        return '< Event: ' + str(self.object) + ',' + str(self.code) + ' >'

    def Perform(self):
        """
        execute the code in self.code
        """
#       print 'Performing: ' + str(self)
        object = self.object
        cmd = self.cmd
        exec self.code

    def RefersTo(self,pWhom):
        if self.object == pWhom or \
        self.cmd and self.cmd.actor == pWhom: return TRUE
        return FALSE

#----------------------------------------------------------------------
# scheduler -- keeps track of the world clock, calls events, etc.
#
class Scheduler:
    """
    Scheduler:
        keeps track of the world clock, calls events, etc.
        
        Basically, it controls 'Event's.

        Appears to work on a realtime model, not sure how
        turns figure in.

        Most actions should take 1 minute 
        This is not true however, for some reason every time I look at a
        clock it take 2 minutes. I don't know why.
        In addition wait can take up to 15 minutes for example

        for some reason it always take an extra minute for an action.
        could be a problem since we don't have any 12:01, 12:03 and
        so forth.
    """
    # initialization method
    def __init__(self,pTimeString='12:00'):
        timeparts = string.split(pTimeString,':')
        self.minutes = string.atoi(timeparts[0])*60 \
                       + string.atoi(timeparts[1])
        self.events = {}
    
    def __str__(self):
        """
        Tells the current time and number of events to be processed
        Called with str(self)
        """
        return '< Scheduler at time ' + self.GetTime() \
                + ' and ' + str(len(self.events)) + ' events >'

    def GetTime(self):
        """
        Get the time of day
        """
        day = self.minutes / 1440
        hour = (self.minutes%1440) / 60
        minute = self.minutes%1440 % 60
        if day: return "%d:%02d (Day %s)" % (hour,minute,day)
        return "%d:%02d" % (hour,minute)

    def AddAbsEvent(self,pAbsTime,pEvent):
        if pAbsTime < self.minutes:
            print "WARNING: scheduling event for a past time"
            self.minutes = pAbsTime
        if self.events.has_key(pAbsTime):
            self.events[pAbsTime].append(pEvent)
        else:
            self.events[pAbsTime] = [pEvent]
    
    def AddEvent(self,pRelTime,pEvent):
        """AddEvent:
        Adds an event to the scheduler. pRelTime should be a number of
        minutes. 
        
        self.AddEvent(5, event) will add a new event 5 minutes from now. 
        
        """
        time = int(self.minutes) + int(pRelTime)
        if self.events.has_key(time):
            self.events[time].append(pEvent)
        else: self.events[time] = [pEvent]

    def Update(self):
        """
        update the scheduler
        """
        if not self.events: return
        eventkeys = self.events.keys()        # get event times
        eventkeys.sort()            # sort them
        nexteventkey = eventkeys[0]        # find earliest time
        self.minutes = nexteventkey        # update clock
        eventlist = self.events[nexteventkey]
        del self.events[nexteventkey]        # remove from the queue
        for e in eventlist:
            # print '[' + self.GetTime() + '] ',
            e.Perform()            # perform scheduled events

    def HasEventFor(self, pFor):
        """
        see if the scheduler has an event for a certain object,
        pass this method a game object.
        """
        if not self.events: return FALSE
        for eventlist in self.events.values():
            if filter(lambda x,a=pFor: x.RefersTo(a), eventlist):
                return TRUE
        return FALSE

#----------------------------------------------------------------------
#    Command -- stores references for variarious parts of a command
#
class Command:
    """
    Command:
            stores references for various parts of a command

            Basically, this is the object that gets passed back
            and forth by objects (mainly actors?).  Parsed tokens?
            Seems to understand parts of speech in some way.

        Used by objects to see what they should do.
        When an object get's passed a command, it checks for various thing.
        for example;
            if cmd.verb == pubverbs.open:
                self.isOpen = TRUE
                cmd.Tell('You open <the dirobj>.')

        pubverbs.open returns the name of open which is most likely 'open'
        and cmd.verb holds the string open, taken from the players input.
        It is quite simple to use but very efficient.

        dirobj is short for direct object
        inobj is short for indirect object
        all other objects are what they imply
    """

    def __init__(self):
            self.Clear()

    def Clear(self):
        """
        clear all references
        """
        self.actor = ''
        self.verb = ''
        self.dirobj = ''
        self.toobj = ''
        self.inobj = ''
        self.atobj = ''
        self.withobj = ''    

    def __str__(self):
        out = '<<'
        if (self.actor): out = out + '  Actor: ' + str(self.actor)
        if (self.verb): out = out + '  Verb: ' + str(self.verb)
        if (self.dirobj): out = out + '  Obj: ' + str(self.dirobj)
        if (self.toobj): out = out + '  To: ' + str(self.toobj)
        if (self.inobj): out = out + '  In: ' + str(self.inobj)
        if (self.atobj): out = out + '  At: ' + str(self.atobj)
        if (self.withobj): out = out + '  With: ' + str(self.withobj)
        out = out + '  >>'
        return out

    def StuffString(self,pStr,pFor=None):
        """
        function to substitute references
        used mainly in cmd.Tell of objects

        cmd.Tell("I'm a <dirobj>.") will end up printing:
        I'm a shrubbery. If the dirobj in fact is a shrubbery.
        """
        if string.find(pStr,'<') < 0 or string.find(pStr,'>') < 0:
            return pStr
        str = pStr.replace('<actor>',self.actor(0,pFor))
        str = str.replace('<Actor>',cap(self.actor(0,pFor)))
        str = str.replace('<The actor>',self.actor(The,pFor))
        str = str.replace('<the actor>',self.actor(the,pFor))
        str = str.replace('<A actor>',self.actor(A,pFor))
        str = str.replace('<a actor>',self.actor(a,pFor))

        if isInstance(self.dirobj):
            str = str.replace('<dirobj>',self.dirobj(0,pFor))
            str = str.replace('<Dirobj>',cap(self.dirobj(0,pFor)))
            str = str.replace('<The dirobj>',self.dirobj(The,pFor))
            str = str.replace('<the dirobj>',self.dirobj(the,pFor))
            str = str.replace('<A dirobj>',self.dirobj(A,pFor))
            str = str.replace('<a dirobj>',self.dirobj(a,pFor))
#           else: print "dirobj not an instance"

        if isInstance(self.inobj):
            str = str.replace('<inobj>',self.inobj(0,pFor))
            str = str.replace('<Inobj>',cap(self.inobj(0,pFor)))
            str = str.replace('<The inobj>',self.inobj(The,pFor))
            str = str.replace('<the inobj>',self.inobj(the,pFor))
            str = str.replace('<A inobj>',self.inobj(A,pFor))
            str = str.replace('<a inobj>',self.inobj(a,pFor))

        if isInstance(self.toobj):
            str = str.replace('<toobj>',self.toobj(0,pFor))
            str = str.replace('<Toobj>',cap(self.toobj(0,pFor)))
            str = str.replace('<The toobj>',self.toobj(The,pFor))
            str = str.replace('<the toobj>',self.toobj(the,pFor))
            str = str.replace('<A toobj>',self.toobj(A,pFor))
            str = str.replace('<a toobj>',self.toobj(a,pFor))

        str = str.replace('<time>',string.split(pub.scheduler.GetTime())[0])

        return str

    def Tell(self, pToActor='', pToOthers='', pToThird='', pWhoIsThird=None ):
        """
        The commands Tell Method:
            usually called with cmd.Tell from objects
            used by objects to tell us what happens to them
    
            for example:
                cmd.Tell(self.succ,self.osucc)

            will print self.succ to the actor and self.osucc to others in 
            room who are listening.

            curious... only things which we can see, can see what we do. 
            rather much a childs point of view =) 
            will have to fix this 
        """
        room = self.actor.container
#       if hasattr(room,'ComputeTotalLight'): room.ComputeTotalLight()
        if pToActor:
            self.actor.Tell( self.StuffString(pToActor,self.actor) )
        if pToThird and pWhoIsThird.listening:
            pWhoIsThird.Tell( self.StuffString(pToThird,pWhoIsThird) )
        if pToOthers:
            for item in self.actor.LocalNouns():
                if item != self.actor and item != self.actor.container \
                and item != pWhoIsThird and item.listening:
                    item.Tell( self.StuffString(pToOthers,item) )

#----------------------------------------------------------------------
#    Parser -- breaks a string into a command or set of commands
#
class Parser:
    """
    Parser:
            breaks a string into a command or set of commands
    """

    
    def __init__(self):
        self.words = []
        self.cmd = Command()
        self.it = ''
        self.me = ''

    def NounWords(self,words):
        """
        given a set of words, see how many words you can lump together
        as a single noun from the beginning of the string. Thus,
            given: "give bucket of fish to bob"  we return: 0
                   "bucket of fish to bob"       ==>        3
               "bucket to bob"               ==>        1
        """

        # the first word must be an integer, "it", or in our noun list
        if not words: return 0    # no words
        if words[0] == 'it': return 1    # "it"
        if words[0][0] == '"': return 1    # quoted string
        if isInt(words[0]):    # integer
            # first word is an integer; convert to generic form
            words[0] = "#"
        if words[0]=="#" or words[0] in nouns:
            # first word is in nouns; how many more words can we munch?
            a = string.join(words)
            matches = filter(lambda x,a=a: a[:len(x)] == x, nouns)
            if not matches: return 1        # (must be a number)
            # we now have a set of potential matches; find the longest
            matches.sort(lambda a,b: cmp(len(a),len(b)))
            longest = matches[len(matches)-1]
            return len(string.split(longest))
        return 0

    def FindPrep(self,words):
        """
        print "Looking for prep in", words
        return the position of the first preposition in words,
        not looking past the first verb.
        Return -1 if no preposition is found
        """
        
        for i in range(0,len(words)):
            if words[i] in verbs: return -1
            if words[i] in preps: return i
        return -1

    def MunchNouns(self,w):
        """
        starting at w, munch a set of nouns joined by conjunctions
        return the set, and remove them from self.words
        """
        
        if w >= len(self.words): return []
        out = []
        nounwords = self.NounWords(self.words[w:])
        while nounwords:
            if self.words[w] == 'it': out = out + self.it
            else: out.append(string.join(self.words[w:w+nounwords]))
            self.words = self.words[:w] + self.words[w+nounwords:]
            if w >= len(self.words) or self.words[w] not in conjs: 
                return out
            while self.words[w] in conjs:
                self.words = self.words[:w] + self.words[w+1:]
            nounwords = self.NounWords(self.words[w:])
        return out    

    def WordEnd(self,pStr,pStart):
        """
        return the position of the end of the word,
        given that it starts at pStart in string pStr
        """

        if pStr[pStart] == '"':
            q = string.find(pStr,'"',pStart+1)
            if q >= 0: return q
        else:
            space = string.find(pStr,' ',pStart)
            comma = string.find(pStr,',',pStart)
            if comma < 0 or (space >= 0 and space < comma):
                if space >= 0: return space
            elif comma >= 0: return comma
        return len(pStr)
    
    def BreakString(self,pStr):
        """
        break the string into a list of words
        - filter garbage and reduce non-quoted stuff to lower case
        - convert commas to conjunctions
        """
            
        w = []
        # loop through string, building list w
        wordstart = 0
        wordend = 0
        strlen = len(pStr)
        while wordstart < strlen:
            # find end of the current word
            wordend = self.WordEnd(pStr,wordstart)
            if pStr[wordstart] == '"':
                w.append(pStr[wordstart:wordend])
            else:
                # copy it into the list (unless it's garbage)
                word = string.lower(pStr[wordstart:wordend])
                if word:
                    if wordend < strlen and pStr[wordend] == ',':
                        if word and word not in garbs: w.append(word)
                        w.append('and')
                        wordend = wordend-1
                    else:
                        if word not in garbs: w.append(word)
            # repeat from the new starting point
            wordstart = wordend+1
        return w
    
    def Parse(self,pStr=''):
        """
        Ok so let's start parsing
        first we send a pStr through the ParseCore which does most of the
        real work. 
        
        Eventually returns a list of quantal commands.
        """
        cmdlist = []
        cmdtext = pStr
        while cmdtext:
            # call the ParseCore routine, to strip one verb's worth
            cmdtext = self.ParseCore(cmdtext)

            # break the multiple objects into single objects, multiple commands
            # hmm, there's gotta be a better way to do this...
            cm = Command()
            #print self.cmd
            cm.verb = self.cmd.verb
            if not self.cmd.dirobj: self.cmd.dirobj = ['']
            if not self.cmd.toobj: self.cmd.toobj = ['']
            if not self.cmd.inobj: self.cmd.inobj = ['']
            if not self.cmd.atobj: self.cmd.atobj = ['']
            if not self.cmd.withobj: self.cmd.withobj = ['']
            for a in self.cmd.dirobj:
              for b in self.cmd.toobj:
                for c in self.cmd.inobj:
                  for d in self.cmd.atobj:
                    for e in self.cmd.withobj:
                        cm.dirobj = a
                        cm.toobj = b
                        cm.inobj = c
                        cm.atobj = d
                        cm.withobj = e
                        #print cm
                        cmdlist.append(copy.copy(cm))
        # now we have a nice list of quantal commands; return it
        return cmdlist
    
    def ParseCore(self,pStr):
        """
        Does all the namecalling, cleaning up and findind our verbs,
        prepositions and so on. 
        """
        #print "Parsing:",pStr
        self.cmd.Clear()

        # special case: check for "say" with no quotes and other shortcuts
        if pStr[0] == '"': pStr = "say "+pStr
        elif len(pStr)>5 and \
        string.lower(pStr[:4]) == "say " and pStr[4] != '"':
            pStr = 'say "'+pStr[4:]
                
        # get words; strip out garbage
        self.words = self.BreakString(pStr)
       
        # apply translations
        if self.me: translations['me'] = self.me
        for i in range(0,len(self.words)):
            if translations.has_key(self.words[i]):
                self.words[i] = translations[self.words[i]]
               
        # first word should be a verb -- if not, supply 'defverb'
        w = 0
        if len(self.words)>w and self.words[w] in verbs:
            self.cmd.verb = self.words[w]
            w = w + 1
        else:    self.cmd.verb = 'defverb'
        
        # after verb: nothing, adverb, noun or conjuction
        if len(self.words) < w+1: return ''        # no more words
        
        # look for verb modifiers
        if self.words[w] in adverbs:
            self.cmd.verb = self.cmd.verb + ' ' + self.words[w]
            self.words = self.words[:w] + self.words[w+1:]
            if w >= len(self.words): return ''
        
        # munch conjunctions
        while self.words[w] in conjs:
            self.words = self.words[:w] + self.words[w+1:]
        
        # munch a direct object
        self.cmd.dirobj = self.MunchNouns(w)
        
        # if there's another noun phrase, then it's the DO and we had IO before
        temp = self.MunchNouns(w)
        if temp:
            self.cmd.toobj = self.cmd.dirobj
            self.cmd.dirobj = temp

        if self.cmd.dirobj: self.it = self.cmd.dirobj
        if len(self.words) < w+1: return ''        # no more words
               
        while self.words[w] in preps:
            # find the object of the preposition, and assign appropriately
            objs = self.MunchNouns(w+1)
            if not objs:
                pub.player.Tell("..." + self.words[w] + " WHAT?!?")
                return '' 
                   
            if self.words[w] == 'at': self.cmd.atobj = objs
            elif self.words[w] == 'in' or self.words[w] == 'into' \
              or self.words[w] == 'from': self.cmd.inobj = objs
            elif self.words[w] == 'with': self.cmd.withobj = objs
            elif self.words[w] == 'to': self.cmd.toobj = objs
            else: print "ERROR: unknown preposition " + self.words[w]
                
            # munch preposition
            self.words = self.words[:w] + self.words[w+1:]

            self.it = objs
            if len(self.words) < w+1: return ''    # no more words
                
        # look for dangling verb modifiers
        if self.words[w] in adverbs:
            self.cmd.verb = self.cmd.verb + ' ' + self.words[w]
            self.words = self.words[:w] + self.words[w+1:]
            if w >= len(self.words): return ''
            # munch conjunctions
            while self.words[w] in conjs:
                self.words = self.words[:w] + self.words[w+1:]
                   
        # next word should be a verb
        if self.words[w] in verbs:
            return string.join(self.words[w:])
        
        # if not, something's wrong -- might be unknown word
        print 'Warning: unknown word '+self.words[w]
        return '' 
        
        def Test(self):
            """
            Test the parser
            """
            if "fish" not in nouns: nouns.append("fish")
            if "fish bucket" not in nouns: nouns.append("fish bucket")
            print "Nouns: ",nouns
            print "Verbs: ",verbs
            done = FALSE
            while not done:
                command = raw_input("Parser Test>")
                if command == "quit": done = TRUE
                else: print string.join(map(str,self.Parse(command)),'\n')

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
            
#----------------------------------------------------------------------

verbs = ['drop','get','go','inv','look','eat','give','put','use']
adverbs = ['on','off']
nouns = ['it','self','me','here','room','fish','fish bucket','bucket','rock']
conjs = ['and','then']
preps = ['at','in','into','with','from','to']
garbs = ['the','a']
translations = {}

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

    def __init__(self,pNames=''):
        self.synonyms = string.split(string.lower(pNames),',')
        self.duration = 1        # time (in minutes) to execute
        self.succ = 'You ' + self.synonyms[0] + '.'
        self.osucc = '<The actor> ' + self.synonyms[0] + 's.'
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
        execute and output the event
        
        do the actual action, i.e. changes to the game objects
        
        do post-processing to provide alternate output
        return OK in either case here, since command executed
        """
        if self.DoPostchecks(cmd) == OK:
            cmd.Tell( self.succ, self.osucc )
        return OK

#----------------------------------------------------------------------
# BaseThing -- base class of any noun in the game
#
class BaseThing:
    """
    BaseThing:
        base class of any noun in the game
        (why not 'Noun'?)
    """
        
    # initialization method
    def __init__(self,pName=''):
        self.a = 'a'    # article to use for 'a'
        self.blind = FALSE    # if TRUE, can't see anything
        self.container = None    # its location
        self.defverb = None    # no default verb
        self.desc = ''   # description
        self.initialDesc = ''    # desc, before it's moved (if different)
        self.initialNote = ''    # note, before it's moved (if different)
        self.invisible = 0    # invisibilty level (0 = plainly visible)
        self.invisName = "something"    # perceived "name" when invisible
        self.light = 0    # light given off (100 = sunlight)
        self.listening = FALSE    # wants Tell() calls?
        self.listLine = ''    # line to print in contents list
        self.name = string.split(pName,',')[0]    # main name
        self.note = ''    # line to print in room contents (if nonstandard)
        self.salient = TRUE    # show in room contents list?
        self.seesDark = 0    # bonus to room light when this is seeing
        self.seesInvisible = 0    # invisibility level which this can see
        self.size = 10    # size (100=human)
        self.synonyms = string.split(string.lower(pName),',')
        self.the = 'the'    # article to use for 'the'
        
        # special initialization
        self.desc = 'It looks like an ordinary '+self.name+'.'

        # add names to the parser's list of nouns
        for n in self.synonyms:
            if n not in nouns: nouns.append(n)

    
    def __getinitargs__(self):
        """
        get arguments (used by copy.copy)
        """
        return (string.join(self.synonyms,','),)
 
    
    def GetName(self, article=0, pLooker=None):
        """
        get name
        """
        if pLooker and not pLooker.CanSee(self):
            if article==The or article==A: return cap(self.invisName)
            return self.invisName
        if not article: return self.name
        if article==the: return self.the + ' ' + self.name
        if article==a: return self.a + ' ' + self.name
        if article==The: return cap(self.the) + ' ' + self.name
        if article==A: return cap(self.a) + ' ' + self.name
        return self.name

    
    def __call__(self,article=0,pLooker=None):
        """
        allow treating an object like a function,
        as a shorthand for GetName
        """
        return self.GetName(article,pLooker)

    
    def NameMatch(self, pName):
        """
        check for a name match
        """
        return pName in self.synonyms


    def GetNote(self):
        """
        get note (for when listing the contents of a room)
        """
        if self.initialNote: return self.initialNote
        if self.note: return self.note
        #This is a nasty hack.  Doing it without a hack will touch
        #a lot more code, though, so I'm doing it this way for now.
        from os import environ
        if environ.get('PUBTESTING')=='true':
            return 'There is ' + self(a) + ' here.'
        #End hack.
        return random.choice( ['You see ' + self(a) + ' lying here.',
                               self(A) + ' is lying here.',
                               'There is ' + self(a) + ' here.'] )
        
                
    
    def GetDesc(self,pDepth=0):
        """
        get description
        """
        if self.initialDesc: return self.initialDesc
        return self.desc

    
    def GetRoom(self):
        """
        get room (not just any container, but the first ROOM container)
        """
        cont = self
        while cont and not hasattr(cont,'ComputeTotalLight'):
            cont = cont.container
        return cont

    
    def GetListLine(self): 
        """
        get line to be printed in a list of items (e.g., for inventory)
        when an item should have a listline you either have to write it
        like so:
            '  - a shrubbery of sorts' or
            self.Getname(a) + ' of sorts' if the main name is shrubbery.
        """
        if self.listLine: return self.listLine        
        return '   - ' + self.GetName(a)


    def CanSee(self, pWhat):
        """
        can we see the given object? (assuming it's present)
        """
        # if we're blind, automatically return FALSE
        if self.blind: return FALSE

        # figure effect of lighting and night vision...

        effectiveLight = self.GetRoom().light + self.seesDark
        # anything which gives off light can always be seen
        # (unless it's the room itself)
        if pWhat.light > 0 and pWhat != self.container:
            effectiveLight = 100

            # figure effect of invisibility and counter-invisibility vision...

        visible = 1 - pWhat.invisible + self.seesInvisible
            
        # return TRUE only if both light and visibility are good
            
        return effectiveLight > 20 and visible > 0


    def CanContain(self, pWhat): 
        """
        can we contain something?
        """
        return FALSE
    

    def Tell(self, pWhat,pCmd=None):
        """
        let the object hear something
        
        by default, do nothing
        the pCmd parameter allows substitution of various
        object names, depending on whether this object can see 'em
        """
        return

    # checks, before and after this object is used as the object of a command
    
    def PreObj(self, cmd): return OK

    def PostObj(self, cmd): return OK

    # checks before and after this object is moved
    def PreMove(self):
        self.GetRoom().ComputeTotalLight()
        return OK
    
    def PostMove(self):
        self.GetRoom().ComputeTotalLight()
        return OK
    
    def MoveTo(self, pWhere):
        """
        move objects to destination in pWhere if checks pass

        if the destination is 'TRASH' delete object
        """
        if pWhere == 'TRASH': 
            if self.container: 
                self.container.contents.remove(self)
                del self
                return CANCEL 
        if not pWhere.CanContain(self) \
        or not self.PreMove():
            return CANCEL
        pWhere.ContainNoCheck(self)
        self.PostMove()
        return OK
                    

#----------------------------------------------------------------------
# Symbol -- Base class for nouns and components -- used by the
#           component based object system
#
class Symbol:
    """
    Symbol:
        Base class of componets and nouns/things.
        It contains methods and variables to handle components 
        mostly.
    """

    advise(instancesProvide=[ISymbol])

    def __init__(self):
        
        self._components = [] # PRIVATE variable
                              # a list of classes or instances
                              # that should be added to the object when
                              # initialized.

        self.components = [] # a list that contains references 
                             # to components after it has been initialized.
                             # this is the variable that the outside uses.
        
        self.addComponents(self._components) # Add the components
            

    def addComponents(self,com):
        """
        method that adds components to the components list.
        checks three possible ways it can be called, with either a list, a class
        or an instance. Only when called with an instance does the component get
        added to the list, in other cases it's converted into an instance and
        resent to addComponents
        """

        if com:
        
            if type(com) == types.ListType:
                for each in com: self.addComponents(each)
            
            elif type(com) == types.ClassType: 
                self.addComponents(com())

            elif type(com) == types.InstanceType and isinstance(com, Symbol): 
                self.components.append(com)
        
            else: raise TypeError('com must be of type List, Class or Instance')

            # there might well be more issues to deal with but this is a start.

    def delComponents(self,com):
        """
        Can be called in the same way as addComponents, with a list, class or
        instance. However dealing with deleting componets is a bit harder.
        When given a list the list is looped through and calls to delComponents
        are made.
        When given a class all classinstances are deleted.
        When given an instance just that instance is removed.        
        """
        
        if com:

            if type(com) == types.ListType: 
                for each in com: self.delComponents(each)

            elif type(com) == types.ClassType: 
                delete = []
                for item in self.components:
                    if item.__class__ == com:
                        delete.append(item)

                #delete all occurences of the class
                for item in delete:
                    self.components.remove(item)
                del delete        

            elif type(com) == types.InstanceType: 
                if com in self.components:
                    self.components.remove(com)
            
            else: raise TypeError('com must be of type List, Class or Instance')
