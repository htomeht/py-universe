# basic state machines

from protocols import Interface, advise

import pub.errors
from pub.component import Component

#---------------------------------------------------------------------
# Opening/Closing Interfaces
#

# Interfaces
class ICloseL(Interface):
    """
    Provides the close method.
    """

    def close(chain,cmd):
       """Method to run when the object is being closed."""

class IOpenL(Interface):
    """ Serves as a way of affecting things which can be opened. """

    def open(chain,cmd):
        """Method to run when the object is being opened."""


# Components
class Openable(Component):
    """
    Give the object the ability to be opened.
    Standard component that provides the open/close state.
    """

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

        #-------------------------------------------------------------
        # Close methods
        @parent.close.when("True %s" % self.check)
        def close(self,cmd,c=self):
            """Tries to close itself."""
           
            c.isOpen = False

        @parent.close.before("c.isOpen == False %s" % self.check)
        def close_fail_closed(self,cmd,c=self):
            """Called when component is already closed."""

            raise pub.errors.StateError

        #
        #-------------------------------------------------------------
        
        #-------------------------------------------------------------
        # Open methods
        @parent.open.when("True %s" % self.check)
        def open(self,cmd,c=self):
            """Tries to open itself."""

            c.isOpen = True

        @parent.open.before("c.isOpen == True %s" % self.check)

        def open_fail_open(self,cmd,c=self):
            """Called when component is already opened."""
            
            raise pub.errors.StateError

        #
        #-------------------------------------------------------------

# End Open/Closing Interface
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# Pulling/Pushing Interface
#

# Interfaces
class IPullL(Interface):
    """
    Provides an interface to pulling for components
    Make a components support this if you want it to react to pulling.
    Can be used in a string, something to be moved and so on.    
    """

    def pull(chain,cmd):
        """Method that listens for pull events"""

class IPushL(Interface):
    """
    Provides an interface to pushing for components.
    Make a component support this if you want the push verb to be able to affect
    the object in a special way.
    Can be used for a lever, a button, a character.
    """

    def push(chain,cmd):
        """Method that listens for push events"""

# Components
class Pullable(Component):
    """Makes an item possible to pull."""

    advise(InstancesProvide = [IPullL]

    def __init__(self):
        Component.__init__(self)

        self.methods = ['pull']

        #Pullable specifics
        self.pulled = False

        self.__call__(self)

    def __call__(self,parent):
        """Register methods to parent."""

        parent.extend(self.methods)

        #-------------------------------------------------------------
        # Pull methods
        @parent.pull.when("True %s" %s self.check)
        def pull(self,cmd,c=self):
            """Pull at this object. It is normaly a lever."""

            c.pulled = True

        @parent.pull.before("c.pulled == True %s" % self.check)
        def pull_fail_pulled(self,cmd,c=self):
            raise pub.errors.StateError

        #
        #-------------------------------------------------------------

    
class Pushable(Component):
    """Makes an item possible to push."""
     
    advise(InstancesProvide = [IPushL]

    def __init__(self):
        Component.__init__(self)

        self.methods = ['pull']

        #Pushable specifics
        self.pushed = False

        self.__call__(self)

    def __call__(self,parent):
        """Register methods to parent."""
        
        parent.extend(self.methods)
    
        #-------------------------------------------------------------
        # Pushing methods
        @parent.push.when("True %s" %s self.check)
        def push(self,cmd,c=self):
            """"""
            
            self.pushed = True

        #
        #-------------------------------------------------------------

# End Pushing/Pulling interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Locking/Unlocking Interface
#

# Interfaces
class ILockL(Interface):
    """
    Used on objects which wish to be lockable.
    Components could be combination locks, key locks, password locks and so on.
    """

    def lock(chain,cmd):
       """Method to lock the lock"""


class IUnlockL(Interface):
    """
    provides Unlock method
    """
    
    def unlock(chain,cmd):
       """Method to unlock the lock"""


# Components
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
        """Register methods to parent."""

        parent.extend(self.methdods)

        #-------------------------------------------------------------
        # Lock methods

        @parent.lock.when("True %s" % self.check)
        def lock(self,cmd,c=self):
            """Method to change isLocked to True if possible."""

            for key in self.keys:
                if cmd.actor.has(key):
                    self.isLocked = True

        @parent.lock.before("c.isLocked = True %s" % self.check)
        def lock_fail_locked(self,cmd,c=self):
            """Fail because already locked."""

            raise pub.errors.LockError
        
        #
        #-------------------------------------------------------------
        
        #-------------------------------------------------------------
        # Unlock methods

        @parent.unlock.when("True %s" % self.check)
        def unlock(self,cmd,c=self):
            """Method to change isLocked to False if possible."""

            for key in self.keys:
                if cmd.actor.has(key):
                    self.isLocked = False

        @parent.unlock.before("c.isLocked = False %s" % self.check)
        def unlock_fail_unlocked(self,cmd,c=self):
            """Fail because not locked."""

            raise pub.errorsLockError

        #
        #-------------------------------------------------------------

        #-------------------------------------------------------------
        # Open methods

        @parent.open.before("c.isLocked = True %s" % self.check)
        def open_fail_locked(self,cmd,c=self):
            """The lock is locked."""

            raise pub.errors.LockError

        #
        #-------------------------------------------------------------

#
#---------------------------------------------------------------------
