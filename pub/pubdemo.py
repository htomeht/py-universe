#	PUB Demo			8/27/96 JJS
#
#	This file demonstrates a few simple objects.
#

import pub				# import global variables
from pubcore import *		# import core datatypes, functions, & constants
import pubobjs				# import standard object library
import gadgets				# import wierd & wonderful things

# create shortcuts for most common object types
Room = pubobjs.Room
Exit = pubobjs.Exit
Thing = pubobjs.Thing
NPC = pubobjs.NPC

pub.scheduler = Scheduler("12:00")		# start the clock!

#----------------------------------------------------------------------
#	Create some objects
#

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
square = Room("Town Square")
square.desc = 'You are in the center of town.  A "Gadget Shop" lies to \
the west, and the street runs north and south.  Wilderness lies to the east.'

square.ContainNoCheck(pub.player)
pub.player.hunger = 2
pub.player.thirst = 2

Bert = NPC("Bert,Herbert")
Bert.desc = "He's just a nondescript, ordinary-looking guy.  (But he just \
might give you a sack if you tell him to.)"

banana = pubobjs.Edible('banana')
banana.poison = 'neural'

bag = pubobjs.Container("bag,sack")
bag.size = 30
bag.canContainLiquid = 0
Bert.ContainNoCheck(bag)

rock = Thing("rock,stone")
rock.desc = "It looks like an ordinary rock, except that it glows very faintly."
rock.light = 5

square_n = Exit("north,n")
square_w = Exit("west,w,gadget,shop")
square_s = Exit("south,s")
square_e = Exit("east,e,out,wilderness")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
northend = Room("North End of Town")
northend.desc = "Standing at the north end of the town, you have shops on \
three sides and the center of town to the south."
square_n.dest = northend

barrel = pubobjs.Container("barrel,keg")
barrel.desc = "A large wooden barrel has been set at the end of the street."
barrel.canContainLiquid = TRUE
barrel.size = 30

water = pubobjs.Drinkable("water,H2O")
water.size = 5
barrel.ContainNoCheck(water)

northend_n = Exit("north,n,clothes")
northend_w = Exit("west,w,magic")
northend_w.desc = "The building to the west appears to be a magic shop."
northend_s = Exit("south,s,main,square,center,street,town")
northend_s.dest = square
northend_e = Exit("east,e,food,inn,spam")
northend_e.desc = "The sign hanging in front of the establishment to the east \
appears to depict a large, calm snake amidst red-hot flames."

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
inn = Room("The Flaming Python")
inn.desc = "This pub is dark, loud, and smells of spirits."
northend_e.dest = inn

mug = pubobjs.Container("mug,glass,stein")
mug.canContainLiquid = TRUE
mug.initialNote = "There's an abandoned mug on one of the tables."
mug.initialDesc = "It's an ordinary beer mug, lying abandoned in a puddle of \
solitude which is probably exceeded only by that surrounding its former owner."
mug.size = 6

chips = pubobjs.Countable("chip,chips")
chips.desc = "Potato chips is potato chips -- what would you expect?"

inn_w = Exit("west,w,exit,out,street")
inn_w.dest = northend

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
magicshop = Room("Magic Shop")
magicshop.desc = "You're in a small building filled with arcane magic items."
northend_w.dest = magicshop

cloak = pubobjs.Garment("cloak")
cloak.desc = "This magic cloak will make you invisible.  It says so, \
right there on the tag."
cloak.effectOnCode = "user.invisible = 1"
cloak.effectOffCode = "user.invisible = 0"

magicshop_e = Exit("east,e,exit,out,street")
magicshop_e.dest = northend

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
southend = Room("South End of Town")
southend.desc = "You're at the south end of the town street.  There are \
buildings to the south, east, and west.  The center of town lies north.  \
There is a dusty manhole in the street."
square_s.dest = southend

trans2 = gadgets.Transceiver('Transceiver2,trans2,tran2')

guard = gadgets.ScriptPlayer("Guard")
guard.script = [
	'DELAY 10', 'DO go north', 'The Guard marches up and down the square.',
	'DELAY 10', 'DO go north',
	'DELAY 10', 'DO go south', 'The Guard marches up and down the square.',
	'DELAY 10', 'DO go south']
guard.desc = "It's a tall, lean man in a crisp uniform, who has decorated \
his face with a neatly trimmed mustache and a perpetual scowl."

southend_n = Exit("north,n,main,square,center,street,town")
southend_n.dest = square
southend_w = Exit("west,w")
southend_s = Exit("south,s")
southend_e = Exit("east,e")
southend_e.desc = "The shop to the east has no sign, and appears to be empty."
southend_d = Exit("down,d,manhole,sewer")
southend_d.desc = "You could barely lift the manhole enough to slip through.  \
It looks like it leads into a sewer."

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
gadshop = Room("Gadget Shop")
gadshop.desc = "This shop is filled with all manner of inscrutable gizmos.  \
You have no idea what most of them could be."
square_w.dest = gadshop

clock = pubobjs.Thing("clock,timepiece,grandfather")
clock.desc = "It's a dark rosewood grandfather clock, which reads <time>. \
The pendulum swings methodically back and forth."
clock.note = "A large clock against the wall reads <time>."
clock.size = 150

glasses = pubobjs.Garment('pair of glasses,glasses,pair,spectacles,eyewear')
glasses.desc = "These magic glasses will let you see invisible objects."
glasses.effectOnCode = "user.seesInvisible = 1"
glasses.effectOffCode = "user.seesInvisible = 0"
glasses.bodypart = "eyes"

trans1 = gadgets.Transceiver('Transceiver1,trans1,tran1')

blindfold = pubobjs.Garment('blindfold,blind,fold')
blindfold.effectOnCode = "user.blind = 1"
blindfold.effectOffCode = "user.blind = 0"
blindfold.bodypart = "eyes"

jack = pubobjs.Timer('jack-in-the-box,box,jack')
jack.onDesc = 'The Jack-in-the-box is ticking softly, as the little \
crank whirls round.'
jack.offDesc = 'The Jack-in-the-box is sitting quietly, just waiting \
for someone to activate it.'
jack.effectOn = 'You push Jack into his box, forcing the crank around.'
jack.oeffectOn = "<The actor> pushes Jack into his box, forcing its crank around."
jack.onNote = "You see a jack-in-the-box, its crank slowly ticking around."
jack.onListLine = "a jack-in-the-box (ticking)"
jack.effectOff = "Jack leaps out of his box with a loud SPROING!"
jack.oeffectOff = jack.effectOff
jack.offOnDrop = FALSE

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

TV = gadgets.ScriptPlayer('TV,telley,television')
TV.script = [
	"DELAY 4", 'On the TV, John says "Marsha, Darling, I love you so much!"',
	'"Don\'t you wish we were married?" says John on the TV.',
	'DELAY 2',
	'"But Darling," Marsha replies, "we are!"',
	'"...or did you mean to each other?"',
	'DELAY 5', 'The TV takes a commercial break.',
	'DELAY 5', 'DO say And now back to our program...']
TV.a = 'a'

camera = gadgets.Camera('camera,cam')

gadshop_s = Exit("east,e,exit,out")
gadshop_s.dest = square

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
invisshop = Room("Invisibility Shop")
invisshop.desc = "This shop has shelves upon shelves of, well, nothing. \
At least, nothing that you can see."
southend_e.dest = invisshop

ring = pubobjs.Garment('ring')
ring.desc = "You see a shimmering, transparent ring."
ring.invisible = 1

invisshop_e = Exit("west,w,exit,out")
invisshop_e.dest = southend

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
sewermain = Room("Sewer, Under the Street")
sewermain.desc = "You're in a sewer main under the street.  A little light \
filters in from the edges of the manhole cover above, but it wouldn't be \
enough for a normal human to see by.  A thin stream of dark water trickles \
by your feet."
sewermain.ownLight = 5
southend_d.dest = sewermain

sewerwater = pubobjs.Liquid('sewer water,stream,water')
sewerwater.desc = "It's a sickly-looking stream of dark liquid."
sewerwater.salient = 0

monitor = pubobjs.Monitor("monitor,mon")
monitor.a = 'a'

sewermain_u = Exit('up,u,out,street,manhole')
sewermain_u.dest = southend
sewermain_u.desc = "You can see a little light filtering in from the edges \
of the manhole.  You can just barely reach it to climb out."
sewermain_u.light = 5

#----------------------------------------------------------------------
#	Run the game
#


pub.player.Tell(pub.player.container.GetDesc(pub.player))

pub.scheduler.AddEvent( 0, Event(pub.player, 'object.Act()') )

while pub.gameStatus == RUNNING:
	try: pub.scheduler.Update()
	except pub.BailOutError: pass
