# englishLang
#
# module provides methods and functions that are specific for english
# an English class used for adapting differnt things in adapters.

# system imports

# pub imports
from pub.interfaces import ILangMod 
import core
#import components
#import verbs
#import objs
#import gadgets

# protocols imports
from protocols import advise

advise(moduleProvides=[ILangMod])

#--------------------------------------------------------------------
# Language specific variables

name = 'english'

# words known to the parser
adverbs = [] # might be provided in verbs or objs
conjs = ['and', 'then'] 
garbs = ['the', 'a']
nouns = ['it', 'self', 'me', 'here', 'room'] 
preps = [] # supplied by each obj
verbs = []
translations = {}

get = {'parser': core.EnglishParser, 'test': core.EnglishTest}

#get = {'parser': core.EnglishParser, 'test': core.EnglishTest, 
#       'objs': objs, 'verbs': verbs, 'components': components, 
#       'gadgets': gadgets}
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# 
