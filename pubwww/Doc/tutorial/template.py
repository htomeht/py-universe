#	The Name of Your Game Goes Here
#
#	by You        <date>
#
#----------------------------------------------------------------------

# required modules:
from pubcore import *		# import core datatypes, functions, & constants
import pubverbs				# import standard verbs
import pubobjs				# import standard object library
import pub					# import global variables

# extra/optional modules:
import gadgets				# miscellaneous gadgets & gizmos

# start the scheduler
pub.scheduler = Scheduler("12:00")

# create shortcuts for most common object types
Exit = pubobjs.Exit
Thing = pubobjs.Thing
NPC = pubobjs.NPC
player = pub.player

#----------------------------------------------------------------------
#	Define special object types used in this game
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


#----------------------------------------------------------------------
#	Create some objects
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


#----------------------------------------------------------------------
#	Run the game
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
print
print "                            YOUR GAME TITLE"
print "                               by You\n"
print "\nHere's the intro blurb (i.e. prologue) to your game.  Make it \
as long as you like, wrapping the words with a backslash if you want."

raw_input("\n\n[Press Return.]")		# wait for Return
print "\n\n\n"

# tell the player the current room description
player.Tell(player.container.GetDesc(player))

# run the game until it's no longer RUNNING
while pub.gameStatus == RUNNING:
	if not pub.scheduler.events:
		pub.scheduler.AddEvent( 0, Event(player, 'object.Act()') )
	pub.scheduler.Update()
