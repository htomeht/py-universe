# (C) 2006 Terry Hancock
#--------------------------------
# l10n
"""
Localization utility module.
"""
# GPLv2+
#--------------------------------

# Prerequisites for Locale modules
# Every locale module should import this module

import os, sys

locales_dir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
pub_dir     = os.path.abspath(os.path.join(locales_dir, '..'))

if os.path.abspath(sys.path[-1]) != pub_dir:
    sys.path.append(pub_dir)

# Note this will fail if the above path mechanics don't work
import config

#print "LOCALE = %s" % config.LOCALE

import interfaces
import semantics


