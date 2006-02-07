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
import pub
from pubcore import Symbol
from interfaces import *
import defaults as d

# protocols imports
from protocols import advise


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
# Components -- 
#--------------------------------------------------------------------
class Askable(Component):
    """
    A simple ask component that provides IAskL. If you want an object to
    be able to respond to questions. 
    """
        
    advise(instancesProvide = [IAskL])

    def __init__(self):
        Component.__init__(self)
      
        # Ask specifics 
        self.answerDict = {} # a dictionary with queries and answers
        
    def ask(self, chain, cmd):
        """takes a chain object and a command object"""

        # All listen methods have to handle cmd being None
        if cmd == None: return chain.next().ask(chain,cmd)

        try: return chain.next().ask(chain,cmd)
        except StopIteration:
            try:
                if self.answerDict[cmd.aboutobj]:
                    cmd.tell(answer = self.answerDict[cmd.aboutobj])
            except KeyError: raise pub.errors.ResponseError 
            raise
        
#--------------------------------------------------------------------
#
class Carriable(Component):
    """
    Component that enables the object to be carried about.
    Should activate picking up, dropping and giving it away as well
    as putting it somewhere.

    One should take into mind that the approch with:
    try: check()
    except ComponentError:
    shouldn't be needed if one designs a good set defaults.
    """

    advise(instancesProvide=[IGetL,IGiveL,IDropL,IPutL])
    
    def __init__(self):
        Component.__init__(self)

        # Carriable specifics
        # I know of no sure cards.

    def drop(self, chain, cmd):
        """
        Try to drop the object.
        """

        if cmd == None: return chain.next().drop(chain,cmd)

        check(cmd.actor, IContainer, 'contains', [cmd.dirobj],d.NoContainer)
        
        #except ComponentError:
        #    raise ContainerError, ("%(actor)s isn't a container."\
        #    % cmd.__dict__)
        
        # This should raise an error if the dirobj isn't in inventory. 
        # InventoryError to be specific.
        # The Verb should handle this, I'm writing it here so I won't
        # forget it.
        
        try: return chain.next().drop(chain,cmd)
        except StopIteration:
            loc = set(cmd.dirobj,ILocatable)
            if loc: loc.moveTo(cmd.actor.container)
            
            cmd.primary = pub.messages['TransitiveSuccess']

            
            raise
        
    def get(self, chain, cmd):
        """
        Try to pick up an object.
        """

        if cmd == None: return chain.next().get(chain,cmd)
        
        # Should raise an error if the object can't be contained.
        check(cmd.actor, IContainer, 'canContain', [cmd.dirobj],d.NoContainer)
            
        try: return chain.next().get(chain,cmd)
        except StopIteration: 
            # Perform the action we've been asked to.
            obj_desc = set(cmd.dirobj,IDescribable)
            obj_desc.initialDesc = ''
            obj_desc.initialNote = ''

            obj_loc = set(cmd.dirobj,ILocatable)
            obj_loc.moveTo(cmd.actor)

            cmd.primary = pub.messages['TransitiveSuccess']
            
            raise
                
    def give(self, chain, cmd):
        """
        Try to give the object to target.
        """
        if cmd == None: return chain.next().give(chain,cmd) 

        try: check(cmd.actor, IContainer, 'contains', [cmd.dirobj])
        except ComponentError:
            raise ContainerError, ("%(actor)s isn't a container."\
            % cmd.__dict__)
            
        
        try: return chain.next().give(chain,cmd)
        except StopIteration:
            try: 
                if invoke(cmd.indobj, IReceiveL, 'receive', cmd):
                    pass # Continue as per usual
            except: raise # Intercept errors.
            #XXX: Here is needed the code for telling cmd that the command
            # was succesfull.
            raise

    def put(self, chain, cmd):
        """
        Put the object on a specific place.
        """

        if cmd == None: return chain.next().put(chain,cmd)
        
        try: check(cmd.actor, IContainer, 'contains', [cmd.dirobj])
        except ComponentError:
            raise ContainerError, ("%(actor)s isn't a container."\
            % cmd.__dict__)
        
        try: return chain.next().put(chain,cmd)
        except StopIteration:
            loc = set(cmd.dirobj, ILocatable)
            loc.moveTo(indobj)
            raise

#--------------------------------------------------------------------          
#
class Drinkable(Component):
    """
    Handles drinking events
    """

    advise(instancesProvide=[IDrinkL])
    
    def __init_(self):
        Component.__init__(self)

        # Drink Specifics
        self.amount = 1 # How much liquid the object consist of. 
                        # 1 is a very small amount a normal glass 
                        # consists of about 5

        
    def drink(self, chain, cmd):
        """
        Method to drink the liquid.
        """

        if cmd == None: pass            
            
        try: return chain.next().drink(chain, cmd) # See that nothing halts.
        except StopIteration: # We've reached the end, so execute
            if self.amount > 1:
                self.amount -= 1
            elif self.amount == 1:
                cmd.dirobj.MoveTo('TRASH')

            raise # reraise Errors and StopIteration
       
#--------------------------------------------------------------------
#
class Edible(Component):
    """
    Handles eating events
    """
    
    advise(instancesProvide=[IEatL])

    def __init__(self):
        Component.__init__(self)

        # Eat specifics

        self.amount = 1 # A bite of food in general.
                        # This might be an idea to change in time
                        # but it's not important now.

    def eat(self, chain, cmd):
        """
        Try to eat something, if not stopped by anything will result in
        either part of the object being removed or the entire object being
        deleted.
        """

        if cmd == None: return chain.next().eat(chain,cmd)

        try: return chain.next().eat(chain, cmd)
        except StopIteration: 
            if self.amount > 1:
                self.amount -= 1
            elif self.amount == 1:
                cmd.dirobj.moveTo('TRASH')

            raise # reraise Errors and StopIteration
                    

#--------------------------------------------------------------------
#
class Visible(Component):
    """
    """
    advise(instancesProvide=[ILookL, IExamineL])

    def __init__(self):
        Component.__init__(self)

        # Visible specifics

        salient = True # Is the item visible
        invisible = 0

    def look(self, chain, cmd):
        """
        """
        try: return chain.next().look(chain,cmd)
        except StopIteration: 
            #XXX: Code for looking at the object including checking it's
            # visibility and the like.
            # This should really be redesigned so that it doesn't use 
            # introspection.
            if self.salient == True:
                if cmd.actor.canSee(cmd.dirobj):
                    desc = set(cmd.dirobj, IDescribable).desc
                    cmd.tell(desc)
                else: raise VisibilityError ("Not visible.")
            raise # Reraise

    def examine(self,chain,cmd):
        """
        """
        try: return chain.next().look(chain,cmd)
        except StopIteration:
            if self.salient == True:
                if cmd.actor.canSee(cmd.dirobj):
                    desc = set(cmd.dirobj, IDescribable).xdesc
                    cmd.tell(desc) 
                else: raise VisibilityError ("Not visible.")
            raise # Reraise
    
#--------------------------------------------------------------------
#
class Mobile(Component):
    """
    
    """
    advise(instancesProvide=[])
    
    def __init__(self):
        Component.__init__(self)

        # Mobile specifics



class Enterable(Component):
    """
    
    """
    advise(instancesProvide=[IGoL])

    def __init__(self):
        """
        """
    
    def go(self, chain, cmd):
        """
        """
    
#--------------------------------------------------------------------
#
class Lockable(Component):
    """
    """

    advise(instancesProvide=[ILockL,IUnlockL])

    def __init__(self):
        Component.__init__(self)

        #Lockable specifics
        self.isLocked = False
        self.keys = []

    def lock(self, chain, cmd):
        """
        Method to change isLocked to True if possible.
        """
        #XXX: One has to check if the lock can be locked, ie if the 
        # door is closed or whatever. Or maybe disregard the door
        # totaly? Just use this class as a base and build on it in other
        # components or create new special components that work on doors or the
        # like.
    
    def unlock(self, chain, cmd):
        """
        Method to change isLocked to False if possible.
        """

        
#--------------------------------------------------------------------
#
class Openable(Component):
    """
    """

    advise(instancesProvide=[ICloseL,IOpenL])

    def __init__(self):
       Component.__init__(self) 

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
            

#--------------------------------------------------------------------
#
class Pullable(Component):
    """
    
    """
    
#--------------------------------------------------------------------
#
class Pushable(Component):
    """
    
    """
    
    
#--------------------------------------------------------------------
#
class Tellable(Component):
    """
    
    """


#--------------------------------------------------------------------
#
class Removeable(Component):
    """
    
    """
    
#--------------------------------------------------------------------
#
class Turnable(Component):
    """
    
    """
    
#--------------------------------------------------------------------
#
class Wearable(Component):
    """
    
    """

######################################################################
#
#
class TestComponent(Component):
    """
    A TestComopnent. Used to check adation and stuff.
    """

    advise(instancesProvide=[ITest])
    def __init__(self):
        Component.__init__(self)    

    def test(self, chain, cmd):
        """
        funtion that does nothing but returns
        most likely this will raise a StopIteration error.
        """

        return chain.next().test(chain, cmd)
