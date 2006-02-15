#  debug.py    contains debugging                  verbs 04/10/22  GJ
#
#   Copyright (C) 2004 Gabriel Jagenstedt
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
"""
Includes several in game verbs
DbgContents, DbgExamine SetBreak and DbgPrompt 

Use this by adding 
import debug
to your gamefile of choice. This will make it
possible for you to use debugging facilities.

*Also includes an option to print what happens during execution of a cmd
*Note -- Not yet
"""

#sytem imports
import code, sys

# pub imports
import pub
from config import OK, CANCEL
from verb import Verb
import verbs

# protocols imports

#--------------------------------------------------------------------

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

class DbgExamine(verbs.Transitive):
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
        
verbs.dbgEx = DbgExamine('@ex,@examine')    # instantiate it


#----------------------------------------------------------------------

class DbgContents(verbs.Transitive):
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

verbs.dbgContents = DbgContents('@contents,@con')

#----------------------------------------------------------------------

class DbgPrompt(Verb):
    """@prompt:
    Creates an interactive prompt from which we can check on our 
    objects our try out instantiating things and using methods or 
    whatever use it might be of.
    """

    def __init__(self,pNames=''):
        Verb.__init__(self,pNames)

    def Finish(self,cmd):
        if self.DoPostchecks(cmd) == CANCEL: return OK
        mod = sys.modules['__main__'].__dict__
        code.interact(banner='', local=mod)
        return OK

verbs.dbgPrompt = DbgPrompt('@prompt')

