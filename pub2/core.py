#   core
"""
Basic game functions: save and restore I/O.

Most of the previous contents have been moved into separate modules.
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
#
#   2006-01/22: Terry Hancock
#       Stripped almost everything out of this module, except for
#       save/restore.  Other stuff is now in: events.py, parser.py,
#       verb.py, noun.py, and utility.py. This is because I think
#       it makes that stuff more intuitive to find, and also because
#       many of these modules are getting larger due to internationalization
#       and other factors.
#
#--------------------------------------------------------------------

# OBSOLETE
#"""
#NOTE: Don't mess with this module unless you know what you're doing!
#
# Too late. ;-) TJH

#Includes Scheduler, Event, Command, Parser, Verb, and Noun 
# Not any more:
#       Scheduler, Event--> event.py
#       Command, Parser --> parser.py
#       Verb            --> verb.py
#       Noun            --> noun.py

#Also a number of utility functions. I'm a little
#disturbed by things like "cap" which simply call
#Python library functions -- not sure that we need
#such a wrapper, as it likely increases the learning
#curve for working with the code. (?)  On the other
#hand, if used frequently enough, it might clarify
#the code. If so, we need to add comments to define
#what these things do.
#
#   I agree that cap(x) is bad.  Replacing with x.capitalize()
#   All the utility functions including these, and the "component architecture"
#   utilities from Gabriel are now in utility.py  (TJH2006/2/01)


#----------------------------------------------------------------------

# FIXME: Review/audit import needs

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
from config import *


# protocols imports

from protocols import adapt, advise

#--------------------------------------------------------------------

def savegame(filename='pub.dat', quiet=FALSE):
    """
    Save the game.
    """
    import sys
    import os
    #import pub
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


