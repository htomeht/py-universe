# properties of matter: mass, volume (size), length, physical state (solid, liquid, gas) etc.


from protocols import Interface, advise

import pub.error

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


# End Interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Visual Interface 
#
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

#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Turning Interface
#
class ITurnL(Interface):
    """
    Provides an interface for turning.
    Can be used if you wish to turn things(rotating)
    if you want to turn on the light or even turn around if you make it
    possible.
    """

    def turn(chain,cmd):
        """Method that listens for turn events"""

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

#
#---------------------------------------------------------------------

