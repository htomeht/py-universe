# put the package root on the Python path:
import sys, os
sys.path = [os.path.abspath(__path__[0])] + sys.path 


# system imports

# pub imports

from pubcore import *           # import core datatypes, functions, & constants
import pubverbs                 # import standard verbs
verbs = pubverbs
import pubobjs                  # import standard object library
objs = pubobjs
import gadgets
import pubtcp
tcp = pubtcp
import lang
import errors
import adapters

# protocols imports
