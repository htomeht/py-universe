# (C) 1998 Joe Strout as pubcore.py
#   events.py
"""
Event object and schedulers.
"""
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
#----------------------------------------------------------------------

# FIXME: audit imports

# system imports

import string
import types
import copy
import random
import re

# pub imports

#import pub
from interfaces import ISymbol, ILangMod 
import adapters
from config import *


# protocols imports

from protocols import adapt, advise

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

# TODO: This is a realtime scheduler. We also need a turn-counting scheduler. (TJH2006/1/20)

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


