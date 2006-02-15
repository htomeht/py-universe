# (C) 2006 Terry Hancock, 2002 Lalo 
# config
"""
Load information from the pub.cfg file (at present, just choice of locale).
"""
#
# Some code is from:
#   constants.py                                          7/2/02 Lalo
#
#--------------------------------------------------------------------
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#--------------------------------------------------------------------

import ConfigParser, StringIO

defaults = StringIO.StringIO("""\
[L14N]
LOCALE=en_US
""")
defaults.seek(0)

config = ConfigParser.ConfigParser()
config.readfp(defaults)
config.read(['pub.cfg'])

# Configuration values
LOCALE = config.get('L14N', 'LOCALE')

# TODO: the above really should deal with the Game Instance directory,
# but I'm not sure how we're going to do that.


#--------------------------------------------------------------------


# This module defines constants used by most other
# PUB modules.  You shouldn't mess with this file unless you
# really know what you're doing.

# Articles will move into the appropriate locales(TJH2006/2/10)
the = 'the'
a = 'a'
The = 'The'
A = 'A'

# I have not attempted to find out where these are used (TJH2006/2/10)

OK = 1
CANCEL = 0
BEGIN = 1
FINISH = 2
RUNNING = 1
QUIT = 0

# It's 2006, and True/False have been in the language for awhile
# now. Also we are now requiring later Python features, so this
# is probably moot.(TJH2006/2/10)
try:
    # use booleans if on 2.2.1+
    TRUE = True
    FALSE = False
except NameError:
    TRUE = 1
    FALSE = 0
    
