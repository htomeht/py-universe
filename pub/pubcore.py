#	pubcore.py			6/01/98 JJS
#
#	This module defines datatypes and constants used by most other
#	PUB modules.  You shouldn't mess with this file unless you
#	really know what you're doing.
#
#	Use this module with:
#	from pubcore import *
#
#----------------------------------------------------------------------

# import standard Python modules needed by the functions below

import string
import types
import copy
import whrandom
import regex

# import the PUB module which declares "global" variables
import pub

# declare some constants

the = 'the'
a = 'a'
The = 'The'
A = 'A'
OK = 1
CANCEL = 0
BEGIN = 1
FINISH = 2
RUNNING = 1
QUIT = 0
TRUE = 1
FALSE = 0

# function to capitalize a string
def cap(s):
	if not s: return s
	return string.upper(s[0]) + s[1:]

# function to determine whether it's a string
def isString(x):
	return type(x) == types.StringType

# function to determine whether it's an Instance
def isInstance(x):
	return type(x) == types.InstanceType

# function to determine whether it's a number, or interpretable as one
def isInt(x):
	try:
		string.atoi(x)
		return TRUE
	except:
		return type(x) == types.IntType

# function to force it to be a number
def toInt(x):
	if type(x) == types.IntType: return x
	try:
		return string.atoi(x)
	except:
		return 0

# function to replace all occurances of one substring with another
def replace(what,withwhat,inwhat):
	# we'll find the fastest way to do this later...
	return string.join(string.split(inwhat,what),withwhat)

# function to strip commas and periods from a string
def stripPunctuation(x):
	out = string.join(string.split(x,','),'')
	out = string.join(string.split(out,'.'),'')
	out = string.join(string.split(out,'!'),'')
	out = string.join(string.split(out,'?'),'')
	return out

# function to save the game
def savegame(filename='pub.dat'):
	import sys
	import pub
	import pubverbs
	import picklemod

	pub.lastroom = None		# (to prevent auto-placement of objects)
	f = open(filename, 'w')
	picklemod.save( f, pubverbs, pub, sys.modules['__main__'] )
	f.close()

# function to restore the game
def restoregame(filename='pub.dat'):
	import sys
	import pub
	import pubverbs
	import picklemod

	pub.lastroom = None		# (to prevent auto-placement of objects)
	f = open(filename, 'r')
	picklemod.restore( f, pubverbs, pub, sys.modules['__main__'] )
	f.close()

#----------------------------------------------------------------------
# event -- a class which keeps something to be executed in the future
#
class Event:

	# initialization method
	def __init__(self,pObject=None,pCode=None,pCmd=None):
		if not pObject: return	# must be unpickling
		self.object = pObject
		self.cmd = copy.copy(pCmd)
		self.code = pCode
#		print "Event created: " + str(self)

	def __str__(self):
		return '< Event: ' + str(self.object) + ',' + str(self.code) + ' >'

	def Perform(self):
#		print 'Performing: ' + str(self)
		object = self.object
		cmd = self.cmd
		exec self.code

	def RefersTo(self,pWhom):
		if self.object == pWhom or \
		self.cmd and self.cmd.actor == pWhom: return TRUE
		return FALSE

#----------------------------------------------------------------------
# scheduler -- keeps track of the world clock, calls events, etc.
#
class Scheduler:

	# initialization method
	def __init__(self,pTimeString='12:00'):
		timeparts = string.split(pTimeString,':')
		self.minutes = string.atoi(timeparts[0])*60 \
			     + string.atoi(timeparts[1])
		self.events = {}
	
	def __str__(self):
		return '< Scheduler at time ' + self.GetTime() \
			+ ' and ' + str(len(self.events)) + ' events >'

	def GetTime(self):
		day = self.minutes / 1440
		hour = (self.minutes%1440) / 60
		minute = self.minutes%1440 % 60
		if day: return "%d:%02d (Day %s)" % (hour,minute,day)
		return "%d:%02d" % (hour,minute)

	def AddAbsEvent(self,pAbsTime,pEvent):
		if pAbsTime < self.minutes:
			print "WARNING: scheduling event for a past time"
			self.minutes = pAbsTime
		if self.events.has_key(pAbsTime):
			self.events[pAbsTime].append(pEvent)
		else:
			self.events[pAbsTime] = [pEvent]
	
	def AddEvent(self,pRelTime,pEvent):
		time = self.minutes + pRelTime
		if self.events.has_key(time):
			self.events[time].append(pEvent)
		else:
			self.events[time] = [pEvent]

	def Update(self):
		if not self.events: return
		eventkeys = self.events.keys()	# get event times
		eventkeys.sort()		# sort them
		nexteventkey = eventkeys[0]	# find earliest time
		self.minutes = nexteventkey	# update clock
		eventlist = self.events[nexteventkey]
		del self.events[nexteventkey]	# remove from the queue
		for e in eventlist:
			# print '[' + self.GetTime() + '] ',
			e.Perform()		# perform scheduled events

	def HasEventFor(self, pFor):
		if not self.events: return FALSE
		for eventlist in self.events.values():
			if filter(lambda x,a=pFor: x.RefersTo(a), eventlist):
				return TRUE
		return FALSE

#----------------------------------------------------------------------
#	Command -- stores references for variarious parts of a command
#
class Command:

	def __init__(self):
		self.Clear()
		
	def Clear(self):
		self.actor = ''
		self.verb = ''
		self.dirobj = ''
		self.toobj = ''
		self.inobj = ''
		self.atobj = ''
		self.withobj = ''	

	def __str__(self):
		out = '<<'
		if (self.actor): out = '  Actor: ' + str(self.actor)
		if (self.verb): out = out + '  Verb: ' + str(self.verb)
		if (self.dirobj): out = out + '  Obj: ' + str(self.dirobj)
		if (self.toobj): out = out + '  To: ' + str(self.toobj)
		if (self.inobj): out = out + '  In: ' + str(self.inobj)
		if (self.atobj): out = out + '  At: ' + str(self.atobj)
		if (self.withobj): out = out + '  With: ' + str(self.withobj)
		out = out + '  >>'
		return out

	def StuffString(self,pStr,pFor=None):
		if string.find(pStr,'<') < 0 or string.find(pStr,'>') < 0:
			return pStr
		str = replace('<actor>',self.actor(0,pFor),pStr)
		str = replace('<Actor>',cap(self.actor(0,pFor)),str)
		str = replace('<The actor>',self.actor(The,pFor),str)
		str = replace('<the actor>',self.actor(the,pFor),str)
		str = replace('<A actor>',self.actor(A,pFor),str)
		str = replace('<a actor>',self.actor(a,pFor),str)

		if isInstance(self.dirobj):
			str = replace('<dirobj>',self.dirobj(0,pFor),str)
			str = replace('<Dirobj>',cap(self.dirobj(0,pFor)),str)
			str = replace('<The dirobj>',self.dirobj(The,pFor),str)
			str = replace('<the dirobj>',self.dirobj(the,pFor),str)
			str = replace('<A dirobj>',self.dirobj(A,pFor),str)
			str = replace('<a dirobj>',self.dirobj(a,pFor),str)
#		else: print "dirobj not an instance"

		if isInstance(self.inobj):
			str = replace('<inobj>',self.inobj(0,pFor),str)
			str = replace('<Inobj>',cap(self.inobj(0,pFor)),str)
			str = replace('<The inobj>',self.inobj(The,pFor),str)
			str = replace('<the inobj>',self.inobj(the,pFor),str)
			str = replace('<A inobj>',self.inobj(A,pFor),str)
			str = replace('<a inobj>',self.inobj(a,pFor),str)

		if isInstance(self.toobj):
			str = replace('<toobj>',self.toobj(0,pFor),str)
			str = replace('<Toobj>',cap(self.toobj(0,pFor)),str)
			str = replace('<The toobj>',self.toobj(The,pFor),str)
			str = replace('<the toobj>',self.toobj(the,pFor),str)
			str = replace('<A toobj>',self.toobj(A,pFor),str)
			str = replace('<a toobj>',self.toobj(a,pFor),str)

		str = replace('<time>',string.split(pub.scheduler.GetTime())[0],str)

		return str

	def Tell(self, pToActor='', pToOthers='', pToThird='', pWhoIsThird=None ):
		room = self.actor.container
#		if hasattr(room,'ComputeTotalLight'): room.ComputeTotalLight()
		if pToActor:
			self.actor.Tell( self.StuffString(pToActor,self.actor) )
		if pToThird and pWhoIsThird.listening:
			pWhoIsThird.Tell( self.StuffString(pToThird,pWhoIsThird) )
		if pToOthers:
			for item in self.actor.LocalNouns():
				if item != self.actor and item != self.actor.container \
				and item != pWhoIsThird and item.listening:
					item.Tell( self.StuffString(pToOthers,item) )

#----------------------------------------------------------------------
#	Parser -- breaks a string into a command or set of commands
#
class Parser:

	def __init__(self):
		self.words = []
		self.cmd = Command()
		self.it = ''
		self.me = ''

	def NounWords(self,words):
		# given a set of words, see how many words you can lump together
		# as a single noun from the beginning of the string.  Thus,
		#	given:  "give bucket of fish to bob"  we return: 0
		#	        "bucket of fish to bob"       ==>        3
		#	        "bucket to bob"               ==>        1
		#---------------------------------------------------------------
		# the first word must be an integer, "it", or in our noun list
		if not words: return 0				# no words
		if words[0] == 'it': return 1		# "it"
		if words[0][0] == '"': return 1		# quoted string
		if isInt(words[0]):					# integer
			# first word is an integer; convert to generic form
			words[0] = "#"
		if words[0]=="#" or words[0] in nouns:
			# first word is in nouns; how many more words can we munch?
			matches = filter(lambda x,a=string.join(words): \
					regex.match(x+'.*',a), nouns)
			if not matches: return 1		# (must be a number)
			# we now have a set of potential matches; find the longest
			matches.sort(lambda a,b: cmp(len(a),len(b)))
			longest = matches[len(matches)-1]
			return len(string.split(longest))
		return 0

	def FindPrep(self,words):
		# print "Looking for prep in", words
		# return the position of the first preposition in words,
		# not looking past the first verb.
		# Return -1 if no preposition is found
		#-------------------------------------------------------
		for i in range(0,len(words)):
			if words[i] in verbs: return -1
			if words[i] in preps: return i
		return -1

	def MunchNouns(self,w):
		# starting at w, munch a set of nouns joined by conjunctions
		# return the set, and remove them from self.words
		#-------------------------------------------------------
		if w >= len(self.words): return []
		out = []
		nounwords = self.NounWords(self.words[w:])
		while nounwords:
			if self.words[w] == 'it': out = out + self.it
			else: out.append(string.join(self.words[w:w+nounwords]))
			self.words = self.words[:w] + self.words[w+nounwords:]
			if w >= len(self.words) or self.words[w] not in conjs: return out
			while self.words[w] in conjs:
				self.words = self.words[:w] + self.words[w+1:]
			nounwords = self.NounWords(self.words[w:])
		return out	

	def WordEnd(self,pStr,pStart):
		# return the position of the end of the word,
		# given that it starts at pStart in string pStr
		if pStr[pStart] == '"':
			q = string.find(pStr,'"',pStart+1)
			if q >= 0: return q
		else:
			space = string.find(pStr,' ',pStart)
			comma = string.find(pStr,',',pStart)
			if comma < 0 or (space >= 0 and space < comma):
				if space >= 0: return space
			else:
				if comma >= 0: return comma
		return len(pStr)
		
	def BreakString(self,pStr):
		# break the string into a list of words
		# - filter garbage and reduce non-quoted stuff to lower case
		# - convert commas to conjunctions
		
		w = []
		# loop through string, building list w
		wordstart = 0
		wordend = 0
		strlen = len(pStr)
		while wordstart < strlen:
			# find end of the current word
			wordend = self.WordEnd(pStr,wordstart)
			if pStr[wordstart] == '"':
				w.append(pStr[wordstart:wordend])
			else:
				# copy it into the list (unless it's garbage)
				word = string.lower(pStr[wordstart:wordend])
				if word:
					if wordend < strlen and pStr[wordend] == ',':
						if word and word not in garbs: w.append(word)
						w.append('and')
						wordend = wordend-1
					else:
						if word not in garbs: w.append(word)
			# repeat from the new starting point
			wordstart = wordend+1
		return w
	
	def Parse(self,pStr=''):
		cmdlist = []
		cmdtext = pStr
		while cmdtext:
			# call the ParseCore routine, to strip one verb's worth
			cmdtext = self.ParseCore(cmdtext)

			# now break the multiple objects into single objects, multiple commands
			# hmm, there's gotta be a better way to do this...
			cm = Command()
			#print self.cmd
			cm.verb = self.cmd.verb
			if not self.cmd.dirobj: self.cmd.dirobj = ['']
			if not self.cmd.toobj: self.cmd.toobj = ['']
			if not self.cmd.inobj: self.cmd.inobj = ['']
			if not self.cmd.atobj: self.cmd.atobj = ['']
			if not self.cmd.withobj: self.cmd.withobj = ['']
			for a in self.cmd.dirobj:
			 for b in self.cmd.toobj:
			  for c in self.cmd.inobj:
			   for d in self.cmd.atobj:
			    for e in self.cmd.withobj:
			    	cm.dirobj = a
			    	cm.toobj = b
			    	cm.inobj = c
			    	cm.atobj = d
			    	cm.withobj = e
			    	#print cm
			    	cmdlist.append(copy.copy(cm))
		# now we have a nice list of quantal commands; return it
		return cmdlist
	
	def ParseCore(self,pStr):	
		#print "Parsing:",pStr
		self.cmd.Clear()

		# special case: check for "say" with no quotes and other shortcuts
		if pStr[0] == '"': pStr = "say "+pStr
		elif len(pStr)>5 and \
		string.lower(pStr[:4]) == "say " and pStr[4] != '"':
			pStr = 'say "'+pStr[4:]

		# get words; strip out garbage
		self.words = self.BreakString(pStr)

		# apply translations
		if self.me: translations['me'] = self.me
		for i in range(0,len(self.words)):
			if translations.has_key(self.words[i]):
				self.words[i] = translations[self.words[i]]
		
		# first word should be a verb -- if not, supply 'defverb'
		w = 0
		if len(self.words)>w and self.words[w] in verbs:
			self.cmd.verb = self.words[w]
			w = w + 1
		else:	self.cmd.verb = 'defverb'

		# after verb: nothing, adverb, noun or conjuction
		if len(self.words) < w+1: return ''		# no more words

		# look for verb modifiers
		if self.words[w] in adverbs:
			self.cmd.verb = self.cmd.verb + ' ' + self.words[w]
			self.words = self.words[:w] + self.words[w+1:]
			if w >= len(self.words): return ''

		# munch conjunctions
		while self.words[w] in conjs:
			self.words = self.words[:w] + self.words[w+1:]

		# munch a direct object
		self.cmd.dirobj = self.MunchNouns(w)

		# if there's another noun phrase, then it's the DO and we had IO before
		temp = self.MunchNouns(w)
		if temp:
			self.cmd.toobj = self.cmd.dirobj
			self.cmd.dirobj = temp
		
		if self.cmd.dirobj: self.it = self.cmd.dirobj
		if len(self.words) < w+1: return ''		# no more words

		while self.words[w] in preps:
			# find the object of the preposition, and assign appropriately
			objs = self.MunchNouns(w+1)
			if not objs:
				print "..." + self.words[w] + " WHAT?!?"
				return ''
			
			if self.words[w] == 'at': self.cmd.atobj = objs
			elif self.words[w] == 'in' or self.words[w] == 'into' \
			  or self.words[w] == 'from': self.cmd.inobj = objs
			elif self.words[w] == 'with': self.cmd.withobj = objs
			elif self.words[w] == 'to': self.cmd.toobj = objs
			else: print "ERROR: unknown preposition " + self.words[w]

			self.words = self.words[:w] + self.words[w+1:]	# munch preposition			
			self.it = objs

			if len(self.words) < w+1:
				return ''					# no more words

		# look for dangling verb modifiers
		if self.words[w] in adverbs:
			self.cmd.verb = self.cmd.verb + ' ' + self.words[w]
			self.words = self.words[:w] + self.words[w+1:]
			if w >= len(self.words): return ''
			# munch conjunctions
			while self.words[w] in conjs:
				self.words = self.words[:w] + self.words[w+1:]
			
		# next word should be a verb
		if self.words[w] in verbs:
			return string.join(self.words[w:])

		# if not, something's wrong -- might be unknown word
		print 'Warning: unknown word '+self.words[w]
		return ''

	def Test(self):
		if "fish" not in nouns: nouns.append("fish")
		if "fish bucket" not in nouns: nouns.append("fish bucket")
		print "Nouns: ",nouns
		print "Verbs: ",verbs
		done = FALSE
		while not done:
			command = raw_input("Parser Test>")
			if command == "quit": done = TRUE
			else:
				print string.join(map(str,self.Parse(command)),'\n')

#----------------------------------------------------------------------
# add a verb or list of verbs, singly, as a list, or separated with commas
def AddVerb( *pVerbs ):
	for item in pVerbs:
		if type(item) == types.StringType:
			if item not in verbs: verbs.append(item)
		else:
			for subitem in item:
				if subitem not in verbs: verbs.append(subitem)
	verbs.sort()
		
#----------------------------------------------------------------------

verbs = ['drop','get','go','inv','look','eat','give','put','use']
adverbs = ['on','off']
nouns = ['it','self','me','here','room','fish','fish bucket','bucket','rock']
conjs = ['and','then']
preps = ['at','in','into','with','from','to']
garbs = ['the','a']
translations = {}

#----------------------------------------------------------------------
# Verb -- base class of any Verb object
#
class Verb:

	def __init__(self,pNames=''):
		self.synonyms = string.split(string.lower(pNames),',')
		self.duration = 1	# time (in minutes) to execute
		self.succ = 'You ' + self.synonyms[0] + '.'
		self.osucc = '<The actor> ' + self.synonyms[0] + 's.'
		AddVerb(self.synonyms)
		for i in self.synonyms:
			pub.verbdict[i] = self

	def __str__(self):
		return '< Verb: ' + self.synonyms[0] + ' >'

	def GetDuration(self, cmd):
		return self.duration

	def DoPrechecks(self, cmd):	# return OK or CANCEL
		# call room hierarchy's PreWitness method, if any
		obj = cmd.actor.container
		while obj:
			if hasattr(obj, 'PreWitness'):
				if not obj.PreWitness(cmd): return CANCEL
			obj = obj.container

		# call objects' PreObj methods, if any
		for obj in (cmd.dirobj, cmd.toobj, cmd.atobj, cmd.withobj, cmd.inobj):
			if isInstance(obj) and hasattr(obj, 'PreObj'):
				if not obj.PreObj(cmd): return CANCEL

		# call actor's PreAct method, if any
		if isInstance(cmd.actor) and hasattr(cmd.actor, 'PreAct'):
			if not cmd.actor.PreAct(cmd): return CANCEL

		# if all checks have passed, return OK
		return OK

	def DoPostchecks(self,cmd):	# return OK or CANCEL
		# call room hierarchy's PostWitness method, if any
		obj = cmd.actor.container
		while obj:
			if hasattr(obj, 'PostWitness'):
				if not obj.PostWitness(cmd): return CANCEL
			obj = obj.container

		# call objects' PostObj methods, if any
		for obj in (cmd.dirobj, cmd.toobj, cmd.atobj, cmd.withobj, cmd.inobj):
			if isInstance(obj) and hasattr(obj, 'PostObj'):
				if not obj.PostObj(cmd): return CANCEL

		# call actor's PostAct method, if any
		if isInstance(cmd.actor) and hasattr(cmd.actor, 'PostAct'):
			if not cmd.actor.PostAct(cmd): return CANCEL

		# if all checks have passed, return OK
		return OK

	def Do(self,cmd):		# schedule command for execution
		if cmd.actor.busytill > pub.scheduler.minutes:
			pub.scheduler.AddAbsEvent(cmd.actor.busytill, \
						Event(self,'object.Begin(cmd)',cmd) )
			return
		# if actor is not busy, then begin command immediately
		self.Begin(cmd)

	def Begin(self,cmd):		# handle the command
		# do pre-checks; see if the command will even work
		if self.DoPrechecks(cmd) == CANCEL: return CANCEL
		
		# finish executing the command
		self.Finish(cmd)

		# make the actor pause appropriately before next comman
		delay = self.GetDuration(cmd)

		if cmd.actor.busytill > pub.scheduler.minutes:
			cmd.actor.busytill = cmd.actor.busytill + delay
		else:	cmd.actor.busytill = pub.scheduler.minutes + delay

		return OK

	def Finish(self,cmd):		# execute and output the event
		# do the actual action, i.e. changes to the game objects

		# do post-processing to provide alternate output
		# (return OK in either case here, since command executed)
		if self.DoPostchecks(cmd) == OK:
			cmd.Tell( self.succ, self.osucc )
		return OK

#----------------------------------------------------------------------
# BaseThing -- base class of any noun in the game
#
class BaseThing:
        
	# initialization method
	def __init__(self,pName=''):
		self.a = 'a'			# article to use for 'a'
		self.blind = FALSE		# if TRUE, can't see anything
		self.container = None	# its location
		self.defverb = None		# no default verb
		self.desc = ''			# description
		self.initialDesc = ''	# desc, before it's moved (if different)
		self.initialNote = ''	# note, before it's moved (if different)
		self.invisible = 0		# invisibilty level (0 = plainly visible)
		self.invisName = "something"	# perceived "name" when invisible
		self.light = 0			# light given off (100 = sunlight)
		self.listening = FALSE	# wants Tell() calls?
		self.listLine = ''		# line to print in contents list
		self.name = string.split(pName,',')[0]	# main name
		self.note = ''			# line to print in room contents (if nonstandard)
		self.salient = TRUE		# show in room contents list?
		self.seesDark = 0		# bonus to room light when this is seeing
		self.seesInvisible = 0	# invisibility level which this can see
		self.size = 10			# size (100=human)
		self.synonyms = string.split(string.lower(pName),',')
		self.the = 'the'		# article to use for 'the'
		
		# special initialization
		self.desc = 'It looks like an ordinary '+self.name+'.'

		# add names to the parser's list of nouns
		for n in self.synonyms:
			if n not in nouns:
				nouns.append(n)

	# get arguments (used by copy.copy)
	def __getinitargs__(self):
		return (string.join(self.synonyms,','),)
		
	# get name
	def GetName(self, article=0, pLooker=None):
		if pLooker and not pLooker.CanSee(self):
			if article==The or article==A: return cap(self.invisName)
			return self.invisName
		if not article: return self.name
		if article==the: return self.the + ' ' + self.name
		if article==a: return self.a + ' ' + self.name
		if article==The: return cap(self.the) + ' ' + self.name
		if article==A: return cap(self.a) + ' ' + self.name
 		return self.name

	# allow treating an object like a function,
	# as a shorthand for GetName
	def __call__(self,article=0,pLooker=None):
		return self.GetName(article,pLooker)

	# check for a name match
	def NameMatch(self, pName):
		return pName in self.synonyms

	# get note (for when listing the contents of a room)
	def GetNote(self):
		if self.initialNote: return self.initialNote
		if self.note: return self.note
		r = whrandom.randint(0,2)
		if r == 0:
			return 'You see ' + self(a) + ' lying here.'
		if r == 1:
			return self(A) + ' is lying here.'
		if r == 2:
			return 'There is '+ self(a) + ' here.'

	# get description
	def GetDesc(self,pDepth=0):
		if self.initialDesc: return self.initialDesc
		return self.desc

	# get room (not just any container, but the first ROOM container)
	def GetRoom(self):
		cont = self
		while cont and not hasattr(cont,'ComputeTotalLight'):
			cont = cont.container
		return cont

	# get line to be printed in a list of items (e.g., for inventory)
	def GetListLine(self): 
		if self.listLine: return self.listLine	
		return "   - " + self.GetName(a)

	# can we see the given object? (assuming it's present)
	def CanSee(self, pWhat):
		# if we're blind, automatically return FALSE
		if self.blind: return FALSE
		
		# figure effect of lighting and night vision...
		
		effectiveLight = self.GetRoom().light + self.seesDark
		# anything which gives off light can always be seen
		# (unless it's the room itself)
		if pWhat.light > 0 and pWhat != self.container:
			effectiveLight = 100

		# figure effect of invisibility and counter-invisibility vision...
		
		visible = 1 - pWhat.invisible + self.seesInvisible
		
		# return TRUE only if both light and visibility are good
		
		return effectiveLight > 20 and visible > 0

	# can we contain something?
	def CanContain(self, pWhat): return FALSE

	# let the object hear something
	def Tell(self, pWhat,pCmd=None):
		# by default, do nothing
		# the pCmd parameter allows substitution of various
		# object names, depending on whether this object can see 'em
		return

	# checks, before and after this object is used as the object of a command
	def PreObj(self, cmd): return OK

	def PostObj(self, cmd):
		return OK

	# checks before and after any movement
	def PreMove(self):
		self.GetRoom().ComputeTotalLight()
		return OK
	
	def PostMove(self):
		self.GetRoom().ComputeTotalLight()
		return OK
	
	def MoveTo(self, pWhere):
		if not pWhere.CanContain(self) \
		or not self.PreMove():
			return CANCEL
		pWhere.ContainNoCheck(self)
		self.PostMove()
		return OK
				
#----------------------------------------------------------------------