# eatable, drinkable, poison, medicine -- anything that character can ingest for good or ill.

from protocols import Interface, advise

import pub.errors
from pub.component import Component

#---------------------------------------------------------------------
# Drinking Interface
#

# Interfaces
class IDrinkL(Interface):
    """
    Used for things you could drink.
    """

    def drink(chain, cmd):
        """Method called when the object is told of a drinking event"""


# Components
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

        #
        #-------------------------------------------------------------

# End Drinking Interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Eating Interface
#

# Interfaces
class IEatL(Interface):
    """
    Used for things you could eat.
    """
    
    def eat(chain, cmd):
        """Method called when something is eaten"""


# Components
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

        @parent.eat.when("True) %s" % self.check)
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

        #
        #-------------------------------------------------------------

# End Eating Interface
#---------------------------------------------------------------------
