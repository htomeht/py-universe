#	pubverbs.py			8/27/96 JJS
#
#	This module defines the standard PUB verbs.
#
#	Use this module with:  import pubverbs
#
#----------------------------------------------------------------------

import string

import pub
from pubcore import *

#----------------------------------------------------------------------
# Transitive verbs -- require a direct object

class Transitive(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		x = self.synonyms[0]
		self.succ = 'You '+x+' <the dirobj>.'
		self.osucc = '<The actor> '+x+'s <a dirobj>.'
		self.fail = cap(x)+' what?!?'
		self.seefail = "You can't see that here."
		self.seesucc = "It takes a bit of groping, but you manage it..."

	def Begin(self,cmd):
		if not cmd.dirobj or not isInstance(cmd.dirobj):
			cmd.actor.Tell(self.fail)
			return CANCEL
		if not cmd.actor.CanSee(cmd.dirobj):
			if cmd.dirobj.container == cmd.actor:
				cmd.Tell(self.seesucc)
			else:
				cmd.Tell(self.seefail)
				return CANCEL
		return Verb.Begin(self,cmd)

	def Finish(self,cmd): return Verb.Finish(self,cmd)

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Social verb class: verbs which do very little, and may either
# have no objects, or one object (which we'll call dirobj).

class Social(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		x = self.synonyms[0]
		self.succ = 'You ' + x + '.'
		self.osucc = '<The actor> ' + x + 's.'
		self.atsucc = 'You ' + x + ' at <the dirobj>.'
		self.atosucc = '<The actor> ' + x + 's at <the dirobj>.'
		self.atobjsucc = '<The actor> ' + x + 's at you.'

	def Finish(self,cmd):		# execute and output the event
		atwhom = cmd.dirobj
		if not atwhom: atwhom = cmd.atobj
		if not atwhom: atwhom = cmd.withobj
		if not atwhom: atwhom = cmd.toobj
		if not atwhom:
			cmd.Tell( self.succ, self.osucc )
		else:
			cmd.dirobj = atwhom		# necessary for correct substitution
			cmd.Tell( self.atsucc, self.atosucc, self.atobjsucc, atwhom )

#----------------------------------------------------------------------
# Default Social Verbs:
#

laugh = Social('laugh,giggle,chuckle')

nod = Social('nod')
nod.succ = 'You nod solemnly.'
nod.osucc = '<The actor> nods solemnly.'
nod.atsucc = 'You nod to <the dirobj>.'
nod.atosucc = '<The actor> nods to <the dirobj>.'
nod.atobjsucc = '<The actor> nods to you.'

grin = Social('grin,smile')
grin.succ = 'You smile charmingly.'
grin.osucc = '<The actor> grins like an idiot.'
grin.atsucc = 'You smile at <the dirobj>.'


#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Use verbs: call the Use(byWhom) method of the object
#
class Use(Transitive):

	def Finish(self,cmd):
		# update the objects
		if cmd.dirobj and isInstance(cmd.dirobj):
			if hasattr(cmd.dirobj,'Use'):
				if cmd.dirobj.Use(cmd.actor) == CANCEL:
					return CANCEL
			else:
				cmd.Tell( '<The dirobj> appears useless.')
				return CANCEL

		# allow superclass to handle postchecks and output
		Transitive.Finish(self,cmd)

#----------------------------------------------------------------------
# Default Use verbs:
#
use = Use('use')
push = Use('push,poke,prod')
push.osucc = '<The actor> pushes <the dirobj>.'
go = Use('go,move,mv,walk,wander')
go.fail = 'Go where?!?'

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# DefVerb: this transitive verb class calls the verb specified by
#	  the defcmd property of the direct object

class DefVerb(Transitive):

	def Begin(self,cmd):
		if not isInstance(cmd.dirobj):
			cmd.actor.Tell('Huh?!?')
			return CANCEL
		if not hasattr(cmd.dirobj,'defverb') or not cmd.dirobj.defverb:
			cmd.Tell('What do you want to do with <the dirobj>?')
			return CANCEL
		theVerb = cmd.dirobj.defverb
		if isString(theVerb): theVerb = pub.verbdict[theVerb]
		cmd.verb = theVerb
		return theVerb.Begin(cmd)

defverb = DefVerb('defverb')		# instantiate it

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Inventory verb (a class unto itself)
#
class Inventory(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		self.succ = 'You are carrying:'
		self.fail = 'You are empty-handed.'

	def Finish(self,cmd):

		# perform post-checks
		if self.DoPostchecks(cmd) == CANCEL: return OK

		# give output
		if cmd.actor.contents:
			cmd.Tell(self.succ)
			for item in cmd.actor.contents:
				if cmd.actor.CanSee(item): cmd.Tell(item.GetListLine())
		else:
			cmd.Tell(self.fail)
		return OK

#----------------------------------------------------------------------
# Inventory verb: can't imagine why you'd need more than one, but...
#
inventory = Inventory('inv,inventory,i')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Get verb -- get an object into your grubby little hands
#
class Get(Transitive):

	def Finish(self,cmd):
		# update the database
		cmd.dirobj.MoveTo(cmd.actor)

		# let superclass handle postchecks and output
		return Transitive.Finish(self,cmd)

#----------------------------------------------------------------------
# Get verb instantiation

get = Get('get,take,grab,obtain,procure')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Drop verb -- place on object into the actor's container
#
class Drop(Transitive):

	def Finish(self,cmd):
		# update the database
		cmd.dirobj.MoveTo(cmd.actor.container)

		# let superclass handle postchecks and output
		return Transitive.Finish(self,cmd)

#----------------------------------------------------------------------
# Drop verb instantiation

drop = Drop('drop')		# couldn't think of any 1-word synonyms!

#----------------------------------------------------------------------
# Follow verb -- follow another Actor
#
class Follow(Transitive):

	def __init__(self,pNames=''):
		Transitive.__init__(self,pNames)
		self.selfsucc = 'You stop following <the dirobj>.'
		self.oselfsucc = '<The actor> stops following <the dirobj>.'
		
	def Begin(self,cmd):
		if not Transitive.Begin(self,cmd): return CANCEL
		if not hasattr(cmd.dirobj,'followers'):
			cmd.Tell("You can't follow <a dirobj>.")
			return CANCEL
		return OK
	
	def Finish(self,cmd):
		# update the database
		if cmd.actor.following:
			cmd.actor.following.followers.remove(cmd.actor)
		if cmd.dirobj != cmd.actor:
			cmd.actor.following = cmd.dirobj
			cmd.dirobj.followers.append(cmd.actor)
			if cmd.dirobj.following == cmd.actor:
				# uh-oh!  following loop!  Have dirobj follow self
				cmd.dirobj.following = None
				cmd.actor.followers.remove(cmd.dirobj)
		else:
			cmd.dirobj = cmd.actor.following
			cmd.actor.following = None
			cmd.Tell( self.selfsucc, self.oselfsucc)
			return OK

		# let superclass handle postchecks and output
		return Transitive.Finish(self,cmd)


follow = Follow('follow,fol')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# On verb -- activate an object
#
class On(Transitive):

	def Begin(self,cmd):
		if not isInstance(cmd.dirobj) or not hasattr(cmd.dirobj,'Activate'):
			cmd.Tell('You can see no way to do that.')
			return CANCEL
		return Transitive.Begin(self,cmd)
		
	def Finish(self,cmd):
		# update the database
		if (cmd.dirobj.Activate(cmd.actor)) == CANCEL: return CANCEL

		# let superclass handle postchecks and output
		return Transitive.Finish(self,cmd)

on = On('activate,on,switch on,turn on,wear,don,light,start')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Off verb -- deactivate an object
#
class Off(Transitive):

	def Begin(self,cmd):
		if not isInstance(cmd.dirobj) or not hasattr(cmd.dirobj,'Deactivate'):
			cmd.Tell('You can see no way to do that.')
			return CANCEL
		return Transitive.Begin(self,cmd)
		
	def Finish(self,cmd):
		# update the database
		cmd.dirobj.Deactivate(cmd.actor)

		# let superclass handle postchecks and output
		return Transitive.Finish(self,cmd)

off = Off('deactivate,off,turn off,switch off,shut off,remove,doff,extinguish,stop')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Toggle verb -- activate or deactivate an object
#
class Toggle(Transitive):

	def Begin(self,cmd):
		if not isInstance(cmd.dirobj) or not hasattr(cmd.dirobj,'Deactivate') \
		or not hasattr(cmd.dirobj,'Activate') or not hasattr(cmd.dirobj,'isActive'):
			cmd.Tell('You can see no way to do that.')
			return CANCEL
		if cmd.dirobj.isActive: cmd.verb = off
		else: cmd.verb = on
		return Transitive.Begin(self,cmd)
		
	def Finish(self,cmd):
		# update the database
		if cmd.dirobj.isActive: cmd.dirobj.Deactivate(cmd.actor)
		else: cmd.dirobj.Activate(cmd.actor)

		# let superclass handle postchecks and output
		return Transitive.Finish(self,cmd)

toggle = Toggle('toggle,switch,turn,change,invert')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Look
#
class Look(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		x = self.synonyms[0]
		self.osucc = '<The actor> '+x+'s around.'
		self.atsucc = 'You ' + x + ' at <the dirobj>.'
		self.atosucc = '<The actor> ' + x + 's at <the dirobj>.'
		self.atobjsucc = '<The actor> ' + x + 's at you.'
		self.fail = cap(x)+' at what?!?'

	def Finish(self,cmd):
		if cmd.atobj: cmd.dirobj = cmd.atobj
		if cmd.dirobj:
			if not isInstance(cmd.dirobj) or not cmd.actor.CanSee(cmd.dirobj):
				cmd.Tell(self.fail)
				return CANCEL
			cmd.Tell(cmd.dirobj.GetDesc(), self.atosucc, self.atobjsucc, cmd.dirobj)
		elif cmd.inobj:
			if not isInstance(cmd.inobj) or not cmd.actor.CanSee(cmd.inobj):
				cmd.Tell(self.fail)
				return CANCEL
			str = cmd.inobj.GetContentsDesc(cmd.actor)
			if str:
				cmd.Tell('It looks like <the inobj> contains:' + str)
			else:
				cmd.Tell('<The inobj> appears to be empty.')
		else:	# no objects specified? describe the room
			cmd.Tell(cmd.actor.container.GetDesc(cmd.actor), self.osucc)
		return OK

#----------------------------------------------------------------------
look = Look('look,l,examine,ex,x,inspect,read')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Put -- put something into something else
#
class Put(Transitive):

	def __init__(self, pNames=''):
		Transitive.__init__(self,pNames)
		self.succ = "You put <the dirobj> into <the inobj>."
		self.osucc= "<The actor> puts <a dirobj> into <a inobj>."
		self.inobjsucc= "<The actor> puts <a dirobj> into you."

	def Begin(self,cmd):
		if not isInstance(cmd.inobj):		# must have inobj
			if isInstance(cmd.dirobj):
				cmd.Tell('Put <the dirobj> where?!?')
			else:
				cmd.Tell('Put what where?!?')
			return CANCEL
		else:
			if not isInstance(cmd.dirobj):
				cmd.Tell('Put *what* into <the inobj>?!?')
				return CANCEL
			if not cmd.inobj.CanContain(cmd.dirobj):
				cmd.Tell("You can't put <the dirobj> into <the inobj>.")
				return CANCEL
		return Transitive.Begin(self,cmd)

	def Finish(self,cmd):
		# update the database
		cmd.dirobj.MoveTo(cmd.inobj)

		if self.DoPostchecks(cmd) == OK:
			cmd.Tell( self.succ, self.osucc, self.inobjsucc, cmd.inobj )
		return OK
		
# instantiate Put
put = Put('put,stuff,stick')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# Give -- give something to someone else
#
class Give(Transitive):

	def __init__(self, pNames=''):
		Transitive.__init__(self,pNames)
		self.succ = "You give <the dirobj> to <the inobj>."
		self.osucc= "<The actor> gives <the inobj> <a dirobj>."
		self.inobjsucc = "<The actor> gives you <a dirobj>."
		self.infail = "Give <the dirobj> to whom?!?"
		
	def Begin(self,cmd):
		if cmd.toobj: cmd.inobj = cmd.toobj
		if not isInstance(cmd.inobj):		# must have inobj
			cmd.Tell(self.infail)
			return CANCEL
		return Transitive.Begin(self,cmd)

	def Finish(self,cmd):
		# update the database
		cmd.dirobj.MoveTo(cmd.inobj)

		if self.DoPostchecks(cmd) == OK:
			cmd.Tell( self.succ, self.osucc, self.inobjsucc, cmd.inobj )
		return OK
		
# instantiate Give
give = Give('give,hand')

#----------------------------------------------------------------------
# Quit the game

class Quit(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		x = self.synonyms[0]
		self.succ = 'Quitting game.'
		self.osucc = '<The actor> '+x+'s the game.'

	def Finish(self,cmd):
		# to quit the game, set pub.gameStatus...
		pub.gameStatus = QUIT

		# let superclass handle postchecks and output
		return Verb.Finish(self,cmd)
		
# instantiate Quit
quit = Quit("quit")

#----------------------------------------------------------------------
# Wait (by default, 5 minutes)

class Wait(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		self.succ = 'Time passes...'
		self.osucc = '<The actor> waits.'
		self.duration = 5				# wait 5 minutes

	def GetDuration(self,cmd):
		# duration may be specified as a direct object
		if isInt(cmd.dirobj): return toInt(cmd.dirobj)
		return self.duration

	def Finish(self,cmd):
		return OK

# instantiate Wait
wait = Wait("wait,z")
zz = Wait("zz")
zz.duration = 10
zzz = Wait("zzz")
zzz.duration = 15

#----------------------------------------------------------------------
# Say

class Say(Verb):

	def __init__(self,pNames=''):
		Verb.__init__(self,pNames)
		self.succ = 'You say'
		self.osucc = '<The actor> says,'
		self.fail = 'Say what?!?'
		self.duration = 0

	def Begin(self,cmd):
		if not cmd.dirobj:
			cmd.actor.Tell(self.fail)
			return CANCEL
		return Verb.Begin(self,cmd)
	
	def Finish(self,cmd):
		# perform post-checks
		if self.DoPostchecks(cmd) == CANCEL: return OK

		# give output
		# (remember to strip the quote which might be the first character)
		text = str(cmd.dirobj)
		if text[0]=='"': text = text[1:]
		cmd.Tell( self.succ + ' "' + text + '"', \
				  self.osucc+ ' "' + text + '"')

		return OK
		
say = Say('say,speak,talk')		# instantiate it

#----------------------------------------------------------------------
# @break -- sets line breaks, or turns them off
#

class SetBreak(Verb):

	def Finish(self,cmd):
		try: num = string.atoi(cmd.dirobj)
		except: num = 0
		cmd.actor.linebreak = num
				
		return OK
		
setBreak = SetBreak('@break')	# instantiate it


#----------------------------------------------------------------------
# @Examine -- a debugging verb which prints all attributes of an object
#

class DbgExamine(Transitive):

	def Finish(self,cmd):
		print '\n', cmd.dirobj,'\n'
		for att in dir(cmd.dirobj):
			print '%20s' % att, ':', getattr(cmd.dirobj,att)
		print
				
		return OK
		
dbgEx = DbgExamine('@ex,@examine')	# instantiate it

#----------------------------------------------------------------------
# @contents -- a debugging verb which prints all contents of an object
#
class DbgContents(Transitive):

	def Finish(self,cmd):
		print '\nContents of', cmd.dirobj,'\n'
		for item in cmd.dirobj.contents:
			print item
		print
		
		return OK

dbgContents = DbgContents('@contents,@con')

#----------------------------------------------------------------------
# verbs -- print all known verbs
#
class VerbsVerb(Verb):

	def Finish(self,cmd):
		print '\nKnown verbs:\n'
		for word in verbs:
			print (word+"               ")[:15],
		print '\n\n'
		return OK

verbsVerb = VerbsVerb('verbs,help')



#----------------------------------------------------------------------
#----------------------------------------------------------------------
# save -- save the game
#
class Save(Verb):

	def Finish(self,cmd):
		cmd.actor.Tell("Saving game to disk...")
		savegame()
		return OK

save = Save('save')

#----------------------------------------------------------------------
#----------------------------------------------------------------------
# restore -- restore the game
#
class Restore(Verb):

	def Finish(self,cmd):
		cmd.actor.Tell("Restoring game from disk...")
		restoregame()
		cmd.actor = pub.player
		cmd.actor.DoCommandString("look")
		raise pub.BailOutError, "Resetting stack to restore game"

restore = Restore('restore')

