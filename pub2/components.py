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
#   2006-07/08 TJH - Changed 'Symbol' to 'DynamicComponentRack' and
#                   moved it into components.py
#
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

from interfaces import *
import defaults as d

# protocols imports
from protocols import advise


class DynamicComponentRack(object):
    """
    Base class of objects which use the dynamic components design.

    Currently this is the base class for Noun only, which is why it's
    in this file. It allows components to be defined dynamically,

    It is also the base class for Component.
    """

    advise(instancesProvide=[IDynamicComponentRack])

    def __init__(self):
        
        self._components = [] # PRIVATE variable
                              # a list of classes or instances
                              # that should be added to the object when
                              # initialized.

        self.components = [] # a list that contains references 
                             # to components after it has been initialized.
                             # this is the variable that the outside uses.
        
        self.addComponents(self._components) # Add the components
            

    def addComponents(self,com):
        """
        method that adds components to the components list.
        checks three possible ways it can be called, with either a list, a class
        or an instance. Only when called with an instance does the component get
        added to the list, in other cases it's converted into an instance and
        resent to addComponents
        """ 
        if com:

            if type(com) == types.ListType:
                for each in com: self.addComponents(each)
                
            elif type(com) == types.ClassType: 
                self.addComponents(com())

            elif type(com) == types.InstanceType \
            and isinstance(com, DynamicComponentRack): 
                self.components.append(com)
                com(self) # This registers the component with self.
                 self.addComponents(com.components) 
                # Add everything that this component provides.
                
            else: raise TypeError('Must be of type List, Class or Instance')

        # there might well be more issues to deal with but this is a start.

    def __iadd__(self, other):
        """
        Synonym to provide n += components syntax.
        """
        self.addComponents(other)

    def delComponents(self,com):
        """
        Can be called in the same way as addComponents, with a list, class or
        instance. However dealing with deleting componets is a bit harder.
        When given a list the list is looped through and calls to delComponents
        are made.
        When given a class all classinstances are deleted.
        When given an instance just that instance is removed.        
        """
        if com:

            if type(com) == list: 
                for each in com: self.delComponents(each)

            elif type(com) == types.ClassType: 
                delete = []
                for item in self.components:
                    if item.__class__ == com:
                        delete.append(item)

                #delete all occurences of the class
                for item in delete:
                    self.components.remove(item)
                del delete        

            elif type(com) == types.InstanceType: 
                if com in self.components:
                    self.components.remove(com)
                    self.delComponents(com.components)
                    # Remove everything provided by the component. 
            
            else: raise TypeError('Must be of type List, Class or Instance')

        def __isub__(self, other):
            """
            Synonym to provide simpler n -= components
            """
            self.delComponents(other)

        def extend(self,meth,component):
            """
            Extends the Object to enable dispatching methods.
            """

            if type(meth) == list:
                for x in meth:
                    extend(meth)

            if type(meth) == str:
                if not meth in dir(self)
                    exec """

@dispatch.generic()
def %(m)s(self,cmd): pass
self.%(m)s = %(m)s
""" % {'m':meth}
                    
            else : raise TypeError, "Must be of type List or String."
                

#--------------------------------------------------------------------
class Component(DynamicComponentRack):
    """
    Component is the base class for all components it holds basic 
    functionality for dealing with composites. However there is 
    currently nothing that differs between DynamicComponentRack and Component.
    """

    advise(instancesProvide=[IDynamicComponentRack])

    def __init__(self):
        DynamicComponentRack.__init__(self)
        
        check = "and self.components.__contains__(c)"


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
        self.methods = ['ask']

        # Ask specifics 
        self.answers = {} # A dictionary with queries and answers

        self.__call__(self)
        
    def __call__(self,parent):
        """Register methods to parent."""
        
        parent.extend(self.methods, self)
                
        #---------------------------------------------------------------
        # Ask methods

        @parent.ask.when("c.answers.__contains__(cmd.aboutobj) %s" % self.check)
        def ask(self, cmd, c=self):

            cmd.tell(answer = c.answerDict[cmd.aboutobj])

        @parent.ask.before("not c.answers.__contains__(cmd.aboutobj) %s"\
        % self.check)
        def ask_fail_no_answer(self,cmd,c=self):
            
            raise pub.errors.NoAnswer
      
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

    advise(instancesProvide=[IDropL,IGetL,IGiveL,IPutL])
    
    def __init__(self):
        Component.__init__(self)
        self.methods = ['drop','get','give','put']
        
        # Carriable specifics.
        

        self.__call__(self) # Register methods.

    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self.methods)

        #-------------------------------------------------------------
        # Drop methods

        @parent.drop.when("cmd.actor.has(self) %s)" % self.check)
        def drop(self,cmd,c=self):
            """
            Try to drop the object.
            """
            
            self.moveTo(cmd.actor.container)

        @parent.drop.before("not cmd.actor.has(self) %s)" % self.check)
        def drop_fail_inventory(self,cmd,c=self):
            """Fail because not in inventory."""

            raise pub.errors.InventoryError


        #---------------------------------------------------------------
        # Get methods
                
        @parent.get.when("cmd.actor.has(self) %s" % self.check)
        def get(self,cmd,c=self):
            """Try to pick up an object."""

            self.moveTo(cmd.actor)    

        
        @parent.get.before("not cmd.actor.has(self) %s" % self.check)
        def get_fail_inventory(self,cmd,c=self):
            """Fail because not in inventory."""

            raise pub.errors.InventoryError
                

        #---------------------------------------------------------------
        # Give methods

        @parent.give.when("cmd.actor.has(self) %s" % self.check)
        def give(self,cmd,c=self):
            """
            Try to give the object to target.
            """
            
            cmd.dirobj.receive(self)

        @parents.give.before("not cmd.actor.has(self) %s" % self.check)
        def give_fail_inventory(self,cmd,c=self):
            """Fail because not in inventory."""

            raise pub.errors.InventoryError

        #---------------------------------------------------------------
        # Put methods

        @parent.put.when("cmd.actor.has(self) %s" % self.check)
        def put(self,cmd,c=self):
            """Put the object on a specific place."""

            self.moveTo(cmd.indirobj)

        @parent.put.before("not cmd.actor.has(self) %s" % self.check
        def put_fail_inventory(self,cmd,c=self):
            """Fail because not in inventory"""

            raise pub.errors.InventoryError

#-----------------------------------------------------------------------        
#
class Drinkable(Component):
    """Handles drinking events."""

    advise(instancesProvide=[IDrinkL])
    
    def __init_(self):
        Component.__init__(self)
        self.methods = ['drink']

        # Drink Specifics
        self.amount = 1 # How much liquid the object consist of. 
                        # 1 is a very small amount a normal glass 
                        # consists of about 5
        
        self.__call__(self)

    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self.methods)

        #---------------------------------------------------------------
        # Drink methods

        @parent.drink.when("cmd.actor.has(self) %s" % self.check)
        def drink(self, cmd, c=self):
            """
            Method to drink the liquid.
            """
            if c.amount > 1:
                c.amount -= 1
            elif c.amount == 1:
                cmd.dirobj.MoveTo('TRASH')
    
        @parent.drink.before("not cmd.actor.has(self) %s" % self.check)
        def drink_fail_inventory(self,cmd,c=self):
            """Fail because not in inventory"""

            raise pub.errors.InventoryError

           
#--------------------------------------------------------------------
#
class Edible(Component):
    """Handles eating events."""
    
    advise(instancesProvide=[IEatL])

    def __init__(self):
        Component.__init__(self)
        self.methods = ['eat']

        # Eat specifics

        self.amount = 1 # A bite of food in general.
                        # This might be an idea to change in time
                        # but it's not important now.

        self.__call__(self)

    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self.methods)

        #---------------------------------------------------------------
        # Eat methods

        @parent.eat.when("cmd.actor.has(self) %s" % self.check)
        def eat(self, cmd, c=self):
            """
            Try to eat something, if not stopped by anything will result in
            either part of the object being removed or the entire object being
            deleted.
            """

            if c.amount > 1:
                c.amount -= 1
            elif c.amount == 1:
                cmd.dirobj.moveTo('TRASH')

        @parent.eat.before("not cmd.actor.has(self) %s" % self.check)
        def eat_fail_inventory(self,cmd,c=self):
            """Fail because not in inventory"""

            raise pub.errors.InventoryError


#--------------------------------------------------------------------
#
class Visible(Component):
    """"""
    advise(instancesProvide=[IExamineL, ILookL])

    def __init__(self):
        Component.__init__(self)
        self.methods = ['examine','look']

        # Visible specifics

        salient = True # Is the item visible
        invisible = 0

        self.__call__(self)

    def __call__(self, parent):
        """Register methods."""

        parent.extend(self.methods)

        #---------------------------------------------------------------
        # Examine methods

        @parent.examine.when("visible(c) %s" % self.check)
        def examine(self,cmd,c=self):
        """Look closer at the object."""
        

        #-----------------------------------------------------------------------
        # Look methods

        @parent.examine.when("visible(c) %s" % self.check)
        def look(self,cmd,c=self):
            """Look at the object."""

        # Not having determined how visibility and the like works I don't know
        # how this should be coded yet.

        
#-----------------------------------------------------------------------
#
class Mobile(Component):
    """Makes the object mobile."""
    advise(instancesProvide=[IFollowL])
    
    def __init__(self):
        Component.__init__(self)
        self.methods = ['follow','move']

        # Mobile specifics
        self.followers = []

        self.__call__(self)

        def __call__(self,parent):
            """Register methods."""

            parent.extend(self.methods)

            @parent.follow.when("cmd.actor.can('move')")
            def follow(self,cmd,c=self):
                """Follow this entity."""

                c.followers.append(cmd.actor)

            @parent.move.when("")
            def move(self,cmd,c=self):
                """Move somewhere."""
                
                self.moveTo(cmd.dirobj)

                for follower in c.followers:
                    follower.moveTo(cmd.dirobj)

                
#-----------------------------------------------------------------------
class Enterable(Component):
    """Make the object enterable."""
    advise(instancesProvide=[IGoL])

    def __init__(self):
        Component.__init__(self)

        self.target = None

        self.__call__(self)
    
    def __call__(self,parent):
        """Register methods."""
        
        parent.extend(self.methods)

        @parent.go.when("self.target not is None %s" % self.check)
        def go(self,cmd,c=self):
            """Enter the object."""

            cmd.actor.moveTo(self.target)
        
    
        @parent.go.before("self.target is None %s" % self.check)
        def go_fail_no_target(self,cmd,c=self):
            """Fail because no target"""

            raise pub.errors.ObjError, "This door leads nowhere."

#--------------------------------------------------------------------
#
class Lockable(Component):
    """Make a lock on the object."""

    advise(instancesProvide=[ILockL,IUnlockL])

    def __init__(self):
        Component.__init__(self)
        self.methods = ['lock','unlock','open','close']

        #Lockable specifics
        self.isLocked = False
        self.keys = []

        self.__call__(self)

    def __call__(self,parent):
        """Register methods to parent"""

        parent.extend(self.methdods)

        @parent.lock.when("c.isLocked = False %s" % self.check)
        def lock(self,cmd,c=self):
            """Method to change isLocked to True if possible."""

            for key in self.keys:
                if cmd.actor.has(key):
                    self.isLocked = True

        @parent.lock.before("c.isLocked = True %s" % self.check)
        def lock_fail_locked(self,cmd,c=self):
            """Fail because already locked."""

            raise pub.errors.LockError
        
        @parent.unlock.when("c.isLocked = True %s" % self.check)
        def unlock(self,cmd,c=self):
            """Method to change isLocked to False if possible."""

            for key in self.keys:
                if cmd.actor.has(key):
                    self.isLocked = False

        @parent.unlock.before("c.isLocked = False %s" % self.check)
        def unlock_fail_unlocked(self,cmd,c=self):
            """Fail because not locked."""

            raise pub.errorsLockError

        @parent.open.before("c.isLocked = True %s" % self.check)
        def open_fail_locked(self,cmd,c=self):
            """The lock is locked."""

            raise pub.errors.LockError
        
#--------------------------------------------------------------------
#
class Openable(Component):
    """Give the object the ability to be opened."""

    advise(instancesProvide=[ICloseL,IOpenL])

    def __init__(self):
        Component.__init__(self) 
        self.methods = ['close','open']

        #Openable specifics
        self.isOpen = True

        self.__call__(self)
    
    
    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self.methods)

        @parent.close.when("c.isOpen == True %s" % self.check)
        def close(self,cmd,c=self):
            """Tries to close itself."""
           
            c.isOpen = False

        @parent.close.before("c.isOpen == False %s" % self.check)
        def close_fail_closed(self,cmd,c=self):
            """Already closed"""

            raise pub.errors.StateError
        
        @parent.open.when("c.isOpen == False %s" % self.check)
        def open(self,cmd,c=self):
            """Tries to open itself."""

            c.isOpen = True

        @parent.open.before("c.isOpen == True %s" % self.check)
        def open_fail_open(self,cmd,c=self):
            """Already opened"""
            
            raise pub.errors.StateError

#--------------------------------------------------------------------
#
class Pullable(Component):
    """"""

    advise(InstancesProvide = [IPullL]

    def __init__(self):
        """"""
        Component.__init__(self)
        self.methods = ['pull']

        self.pulled = False

        self.__call__(self)

    def __call__(self,parent):
        """Register methods."""

        parent.extend(self.methods)

        @parent.pull.when("True %s" %s self.check)
        def pull(self,cmd,c=self):
            """Pull at this object. It is normaly a lever."""


            c.pulled = True
    
#--------------------------------------------------------------------
#
class Pushable(Component):
    """"""
     
    advise(InstancesProvide = [IPushL]

    def __init__(self):
        """"""
        Component.__init__(self)

        self.methods = ['pull']
        self.pushed = False

        self.__call__(self)


    def __call__(self,parent):
        
        parent.extend(self.methods)
    
        @parent.push.when("True %s" %s self.check)
        def push(self,cmd,c=self):
            """"""
            
            self.pushed = True
            

#--------------------------------------------------------------------
#
class Tellable(Component):
    """"""

    advise(InstancesProvide = [ITellL]

    def __init__(self):
        """"""
        Component.__init__(self)

        self.methods = ['tell']

        self.__call__(self)

    def __call__(self,parent):
        
        parent.extend(self.methods)
        
        @parent.tell.when("True %s" %s self.check)
        def tell(self,cmd,c=self):
            """
            This would likely be seen as a metaclass of
            sorts. Creating a general Tellable class would most likely
            just send information from the tell to a parser. In the case
            of an agent this parser could make it possible to react on 
            actions.
            """
            continue


#--------------------------------------------------------------------
#
class Turnable(Component):
    """"""
    
    advise(InstancesProvide = [IPullL]

    def __init__(self):
        """"""
        Component.__init__(self)

        self.methods = ['turn']
        self.turnaction = None

    def __call__(self,parent):
        
        parent.extend(self.methods)

        @parent.turn.when("True %s" % self.check)
        def turn(self,cmd,c=self);
            """Turn something. What happens depends on turnaction."""
            if self.turnaction != None:
                exec turnaction
            

#--------------------------------------------------------------------
#
class Wearable(Component):
    """"""

    advice(instancesProvide = [IWearL,IRemoveL]

    def __init__(self):
        """"""
        Component.__init__(self)
        self.methods = ['wear', 'remove']

        self.isWorn = False
        self.wornBy = None

        self.__call__(self)

        
    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self)

        @parent.wear.when("cmd.actor.has(self) %s" % self.check)
        def wear(self,cmd,c=self):
            """"""
            
            c.isWorn = True
            c.wornBy = cmd.actor

        @parent.wear.before("not cmd.actor.has(self) %s" % self.check)
        def wear_fail_inventory(self,cmd,c=self):
            """"""

            raise pub.errors.InventoryError
            

        @parent.remove.when("c.wornBy == cmd.actor %s" % self.check)
        def remove(self,cmd,c=self):
            """"""

            c.isWorn = False
            c.wornBy = None

        @parent.remove.when("c.wornBy not is cmd.actor %s" % self.check)
        def remove_fail_not_wearing(self,cmd,c=self):
            """"""

            raise pub.errors.InventoryError



        
######################################################################
#
#
class TestComponent(Component):
    """A TestComopnent. Used to check adation and stuff."""

    advise(instancesProvide=[ITest])
    def __init__(self):
        Component.__init__(self)    

        self.methods = ['test']

        self(self)

    def __call__(self,parent):

        parent.extentd(self.methods)

        @parent.test.when("cmd is 'test'")
        def test(self,cmd,c=self):
            print 'Testing finished.'
