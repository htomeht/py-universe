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
downstairs = pub.objs.Room("Downstairs Room")
downstairs.desc = "You're on the ground floor of a tiny house.  The walls \
are featureless, and you can find no doors or windows.  However, there is \
a ladder that leads up through a little hole in the ceiling."
player.MoveTo(downstairs)

downstairs_u = pub.objs.Exit("up,ladder,exit,u,hole,upstairs")
downstairs_u.desc = "Looking up, you get a glimpse of a tiny room much like \
the one you're in."
plant = pub.objs.Thing("potted plant,plant,potted")
plant.desc = "It's a nice green ivy, growing merrily despite the lack of \
direct sunlight."


upstairs = pub.objs.Room("Upstairs Room")
upstairs.desc = "You're in the upper room of this tiny house.  There are no \
windows, and no doors either except for a hole in the floor, through which \
a ladder leads down."

upstairs_d = pub.objs.Exit("down,d,ladder,exit,out,hole,downstairs")
upstairs_d.desc = "It's just a ladder leading down."
Monty = pub.objs.NPC("Monty,Mon,Mr. Python")
Monty.desc = "Monty's a tall man with a large mustache and a very silly walk."
Monty.replies['walk'] = [
	"It's not very silly, but I think with some funding I could develop it.",
	"You think it's silly?  You've got a pretty ordinary walk yourself." ]
Monty.replies['silly'] = Monty.replies['walk']

downstairs_u.dest = upstairs
upstairs_d.dest = downstairs

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
