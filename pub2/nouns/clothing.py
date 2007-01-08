# Noun components providing wearable traits.

from protocols import Interface, adapt

import pub.errors
from pub.component import Component

#---------------------------------------------------------------------
# Wearing/Removing Interface
#

# Interfaces
class IWearL(Interface):
    """
    Provides an interface for wearing.
    Most likely used for clothing like objects.
    Example: Jewelry, pants, armor.
    """

    def wear(chain,cmd):
        """Method that listens for wearing events"""
        
class IRemoveL(Interface):
    """
    Provides an interface for removing.
    Used mainly for clothing like objects.
    Example: ring, shirt.
    """

    def remove(chain,cmd):
        """Method that listens fo remove events"""


# Components
class Wearable(Component):
    """Handles wearing events."""

    advice(instancesProvide = [IWearL,IRemoveL]

    def __init__(self):
        Component.__init__(self)
        self.methods = ['wear', 'remove']

        # Wearable specifics
        self.isWorn = False
        self.wornBy = None

        self.__call__(self)

    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self)

        #-------------------------------------------------------------
        # Wearing methods
        @parent.wear.when("cmd.actor.has(self) %s" % self.check)
        def wear(self,cmd,c=self):
            """"""
            
            c.isWorn = True
            c.wornBy = cmd.actor

        @parent.wear.before("not cmd.actor.has(self) %s" % self.check)
        def wear_fail_inventory(self,cmd,c=self):
            """"""

            raise pub.errors.InventoryError

        #
        #-------------------------------------------------------------
            
        #-------------------------------------------------------------
        # Removing methods
        @parent.remove.when("c.wornBy == cmd.actor %s" % self.check)
        def remove(self,cmd,c=self):
            """"""

            c.isWorn = False
            c.wornBy = None

        @parent.remove.when("c.wornBy not is cmd.actor %s" % self.check)
        def remove_fail_not_wearing(self,cmd,c=self):
            """"""

            raise pub.errors.InventoryError

        #
        #-------------------------------------------------------------

# End Wering/Removing Interface
#---------------------------------------------------------------------

