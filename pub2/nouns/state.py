# basic state machines

from protocols import Interface, advise

import pub.error

#---------------------------------------------------------------------
# Opening/Closing Interface 
#
class ICloseL(Interface):
    """
    Provides the close method.
    """

    def close(chain,cmd):
       """Method to run when the object is being closed."""

class IOpenL(Interface):
    """
    Serves as a way of effecting things which can be opened. 
    """

    def open(chain,cmd):
        """Method to run when the object is being opened."""


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

# End Open/Closing Interface
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# Pulling/Pushing Interface
#
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

#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Locking/Unlocking Interface
#

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

#
#---------------------------------------------------------------------

