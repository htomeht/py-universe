#   interfaces.py    contains interfaces for pub/pyuniverse 04/03/24
#
#   Copyright (C) 2004 Gabriel Jägenstedt
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
This module should contain all interfaces for pub. An interface is a class
which documents how other classes or class instances should work. 
For instance the interface IOpenL documents functions that must be 
supported by objects like doors and books to be funtional. 
The interfaces are in alphabetical order.

We use interfaces by using advise to make an object support the protocol.
like so:

class Test(pub.core.Component):
    advise(instancesProvide=[IOpenL])

This makes a component which we can add as a part of gameobjects.


Interfaces have a very basic set of methods, these MUST be provided in 
components. They don't have to do anything more than just calling 
chain.next(). You can also have methods raising specific errors depending on
what you want to do.


Other methods are component specific. 
All methods that a component provides on behalf of an interface must be 
callable with the minimum of (chain). This ensures that invoke works with all
these methods.
"""


#protocols imports

from protocols import Interface,advise

#------------------------# VERB LISTENERS #-------------------------#
# The next Section contains Verb Listener Interfaces
# A Verb listener is a method that gets called when a verb tries
# to execute something.
# Example: 
#       > open door
#       behind the scenes calls invoke(doorObj, IOpenL, open, cmd)
# Most of pubs object systems is built around listeners.



#--------------------------------------------------------------------
# InterfaceAskListener
class IAskL(Interface):
    """
    provides an interface to asking the components owner.
    """

    def ask(chain,cmd):
        """method to ask the being something"""

#--------------------------------------------------------------------
#InterfaceCloseListener
class ICloseL(Interface):
    """
    Provides the close method.
    """

    def close(chain,cmd):
       """Method to run when the object is being closed."""

#--------------------------------------------------------------------
# IDrinkListener
class IDrinkL(Interface):
    """
    Used for things you could drink.
    """

    def drink(chain, cmd):
        """method called when the object is told of a drinking event"""

#--------------------------------------------------------------------
#InterfaceDropListener
class IDropL(Interface):
    """
    Provides the  drop method.
    """

    def drop(chain,cmd):
        """method that listens for drop events."""

#--------------------------------------------------------------------
# IEatListener
class IEatL(Interface):
    """
    Used for things you could eat.
    """
    
    def eat(chain, cmd):
        """Method called when something is eaten"""

#--------------------------------------------------------------------
#InterfaceExamineListener
class IExamineL(Interface):
    """
    Provides an interface for examining.
    Used to examine objects.
    """

    def examine(chain,cmd):
        """method that listens for examine events"""

#--------------------------------------------------------------------
#InterfaceFollowListener
class IFollowL(Interface):
    """
    Provides an interface for following.
    Can be be used to have an object notice it is being followed.
    Normaly used in things which are mobile, like an actor or a car.
    """

    def follow(chain,cmd):
        """method that listens for following events"""

#--------------------------------------------------------------------
#InterfaceGetListener
class IGetL(Interface):
    """
    Provides the get method.
    """

    def get(chain,cmd):
        """method that listens for get events."""

#--------------------------------------------------------------------
#InterfaceGiveListener
class IGiveL(Interface):
    """
    Provides the give method.
    """

    def get(chain,cmd):
        """method that listens for give events"""

#--------------------------------------------------------------------
# InterfaceGoListener
class IGoL(Interface):
    """
    Something that can be entered like a door, a portal or something 
    else entirely.
    """
    
    def go(chain,cmd):
        """method to use an exit like it was intended."""
        
#--------------------------------------------------------------------
# InterfaceLockListener
class ILockL(Interface):
    """
    Used on objects which wish to be lockable.
    Components could be combiantion locks, key locks, password locks and so on.
    """

    def lock(chain,cmd):
       """method to lock the lock"""

#--------------------------------------------------------------------
#InterfaceLookListener
class ILookL(Interface):
    """
    provides the look method
    """

    def look(chain,cmd):
        """method listening for look events"""

#--------------------------------------------------------------------
# InterfaceOpenListener
class IOpenL(Interface):
    """
    Serves as a way of effecting things which can be opened. 
    """

    def open(chain,cmd):
        """Method to run when the object is being opened."""

#--------------------------------------------------------------------
#InterfacePullListener
class IPullL(Interface):
    """
    Provides an interface to pulling for components
    Make a components support this if you want it to react to pulling.
    Can be used in a string, something to be moved and so on.    
    """

    def pull(chain,cmd):
        """method that listens for pull events"""

#--------------------------------------------------------------------
#InterfacePushListener
class IPushL(Interface):
    """
    Provides an interface to pushing for components.
    Make a component support this if you want the push verb to be able to affect
    the object in a special way.
    Can be used for a lever, a button, a character.
    """

    def push(chain,cmd):
        """method that listens for push events"""

#--------------------------------------------------------------------
#InterfacePutListener
class IPutL(Interface):
    """
    Provides the put method.
    """

    def put(chain,cmd):
        """method that listens for put events"""

#--------------------------------------------------------------------
# InterfaceTalkListener
class ITalkL(Interface):
    """
    Provides the talk method.
    """

    def talk(chain,cmd):
        """method listening for talk events."""


#--------------------------------------------------------------------
# InterfaceTellListener
class ITellL(Interface):
    """
    provides tell method.
    """

    def tell(chain,cmd):
        """method to tell the being about something"""

#--------------------------------------------------------------------
# InterfaceReceiveListener
class IReceiveL(Interface):
    """
    Provides receive method.
    """

    def receive(chain,cmd):
        """method that listens for receive events"""


#--------------------------------------------------------------------
#InterfaceRemoveListener
class IRemoveL(Interface):
    """
    Provides an interface for removing.
    Used mainly for clothing like objects.
    Example: ring, shirt.
    """

    def remove(chain,cmd):
        """method that listens fo remove events"""


#--------------------------------------------------------------------
#InterfaceTurnListener
class ITurnL(Interface):
    """
    Provides an interface for turning.
    Can be used if you wish to turn things(rotating)
    if you want to turn on the light or even turn around if you make it
    possible.
    """

    def turn(chain,cmd):
        """method that listens for turn events"""

#--------------------------------------------------------------------
#InterfaceUnlockListener
class IUnlockL(Interface):
    """
    provides Unlock method
    """
    
    def unlock(chain,cmd):
       """method to unlock the lock"""
    

#--------------------------------------------------------------------
#InterfaceWearListener
class IWearL(Interface):
    """
    Provides an interface for wearing.
    Most likely used for clothing like objects.
    Example: Jewelry, pants, armor.
    """

    def wear(chain,cmd):
        """method that listens for wearing events"""
        

#----------------------Interface Packages---------------------------#        
# This section contains interfaces who in some way provide several
# listeners and other methods.
# Interfaces like IContainer.
#
# We will use advise to tell the framework that these packages are subclasses
# of others.
# advise(protocolIsSubsetOf = [IOpenL, ICloseL] for some openable package.

class IContainer(Interface):
    """
    IContainer is an interface package. It sets some extra methods that should
    be requitered by all containers.
    """
    
    advise(protocolIsSubsetOf = [IPutL])

    
    def containNoCheck(chain,*pThing):
        """Method that moves the object into the container."""


    def visibleContents(chain):
        """returns a list of contents"""

    def put(chain,cmd):
        """the put listener method"""


