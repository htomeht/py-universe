# testcomponents.py
# A preliminary version of component testing.
# There are several references to pub.errors, the errors that are 
# referred have primary names and most likely we will want to change these, I
# just wanted to give examples.
#
# I'm very unsure about exact implementation details for several things.
# This makes writing the tests kind of hard.
# 1. invoke: I feel that invoke should have 5 possible arguments of which only 
# three are needed. def invoke(obj, proto, meth, cmd = None, output = True)
# calling invoke without a cmd should simply try to do the action if possible.
# invoke(obj, IOpenable, 'open') should without checks open the door.
# the output variale can be set to suppress output. This might be a bit over the
# top but It's very convenient at least in testing and there might be more use.

# On another note I'm thinking of letting the Command object take a bigger place
# in evaluation of an action. ALL methods on a component should support (self,
# chain, cmd) and each object will have to determine how they will use cmd.

from unittest import main, TestCase, TestSuite, MakeSuite

import pub

from pub.core import invoke



#--------------------------------------------------------------------
# Test Objects



#--------------------------------------------------------------------
# Unit Tests

class TestICarriable(TestCase):
    """Test ICarriable:
        Subclass this class for each component that supports
        ICarriable.
    """

    def setUp(self):
        self.obj = pub.objs.Thing() #the test object
        
        self.room = pub.objs.Room() #a room in which everything takes place
        self.actor = pub.objs.Actor() #the test actor
        self.actor.moveTo(self.room) #move the actor to self.room
        
        self.cmd = pub.core.Command() #the Command object
        self.cmd.actor = self.actor #set the cmd.actor to actor
        
    def testGetDone(self):
        """check that you are able to pick up an object."""
        self.obj.moveTo(self.room)
        #Test it
        self._assert(invoke(self.obj, ICarriable, 'get', self.cmd) == True)
        
    
    def testGetFailSize(self):
        """check that you can't pick up too big items"""
        self.obj.moveTo(self.room)
        self.obj.size = 150
        #Test it
        try: invoke(self.obj, ICarriable, 'get', self.cmd)
        except pub.SizeError: pass
    
    def testDropDone(self):
        """check that you can put the object into your own container."""
        self.obj.moveTo(self.actor)
        #Test it
        self._assert(invoke(self.obj, ICarriable, 'drop', self.cmd) == True)

    def testDropFailNotHave(self):
        """check that you need to have the object in your inventory"""
        self.obj.moveTo(self.room)
        #Test it
        try: invoke(self.obj, ICarriable, 'drop', self.cmd)
        except pub.InventoryError: pass
       
    def testGiveDone(self):
        """check that you can give away a normal object"""
        self.obj.moveTo(self.actor)
        
        self.actor2 = pub.objs.Actor()
        self.actor2.moveTo(self.room)
        self.cmd.dirobj = self.actor2
        #Test it
        self._assert(invoke(self.obj, ICarriable, 'give', self.cmd) == True)


    def testGiveFailNotHave(self):
        """check that you need to have the object before giving it away"""
        self.obj.moveTo(self.room)
        
        self.actor2 = pub.objs.Actor()
        self.actor2.moveTo(self.room)
        self.cmd.dirobj = self.actor2
        #Test it
        try: invoke(self.obj, ICarriable, 'give', self.cmd)
        except pub.InventoryError: pass
                


#--------------------------------------------------------------------
class TestIContainer(TestCase):
    """Test IContainer"""

    
    def setUp(self):
        self.obj = pub.objs.Thing() #the test object
        self.normObj = pub.objs.Thing() #object that get's put in the container

        self.room = pub.objs.Room() #a room in which everything takes place
        self.actor = pub.objs.Actor() #the test actor
        self.actor.moveTo(self.room) #move the actor to self.room
        
        self.cmd = pub.core.Command() #the Command object
        self.cmd.actor = self.actor #set cmd.actor to self.actor
        self.cmd.dirobj = self.normObj
        
    def testCanContain(self):
        """check that the container can contain the direct object"""
        self._assert(invoke(self.obj, IContainer, 'canContain', self.cmd)
        == True)

    def testContainNoCheck(self):
        """move direct object into container"""
        self._assert(invoke(self.obj, IContainer, 'containNoCheck', self.cmd) 
        == True)

    def testGetContentsDesc(self):
        pass

    def testVisibleContents(self):
        pass
    
    def testPutDone(self):
        """check that you can put an object somewhere."""
        self.cmd.dirobj = self.normObj
        self._assert(invoke(self.obj, IContainer, 'put', self.cmd) == True)

    def testPutFailOnSelf(self):
        """check that you can't put an object into itself."""
        self.cmd.dirobj = self.obj
        try: invoke(self.obj, IContainer, 'put', self.cmd, False)
        except pub.errors.TargetError

    def testPutFailWrongSize(self):
        """check that you can't put too big an object in"""
        self.cmd.dirobj = actor1
        try: invoke(self.obj, IContainer, 'put', self.cmd, False)
        except pub.errors.SizeError

        
#--------------------------------------------------------------------
class TestIEdible(TestCase):
    """Test IEdible"""
    def setUp(self):
        self.obj = pub.objs.Thing()

        self.room = pub.objs.Room()
        self.actor = pub.objs.Actor()
        self.actor.moveTo(self.room)
        
        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor

    def testEatDone(self):
        """check that an object can be eaten."""
        self.obj.moveTo(self.actor)
        self._assert(invoke(self.obj, IEdible, 'eat', self.cmd, False)
        == True)

    def testDrinkDone(self):
        """check that the object can be drunk"""
        self.obj.moveTo(self.actor)
        self._assert(invoke(self.obj, IEdible, 'drink', self.cmd, False) 
        == True)



#--------------------------------------------------------------------
class TestIEnterable(TestCase):
    """
    Test IEnterable Components

    Needs to have another room into which the object connects.
    """

    def setUp(self):
        self.obj = pub.objs.Thing()
        
        self.room = pub.objs.Room()
        self.actor = pub.objs.Actor()
        self.actor.moveTo(self.room)
        
        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor
        
    def testGoDone(self):
        """check that we can enter the object"""
        self._assert(invoke(self.obj, IEnterable, 'go', self.cmd, False) 
        == True)

    def testGoFailClosed:
        """check that you can't pass through a closed door"""
        pass


#--------------------------------------------------------------------
class TestILockable(TestCase):
    """
    Test ILockable components:
        subclass and supply two things for each lock components you need to 
        test.
        
        self.component = pub.components.Lock()
        self.component.keys = [self.key]
    """

    def setUp(self):
        self.obj = pub.objs.Thing()
        self.key = pub.objs.Thing()
        
        self.room = pub.objs.Room()

        self.actor = pub.objs.Actor()
        self.actor.moveTo(self.room)
        self.key.moveTo(self.actor)

        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor
        self.cmd.withobj = self.key
        
    def testLockDone(self):
        """check that you can lock the obj"""
        invoke(self.obj, ILockable, 'unlock')
        self._assert(invoke(self.obj, ILockable, 'lock', self.cmd, False) 
        == True)

    def testLockFailNoKey(self):
        """check that not having the key returns an error"""
        invoke(self.obj, ILockable, 'unlock')
        self.key.moveTo(self.room)
        try: invoke(self.obj, ILockable, 'lock', self.cmd, False)
        except pub.errors.KeyError: pass

    def testLockFailLocked(self):
        """check that you can't lock what is locked"""
        invoke(self.obj, ILockable, 'lock')
        try: invoke(self.obj, ILockable, 'lock',self.cmd, False)
        except pub.errors.StateError: pass

    def testUnlockDone(self):
        """check that the object can be unlocked"""
        invoke(self.obj, ILockable, 'lock')
        self._assert(invoke(self.obj, ILockable, 'unlock', self.cmd, False) 
        == True)
            
    def testUnlockFailNoKey(self):
        """check that not having the key returns an error"""
        invoke(self.obj, ILockable, 'lock')
        self.key.moveTo(self.room)
        try: invoke(self.obj, ILockable, 'unlock', self.cmd, False)
        except pub.errors.KeyError: pass

    def testUnlockFailNotLocked(self):
        """check that you can't unlock what is not locked"""
        invoke(self.obj, ILockable, 'unlock')
        try: invoke(self.obj, ILockable, 'unlock', self.cmd, False)
        except pub.errors.StateError: pass


#--------------------------------------------------------------------
class TestIMobile(TestCase):
    """
    Test IMobile
    
    Just a frame as of yet
    """

    def setUp(self):
        self.obj = pub.objs.Thing()
        self.obj.addComponents([pub.components.Mobile]
        self.actor = pub.objs.Actor()
        
        self.cmd = pub.core.Command()

    def testFollowDone(self):
        self.cmd.actor = self.actor
        self._assert(invoke(self.obj, IMobile, 'follow', self.cmd, False) 
        == True)

    def testFollowFailNoTarget(self):
        pass                        

#---------------------------------------------------------------------
class TestIOpenable(TestCase):
    """Test IOpenable"""

    def setUp(self):
        self.obj = pub.objs.Thing()
                
        self.room = pub.objs.Room()
        
        self.actor = pub.objs.Actor()
        self.actor.moveTo(self.room)
        
        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor

    def testOpenDone(self):
        invoke(self.obj, IOpenable, 'close') # No cmdObject
        self._assert(invoke(self.obj, IOpenable, 'open', self.cmd, False)
        == True)

    def testOpenFailOpen(self):
        invoke(self.obj, IOpenable, 'open') # No cmdObject
        try: invoke(self.obj, IOpenable, 'open', self.cmd, False)
        except pub.errors.StateError: pass
        
    
    def testCloseDone(self):
        invoke(self.obj, IOpenable, 'open')
        self._assert(invoke(self.obj, IOpenable, 'close', self.cmd, False)
        == True)

    def testCloseFailClosed(self):
        invoke(self.obj, IOpenablel, 'close') # No cmdObject
        try: invoke(self.obj, IOpenable, 'close', self.cmd, False)
        except pub.errors.StateError


#--------------------------------------------------------------------
class TestISentience(TestCase):
    """
    Test ISentience
    
    Just a frame for now
    """

    def setUp(self):
        self.obj = pub.objs.Thing()
        self.normObj = pub.objs.Thing()

        self.room = pub.objs.Room()
        self.actor = pub.objs.Actor()
        self.actor.moveTo(self.room)
        self.actor2 = pub.objs.Actor()
        self.actor2.moveTo(self.room)

        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor
        self.cmd.dirobj = self.actor2

    def testAskDone(self):
        pass
    
    def testHearSpeechDone(self):
        pass
    
    def testReceiveDone(self):
        self._assert(invoke(self.obj, ISentience, 'receive', self.cmd, False)
        == True)

    def testTalkDone(self):
        pass

    def testTellDone(self):
        pass




#---------------------------------------------------------------------
class TestISwitchable(TestCase):
    """Test ISwitchable"""

    def setUp(self):
        self.obj = pub.objs.Thing()
        
        self.room = pub.Objs.Room()
        self.actor = pub.objs.Actor()
        self.actor.moveTo(self.room)

        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor
        
    def testActivateDone(self):
        invoke(self.obj, ISwitchable, 'deactivate') 
        self._assert(invoke(self.obj, ISwitchable, 'activate', self.cmd, False)
        == True)

    def testActivateFailActive(self):
        invoke(self.obj, ISwitchable, 'activate') 
        self._assert(invoke(self.obj, ISwitchable, 'activate', self.cmd, False)
        == True)
        

    def testDeActivateDone(self):
        invoke(self.obj, ISwitchable, 'activate') 
        self._assert(invoke(self.obj, ISwitchable, 'deactivate', self.cmd, False        ) == True)

    def testDeActivateFailActive(self):
        invoke(self.obj, ISwitchable, 'deactivate') 
        self._assert(invoke(self.obj, ISwitchable, 'deactivate', self.cmd, False        ) == True)
