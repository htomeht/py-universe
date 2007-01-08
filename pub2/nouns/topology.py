# Components supporting topological models: simple container, rel/abs brick, room models, etc.

from protocols import Interface, advise

import pub.errors
from pub.component import Component

#---------------------------------------------------------------------
# Entering Interface

# Interfaces
class IGoL(Interface):
    """
    Something that can be entered like a door, a portal or something 
    else entirely.
    """
    
    def go(chain,cmd):
        """Method to use an exit like it was intended."""

# Components
class Enterable(Component):
    """Make the object enterable."""
    advise(instancesProvide=[IGoL])

    def __init__(self):
        Component.__init__(self)

        # Enterable specifics
        self.target = None

        self.__call__(self)
    
    def __call__(self,parent):
        """Register methods."""
        
        parent.extend(self.methods)

        #-------------------------------------------------------------
        # Going methods
        @parent.go.when("self.target not None %s" % self.check)
        def go(self,cmd,c=self):
            """Enter the object."""

            cmd.actor.moveTo(self.target)
        
    
        @parent.go.before("self.target is None %s" % self.check)
        def go_fail_no_target(self,cmd,c=self):
            """Fail because no target is specified."""

            raise pub.errors.ObjError, "This leads nowhere."

        #
        #-------------------------------------------------------------

# End Entering Interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Containment Interface
#

# Interfaces
class IContainer(Interface):
    """
    An interface to make components support containability.
    """

    advise(protocolExtends = [IPutL])

    def put():
        """The put listener method"""

    def visible_contents():
        """Returns a list of contents"""

    def get_contents_desc():
       """Describes the contents of the container."""

# Components
class Container(Component):
    """
    A container can hold objects.
    """

    def __init__(self):
        Component.__init__(self)
        self.methods = ['visibleContents','put','getContentsDesc']

        # Container specifics
        self.contents = []

        self.__call__(self)

    def __call__(self,parent):
        
        parent.extend(self.methods)

        #-------------------------------------------------------------
        # Put methods
        @parent.put.when("cmd.dirobj in self.contents %s" % self.check)
        def put(self,cmd,c=self):
            """
            Method that is called by a verb when something is to be moved
            into the container.
            """
            cmd.dirobj.moveTo(self.contents)

        @parent.put.before("cmd.dirobj in self.contents %s" % self.check)
        def put_fail_in_contents(self,cmd,c=self):
            """
            When an object is already in the container this 
            method is called.
            """
            raise pub.errors.InventoryError
        
        @parent.put.before("parent.size < cmd.dirobj.size %s" % self.check)
        def put_fail_size(self,cmd,c=self):
            """
            When an object is too big to fit into a container this is the
            method that will be called.
            """
            raise pub.errors.SizeError

        #
        #-------------------------------------------------------------

        #-------------------------------------------------------------
        # Visible contents methods
        @parent.visible_contents.when("True %s" % self.check)
        def visible_contents(self,cmd,c=self):
            """
            When an object has contents return them.
            """
            return c.contents

        @parent.visible_contents.before("not c.contents %s" % self.check)
        def visible_contents_fail_inventory(self,cmd,c=self):
            """
            Called when there are no contents.
            """
            raise pub.errors.InventoryError

        #
        #-------------------------------------------------------------
        
        #-------------------------------------------------------------
        # Get contents desc
        @parent.get_contents_desc.when("True %s" % self.check)
        def get_contents_desc(self,cmd,c=self):
            """
            Called when getting objects from a container.
            """
            out = [] 
            for item in c.contents:
                out.append(item.desc())
            return out

        #
        #-------------------------------------------------------------

# End Containment Interface
#---------------------------------------------------------------------
