#       pub.py                                             8/27/96 JJS
#
#       This module defines some "global" variables.
#
#       To use it:   import pub
#                    print pub.scheduler  (or whatever)
#
#----------------------------------------------------------------------

scheduler = None    # this should be set to a Scheduler at start-up time
verbdict = {}       # dictionary, converts words to Verb objects
gameStatus = 1      # game is RUNNING
lastroom = None     # last room created; default location for new objects
universe = None     # room which contains all other rooms
player = None       # game player (esp. for single-user games)
debugging = 0       # are we dubugging?  Don't set this, see 'Debugging' below
dbgverbs = []       # a list of verbs for debugging

from pubcore import *           # import core datatypes, functions, & constants
import pubverbs                 # import standard verbs
verbs = pubverbs
import pubobjs                  # import standard object library
objs = pubobjs
import gadgets
import pubtcp
tcp = pubtcp

class BailOutError(Exception):  # exception to raise to bail out of current
    pass                        # stack frame (used when restoring, etc.)

def Debugging(mode='on'):
    """
    to enable debugging mode
    used by putting pub.Debugging() after import pub like so:

        import pub; pub.Debugging()

    in your game file when doing the importing.

    Turn if off with:

        pub.Debugging('off')

    """
    if mode.lower() == 'on':
        if 'pubdebug' not in locals():
            try: import pubdebug
            except: pass
        debugging = 1
        print 'Debugging On'
    if mode.lower() == 'off':
        try: del pubdebug
        except: pass
        for verb in verbs:
            if verb in dbgverbs:
                del verb
        debugging = 0
