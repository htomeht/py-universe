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
# chain).

from unittest import main, TestCase, TestSuite, makeSuite

import pub

from pub.pubcore import invoke



#--------------------------------------------------------------------
# Test Objects



#--------------------------------------------------------------------
#Listener Tests
# Here we test components that support listeners.
# like door supports IOpenL

class TestListener(TestCase):
    """
    Main test for listeners.
    Provides a setup that sets everything we might need for a generic test.
    """

    def setUp(self):
        self.obj = pub.objs.Thing()

        self.room = pub.objs.Room()
        self.actor = pub.objs.Actor()

        self.obj.moveTo(self.room)

        self.cmd = pub.core.Command()
        self.cmd.actor = self.actor

   #XXX: There should be a few generic tests here that check what happens if the
   # object doesn't exist, if you can't see it or if the word is unknown to the
   # engine.

#--------------------------------------------------------------------
class TestAskL(TestListener):
    """
    A testcase for objects that support or have components that support the ask
    listener.
    Subclass for objects that support the ask listener.
    Also provide a topic named "shrubbery".
    """

    def setUp(self):
        TestListener.setUp(self)

        self.cmd.aboutobj = 'shrubbery'
        
    def testAskDone(self):
        """check that we can ask about things in the topics"""

        self.assert_(invoke(self.obj, IAskL, 'ask', self.cmd, False))
        

    def testAskFailNoAboutObj(self):
        """check that not having an aboutobj raises an error"""

        self.cmd.aboutobj = ''
        try: invoke(self.obj, IAskL, 'ask', self.cmd, False)
        except pub.errors.ObjError: pass
        else: self.fail("Expected an ObjError")


#--------------------------------------------------------------------
class TestCloseL(TestListener):
    """
    Tests for objects and components that support the ICloseL
    Subclass for components that support the close listener.
    Always name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)
        
        self.com.isOpen = True
        
    def testCloseDone(self):
        """check that the component can be closed, given that it is open"""
        self.assert_(invoke(self.obj, ICloseL, 'close', self.cmd, False) )

    def testCloseFailOpen(self):
        """check that the test fails if the object is closed"""
        self.com.isOpen = False
        try: invoke(self.obj, ICloseL, 'close', self.cmd, False)
        except pub.errors.StateError: pass
        else: self.fail("Expected a StateError")
        

#--------------------------------------------------------------------
class TestDrinkL(TestListener):
    """
    Tests for components that support IDrinkL
    
    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)


    def testDrinkDone(self):
        """check that we can drink the object"""
        self.assert_(invoke(self.obj, IDrinkL, 'drink', self.cmd, False) )


#--------------------------------------------------------------------
class TestDropL(TestListener):
    """
    Tests for components that support IDropL
    
    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

        self.obj.moveTo(self.actor)

    def testDropDone(self):
        """check that the object can be dropped under normal circumstances"""

        self.assert_(invoke(self.obj, IDrinkL, 'drink', self.cmd, False) )

    def testDropFailNoInventory(self):
        """check that you can't drop what you don't have"""
        self.obj.moveTo(self.actor.getRoom())
        try: invoke(self.obj, IDropL, 'drop', self.cmd, False)
        except pub.errors.InventoryError: pass
        else: self.fail("Expected an InventoryError")


#--------------------------------------------------------------------
class TestEatL(TestListener):
    """
    Tests for components that provide IEatL

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)


    def testEatDone(self):
        """check that the object can be eaten"""

        self.assert_(invoke(self.obj, IEatL, 'eat', self.cmd, False) )


#--------------------------------------------------------------------
class TestExamineL(TestListener):
    """
    Tests for components that provide IExamineL

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testExamineDone(self):
        """check that the object can be examined"""

        self.assert_(invoke(self.obj, IExamineL, 'examine', self.cmd, False) )


#--------------------------------------------------------------------
class TestFollowL(TestListener):
    """
    Tests for IFollowL components
    
    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

        
    def testFollowDone(self):
        """check that an object can be followed"""
        self.assert_(invoke(self.obj, IFollowL, 'follow', self.cmd, False) )


#--------------------------------------------------------------------
class TestGetL(TestListener):
    """
    Tests for IGetL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testGetDone(self):
        """checks that you can pick up the object"""

        self.assert_(invoke(self.obj, IGetL, 'get', self.cmd, False) )

    #XXX: Tests for getting to big items, or items that simply won't be able to
    # pick up.


#--------------------------------------------------------------------
class TestGiveL(TestListener):
    """
    Tests for IGiveL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

        self.a2 = pub.objs.Actor()
        self.cmd.toObj = self.a2

    def testGiveDone(self):
        """check that we can give away the object"""
        self.assert_(invoke(self.obj, IGiveL, 'give', self.cmd, False) )

    def testGiveFailNoToObj(self):
        """check that having no toObj raises an error"""
        self.cmd.toObj = ''
        try: invoke(self.obj, IGiveL, 'give', self.cmd, False) 
        except pub.errors.ObjError: pass
        else: self.fail("Expected an ObjError")


#--------------------------------------------------------------------
class TestGoL(TestListener):
    """
    Tests for IGoL components 

    Subclass for component testting
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testGoDone(self):
        """checks that an actor can go the object"""

        self.assert_(invoke(self.obj, IGoL, 'go', self.cmd, False) )

    def testGoFailNoDest(self):
        """checks that you get an error when the exit doesn't have a room
        reference"""

        self.obj.dest = None

        try: invoke(self.obj, IGo, 'go', self.cmd, False)
        except pub.errors.DestinationError: pass
        else: self.fail('Expected a DestinationError')
    
#--------------------------------------------------------------------
class TestLockL(TestListener):
    """
    Tests for ILockL components

    Subclass for component testing
    name the component self.com

    When subclassing for testing create a keyobject and move it to the actor
    self.key = pub.objs.Thing()
    self.key.moveTo(self.actor)

    also make sure the lock knows about the key.
    self.com.keys = [self.key]
    
    """

    #XXX: Add a key
    
    def setUp(self):
        TestListener.setUp(self)

        self.com.isLocked = False

    def testLockDone(self):
        """checks that the object can be locked"""
        self.assert_(invoke(self.obj, ILockL, 'lock', self.cmd, False) )

    def testLockFailLocked(self):
        """checks that a locked object returns an error if locked."""
        self.com.isLocked = True

        try: invoke(self.obj, ILockL, 'lock', self.cmd, False)
        except pub.errors.StateError: pass
        else: self.fail("Expected a StateError")


#--------------------------------------------------------------------
class TestILookL(TestListener):
    """
    Tests for ILookL components
    
    Subclass for component testing
    name the component self.com.
    """

    def setUp(self):
        TestListener.setUp(self)

    def testLookDone(self):
        """check that the object can be looked upon"""
        
        self.assert_(invoke(self.obj, ILookL, 'look', self.cmd, False) )


#--------------------------------------------------------------------
class TestOpenL(TestListener):
    """
    Tests for IOpenL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

        self.com.isOpen = False

    def testOpenDone(self):
        """checks that the object can be opened"""

        self.assert_(invoke(self.obj, IOpenL, 'open', self.cmd, False) )


#--------------------------------------------------------------------
class TestIPullL(TestListener):
    """
    Tests for IPullL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testPullDone(self):
        """checks that the object can be pulled."""
        self.assert_(invoke(self.obj, IPullL, 'pull', False) )

    #XXX: Tests for making sure you can't pull too heavy objects, or objects
    # that are in other ways stuck.

    
#--------------------------------------------------------------------
class TestPushL(TestListener):
    """
    Tests for IPushL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)


    def testPushDone(self):
        """checks that the object can be pushed."""
        self.assert_(invoke(self.obj, IPushL, 'push', False) )
                        
    #XXX: Test that check you can't push heavy objects.

#--------------------------------------------------------------------
class TestPutL(TestListener):
    """
    Tests for IPutL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

        self.cont = pub.objs.Container()
        self.cmd.inobj = self.cont
        
    def testPutLDone(self):
        """checks that you can put the object in another."""
        self.assert_(invoke(self.obj, IPutL, 'put', False) )

    #XXX: Tests that check you need an indirect object.


#--------------------------------------------------------------------
class TestTalkL(TestListener):
    """
    Tests for ITalkL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

        self.actor2 = pub.objs.Actor()

    def testTalkLDone(self):
        """checks that you can talk"""
        self.assert_(invoke(self.obj, ITalkL, 'talk', False) )

##XXX: Write tests for talking to objects


#--------------------------------------------------------------------
class TestTellL(TestListener):
    """
    Tests for ITellL components

    Subclass for component testing
    name the component self.com
    
    provide a topic named 'shrubbery' 
    """

    def setUp(self):
        TestListener.setUp(self)

        self.actor2 = pub.objs.Actor()
        
        self.cmd.dirobj = self.actor2
        self.cmd.aboutobj = 'shrubbery'
        
    def testTellDone(self):
        """checks that you can tell actors about shrubberies"""
        self.assert_(invoke(self.obj, ITellL, 'tell', self.cmd, False) )

#XXX: Add tests for telling actors to do things


#--------------------------------------------------------------------
class TestReceiveL(TestListener):
    """
    Tests for IReceiveL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testReceiveDone(self):
        """test that you can receive an object."""
        
        self.assert_(invoke(self.obj, IReceiveL, 'receive', self.cmd, False) )


#--------------------------------------------------------------------
class TestRemoveL(TestListener):
    """
    Tests for IRemoveL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testRemoveDone(self):
        """tests that an object can be removed"""

        self.assert_(invoke(self.obj, IRemoveL, 'remove', self.cmd, False) )


#--------------------------------------------------------------------
class TestTurnL(TestListener): 
    """
    Tests for ITurnL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testTurnL(self):
        """check that an object can be turned."""

        self.assert_(invoke(self.obj, ITurnL, 'turn', self.cmd, False) )


#--------------------------------------------------------------------
class TestIUnlockL(TestListener):
    """
    Tests for IUnlockL components

    Subclass for component testing
    name the component self.com
    
    When subclassing for testing create a keyobject and move it to the actor
    self.key = pub.objs.Thing()
    self.key.moveTo(self.actor)

    also make sure the lock knows about the key.
    self.com.keys = [self.key]
    """
    

    #XXX: Add a key

    def setUp(self):
        TestListener.setUp(self)

        self.obj.isLocked = True

    def testUnlockLDone(self):
        """check that an object can be unlocked."""

        self.assert_(invoke(self.obj, IUnlockL, 'unlock', self.cmd, False) )

    def testUnlockFailNotLocked(self):
        """check that unlocking a not locked object will result in an error"""
        
        self.obj.isLocked = False

        try: invoke(self.obj, IUnlockL, 'unlock', self.cmd, False)
        except pub.errors.StateError: pass
        else: self.fail("Expected a StateError")

#--------------------------------------------------------------------
class TestIWearL(TestListener):
    """
    Tests for IWearL components

    Subclass for component testing
    name the component self.com
    """

    def setUp(self):
        TestListener.setUp(self)

    def testWearL(self):
        """check that an object can be worn."""

        self.assert_(invoke(self.obj, IWearL, 'wear', self.cmd, False) )



#-------------------------------------------------------------------- 
# Unit Tests
#  These tests are really not finished, just there for the sake of it.
#
#  Bla bla
#
class TestICarriable(TestCase):
    """
    Test ICarriable:
    
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
        self.assert_(invoke(self.obj, ICarriable, 'get', self.cmd) )
        
    
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
        self.assert_(invoke(self.obj, ICarriable, 'drop', self.cmd) )

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
        self.assert_(invoke(self.obj, ICarriable, 'give', self.cmd) )


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
        self.assert_(invoke(self.obj, IContainer, 'canContain', self.cmd) )

    def testContainNoCheck(self):
        """move direct object into container"""
        self.assert_(invoke(self.obj, IContainer, 'containNoCheck', self.cmd) 
        )

    def testGetContentsDesc(self):
        pass

    def testVisibleContents(self):
        pass
    
    def testPutDone(self):
        """check that you can put an object somewhere."""
        self.cmd.dirobj = self.normObj
        self.assert_(invoke(self.obj, IContainer, 'put', self.cmd) )

    def testPutFailOnSelf(self):
        """check that you can't put an object into itself."""
        self.cmd.dirobj = self.obj
        try: invoke(self.obj, IContainer, 'put', self.cmd, False)
        except pub.errors.TargetError: pass

    def testPutFailWrongSize(self):
        """check that you can't put too big an object in"""
        self.cmd.dirobj = actor1
        try: invoke(self.obj, IContainer, 'put', self.cmd, False)
        except pub.errors.SizeError: pass


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
        self.assert_(invoke(self.obj, ILockable, 'lock', self.cmd, False) )

    def testLockFailNoKey(self):
        """check that not having the key returns an error"""
        invoke(self.obj, ILockable, 'unlock')
        self.key.moveTo(self.room)
        try: invoke(self.obj, ILockable, 'lock', self.cmd, False)
        except pub.errors.InventoryError: pass

    def testLockFailLocked(self):
        """check that you can't lock what is locked"""
        invoke(self.obj, ILockable, 'lock')
        try: invoke(self.obj, ILockable, 'lock',self.cmd, False)
        except pub.errors.StateError: pass

    def testUnlockDone(self):
        """check that the object can be unlocked"""
        invoke(self.obj, ILockable, 'lock')
        self.assert_(invoke(self.obj, ILockable, 'unlock', self.cmd, False) )
            
    def testUnlockFailNoKey(self):
        """check that not having the key returns an error"""
        invoke(self.obj, ILockable, 'lock')
        self.key.moveTo(self.room)
        try: invoke(self.obj, ILockable, 'unlock', self.cmd, False)
        except pub.errors.InventoryError: pass

    def testUnlockFailNotLocked(self):
        """check that you can't unlock what is not locked"""
        invoke(self.obj, ILockable, 'unlock')
        try: invoke(self.obj, ILockable, 'unlock', self.cmd, False)
        except pub.errors.StateError: pass


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
        self.assert_(invoke(self.obj, IOpenable, 'open', self.cmd, False) )

    def testOpenFailOpen(self):
        invoke(self.obj, IOpenable, 'open') # No cmdObject
        try: invoke(self.obj, IOpenable, 'open', self.cmd, False)
        except pub.errors.StateError: pass
        
    
    def testCloseDone(self):
        invoke(self.obj, IOpenable, 'open')
        self.assert_(invoke(self.obj, IOpenable, 'close', self.cmd, False) )

    def testCloseFailClosed(self):
        invoke(self.obj, IOpenablel, 'close') # No cmdObject
        try: invoke(self.obj, IOpenable, 'close', self.cmd, False)
        except pub.errors.StateError: pass


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
        self.assert_(invoke(self.obj, ISentience, 'receive', self.cmd, False) )

    def testTalkDone(self):
        pass

    def testTellDone(self):
        pass


suitelist = []
suite =  TestSuite([makeSuite(suite) for suite in suitelist])
