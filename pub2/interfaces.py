#   interfaces.py    contains interfaces for PUB         04/03/24  GJ
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
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# CHANGELOG
#
#   2004-22/10: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#---------------------------------------------------------------------
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

# system imports 

# pub imports

# protocols imports

from protocols import Interface, advise


#--------------------------------------------------------------------#
# Language interfaces.
#


class ILangMod(Interface):
    """
    ILangMod documents what a language module needs to be accepted as such

    english.py should provide ILangMod like: 

    advise(moduleProvides=[ILangMod])

    as should all other language modules.

    This is to ensure that the module is really a language.
    """
    
#---------------------------------------------------------------------
#
class ISymbol(Interface):
    """
    Interface for Symbol and classes that need to provide component handling.
    """

    def addComponents(com):
        """
        Method that adds components listed in com if of the right type.
        """

    def delComponents(com):
        """
        Method that removes components listed in com if it can be found.
        """

#---------------------------------------------------------------------
#
class INoun(Interface):
    """
    INoun is a marker interface mainly.
    It is used to adapt to Noun Interfaces.
    """

#---------------------------------------------------------------------
#
class IVerb(Interface):
    """
    Documents what a verb has to do in PUB.
    """

    def do(cmd):
        """
        Initiates the command.
        Generally just calls begin.
        """

    def begin(cmd):
        """
        Does the invoking.
        ie 
        try: 
            if invoke(obj,ITest,'test',cmd):
                self.finish(cmd)
        except RandomError:
            cmd.tell(pub.error['RandomError'])
        """

    def finish(cmd):
        """
        Calls cmd.tell() to let the player and all who see 
        know what has happened
        """

#-----------------------# NOUN INTERFACES #-------------------------#
#
# This Section contains interfaces that might be added to Nouns, like
# IDescribable and ILocatable.
#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# IDescribable
#
class IDescribable(Interface):
    """
    Classes that provide IDescribable can be given descriptions and have 
    methods for evaluating them. IDescribable is language specific. 
    IDescribable components also provide the syntax for an object like 
    gender and case.
    """

    def getDesc():
        """
        method to aquire a normal description of an item.
        """

    def getXDesc():
        """
        method to aquire a detailed description of an item if it exists.
        otherwise call getDesc
        """

#--------------------------------------------------------------------
#ILocatable
#
class ILocatable(Interface):
    """
    Classes that provide ILocatable are used to show where an item is situated
    and if any items are contained within the obj it's a part of.
    In short it's used to localize objects.
    """


#--------------------------------------------------------------------
#ITangible
#
class ITangible(Interface):
    """
    Classes that provide ITangible have size and weight and ways to deal with
    these attributes. It is a bit uncertain that this is a Thing Interface but
    since it's fully possible to have objects without this attribute I will
    leave it in.
    """



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
        """Method to ask the being something"""

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
        """Method called when the object is told of a drinking event"""

#--------------------------------------------------------------------
#InterfaceDropListener
class IDropL(Interface):
    """
    Provides the  drop method.
    """

    def drop(chain,cmd):
        """Method that listens for drop events."""

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
        """Method that listens for examine events"""

#--------------------------------------------------------------------
#InterfaceFollowListener
class IFollowL(Interface):
    """
    Provides an interface for following.
    Can be be used to have an object notice it is being followed.
    Normaly used in things which are mobile, like an actor or a car.
    """

    def follow(chain,cmd):
        """Method that listens for following events"""

#--------------------------------------------------------------------
#InterfaceGetListener
class IGetL(Interface):
    """
    Provides the get method.
    """

    def get(chain,cmd):
        """Method that listens for get events."""

#--------------------------------------------------------------------
#InterfaceGiveListener
class IGiveL(Interface):
    """
    Provides the give method.
    """

    def give(chain,cmd):
        """Method that listens for give events"""

#--------------------------------------------------------------------
# InterfaceGoListener
class IGoL(Interface):
    """
    Something that can be entered like a door, a portal or something 
    else entirely.
    """
    
    def go(chain,cmd):
        """Method to use an exit like it was intended."""
        
#--------------------------------------------------------------------
# InterfaceLockListener
class ILockL(Interface):
    """
    Used on objects which wish to be lockable.
    Components could be combination locks, key locks, password locks and so on.
    """

    def lock(chain,cmd):
       """Method to lock the lock"""

#--------------------------------------------------------------------
#InterfaceLookListener
class ILookL(Interface):
    """
    provides the look method
    """

    def look(chain,cmd):
        """Method listening for look events"""

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
        """Method that listens for pull events"""

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
        """Method that listens for push events"""

#--------------------------------------------------------------------
#InterfacePutListener
class IPutL(Interface):
    """
    Provides the put method.
    """

    def put(chain,cmd):
        """Method that listens for put events"""

#--------------------------------------------------------------------
# InterfaceTalkListener
class ITalkL(Interface):
    """
    Provides the talk method.
    """

    def talk(chain,cmd):
        """Method listening for talk events."""


#--------------------------------------------------------------------
# InterfaceTellListener
class ITellL(Interface):
    """
    Provides tell method.
    """

    def tell(chain,cmd):
        """
        Method to tell the being about something. Usually used by cmd.tell
        to let a player know what has happened after a command was executed.
        """

#--------------------------------------------------------------------
# InterfaceReceiveListener
class IReceiveL(Interface):
    """
    Provides receive method.
    """

    def receive(chain,cmd):
        """Method that listens for receive events"""


#--------------------------------------------------------------------
#InterfaceRemoveListener
class IRemoveL(Interface):
    """
    Provides an interface for removing.
    Used mainly for clothing like objects.
    Example: ring, shirt.
    """

    def remove(chain,cmd):
        """Method that listens fo remove events"""


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
        """Method that listens for turn events"""

#--------------------------------------------------------------------
#InterfaceUnlockListener
class IUnlockL(Interface):
    """
    provides Unlock method
    """
    
    def unlock(chain,cmd):
       """Method to unlock the lock"""
    

#--------------------------------------------------------------------
#InterfaceWearListener
class IWearL(Interface):
    """
    Provides an interface for wearing.
    Most likely used for clothing like objects.
    Example: Jewelry, pants, armor.
    """

    def wear(chain,cmd):
        """Method that listens for wearing events"""
        

#----------------------Interface Packages---------------------------#        
# This section contains interfaces who in some way provide several
# listeners and other methods.
# Interfaces like IContainer.
#
# We will use advise to tell the framework that these packages are subclasses
# of others.
# advise(protocolExtends = [IOpenL, ICloseL] for some openable package.

class IContainer(Interface):
    """
    IContainer is an interface package. It sets some extra methods that should
    be requitered by all containers.
    """
    
    advise(protocolExtends = [IPutL])

    
    def containNoCheck(chain,*pThing):
        """Method that moves the object into the container."""


    def visibleContents(chain):
        """returns a list of contents"""

    def put(chain,cmd):
        """the put listener method"""

        


#--------------------------------------------------------------------
# Verb Interfaces --
#   Verb interfaces tells us how a verb should do its work.
#   For example it says what errors a verb should be able to handle.
#   Like Open should be able to handle StateError, ObjError, LockError
 
#--------------------------------------------------------------------
# ITest -- Used to test adaption in different places.
#
#  Amonst others used inside language modules for adapters.
#  Should also be used heavily by the testing framework.
#
class ITest(Interface):
    """A Test Interface Facility, use where you deem fit."""

    def test(obj,proto):
        """should just print out that everything worked out."""
        print 'aok'
