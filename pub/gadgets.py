#	gadgets.py			6/01/98 JJS
#
#	This module defines a number of handy (or at least cool) gadgets.
#
#	Use this module with:  import gadgets
#
#	2002-5/10: Terry Hancock
#		Copy brief comments into doc strings.
#
#----------------------------------------------------------------------
"""
Extended collection of 'Thing's useful in making games.

These are convenience objects which implement various useful
things you might want in a game. They can be used as is or
inherited into even more specialized objects.
"""

# standard modules
import whrandom
import string
import types
import regex
import copy

# PUB modules
import pub
from pubcore import *
import pubverbs
import pubobjs

#----------------------------------------------------------------------
#	ScriptPlayer: executes a script, which is a list of strings.
#	The strings are stored in the "script" attribute.
#
#		Each string may be one of:
#			DELAY delay
#			DO command
#			text to be announced to the room
#
class ScriptPlayer(pubobjs.Actor):
	"""
	ScriptPlayer: executes a script.
	
	Which is a list of strings stored in the "script" attribute.
	This is a subclass of Actor.
	"""

	def __init__(self,pNames):
		pubobjs.Actor.__init__(self,pNames)
		self.script = []
		self.curItem = 0
		pub.scheduler.AddEvent(3,Event(self,'object.Play()'))

	def Play(self):
		"""
		Playback the script.
		"""
		if not self.script: return
		item = self.script[self.curItem]
		self.curItem = self.curItem + 1
		if self.curItem >= len(self.script): self.curItem = 0
		firstword = string.split(item)[0]
		delay = 1
		if firstword == "DELAY":
			delay = toInt(string.split(item)[1])
		elif firstword == "DO":
			command = item[3:]
			self.DoCommandString(command)
		else:
			self.Announce(item)
		pub.scheduler.AddEvent(delay, Event(self,'object.Play()'))

#----------------------------------------------------------------------
#	Transceiver: when on, transmits to all others
#		(makes a pub.transceiverList variable)
#
class Transceiver(pubobjs.Switch):
	"""
	Transceiver when on, transmits to all others what it hears.
	(makes a pub.transceiverList variable)
	"""

	def __init__(self,pNames):
		pubobjs.Switch.__init__(self,pNames)
		# add to the global radio list
		try:
			pub.transceiverList.append(self)
		except:
			pub.transceiverList = [self]
		self.prefix = "On the transceiver: "
		self.effectOnCode = "self.listening = 1"
		self.effectOffCode = "self.listening = 0"
		self.effectOn = '<The dirobj> is now on.'
		self.effectOff = '<The dirobj> is now off.'
		self.oeffectOn = '<The actor> activates <the dirobj>.'
		self.oeffectOff = '<The actor> deactivates <the dirobj>.'
		self.getOnOn = FALSE
		self.offOnDrop = FALSE
		
	def Tell(self,pWhat):
		# we have to be careful not to tell other transceivers,
		# or we'd get a positive feedback loop!
		for rcvr in pub.transceiverList:
			if rcvr.listening and rcvr != self:
				for item in rcvr.GetRoom().contents:
					if item.listening and item not in pub.transceiverList:
						item.Tell(self.prefix + pWhat)

#----------------------------------------------------------------------
#	Button
#
class Button(pubobjs.Thing):
	"""
	A simple button.
	Python code is assigned to <button>.useCode to
	define action. (I think).
	"""

	def __init__(self,pNames):
		pubobjs.Thing.__init__(self,pNames)
		self.useCode = ''
		self.defverb = pubverbs.push
		self.salient = 0
		self.object = None
	
	def Use(self,pByWhom):
		if self.object: 
			object = self.object
		else: 
			object = self.container
		if self.useCode: 
			exec self.useCode

#----------------------------------------------------------------------
#	Elevator
#
class Elevator(pubobjs.Room):
	"""
	Elevator object -- 
		'LinkFloor', 'HandleButton', 'CloseDoors', 'MoveByName',
		'MoveToFloor', 'OpenDoors', 'Idle', 'GetDesc'

	I still don't fully understand how to use this object.

	Probably similar to Vehicle.
	"""

	def __init__(self,pNames):
		pubobjs.Room.__init__(self,pNames)
		self.floors = []		# list of accessible floors
		self.inlink = {}		# Exit from floor to elevator
		self.currentFloor = None	# current floor
		self.inNames = 'elevator'	# names to call entrance links
		self.outlink = pubobjs.Exit('out,exit')		# Exit from elevator to floor
		self.ContainNoCheck(self.outlink)
		self.closedDesc = 'The elevator doors are closed.'
		self.openDesc = 'The elevator doors are open.'
		self.open = FALSE
		self.busytill = 0

	def LinkFloor(self,pRoom,pNames = ''):
		"""
		Used to build an elevator?

		I think you use this method to construct the connections
		that make up an elevator/elevator shaft object. (I.e.
		rather than it being an action the elevator takes).
		"""
		if pRoom in self.floors: return
		
		# make a link to the elevator
		self.floors.append(pRoom)
		self.inlink[pRoom] = pubobjs.Exit(self.inNames)
		self.inlink[pRoom].dest = self
		self.inlink[pRoom].open = FALSE
		pRoom.ContainNoCheck(self.inlink[pRoom])
		
		# make a button inside the elevator
		if pNames:
			button = Button( pNames )
		else:
			button = Button( string.join(pRoom.synonyms,',') )
		self.ContainNoCheck(button)
		button.useCode = "object.HandleButton(self)"
		button.floor = pRoom

		# make a button on the floor itself
		button = Button( 'button' )
		button.useCode = "object.HandleButton(self)"
		button.floor = pRoom
		button.object = self
		pRoom.ContainNoCheck(button)
		
	def HandleButton(self, pButton):
		if self.busytill < pub.scheduler.minutes:
			t = pub.scheduler.minutes + 1
		else:
			t = self.busytill + 1
		if self.open:
			pub.scheduler.AddAbsEvent(t, Event(self,'object.CloseDoors()'))
			t = t + 2
		if self.currentFloor != pButton.floor:
			pub.scheduler.AddAbsEvent(t, \
					Event(self,'object.MoveByName("'+pButton.floor.name+'")') )
			t = t+1
		pub.scheduler.AddAbsEvent(t, Event(self,'object.OpenDoors()'))
		t = t+5
		pub.scheduler.AddAbsEvent(t, Event(self,'object.Idle()'))
		self.busytill = t
		return

	def CloseDoors(self):
		self.Tell('The elevator doors close.')
		self.outlink.dest.Tell('The elevator doors close.')
		if self.currentFloor:
			self.inlink[self.currentFloor].desc = self.closedDesc
			self.inlink[self.currentFloor].open = FALSE
		self.outlink.desc = self.closedDesc
		self.outlink.dest = None
		self.outlink.open = FALSE
		self.open = FALSE
	
	def MoveByName(self,pName):
		"""
		Move to a floor according to the floor's name.
		"""
		f = filter(lambda x,a=pName: x.name==a, self.floors)
		self.MoveToFloor(f[0])
	
	def MoveToFloor(self,pRoom):
		"""
		Move to a floor (object)
		This is called by MoveByName.
		"""
		if pRoom not in self.floors:
			print "Error: invalid floor specified in Elevator.MoveToFloor()"
			return
		if self.open: self.CloseDoors()
		self.currentFloor = pRoom
		self.Tell('The elevator has arrived at '+pRoom.GetName()+'.')
	
	def OpenDoors(self):
		"""
		Open the elevator doors and generate appropriate views.
		Could be generated by a button or some more complex scheduling?
		"""
		if not self.currentFloor:
			print "Error: can't open Elevator doors without a current floor."
			return
		self.inlink[self.currentFloor].desc = self.openDesc
		self.inlink[self.currentFloor].dest = self
		self.inlink[self.currentFloor].open = TRUE
		self.outlink.desc = self.openDesc
		self.outlink.dest = self.currentFloor
		self.outlink.open = TRUE
		self.open = TRUE
		self.Tell('The elevator doors open.')
		self.outlink.dest.Tell('The elevator doors open.')

	def Idle(self):
		"""
		Close doors automatically after some time.
		"""
		# if not in use, close the doors
		if self.open and self.busytill <= pub.scheduler.minutes:
			self.CloseDoors()

	def GetDesc(self,pLooker=None):
		"""
		Description of the inside of the elevator.
		"""
		out = pubobjs.Room.GetDesc(self,pLooker)
		out = out + "\nYou see the following buttons: "
		for floor in self.floors:
			out = out + "\n     " + floor.GetName()
			if floor == self.currentFloor:
				out = out + " (current floor)"
		return out

#----------------------------------------------------------------------
#	Window
#
class Window(pubobjs.Thing):
	"""
	Object with a view returned by GetDesc. --
		'GetDesc' returns <window>.dest to looker when
		called. If not set, returns a dull message.
	"""

	def __init__(self, pNames):
		pubobjs.Thing.__init__(self,pNames)
		self.prefix = "Through "+self(the)+", you see:"
		self.dest = None
		self.noview = "There's nothing much to see."
		
	def GetDesc(self, pLooker=None):
		if not self.dest or self.dest == pub.universe:
			return self.noview
		return self.prefix + self.dest.GetDesc(pLooker)
	
#----------------------------------------------------------------------
#	Vehicle
#
class Vehicle(pubobjs.Room):
	"""
	Vehicle (car, boat etc).
		Basically a moveable room.  Has a window object which
		changes views when moved. A set of destinations are
		defined in <vehicle>.dests (a dictionary).
		
		'Use' = Get into the vehicle
		'TravelToNamed' = recommended way to cause it to go there.
		
		'PreObj', 'PostObj' appear to be for internal accounting of
		some kind? 
		
		'Leave', 'Arrive', 'TravelTo', 'MoveTo' appear to be mostly
		for internal use (all used by TravelToNamed).	
	"""

	def __init__(self,pNames):
		pubobjs.Room.__init__(self,pNames)
		# create the window, to view the outside from within
		self.window = Window("window,windows,out")
		self.window.MoveTo(self)
		self.window.salient = 0
		# create the exit from the inside
		self.exit = pubobjs.Exit("out,exit,outside,leave")
		self.exit.MoveTo(self)
		# set good notes etc.
		self.note = self(A) + " is parked here."
		self.dests = {}
		self.route = pub.universe
		self.leave = self(The) + " gets underway."
		self.oleave = self(The) + " departs."
		self.arrive = self(The) + " has arrived."
		self.oarrive = self(A) + " has arrived."
		self.goingTo = None
		self.defverb = pubverbs.use
		self.size = 400
		self.opostsucc = '<The actor> enters <the dirobj>.'

	def MoveTo(self, pWhere):
		# when being moved, have to also change the window and exit dest
		self.window.dest = pWhere
		self.exit.dest = pWhere
		return BaseThing.MoveTo(self, pWhere)

	def TravelToNamed(self,pStr):
		if not self.dests.has_key(pStr):
			return CANCEL
		self.TravelTo(self.dests[pStr])
		return OK
	
	def TravelTo(self, pWhere):
		self.Leave()
		self.goingTo = pWhere
		pub.scheduler.AddEvent(10, Event(self,"object.Arrive()") )
	
	def Leave(self):		# cleanly move to self.route
		# close the window and exit
		self.exit.open = FALSE
		self.window.dest = None
		# announce the departure
		self.Tell( self.leave )
		self.container.Tell( self.oleave )
		# move to the enroute room
		self.MoveTo(self.route)
	
	def Arrive(self):		# cleanly move to self.goingTo
		self.MoveTo(self.goingTo)
		self.exit.open = 1
		# announce the arrival
		self.Tell( self.arrive )
		self.container.Tell( self.oarrive )

	def Use(self,pByWhom):	# Use for this means enter it
		pByWhom.MoveTo(self)
		return OK

	def PreObj(self,cmd):
		if cmd.verb == pubverbs.go or cmd.verb == pubverbs.use:
			if not self.exit.open:
				cmd.Tell( "The door is closed." )
				return CANCEL
			if self.size < cmd.actor.size or not self.CanContain(cmd.actor):
				cmd.Tell("You don't fit!")
				return CANCEL
			if pubobjs.Thing.PreObj(self,cmd):
				cmd.Tell("You enter <dirobj>.", "<The actor> enters <the dirobj>.")
				return OK
			return CANCEL
			
		# in any other case, return inherited method
		return pubobjs.Room.PreObj(self,cmd)

	def PostObj(self,cmd):
		if cmd.verb == pubverbs.go or cmd.verb == pubverbs.use:	
			cmd.Tell('', self.opostsucc)
			cmd.Tell(self.GetDesc(cmd.actor))
			return CANCEL	# so that no further output is printed
		# any other condition, return OK for normal output
		return OK
		
#----------------------------------------------------------------------
#	Driver
#

class Driver(pubobjs.NPC):
	"""
	NPC who operates a Vehicle --
		A non-player character who drives a "car" which is defined
		as the container (which is presumeably class Vehicle.
		
		'HearSpeech' appears to be the means of sending a message to
		the driver, and it responds according to capabilities of the
		car object.
	"""

	def HearSpeech(self, pSpeaker, pSpeech):
		car = self.container
		if not hasattr(car,'dests') or not hasattr(car,'TravelToNamed'):
			return CANCEL
		for destname in car.dests.keys():
			if string.count(string.lower(pSpeech),destname):
				self.DoCommandString("nod")
				if not car.TravelToNamed(destname):
					self.DoCommandString("say dern thing won't work!")
					return CANCEL
				return OK
		self.DoCommandString("say Where do you want to go?")

				
#----------------------------------------------------------------------
#	Camera	- a gadget that takes pictures (just "use" it)
#
class Camera(pubobjs.Thing):
	"""
	Takes 'pictures' of container and stores them.
		'Use' = Take a picture of the container, which means to
		record its description.

		'PostObj' After using generates messages. (?) This is
		probably a service called by another module.

		It's like a polaroid -- you don't have to develop the
		pictures.  As soon as the picture is taken, you get
		a picture in your inventory.
	"""

	def Use(self, pByWhom):
		# create a picture of the current scene
		scene = pByWhom.container
		pic = pubobjs.Thing("photo of "+scene()+",photo,picture,pic")
		pic.desc = "The photograph depicts:\n" + scene.GetDesc(pByWhom)

		# and give it to the user
		pByWhom.ContainNoCheck(pic)

		return OK

	def PostObj(self, cmd):
		if cmd.verb == pubverbs.use:
			cmd.Tell("You snap a picture.", \
				"<The actor> snaps a picture.")
			return CANCEL
		return pubobjs.Thing.PostObj(self,cmd)
