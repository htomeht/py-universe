# properties of matter: mass, volume (size), length, physical state (solid, liquid, gas) etc.

from protocols import Interface, advise

import pub.errors
from pub.component import Component

#---------------------------------------------------------------------
# Dropping/Getting/Giving/Puting Interface
#
class IDropL(Interface):
    """
    Provides the  drop method.
    """

    def drop(chain,cmd):
        """Method that listens for drop events."""


class IGetL(Interface):
    """
    Provides the get method.
    """

    def get(chain,cmd):
        """Method that listens for get events."""

class IGiveL(Interface):
    """
    Provides the give method.
    """

    def give(chain,cmd):
        """Method that listens for give events"""

class IPutL(Interface):
    """
    Provides the put method.
    """

    def put(chain,cmd):
        """Method that listens for put events"""


class Carriable(Component): 	 
    """ 	 
    Component that enables the object to be carried about. 	 
    Should activate picking up, dropping and giving it away as well 	 
    as putting it somewhere. 	 
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

 	    #
        #---------------------------------------------------------------------
        
 	 
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

 	    #
        #---------------------------------------------------------------------

 	 
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

        #
        #---------------------------------------------------------------------

 	 
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

        #
        #---------------------------------------------------------------------


# End Dropping/Getting/Giving/Puting Interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Visual Interface 
#

# Interfaces
class IExamineL(Interface):
    """
    Provides an interface for examining.
    Used to examine objects.
    """

    def examine(chain,cmd):
        """Method that listens for examine events"""

class ILookL(Interface):
    """
    provides the look method
    """

    def look(chain,cmd):
        """Method listening for look events"""


# Components
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

        #-------------------------------------------------------------
        # Examine methods

        @parent.examine.when("visible(c) %s" % self.check)
        def examine(self,cmd,c=self):
            """Look closer at the object."""

            pass
        
        #
        #-------------------------------------------------------------

        #-------------------------------------------------------------
        # Look methods

        @parent.examine.when("visible(c) %s" % self.check)
        def look(self,cmd,c=self):
            """Look at the object."""

            pass

        # Not having determined how visibility and the like works I don't know
        # how this should be coded yet.

        #
        #-------------------------------------------------------------

# End Visual Interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Turning Interface
#

# Interfaces
class ITurnL(Interface):
    """
    Provides an interface for turning.
    Can be used if you wish to turn things(rotating)
    if you want to turn on the light or even turn around if you make it
    possible.
    """

    def turn(chain,cmd):
        """Method that listens for turn events"""


# Components
class Turnable(Component):
    """"""
    
    advise(InstancesProvide = [ITurnL]

    def __init__(self):
        """"""
        Component.__init__(self)

        self.methods = ['turn']
        self.turnaction = None

    def __call__(self,parent):
        
        parent.extend(self.methods)

        #-------------------------------------------------------------
        # Turn methods
        @parent.turn.when("True %s" % self.check)
        def turn(self,cmd,c=self);
            """Turn something. What happens depends on turnaction."""
            if c.turnaction != None:
                exec turnaction

        #
        #-------------------------------------------------------------

# End Turning Interface
#---------------------------------------------------------------------

