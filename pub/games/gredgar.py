#	The Greedy Gargoyle
#
#	A mini-adventure by Joe Strout       5/11/96
#                     last revised       8/27/96

from pubcore import *		# import core datatypes, functions, & constants
import pubverbs				# import standard verbs
import pubobjs				# import standard object library
import pub					# import global variables
import gadgets

pub.scheduler = Scheduler("12:00")		# start the clock!

# create shortcuts for most common object types
Exit = pubobjs.Exit
Thing = pubobjs.Thing
NPC = pubobjs.NPC

#----------------------------------------------------------------------
#	Define special object types used in this game
#
class Gargoyle(NPC):

	def __init__(self,pNames):
		NPC.__init__(self,pNames)
		self.door = None
		self.openDesc = "The gargoyle is split in half, leaving the door \
open in between."
		
	def Freeze(self):
		self.Announce('\nThe gargoyle resumes its original pose on the door \
and freezes in position, apparently nothing more than lifeless stone.\n')
	
	def Throw(self,what):
		# first, find the object named by what
		obj = filter(lambda x,a=what: x.name==a, self.contents)
		if not obj: return
		obj = obj[0]
		# now find the pool
		pool = self.FindNoun('pool')
		if not obj: return
		# throw 'em
		if hasattr(obj,'quantity') and obj.quantity > 1:
			self.Announce(obj(The)+" land in the pool with a >splunk!<.")
		else:
			self.Announce(obj(The)+" lands in the pool with a >splunk!<.")
		obj.MoveTo(pool)

	def Open(self):
		self.Announce("Grinning, the gargoyle splits in half, right down \
the middle.  His two halves separate and slide apart, taking the two halves \
of the great stone door with them.  A dark passageway extends beyond the \
door to the north.")
		if self.door: self.door.open = TRUE
		self.closedDesc = self.desc
		self.desc = self.openDesc
		pub.scheduler.AddEvent(10,Event(self,'object.Close()'))
	
	def Close(self):
		self.Announce("The gargoyle door slides shut again, and the two \
halves of the gargoyle fuse with an evil grin.")
		if self.door: self.door.open = FALSE
		self.desc = self.closedDesc
		pub.scheduler.AddEvent(2,Event(self,'object.Freeze()'))
	
	def PostObj(self,cmd):
		if cmd.verb == pubverbs.give:
		
			if cmd.dirobj.name == "gold coin":
				cmd.Tell("As you place the coin in the gargoyle's palm, \
its face comes to life.  It cocks one bulging eye at the coin for a moment, \
then nods approvingly.  With the help of a clawed finger, it begins to \
count -- but, finding only one coin in its palm, it stops abruptly and \
throws the coin down in disgust.")
				cmd.dirobj.MoveTo(self.container)
				pub.scheduler.AddEvent(3,Event(self,'object.Freeze()'))

			if cmd.dirobj.synonyms[0] == "tin coin":
				if self.CanSee(cmd.dirobj):
					cmd.Tell("As you place the false coinage in the gargoyle's \
hand, its face springs to life.  It cocks a bulging eye at your offering.  \
Noting the dull grey color and featureless surfaces, its eyes grow wide.  \
With an angry flick of its arm, it hurls "+cmd.dirobj(the)+" over your head.")
					pub.scheduler.AddEvent(3,Event(self, \
					'object.Throw("'+cmd.dirobj.name+'")'))

					pub.scheduler.AddEvent(4,Event(self,'object.Freeze()'))

				else:	#---- tin coin in the dark ----#
					if cmd.dirobj.quantity > 1: 
						shapes = "shapes"
						their = "their"
						coins = "coins"
					else:
						shapes = "shape"
						their = "its"
						coins = "coin"
					cmd.Tell("As you place "+cmd.dirobj(the)+" into the \
gargoyle's glowing hand, its face comes to life once again.  It cocks an \
eye at the dark round "+shapes+" in its hand.  Frowning, it turns them over \
and appears to be judging "+their+" weight.  With a shrug, it lifts a \
clawed finger and begins counting.")
					if cmd.dirobj.quantity < 3:
						cmd.Tell("Finding only "+str(cmd.dirobj.quantity) \
+ ' ' + coins + ", it stops abruptly and throws the "+ coins + " down in \
disgust.")
						cmd.dirobj.MoveTo(self.container)
						pub.scheduler.AddEvent(3,Event(self,'object.Freeze()'))				
					else:
						cmd.Tell("It stabs its finger at the coins three \
times, and compares this to the three clawed toes on its foot.  Apparently \
satisfied, the gargoyle opens its mouth and tosses the coins down.")
						pub.scheduler.AddEvent(3,Event(self,'object.Open()'))

			return CANCEL
		return OK

#----------------------------------------------------------------------
#	Create some objects
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
room = pubobjs.Room("Fountain Room")
room.desc = "You're in a small room with walls of stone.  In the middle of \
the room is a raised stone pool filled with water.  To the north is a great \
stone door, into which a gargoyle has been carved with amazingly lifelike \
detail."
pub.player.MoveTo(room)
room.ownLight = 5

pool = pubobjs.Container("pool,fountain")
pool.desc = "The pool is composed of circular stone walls about a foot \
high and five feet across.  The floor of the pool is also depressed \
several inches below the floor of the room.  It's filled with a clear \
liquid that appears to be water."
pool.size = 20
pool.salient = FALSE

water = pubobjs.Liquid("water,liquid")
water.desc = "It appears to be ordinary water, and fairly clean."
water.MoveTo(pool)

coins = pubobjs.Countable("tin coin,tin coins,coins,coin,tin,slugs,slug")
coins.desc = "Each tin slug feels just like a genuine gold coin, but \
one can easily tell that it's fake by its color and smooth pattern."
coins.quantity = 3
coins.MoveTo(pool)

gold = Thing("gold coin,gold,coin")
gold.desc = "It's a small coin, but from the gold color and elaborate pattern \
stamped into it, you know it's quite valuable."
gold.MoveTo(pub.player)

garg = Gargoyle("gargoyle,garg,gar,statue,carving")
garg.desc = "The gargoyle is carved into the door with amazing \
three-dimensional relief.  Its face wears an exaggerated expression \
of boredom.  Its hand juts out from the door, palm up."
garg.salient = FALSE
garg.light = 10
garg.note = 'The gargoyle on the door glows faintly in the dark, as \
magical items frequently do.'

door = Exit('north,n,door,exit,leave,out')
door.open = FALSE
door.desc = "It's a great stone door, with a carving of a gargoyle \
that appears amazingly lifelike."
garg.door = door

lamp = pubobjs.Switch('lamp')
lamp.onDesc = 'The lamp is glowing brightly.'
lamp.offDesc = 'The lamp is dark.'
lamp.effectOnCode = 'self.light = 40'
lamp.effectOffCode = 'self.light = 0'
lamp.effectOn = "You turn on the lamp, and it glows brightly."
lamp.oeffectOn = "<The actor> activates the lamp, which glows brightly."
lamp.effectOff = "You turn off the lamp."
lamp.oeffectOff = "<The actor> turns the lamp off."
lamp.offOnDrop = FALSE
lamp.onNote = "A lamp is lying here, glowing brightly."
lamp.onListLine = "a lamp (lit)"
lamp.MoveTo(pub.player)
lamp.Activate(pub.player)

endroom = pubobjs.Room("Congratulations!")
endroom.desc = "You've gotten past the greedy gargoyle -- and it only cost \
you three fake coins!  Nicely done.  You may examine the credits, or quit."
door.dest = endroom

credits = Thing("credits,cred")
credits.desc = "The Greedy Gargoyle was written on May 11, 1996 by \
Joseph J. Strout, using the Python Universe Builder (also by J. Strout).  \
At the time of this writing, there have been no beta testers; give me \
some constructive comments and I'll put your name in this space!"
credits.a = 'the'

tester = Thing("testerama")

#----------------------------------------------------------------------
#	Run the game
#
print
print "                            THE GREEDY GARGOYLE"
print "                           A 5-Minute Text Puzzle"
print "                               by Joe Strout\n"
pub.player.Tell( "Holding your latern high, you cautiously explore the stone panel \
before you.  According to the maps, the entrance to the tomb should be \
right at the end of this passageway -- but you find only smooth stone.")

pub.player.Tell( "\nJust as you're about to give up and go home, your fingers catch \
on a small indentation on the adjoining wall.  When you press the knob \
inside, the panel spins around, carrying you with it." )

pub.player.Tell( "\nYou find yourself in a small room.  The panel through which \
you entered joins perfectly with the wall on this side, leaving no \
hope of returning the way you came.  You'd been studying for years to \
find a way into the tomb -- now, if you can just find a way out...\n\n" )
raw_input("\n\n[Press Return.]")
print "\n\n\n"

#----------------------------------------------------------------------
#	Run the game
#
pub.player.Tell(pub.player.container.GetDesc(pub.player))

pub.scheduler.AddEvent( 0, Event(pub.player, 'object.Act()') )

while pub.gameStatus == RUNNING:
	try: pub.scheduler.Update()
	except pub.BailOutError: pass

