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
which documents how other classes should work. 
For instance the interface IOpenable documents functions that must be 
supported by objects like doors and books to be funtional. 
The interfaces are in alphabetical order.

We use interfaces by using advise to make an object support the protocol.
like so:

class Test(pub.core.Component):
    advise(instancesProvide=[IOpenable])

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

from protocols import Interface


   
#--------------------------------------------------------------------
#ICarriable
class ICarriable(Interface):
    """
    To be carrible an object must support ICarriable.
    Checked for when you try to pick something up.
    """

    def get(chain,cmd):
        """Method called when something is picked up."""
    
    def drop(chain,cmd):
        """Method called when the object is dropped"""

    def give(chain,cmd):
        """method called when an object is given away."""
        

#--------------------------------------------------------------------
# IContainer
class IContainer(Interface):
    """
    Used to create containers like a room or a box.
    """

    def canContain(chain,pThing):
        """method to see if pThing can be contained in the container
        the result depends on many things, for example ContainLiquid might
        define a special canContain method"""

    def containNoCheck(chain,*pThing):
        """Moves an object into a container"""

    def getContententsDesc(chain,pLooker=None):
        """describes the contents of an object using getListLine"""

    def visibleContents(chain):
        """returns a list of contents"""

    def put(chain,cmd):
        """Method to put something on, in, under object or where the object 
        can contain another object."""


#--------------------------------------------------------------------
# IConsumable
class IConsumable(Interface):
    """
    Used for things you could eat and drink.
    If something can be eaten but not drunk you should raise an error
    in the drink method. 
    raise pub.errors.MethodError.
    This should be caught by whichever verb made the call.
    """
    
    def eat(chain, cmd):
        """Method called when something is eaten"""

    def drink(chain, cmd):
        """Method called when something is drunk"""


#--------------------------------------------------------------------
# IEnterable
class IEnterable(Interface):
    """
    Something that can be entered like a door, a portal or something 
    else entirely.
    """
    
    def go(chain,cmd):
        """method to use an exit like it was intended."""

    
#--------------------------------------------------------------------
# ILightsource
class ILightSource(Interface):
    """An interface for lightsources"""

    def getLight(chain):
        """get the light value from a component"""


#--------------------------------------------------------------------
# ILockable
class ILockable(Interface):
    """
    Used on objects which wish to be lockable.
    Components could be combiantion locks, key locks, password locks and so on.
    """

    def lock(chain,cmd):
       """method to lock the lock"""

    def unlock(chain,cmd):
       """method to unlock the lock"""
    
    

#--------------------------------------------------------------------
# IMobile
class IMobile(Interface):
    """
    Something that can move on it's own, or atleast holds the powerdevice
    to do it, like a person, a car or the like.
    """

    def follow(chain,cmd):
        """
        method called when someone tries to follow the object.
        could result in calling methods to evade the following or just
        make sure the system knows of the following.
        """
    

#--------------------------------------------------------------------
# IOpenable
class IOpenable(Interface):
    """
    Serves as a way of effecting things which can be opened. 
    """

    def open(chain,cmd):
        """Method to run when the object is being opened."""

    def close(chain,cmd):
       """Method to run when the object is being closed."""


#--------------------------------------------------------------------
# ISentience
class ISentience(Interface):
    """
    Provides the item with some intelligence, used for actors.
    And objects which know what they are talking about.
    These are one of the the more difficult interfaces to write
    this because I have no real grasp on how we should create sentience, and
    what should be part of it.

    Most likely all things like seeing and hearing should be part of this.
    """
     
    def ask(chain,cmd):
        """method to ask the being something"""

    def hearSpeech(chain,cmd):
        """method to react to speach, say a person is schizo, we want
        his both personalities to react by their own accord."""

    def receive(chain,cmd):
        """method called when given an object"""

    def smell(chain,cmd):
        """method to smell something"""
    
    def talk(chain,cmd):
        """method called when trying to talk to the individual"""
    
    def tell(chain, cmd, pWhat):
        """
        Hear something told to me.
            This is the primary function for interaction
            with Sentient beings.
            Just call the tell method on them
        """
    
    
#--------------------------------------------------------------------
# ISwitchable
class ISwitchable(Interface):
    """
    Used to provide a two-way behaviour for objects.
    Can be used to create buttons, switches, clothing
    and anything wich you can that has on or off behaviour 
    """

    def activate(chain,cmd):
        """the activate method for a switch object"""

    def deactivate(chain,cmd):
        """deactivate method for switch objects"""


#--------------------------------------------------------------------
# IWearable
class IWearable(Interface):
    """Used for creating clothes, jewelry or other things that are worn."""

    def wear(chain,cmd):
        """method called when you try to put something on"""

    def remove(chain,cmd):
        """method called when you take something off"""
   
