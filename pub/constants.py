#	constants.py			7/2/02 Lalo
#
#	This module defines constants used by most other
#	PUB modules.  You shouldn't mess with this file unless you
#	really know what you're doing.
#
#	Use this module with:
#	from pub.constants import *

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
try:
	# use booleans if on 2.2.1+
	TRUE = True
	FALSE = False
except NameError:
	TRUE = 1
	FALSE = 0

