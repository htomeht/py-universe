#	pub.py				8/27/96 JJS
#
#	This module defines some "global" variables.
#
#	To use it:   import pub
#				 print pub.scheduler  (or whatever)
#
#----------------------------------------------------------------------

scheduler = None		# this should be set to a Scheduler at start-up time
verbdict = {}			# dictionary, converts words to Verb objects
gameStatus = 1			# game is RUNNING
lastroom = None			# last room created; default location for new objects
universe = None			# room which contains all other rooms
player = None			# game player (esp. for single-user games)

class BailOutError(Exception):	# exception to raise to bail out of current
    pass			# stack frame (used when restoring, etc.)


from pubcore import *		# import core datatypes, functions, & constants
import pubverbs			# import standard verbs
verbs = pubverbs
import pubobjs 			# import standard object library
objs = pubobjs
import gadgets
import pubtcp
tcp = pubtcp
