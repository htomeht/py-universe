#  debug.py
#
#  This module contains and defines several functions useful for 
#  debugging

"""debug
Includes several in game verbs
DbgContents, DbgExamine SetBreak and DbgPrompt 

Use this by adding 
import debug
to your gamefile of choice. This will make it
possible for you to use debugging facilities.

*Also includes an option to print what happens during execution of a cmd
*Note -- Not yet
"""

import code, sys


import pub
from constants import OK, CANCEL
from pubcore import Verb
import pubverbs 
#----------------------------------------------------------------------

class SetBreak(Verb):
    """
    @break:    sets line breaks, or turns them off.
    (for debugging)
    It appears that the '@' prefix is used for
    verbs the player isn't really supposed to use.
    """

    def Finish(self,cmd):
        try: num = string.atoi(cmd.dirobj)
        except: num = 0
        cmd.actor.linebreak = num

        return OK

pubverbs.setBreak = SetBreak('@break')    # instantiate it


#----------------------------------------------------------------------

class DbgExamine(pubverbs.Transitive):
    """
    @examine: Print all attributes of an object.
    (for debugging)
    """

    def Finish(self,cmd):
        print '\n', cmd.dirobj,'\n'
        for att in dir(cmd.dirobj):
            print '%20s' % att, ':', getattr(cmd.dirobj,att)
        print
                
        return OK
        
pubverbs.dbgEx = DbgExamine('@ex,@examine')    # instantiate it


#----------------------------------------------------------------------

class DbgContents(pubverbs.Transitive):
    """
    @contents: Print all contents of an object.
    (for debugging)
    """
    def Finish(self,cmd):
        print '\nContents of', cmd.dirobj,'\n'
        if hasattr(cmd.dirobj, 'contents'):
            for item in cmd.dirobj.contents:
                print item, item()
            print
        else: print cmd.dirobj, 'has no contents'
        
       

        return OK

pubverbs.dbgContents = DbgContents('@contents,@con')

#----------------------------------------------------------------------

class DbgPrompt(Verb):
    """@prompt:
    Creates an interactive prompt from which we can check on our 
    objects our try out instantiating things and using methods or 
    whatever use it might be of.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)
        self.mod = sys.modules['__main__'].__dict__

    def Finish(self,cmd):
        if self.DoPostchecks(cmd) == CANCEL: return OK
        mod = sys.modules['__main__'].__dict__
        code.interact(banner='', local=mod)
        return OK

pubverbs.dbgPrompt = DbgPrompt('@prompt')

