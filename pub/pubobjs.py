#	pubobjs.py			6/01/98 JJS
#
#	This module defines the standard PUB objects (Things).
#
#	Use this module with:  import pubobjs
#
#	2002-5/10:
#	Terry Hancock
#		Added docstrings based on comments and some simple
#		code analysis.
#
#----------------------------------------------------------------------

"""
Defines all the most basic objects (see Gadget for some more derivatives).
Also instantiates the "Universe" Room and the Player, named "Everyman"
(presumeably you can change the name afterwards).
"""

# standard modules
import whrandom
import string
import types
import re
import copy

# PUB modules
import pub
from pubcore import *
import pubverbs


#----------------------------------------------------------------------
# Thing -- overrides BaseThing to provide some common PreObj checks
#		(couldn't do this in BaseThing, since it references pubverbs)
#
class Thing(BaseThing):
	"""
	Basic type for most PUB nouns. --
		This is the basic type most PUB objects are based on. It
		actually inherits from BaseThing which is an even more
		basic object.  The difference is that Thing has PreObj
		and PostObj with sensible defaults defines.
	"""

	def __init__(self,pNames=''):
		# if we've already initialized, don't do it again:
		if hasattr(self,'name'): return
		BaseThing.__init__(self,pNames)
		if (pub.lastroom): pub.lastroom.ContainNoCheck(self)

	def PreObj(self,cmd):
		if cmd.verb == pubverbs.get and cmd.dirobj == self:
			if not cmd.actor.CanContain(self):
				cmd.Tell("You can't pick that up.")
				return CANCEL
			if cmd.dirobj.container == cmd.actor:
				cmd.Tell("You've already got <the dirobj>.")
				return CANCEL
		elif cmd.verb == pubverbs.drop:
			if isInstance(cmd.dirobj) and cmd.dirobj.container != cmd.actor:
				cmd.Tell("You don't have <a dirobj>.")
				return CANCEL
		# no other verbs need special checks, so...
		return OK
	
	def PostObj(self,cmd):
		if cmd.verb == pubverbs.get \
		or (cmd.verb == pubverbs.put and cmd.dirobj == self):
			# if we have an "initial" note or desc, delete them when we're moved
			self.initialNote = ''
			self.initialDesc = ''
		return BaseThing.PostObj(self,cmd)

#----------------------------------------------------------------------
# Openable -- object which can be opened, closed, locked, & unlocked
#
#class Openable (Thing):
#
#	# initialization method
#	def __init__(self,pNames=''):
#		Thing.__init__(self,pNames)
#		self.isOpen = TRUE			# currently open?
#		self.isLocked = FALSE		# currently locked?
#		self.key = None				# object required to unlock with
#		self.autolock = FALSE		# automatically lock when closed?
#		self.openFail = "It won't budge."	# open fail msg
#		self.oopenFail= "<The actor> tries to open <the dirobj>, but it won't budge."
#		self.unlockFail = "You don't have the key."		# unlock fail msg
#		self.ounlockFail= "<The actor> tries to unlock <the dirobj>, but has no key."
#		self.onOpenCode = ''		# code to execute upon opening
#		self.onCloseCode= ''		# code to execute upon closing
#		self.openDesc = ''			# special description when open
#		self.closedDesc = ''		# special description when closed
#	
#	def Open(self,pByWhom=None):
#		if self.isOpen: return		# (already open, do nothing)
#		self.isOpen = TRUE
#		if self.openDesc: self.desc = self.openDesc
#		if self.onOpenCode:
#			actor = pByWhom
#			object = self
#			exec self.onOpenCode
#
#	def Close(self,pByWhom=None):
#		if not self.isOpen: return	# (already closed, do nothing)
#		self.isOpen = FALSE
#		if self.closedDesc: self.desc = self.closedDesc
#		if self.onCloseCode:
#			actor = pByWhom
#			object = self
#			exec self.onOpenCode
	

#----------------------------------------------------------------------
# class Switch -- has Activate and Deactivate (and supporting) methods
#
class Switch(Thing):
	"""
	A 'Thing' with simple On-Off behavior --
		Also the base class for garments, boxes, and other
		things which have a basic two-state behavior.
		
		'Use'='Activate'.
		Activate = turn the switch on
		Deactivate = turn the switch off
		No toggle method -- a "toggle" verb does this.
	"""

	def __init__(self,pNames=''):
		Thing.__init__(self,pNames)
		self.effectOnCode = ''	# code to execute when switched on
		self.effectOn = 'You activate <the dirobj>.'	# what to print on On
		self.oeffectOn = '<The actor> activates <a dirobj>.'	# and to others
		self.effectOffCode = ''	# code to execute when switched off
		self.effectOff = 'You deactivate <the dirobj>.'	# what to print on Off
		self.oeffectOff = '<The actor> deactivates <a dirobj>.'
		self.isActive = FALSE	# currently active?
		self.getOnOn = FALSE	# try to GET it when you activate it?
		self.offOnDrop = FALSE	# turn it off when you drop it?
		self.onDesc = ''		# special description when on
		self.offDesc = ''		# special description when off
		self.onNote = ''		# special note when on
		self.offNote = ''		# special note when off
		self.onListLine = ''	# special list line when on
		self.offListLine = ''	# special list line when off
	
	# define some new methods
	def Activate(self,pUser=None):
		"""
		Turn the Switch 'On'.
		"""
		self.isActive = TRUE
		if self.onDesc: self.desc = self.onDesc
		else: 		self.desc = ''
		if self.onNote: self.note = self.onNote
		else: 		self.note = ''
		if self.onListLine: self.listLine = "   - " + self.onListLine
		else: 		    self.listLine = ''
		if pUser: 	user = pUser
		else: 		user = self
		object = self
		here = user.container
		if self.effectOnCode: exec self.effectOnCode
		self.GetRoom().ComputeTotalLight()
	
	def Deactivate(self,pUser=None):
		"""
		Turn the Switch 'Off'.
		"""
		self.isActive = FALSE
		if self.offDesc: self.desc = self.offDesc
		else: self.desc = ''
		if self.offNote: self.note = self.offNote
		else: self.note = ''
		if self.offListLine: self.listLine = "   - " + self.offListLine
		else: self.listLine = ''
		if pUser: user = pUser
		else: user = self
		object = self
		here = user.container
		if self.effectOffCode: exec self.effectOffCode
		self.GetRoom().ComputeTotalLight()

	def Use(self,pUser):
		"""
		Same as 'Activate'.
		"""
		return self.Activate(pUser)

	# see whether the thing can be activated/deactivated
	def PreObj(self,cmd):
		if (cmd.verb == pubverbs.on or cmd.verb == pubverbs.use \
		or cmd.verb == pubverbs.push) and cmd.dirobj == self:
			if self.isActive:
				cmd.Tell('<The dirobj> is already on.')
				return CANCEL
			if self.container != cmd.actor and self.getOnOn:
				#cmd.Tell("You don't have <the dirobj>.")
				cmd.actor.DoCommandString("get "+ self.name)
				return OK
				#return CANCEL
		elif cmd.verb == pubverbs.off and cmd.dirobj == self:
			if not self.isActive:
				cmd.Tell('<The dirobj> is not on.')
				return CANCEL
		elif cmd.verb == pubverbs.drop or cmd.verb == pubverbs.give:
			if self.isActive and self.offOnDrop:
				self.Deactivate(cmd.actor)
				cmd.Tell( self.effectOff, self.oeffectOff )
		return Thing.PreObj(self,cmd)

	# PostObj: perform action, give the appropriate output
	def PostObj(self,cmd):
		if cmd.verb == pubverbs.on or cmd.verb == pubverbs.use \
		or cmd.verb == pubverbs.push:
			cmd.Tell( self.effectOn, self.oeffectOn )
			return CANCEL
		elif cmd.verb == pubverbs.off:
			self.Deactivate(cmd.actor)
			cmd.Tell( self.effectOff, self.oeffectOff )
			if cmd.verb == pubverbs.off: return CANCEL			
		return Thing.PostObj(self,cmd)

#----------------------------------------------------------------------
# Container -- base type of any object which can contain another
#
class Container (Thing):
	"""
	Object which can contain other objects.
		<container>.contents is just a list of contained
		objects (i.e. references).

		Ability to contain a 'Thing' is based on the Thing's
		single-parameter "size". (i.e. nothing as complex
		as length/breasth/weight or other considerations).
		Also sizes seem not to be additive, can contain
		as many smaller things as we want..
	"""

	# initialization method
	def __init__(self,pNames=''):
		Thing.__init__(self,pNames)
		self.contents = []
		self.fail = "You can't put <a dirobj> in <the inobj>."

	# return true if this object can contain another
	def CanContain(self,pThing):
		"""
		Determines if the 'Thing' to be contained is smaller
		than this container.
		"""
		return pThing.size < self.size;

	# move the given object to the contents of this one
	def ContainNoCheck(self,*pThing):
		"""
		Puts an object into the container.
		"""
		#print self(the)+" contains ",pThing
		for item in pThing:
			if item.container != None:
				# remove from previous container
				item.container.contents.remove(item)
			item.container = self
			self.contents.append(item)

	def PreObj(self,cmd):
		if cmd.verb == pubverbs.put and cmd.inobj == self:
			if not self.CanContain(cmd.dirobj):
				cmd.Tell(self.fail)
				return CANCEL
		return Thing.PreObj(self,cmd)

#	def GetDesc(self):
#		if not self.contents: return Thing.GetDesc(self)
#		return Thing.GetDesc(self) + '\n' + self.GetContentsDesc()

	def GetContentsDesc(self, pLooker=None):
		"""
		Describes the contents of the object by reporting their
		'GetListLine' method results.
		"""
		out = ''
		contentslist = filter(lambda x:x.salient, self.contents)
		if pLooker:
			contentslist = filter( lambda x,a=pLooker: a.CanSee(x), contentslist)
		for item in contentslist:
			out = out + '\n' + item.GetListLine()
		return out

	# return list of visible contents as objects (recursively)
	def VisibleContents(self):
		"""
		Returns a list of contents recursively. The comments say
		it must be transparent or open, but I don't see any code
		to check that.
		"""
		out = self.contents
		for item in out:
			if hasattr(item,'contents'):	# and is open or transparent...
				out = out + item.VisibleContents()
		return out

# end of class Container

#----------------------------------------------------------------------

# base class of any room or location
class Room(Container):
	"""
	Basic 'Room' object, a special 'Container'.
		A special case of container to use as a room. The
		room is contained in the PUB universe and has a light
		property and a large size (5000), so that it will not
		complain about containing objects including the player.

		It also has a Tell method which seems to broadcast
		messages to anyone in the room (Player or NPC?)
	"""

	def __init__(self,pNames=''):
		Container.__init__(self,pNames)
		self.ownLight = 75		# internal light, where 0=pitch black, 100=sunlight
		self.light = 75			# total light (including light sources)
		self.size = 5000
		if pub.universe and pub.universe != self: pub.universe.ContainNoCheck(self)
		pub.lastroom = self		# note last room created

	def GetDesc(self, pLooker=None):
		"""
		Get the Room's Description --
		Get a description of the room for 'Look'ers
		and 'Camera's (etc.)
		"""
		if pLooker and not pLooker.CanSee(self):
			isDark = TRUE
			out = "It's too dark to see much.\n"
		else:
			isDark = FALSE
			out = '\n' + self.GetName() + '\n'
			out = out + Thing.GetDesc(self) + '\n'
		for item in self.contents:
			if item != pLooker and (not pLooker or pLooker.CanSee(item)) and \
			(item.salient or (isDark and item.light>5)):
				out = out + '\n  ' + item.GetNote()
		return out + '\n'

	def Tell( self, pWhat, *pExcept):
		"""
		Broadcast info to Actors in Room --
		If we 'Tell' a 'Room', it means 'Tell' all the 'Actor's
		in the 'Room'.
		"""
		whom = filter(lambda x,n=pExcept: x.listening and x not in n, self.contents)
		for i in whom: i.Tell(pWhat)

	def ComputeTotalLight(self):
		"""
		Count how many light sources we have available. --
		Including ones contained in (transparent or open?)
		containers in the room.
		"""
		if self == pub.universe: return	# don't bother for universe object
		self.light = self.ownLight
		for item in self.VisibleContents():
			self.light = self.light + item.light
		return self.light

# end of class Room

#----------------------------------------------------------------------
# Box -- a Container which can be opened, closed, locked, etc.
#
class Box (Container,Switch):
	"""
	Minimal 'Container' plus 'Switch' --
		A very minimal container which also inherits from switch.
		(I guess you Activate it to open it?).  Doesn't seem to
		be more than the sum of its parts, though (e.g. nothing
		seems to make Activate determine whether it can accept
		contents).
	"""

	def __init__(self,pNames=''):
		Container.__init__(self,pNames)
		Switch.__init__(self,pNames)

	def PreObj(self,cmd):
		return Switch.PreObj(self,cmd) and Container.PreObj(self,cmd)
	
	def PostObj(self,cmd):
		return Switch.PostObj(self,cmd) and Container.PostObj(self,cmd)

#----------------------------------------------------------------------
# class for exits -- things which connect one room to another
#
class Exit(Thing):
	"""
	Exit / Entrance to a Room --
		Connections between rooms (e.g. Door).
		Size is "3 people" = 300 (which means people are 100).
		Default verb is 'Go'. 'Use' is the same?

		Default is it goes nowhere.

		Note that an Exit is also an entrance.  (I think you
		connect 'Exit' to 'Exit' rather than Exit to Room,
		but I haven't verified this yet).
	"""

	def __init__(self,pNames=''):
		Thing.__init__(self,pNames)
		self.dest = None		# by default, no destination
		self.salient = 0		# and not salient
		self.light = 1			# but glows in the dark (i.e., usable in dark)
		self.size = 300			# and as big as 3 people
		self.defverb = pubverbs.go	# no verb needed to go thru
		self.opostsucc = '<The actor> enters the room.'	# msg to others in destination
		self.open = TRUE		# door is open by default
		
		if 'north' in self.synonyms:
			self.opostsucc = '<The actor> enters from the south.'
		elif 'south' in self.synonyms:
			self.opostsucc = '<The actor> enters from the north.'
		elif 'east' in self.synonyms:
			self.opostsucc = '<The actor> enters from the west.'
		elif 'west' in self.synonyms:
			self.opostsucc = '<The actor> enters from the east.'
		self.note = 'You can go to the '+self()+' from here.'

	# move someone through the exit, if possible
	def Use(self,pWhom):
		"""
		Move an actor through the exit,
		if possible.
		"""
		if not self.open: return
		# perform the move
		pWhom.MoveTo(self.dest)

	# check to see whether using this exit is possible
	def PreObj(self,cmd):
		if cmd.verb == pubverbs.go or cmd.verb == pubverbs.use:
			if not self.open:
				cmd.Tell( "The door is closed." )
				return CANCEL
			if not self.dest:
				cmd.Tell("<Dirobj> leads nowhere.")
				return CANCEL
			if self.size < cmd.actor.size or not self.dest.CanContain(cmd.actor):
				cmd.Tell("You don't fit!")
				return CANCEL
			if Thing.PreObj(self,cmd):
				cmd.Tell("You head <dirobj>.", "<The actor> exits to <the dirobj>.")
				return OK
			return CANCEL
		
		if cmd.verb == pubverbs.push:
			cmd.Tell("Pushing has no effect.")
			return CANCEL
			
		# in any other case, return inherited method
		return Thing.PreObj(self,cmd)

	def PostObj(self,cmd):
		if cmd.verb == pubverbs.go or cmd.verb == pubverbs.use:	
			cmd.Tell('', self.opostsucc)
			cmd.Tell(self.dest.GetDesc(cmd.actor))
			return CANCEL	# so that no further output is printed
		# any other condition, return OK for normal output
		return OK

# end of class Exit

#----------------------------------------------------------------------

# base class of any person, monster, or other chanacter
class Actor(Container):
	"""
	Base class of People or other active Creatures.
		Implements agent-like behavor.
	
		This will probably be the parent class of
		agent-extensions to PUB. (See 'NPC' for
		what will probably be expected of them.
	"""

	def __init__(self,pNames=''):
		Container.__init__(self,pNames)
		self.a = ''			# no article for Actors
		self.cmdList = []		# list of commands to be executed
		self.size = 100			# human-sized
		self.listening = 1		# wants Tell() calls
		self.par = Parser()		# my very own command interpreter
		self.par.me = self.synonyms[0]	# which knows my name
		self.speakingTo = None	# whom we're addressing
		self.busytill = 0		# busy until what time?
		self.invisName = "someone"
		self.followers = []		# list of actors following
		self.following = None	# whom we're following
		self.the = ''			# no article for Actors
		self.note = self(The) + " is here."

	def GetName(self,article=0,pLooker=None):
		"""
		Get the actor's name. --
		By default, no article will be used with it (e.g. we 
		don't say "a John is here", we say "John is here").
		"""
		# don't use articles with Actors, unless explicitly specified
		if self.the or self.a or (pLooker and not pLooker.CanSee(self)):
			return Container.GetName(self,article,pLooker)
		return self.name

	def Act(self):
		"""
		Does nothing -- overload?
		"""
		return

	def Announce(self, pWhat):
		"""
		Speak to the room --
		This character says something which is heard by everyone
		in the 'Room' (more precisely, the container).
		"""
		if self.container:
			self.container.Tell( pWhat, self )

	# get list of objects within visible/reachable range
	def LocalNouns(self):
		"""
		Everything visible from the room. --
		
		Gets a list of objects in visible/reachable range.
		
		There's a note here about extending it to include container's
		container in the search. (Not sure if that's a good idea).
		"""
		# that'd be everything visible from the room...
		out = self.container.VisibleContents()
		# plus room's container's contents (maybe later)
		return out

	# given the name of a noun, return the visible object
	def FindNoun(self,pName,cmd=None):
		"""
		Find a thing if in the room --
		Given the name of a noun, return the visible object.
		Returns None if the noun can't be found (?).
		"""
		if not pName: return None
		if pName == 'self' or pName == 'me': return self
		if pName == 'here' or pName == 'room': return self.container
		l = filter(lambda x,a=pName: x.NameMatch(a),self.LocalNouns())
		if len(l) > 1 and cmd:
			# multiple matches... try to resolve by context
			l2 = []
			if cmd.verb == pubverbs.drop or cmd.verb == pubverbs.give:
				l2 = filter(lambda x,a=cmd.actor: x.container==a, l)
			elif cmd.verb == pubverbs.get:
				l2 = filter(lambda x,a=cmd.actor: x.container!=a, l)
			elif cmd.verb == pubverbs.defverb:
				l2 = filter(lambda x:x.defverb, l)
			if len(l2) > 0: l = l2
		if not l: return None
		if len(l)==1: return l[0]
		# still can't resolve?  For now, pick arbitrarily
		return l[0]

	# similar to above, but if it can't find the object, return the given string
	def NameToObj(self,pName,cmd=None):
		"""
		Find a thing in the room --
		Given the name of a noun, return the visible object.
		If not found, returns the name (first argument to this method).
		"""
		ans = self.FindNoun(pName,cmd)
		if ans: return ans
		return pName

	def DoCommandString(self,cmdstr):
		"""
		Interpret a command to the actor. --

		If first word is an Actor's name, interpret it as
		a "say" action.

		There's a concept here of a 'command list', which I hope
		will become clear from other parts of the code.

		Anyway, this code executes the first command as it's
		last act (presumeably the command list is completed by
		some other part of the code -- perhaps commands consume
		turns?).
		"""
		# check for direct address
		firstword = stripPunctuation( string.split(cmdstr)[0] )
		obj = self.NameToObj(firstword)
		if hasattr(obj,'DoCommandString'):
			# a-ha!  Direct address... make it into a SAY command
			cmdstr = 'say "' + cmdstr + '"'

		# build the command list from the command string
		# (insert at beginning, so we can insert prerequisite commands)
		self.cmdList = self.par.Parse(cmdstr) + self.cmdList
		#print "@Got: ",map(str,self.cmdList)

		# do the first command in the list immediately
		self.DoNextCmd();
	
	def DoNextCmd(self):
		"""
		Do the next command in the list --
			The command interpretation process.  When complete,
			adds the next command via the "Scheduler".
			
			So commands consume turns or time.
		"""
		if not self.cmdList: return CANCEL
		cmd = copy.copy(self.cmdList[0])
		self.cmdList = self.cmdList[1:]
		#if self == pub.player: print "Executing:", cmd
		cmd.actor = self

		if pub.verbdict.has_key(cmd.verb):
			cmd.verb = pub.verbdict[cmd.verb]
		
		# attempt to find object references for all nouns in cmd
		cmd.toobj = self.NameToObj(cmd.toobj,cmd)
		cmd.dirobj = self.NameToObj(cmd.dirobj,cmd)
		cmd.inobj = self.NameToObj(cmd.inobj,cmd)
		cmd.atobj = self.NameToObj(cmd.atobj,cmd)
		cmd.withobj = self.NameToObj(cmd.withobj,cmd)
		
		# start the command
		# (the Verb object does most of the work)
		if isInstance(cmd.verb):
			cmd.verb.Do(cmd)
			# special check: if "restoring" a game, then
			# this object must bail out immediately!
			if cmd.verb.__class__ == pubverbs.Restore:
				print "bailing out"
		else:
			self.Tell('Unknown verb '+cmd.verb)

		if self.busytill < pub.scheduler.minutes:
			self.busytill = pub.scheduler.minutes

		self.busytill = self.busytill + 1
		
		# if there's more commands to be done, schedule an event to do it...
		if self.cmdList:
				pub.scheduler.AddAbsEvent( self.busytill, \
						Event(self, 'object.DoNextCmd()' ) )
		else:
			# if not, schedule an Act() event to get more commands
			pub.scheduler.AddAbsEvent( self.busytill, Event(self, 'object.Act()' ) )

		return

	def PreAct(self, cmd):
		"""
		Gets called before doing things --
			Gets called before doing things. Notably, if
			the actor has "followers" (actors who follow
			it, presumeably), they are commanded to follow
			when this actor moves.

			(This seems to be its only current use).
		"""
		if cmd.verb == pubverbs.go and self.followers:
			for item in self.followers:
				item.DoCommandString('go '+cmd.dirobj())
		return OK

# end of class Actor

#----------------------------------------------------------------------

# class of the player -- i.e., the Actor interfaced to the terminal
class Player(Actor):
	"""
	Player's persona in the game --
		This is the interface between the player and the game.
		The player inherits from Actor. 

		However, the player prompts the user for the next action,
		instead of simply reacting as other actors do. (?)

		Has 'Tell' and 'Act' methods.
	"""

	def __init__(self,pNames=''):
		Actor.__init__(self,pNames)
		self.linebreak = 80

	def Tell(self, pWhat):
		"""
		Get information from (actual) player to 'Player'. (?)
		"""
		if self.linebreak:
			# break lines every <linebreak> characters:
			while len(pWhat) >= self.linebreak:
				pos = string.rfind(pWhat[:self.linebreak],' ')
				pos2 = string.rfind(pWhat[:self.linebreak],'\n')
				if pos2 < pos and pos2 > -1: pos = pos2
				print pWhat[:pos]
				pWhat = pWhat[pos+1:]
		print pWhat

	def Act(self):
		"""
		Act on commands in scheduler, or prompt --
		
		If the player's persona already has commands to follow,
		it does, otherwise it asks what to do next.
		"""
		if pub.scheduler.HasEventFor( self ): 
			# I've already got a scheduled event; no need to ask for input
			pub.scheduler.Update()
			return
		# no scheduled events, so ask the user what to do
		#cmdstr = raw_input(pub.scheduler.GetTime()+'>')
		print
		if self != pub.player:
			print "WARNING: self != pub.player>",
		cmdstr = raw_input('>')
		if cmdstr: self.DoCommandString(cmdstr)
		else: pub.scheduler.AddEvent( 1, Event(self, 'object.Act()') )

# end of class Player

#----------------------------------------------------------------------

# class Monitor -- puts whatever it hears to the terminal
class Monitor(Actor):
	"""
	Monitor 'Tell' messages --
		Listens to Tell broadcasts and prints them (I suspect this
		is mostly for debugging). Clearly you could bug a Room
		with this object and tell what NPCs or other Actors are
		up to.
	"""

	def Tell(self,pWhat):
		print '[' + self() + ' hears] ' + pWhat

# end of class Monitor


#----------------------------------------------------------------------
# class Timer -- something that goes off after a certain amount of time on
#
class Timer(Switch):
	"""
	Timer switch --
		This is a real time timer!  Uses the scheduler, which see.
		'Activate' = set the timer for the delay (default= 8 minutes)
		When the time runs out ('ComeDue') it will 'Deactivate'
		(or you can call the method directly?).  
	"""

	def __init__(self,pNames=''):
		Switch.__init__(self,pNames)
		self.delay = 8			# by default, waits 8 minutes
		self.dueCode = ''
		self.canTurnOff = TRUE
		self.failTurnOff = "You can't see any way to deactivate <the dirobj>."
		self.getOnOn = FALSE
		self.offOnDrop = FALSE
		
	def Activate(self,pUser):
		"""
		Upon activation, schedule a 'ComeDue' event.
		"""
		pub.scheduler.AddEvent(self.delay,Event(self,'object.ComeDue()'))
		Switch.Activate(self,pUser)
	
	def ComeDue(self):
		"""
		Deactivate the switch when the time runs out.
		"""
		here = self.container
		if self.dueCode: exec self.dueCode
		Switch.Deactivate(self)
		self.container.Tell( self.oeffectOff )
	
	def PreObj(self,cmd):
		if cmd.verb == pubverbs.off and cmd.dirobj == self:
			if  self.isActive and not self.canTurnOff:
				cmd.Tell(self.failTurnOff)
				return CANCEL
		return Switch.PreObj(self,cmd)

#----------------------------------------------------------------------
# class Garment -- something you can wear (and may have an effect)
#
class Garment(Switch):
	"""
	Clothes or other thing you wear.
		Something you wear, with appropriate messages.
		Inherits from Switch, so it is activated when
		worn.
	"""

	def __init__(self,pNames=''):
		Switch.__init__(self,pNames)
		self.bodypart = ''
		self.effectOn = 'You wear <the dirobj>.'
		self.oeffectOn = '<The actor> dons <a dirobj>.'
		self.effectOff = 'You remove <the dirobj>.'
		self.oeffectOff = '<The actor> removes <a dirobj>.'
		self.onListLine =  self.GetName(a) + " (worn)"

	# check to see whether wearing this garment is possible
	def PreObj(self,cmd):
		if cmd.verb == pubverbs.on:
			if self.isActive:
				cmd.Tell("You're already wearing <the dirobj>.")
				return CANCEL
			
			# check for something already on that body part
			for item in cmd.actor.contents:
				if hasattr(item,'isActive') and item.isActive \
				  and hasattr(item,'bodypart') and item.bodypart == self.bodypart:
					cmd.Tell("You're already wearing something on your " \
								+ self.bodypart + ".")
					return CANCEL
		elif cmd.verb == pubverbs.off:
			if not self.isActive or self.container != cmd.actor:
				cmd.Tell("You're not wearing <the dirobj>.")
				return CANCEL

		return Switch.PreObj(self,cmd)
	
	def PreMove(self):
		self.Deactivate()
		return Thing.PreMove(self)
		
#----------------------------------------------------------------------
# Liquid -- a Thing with some special properties
#
class Liquid(Thing):
	"""
	Liquid objects. --
		Obviously this implements basic liquid behaviors --
		has to be contained to get it, can't put it in
		a container unless it has 'canContainLiquid'
		property.
	"""

	def __init__(self,pNames=''):
		Thing.__init__(self,pNames)
		self.a = "some"
		
	def PreObj(self,cmd):
		if cmd.verb == pubverbs.get:
			cmd.Tell("You'll have to put it in something.")
			return CANCEL
		if cmd.verb == pubverbs.put:
			if not hasattr(cmd.inobj,'canContainLiquid') \
			or not cmd.inobj.canContainLiquid:
				cmd.Tell("<The inobj> can't hold liquids.")
				return CANCEL
		return Thing.PreObj(self,cmd)

#----------------------------------------------------------------------
# Countable -- a Thing with a quantity, can be divided and recombined
#
class Countable(Thing):
	"""
	Countable object (can be plural). --
		Thing with quantity, which is apparently treated as
		a single object otherwise. Can be combined/divided
		etc.
	"""

	def __init__(self,pNames=''):
		Thing.__init__(self,pNames)
		self.quantity = 10
		self.pluralname = self.name + 's'
		for item in self.synonyms:
			term = "# "+item
			if term not in nouns: nouns.append(term)
		self.newquantity = 0
		self.prevqty = 0
	
	def GetName(self,article=0,pLooker=None):
		"""
		Return singular or plural name with appropriate article.
		"""
#		return self.pluralname + ' (' + str(self.quantity) + ')'
		if self.quantity == 1:
			self.a = 'a'
			self.the = 'the'
			self.name = self.synonyms[0]
		else:
			self.a = str(self.quantity)
			self.the = str(self.quantity)
			self.name = self.pluralname
		return Thing.GetName(self,article,pLooker)
	
	def GetNote(self):
		"""
		Gets appropriate note with quantity indicated.
		"""
		return "You see " + self.GetName(a) + " here."
	
	def NameMatch(self,str):
		"""
		See if it is (at least) N objects.
		"""
		# print "Trying name match of ",str," with ",self.GetName()
		# name should match if it starts with a number less that self.quantity
		self.newquantity = self.quantity
		words = string.split(str)
		if len(words) < 2 or not isInt(words[0]):
			return Thing.NameMatch(self,str)
		givenNum = toInt(words[0])
		if givenNum > 0 and givenNum <= self.quantity:
			if Thing.NameMatch(self, string.join(words[1:]) ):
				self.newquantity = givenNum		# remember number used...
				return TRUE
			else: return FALSE
		# number's invalid... no match
		return FALSE

	def Split(self,pQty):
		"""
		Divide the plural object into more than one
		plural object containing the same amount in total.
		"""
		# create a new object, pQty less than the current one
		newobj = copy.copy(self)
		# copy.copy calls the constructor, so the new object
		# may get put into the last room built...
		if pub.lastroom: pub.lastroom.contents.remove(newobj)
		self.container.contents.append(newobj)
		# split the quantities between the old and new objects
		newobj.quantity = newobj.quantity - pQty
		newobj.newquantity = newobj.quantity
		self.quantity = pQty
		self.newquantity = pQty
	
	def Absorb(self, pOther):
		"""
		Combine more than one similar object into a
		single collection object.
		"""
		# absorb the other one into this one, and delete the other
		self.quantity = self.quantity + pOther.quantity
		pOther.container.contents.remove(pOther)
		del pOther
	
	def PostMove(self):
		self.prevqty = self.quantity
		for item in self.container.contents:
			if item != self and item.synonyms == self.synonyms:
				self.Absorb(item)	
		return BaseThing.PostMove(self)

	def PreObj(self,cmd):
		# if we do something that would GET or DROP some items,
		# but not all of them, then we need to split this object		
		if (cmd.verb == pubverbs.get or cmd.verb == pubverbs.drop \
		or cmd.verb == pubverbs.give) \
		and self.newquantity < self.quantity:
			# print self.newquantity,'<',self.quantity,', so...'
			self.Split(self.newquantity)
			return OK
		return Thing.PreObj(self,cmd)

	def PostObj(self,cmd):
		# here, we need to see if we can consolidate with others like us
		if cmd.verb == pubverbs.get or cmd.verb == pubverbs.drop \
		or cmd.verb == pubverbs.give:
			# special output for when we've absorbed some other items
			if self.prevqty != self.quantity:
				amount = str(self.prevqty) + ' '
				if self.prevqty == 1: amount = amount + self.synonyms[0]
				else: amount = amount + self.pluralname
				if cmd.verb == pubverbs.get:
					cmd.Tell('You take ' + amount + ' (you now have '+ \
							  str(self.quantity)+').', \
							'<The actor> takes ' + amount + '.')
				elif cmd.verb == pubverbs.drop:
					cmd.Tell('You drop ' + amount + '.', \
							'<The actor> drops ' + amount + '.')
				elif cmd.verb == pubverbs.give:
					cmd.Tell('You give ' + amount + ' to <toobj>.', \
							'<The actor> gives ' + amount + ' to <toobj>.',
							'<The actor> gives you ' + amount + ' (you now have '+ \
							 str(self.quantity)+').', cmd.toobj )
				else:
					cmd.Tell('You '+cmd.verb.synonyms[0]+' '+amount+'.', \
							'<The actor> '+cmd.verb.synonyms[0]+'s '+amount+'.' )
				return CANCEL
		return OK
		
#----------------------------------------------------------------------
# NPC -- a Non-Player Character; an Actor with simple responses
#
class NPC(Actor):
	"""
	Non-Player Character -- 
	
		Actor with simple responses.
		
		Responds to commands, etc. If we want a more full-featured
		agent character, we'll probably attempt to mimic this
		interface.

		An advanced agent-based character would probably be
		written to support this interface.  (Possibly with
		additional methods to interact with other advanced
		agents).
	"""

	def __init__(self,pNames=''):
		Actor.__init__(self,pNames)
		self.obedient = TRUE
		self.replies = { 
			'hello': [ 'Hi', 'Hello', 'Hi already!', 'Sheesh!' ],
			'howdy': [ 'Howdy to you.', 'Hi' ],
			'weather': [ "Yes, isn't it?", "Beautiful, just beautiful." ],
			'thank': [ "You're welcome.", "No problem.", "Think nothing of it."]
		}
		self.replies['hi'] = self.replies['hello']
		self.replies['thanks'] = self.replies['thank']
		self.noReply = self.GetName() + " does not reply."
		self.replyCounter = {}

	# some compiled regular expressions to speed things up
	_yousay_re = re.compile('You say ".*"')
	_othersays_re = re.compile('.* says, ".*"')
	
	# Here's the main function through which NPC's react:
	# they hear something, via their Tell() method
	def Tell(self, pWhat):
		"""
		Hear something told to me --
			Here's the main function through which NPC's react:
			they hear something, via their Tell() method.
		"""
		#print "@", self.synonyms[0], "heard:", pWhat
		# if it's something we said, don't reply
		if self._yousay_re.match(pWhat): return

		# if it's someone else speaking, figure out who
		if self._othersays_re.match(pWhat):
			speakername = string.split(pWhat)[0]
			speaker = self.FindNoun( string.lower(speakername) )
			if not speaker:
				self.Announce( self.GetName()+' looks around in confusion. ' \
					+ '"Who said that?!?"' )
				return
			
			sezwhat = string.split(pWhat,'"')[1]

			return self.HearSpeech( speaker, sezwhat )

		# if it's not either, it must be some effect
		self.HearEffect( pWhat )
	
	def HearSpeech(self, pSpeaker, pSpeech):
		"""
		Hear speech from another actor --
		A special case of Tell, when another actor is
		speaking to me.
		"""
		# is the speaker speaking to me?
		for word in self.synonyms:
			if (string.count( string.lower(pSpeech), word )):
				pSpeaker.speakingTo = self

		#print "@", pSpeaker, ' speaking to ', pSpeaker.speakingTo
		
		# if not speaking to me, then maybe ignore it
		if pSpeaker.speakingTo != self and whrandom.randint(0,1): return
		
		words = string.split( stripPunctuation(pSpeech) )
		if not words: return
		# for now, assume speaker is speaking to me
		# check for keywords
		for word in words:
			# remove punctuation
			word = stripPunctuation(word)
			if self.replies.has_key(word):
				# found a word!
				if not self.replyCounter.has_key(word): repnum = -1
				else: repnum = self.replyCounter[word]
				repnum = repnum + 1
				if repnum >= len(self.replies[word]): repnum = 0
				self.replyCounter[word] = repnum
				self.DoCommandString('say '+self.replies[word][repnum])
				return
		
		# no keywords found?  Check for a verb (or name, then verb)
		w = 0
		if self.NameMatch(words[w]):
			# ah, my name -- definitely speaking to me!
			if len(words) < 2: return
			w = 1
		#print "@Checking for a verb: ", words[w]
		if pub.verbdict.has_key(words[w]):
			# looks like a command!
			return self.HearCommand( pSpeaker, string.join(words[w:]) )
			
		# no verbs either?  Give null reply (or nothing at all)
		if whrandom.randint(0,2): self.Announce( self.noReply )

	def HearCommand(self, pCommander, pCmdStr ):
		"""
		Hear and react to commands --
		May act on the command or not, depending on whether
		the 'obedient' property has been set. Doesn't seem
		to distinguish who I'm obedient to -- this would seem
		to be necessary with advanced characters who might be
		expected to give orders as well as take them.
		"""
		# if not obedient...
		if not self.obedient:
			pCommander.Tell( self.GetName() + " ignores you.")
			return
		# if obedient, then execute the command
		# after converting all "me"s to commander's name
		pCmdStr = replace( "me", string.capwords(pCommander.synonyms[0]), pCmdStr )
		self.DoCommandString( pCmdStr )

	def HearEffect(self, pStr ):
		"""
		Does nothing. --
		I think it's a hook for responding to non-verbal inputs.
		"""
		# nothing for now...
		return

#----------------------------------------------------------------------
#
# create the two required objects
#

pub.universe = Room("Universe")
pub.player = Player("Everyman")
