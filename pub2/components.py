# components.py    contains components for pub            04/10/22 GJ
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

#--------------------------------------------------------------------
#  CHANGELOG
#
#--------------------------------------------------------------------
""" 
This module provides components that are made into parts of an object. 
Add these components or instances thereof to objs with:
obj.addComponents(compo)
"""

# system imports

# pub imports
from noun import Symbol
from interfaces import *

# protocols imports
from protocols import advise


#XXX: Write a testComponent, needs a Component class first.
#--------------------------------------------------------------------
class Component(Symbol):
    """
    Component is the base class for all components it holds basic 
    functionality for dealing with composites. However there is 
    currently nothing that differs between Symbol and Component.
    """

    def __init__(self):
        Symbol.__init__(self)
    
    advise(instancesProvide=[ISymbol])
    

#--------------------------------------------------------------------
class Askable(Component):
    """
    A simple ask component that provides IAskL. If you want an object to
    be able to respond to questions.
    """
        
    advise(instancesProvide = [IAskL])

    def __init__(self, obj, proto):
        Component.__init__(self)
        self.obj = obj
        self.proto = proto
        
        # Ask specifics 
        self.answerDict = {} # a dictionary with queries and answers
        
    def ask(self, chain, cmd):
        """takes a chain object and a command object"""

        # All listen methods have to handle cmd being None
        if cmd == None: pass 

        try: return chain.next().ask(chain,cmd)
        except StopIteration:
            try:
                if self.answerDict[cmd.aboutobj]:
                    cmd.tell(answer = self.answerDict[cmd.aboutobj])
            except KeyError: raise pub.errors.PubError # some error 
            raise
        

class Carriable(Component):
    """
    Component that enables the object to be carried about.
    Should activate picking up, dropping and giving it away.
    """

    def __init__(self, obj, proto):
        """
        """
        Component.__init__(self)
        self.obj = obj
        self.proto = proto

        # Carriable specifics
        
    def get(self, chain, cmd):
        """
        """

        if cmd == None: pass
        
        #XXX: Check if the object can be picked up.
        # More checks
        # How do we check such things?
        if not check(cmd.actor, IContainer, 'canContain', self.obj):
            raise CanContainError
            
            
        try: return chain.next().get(chain,cmd)
        except StopIteration: 
            self.obj.desc.initialDesc = ''
            self.obj.desc.initialNote = ''

            self.obj.moveTo(cmd.actor)
            raise
                
    def give(self, chain, cmd):
        """
        """
    
    def drop(self, chain, cmd):
        """
        """


class Drinkable(Component):
    """
    Handles drinking events
    """

    advise(instancesProvide=[IDrinkL])
    
    def __init_(self,obj,proto):
        Component.__init__(self)
        self.obj = obj
        self.proto = proto

        # Drink Specifics
        self.amount = 1 # How much liquid the object consist of. 
                        # 1 is a very small amount a normal glass 
                        # consists of about 5

        
    def drink(self, chain, cmd):
        """
        method to drink the liquid.
        """

        if cmd == None: pass            
            
        try: return chain.next().drink(chain, cmd) # Check that nothing halts us
        except StopIteration: # We've reached the end, so execute
            if self.amount > 1:
                self.amount -= 1
            elif self.amount == 1:
                cmd.dirobj.MoveTo('TRASH')

            raise # reraise StopIteration
       
    
class Edible(Component):
    """
    Handles eating events
    """

class Visible(Component):
    """
    
    """
    
class Mobile(Component):
    """
    
    """
    
class Enterable(Component):
    """
    
    """
    advise(instancesProvide=[IGoL])

    def __init__(self, obj, proto)
    
    def go(self, chain, cmd):
        """
        """
    
class Lockable(Component):
    """
    
    """

    advise(instancesProvide=[ILockL,IUnlockL,IOpenL,ICloseL]

    def __init__(self, obj, proto):
        Component.__init__(self)
        self.obj = obj
        self.proto = proto

        #Lockable specifics
        self.isLocked = False
        self.keys = []
        self.autolock = False

    def lock(self, chain, cmd):
        """
        """
    
    def unlock(self, chain, cmd):
        """
        """
        
    def open(self, chain, cmd):
        """
        If the object is locked raise an error
        """
        
    def close(self, chain, cmd):
        """
        """
    
class Openable(Component):
    """
    
    """

    advise(instancesProvide=[ICloseL,IOpenL])

    def __init__(self, obj, proto):
       Component.__init__(self) 
       self.obj = obj
       self.proto = proto

       #Openable specifics
       self.isOpen = True
    
   def close(self, chain, cmd):
        """
        Tries to close itself.
        """
       
        if cmd == None: # We have been told to close regardless of state
            self.isOpen = False
            return chain.next().close(chain, cmd)

        if not self.isOpen: raise pub.errors.StateError

        try: return chain.next().close(chain, cmd)
        except StopIteration:
            self.isOpen = False
            
            raise # reraise StopIteration

    def open(self, chain, cmd):
        """
        Tries to open itself.
        """

        if cmd == None: #Open regardless of state or locks.
            self.isOpen = True 
            return chain.next().open(chain,cmd)

        if self.isOpen: raise pub.errors.StateError
       
        try: return chain.next().open(chain, cmd)
        except StopIteration:
            self.isOpen = True
            
            raise # reraise StopIteration
            

class Pullable(Component):
    """
    
    """
    
class Pushable(Component):
    """
    
    """
    
    
class Tellable(Component):
    """
    
    """


class Removeable(Component):
    """
    
    """
    
class Turnable(Component):
    """
    
    """
    
class Wearable(Component):
    """
    
    """

#######################################################################
#
#
class TestComponent(Component):
    """
    A TestComopnent. Used to check adation and stuff.
    """

    advise(instancesProvide=[ITest])
