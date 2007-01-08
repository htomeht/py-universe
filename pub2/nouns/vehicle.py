# noun components defining generic vehicles, and common examples: car, elevator, bicycle, etc.

from protocols import Interface, advise

import pub.errors
from pub.component import Component

#---------------------------------------------------------------------
# Mobile interface
#

# Interfaces
class IFollowL(Interface):
    """
    Provides an interface for following.
    Can be be used to have an object notice it is being followed.
    Normaly used in things which are mobile, like an actor or a car.
    """

    def follow(chain,cmd):
        """Method that listens for following events"""

# Components
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

        #---------------------------------------------------------
        # Following methods
        @parent.follow.when("cmd.actor.can('move') %s" % self.check)
        def follow(self,cmd,c=self):
            """Follow this entity."""

            c.followers.append(cmd.actor)

        #
        #---------------------------------------------------------
        
        #---------------------------------------------------------
        # Moving methods
        @parent.move.when("True %s" % self.check)
        def move(self,cmd,c=self):
            """Move somewhere."""
            
            self.moveTo(cmd.dirobj)

            for follower in c.followers:
                follower.moveTo(cmd.dirobj)

        #
        #---------------------------------------------------------

# End mobile interface
#---------------------------------------------------------------------
