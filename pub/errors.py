#    errors.py    contains the pub exception classes      04/10/22 GJ
#
#   Copyright (C) 2004 Gabriel Jagenstedt
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
Contains PubError and several exceptions derived from it.
"""

# system imports

# pub imports

# protocols imports

class PubError(Exception): # Basic pub error class subclass this to create more
                           # specific exceptions.


    """
    ObjError
    StateError
    InventoryError
    DestinationError
    SizeError
    TargetError
    """
    pass


class BailOutError(PubError): # exeption to raise to bail out of current
    pass                      # stack frame (used when restoring etc.)


class ComponentError(PubError): # exception to raise when components act up.
    pass                        # iow don't exist and the like.

class LanguageError(PubError): # exception raised when a language can't be 
    pass                       # found

class NoOutput(PubError): # exception raised when no output should be generated
    pass                  # by a command
    

    
