#   constants.py                                          7/2/02 Lalo
#
#   Copyright (C) 2002 Lalo
#
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
"""
This module defines constants used by most other
PUB modules.  You shouldn't mess with this file unless you
really know what you're doing.
"""

#system imports

# pub imports

# protocols imports


#--------------------------------------------------------------------

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
