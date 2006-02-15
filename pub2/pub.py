#    pub    contains "global" variables                   8/27/96 JJS
#
#   Copyright (C) 1996 Joe Strout
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
#----------------------------------------------------------------------


#--------------------------------------------------------------------
# CHANGELOG
#
#   2004-22/10: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
Main pub package 

use by doing -- import pub

Variables are declared first because module that are imported may actually call
some of them.

Further info -- this module is really the "game state", all the stuff that is
needed for a saved game is stuffed into this module, then saved with picklemod.
At least, I think that's how it works. (TJH 2006-2/13)
"""

scheduler = None    # this should be set to a Scheduler at start-up time
verbdict = {}       # dictionary, converts words to Verb objects
gameStatus = 1      # game is RUNNING
lastroom = None     # last room created; default location for new objects
universe = None     # room which contains all other rooms
player = None       # game player (esp. for single-user games)
debugging = False   # are we debugging? 
language = 'english'# a string containing a language default: 'english'


