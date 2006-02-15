#(C)2006 Terry Hancock
# locale
"""
The locale module finds and constructs locale-specific information for the
PUB engine. It has to collect this information from multiple sources:

 o Engine-locale python files (these contain data structures which are
   tightly-bound to the language engine, so they have to be done using
   special consideration for PUB).

 o Game engine-extensions python file (may extend meanings understood by
   the interpreter). Tightly-bound to the game extensions code.

 o Gettext "op" files for Game-locale. Since these are essentially translations
   of game-data, they are much more conventional, and we use the Gnu gettext
   tools and the standard I18N/L14N methods of translation. This should make
   it a little easier on both game designers and translators. This is also
   the "sub locale" or "text locale" for Universe.  Loosely bound (mainly
   for making sense to the player, not the engine).

 o If we are being used with Universe, we may also need access to the "dub
   locale" or "resource locale" from the game.  These may include voice
   files, or alternate versions of pictures or models (to fix signage,
   for example).
"""

# ENGINE LOCALE
#
# This uses moderately deep magic with the Python import mechanism.
# What we are doing is not so complicated, though:
#
# 1) Check to see if the correct locale module is already loaded,
#    if so, just update names.
#
# 2) Otherwise, look for a module named by the locale (e.g. 'en_US.py')
#    in the directory 'locale'.
#
# 3) If you can't find the exact locale (like 'en_US.py'), look for
#    the nearest "major locale" (like 'en.py') and load that as "major".
#
# 4) If you find both a major and an exact locale, then load the major
#    locale first, then the exact one -- this way the minor locale
#    can clobber values from the major locale, but will inherit the
#    major locale's names.
#
# 5) If all else fails, fall back on the English (en_US) locale that
#    is native for PUB.
#
# The hard part is that the normal Python import statement doesn't allow
# you to load a module by a name in a variable. So you have to go to the
# more primitive functions that it uses, and emulate the behavior of
# the import statement.
#

import sys, imp
from config import LOCALE

MAJOR = LOCALE[:2]

if LOCALE in sys.modules.keys():
    locale = sys.modules[LOCALE]
    major  = None
else:
    if MAJOR in sys.modules.keys():
        major = sys.modules[MAJOR]
    else:
        try:
            found = imp.find_module(MAJOR, ['locales'])
            try:
                major = imp.load_module(MAJOR, *found)
            finally:
                found[0].close()
        except ImportError:
            major = None
                
    try:
        found = imp.find_module(LOCALE, ['locales'])
        try:
            locale = imp.load_module(LOCALE, *found)
        finally:
            found[0].close()
    except ImportError:
        locale = None

if not locale and not major:
    # Requested locale doesn't exist, use native en_US locale:
    found = imp.find_module('en', ['locales'])
    locale = imp.load_module('en', *found)
    
if major:
    try:
        all = major.__all__
    except AttributeError:
        all = [n for n in major.__dict__ if n[0]!='_']
    for n in all:
        globals()[n] = major.__dict__[n]
        
if locale:
    try:
        all = locale.__all__
    except AttributeError:
        all = [n for n in locale.__dict__ if n[0]!='_']
    for n in all:
        globals()[n] = locale.__dict__[n]
   
       
# GAME LOCALE

# FIXME: Get game locale files
# We need to traverse to the game instance directory, find the localization
# files of interest (and fall back on native localization if they aren't there)
# 


