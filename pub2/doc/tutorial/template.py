#	The Name of Your Game Goes Here
#
#	by You        <date>
#
#----------------------------------------------------------------------

import pub
from pub.constants import *
player = pub.player

# start the scheduler
pub.scheduler = pub.Scheduler("12:00")

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
		pub.scheduler.AddEvent( 0, pub.Event(player, 'object.Act()') )
	pub.scheduler.Update()
