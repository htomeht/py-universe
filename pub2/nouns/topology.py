# Components supporting topological models: simple container, rel/abs brick, room models, etc.

from protocols import Interface, advise

import pub.error

#---------------------------------------------------------------------
# Entering Interface
class IGoL(Interface):
    """
    Something that can be entered like a door, a portal or something 
    else entirely.
    """
    
    def go(chain,cmd):
        """Method to use an exit like it was intended."""

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

            raise pub.errors.ObjError, "This leads nowhere."

#
#---------------------------------------------------------------------

