#	pubrestore.py
#
#	This file demonstrates how a very simple main program can
#	be used to implement a game saved in a pub.dat file.
#

from pubcore import *		# import core datatypes, functions, & constants
import pubobjs				# import standard object library
import pub					# import global variables


#----------------------------------------------------------------------
#	Run the game
#
print "Restoring..."
restoregame()		# load game from file

pub.player.Tell(pub.player.container.GetDesc(pub.player))

pub.scheduler.AddEvent( 0, Event(pub.player, 'object.Act()') )

while pub.gameStatus == RUNNING:
	pub.scheduler.Update()
