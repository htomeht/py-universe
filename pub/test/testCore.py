from unittest import main, TestCase, TestSuite, makeSuite

import pub.pubcore as core

class TestScheduler(TestCase):
    """
    Tests that try various things with the Scheduler. 
    """
    
    def setUp(self):
        """Create some objects used by several methods of TestSceduler."""
        self.scheduler = core.Scheduler()
        self.obj = core.BaseThing('obj')
        self.event = core.Event(self.obj, "")

    def testTime(self):
        """Check that default time is set correctly"""
        assert self.scheduler.GetTime() == '12:00'
        
    def testHasEvent(self):
        """Check that the scheduler has an event if it's been given one."""
        self.scheduler.AddEvent(1, self.event)
        assert self.scheduler.HasEventFor(self.obj) == True

    def testTimeLapse(self):
        """Check that the Scheduler set's the right time after an update."""
        self.scheduler.AddEvent(1, self.event)
        self.scheduler.Update()
        assert self.scheduler.GetTime() == '12:01'
    
    def testHasNrEvents(self):
        """Check that the Scheduler has the correct amount of events"""
        self.scheduler.AddEvent(1, self.event)
        assert len(self.scheduler.events) == 1 

class TestEvent(TestCase):
    """
    """

class TestSceduler(TestCase):
    """
    """

class TestParser(TestCase):
    """
    """

class TestCommand(TestCase):
    """
    """

class TestVerb(TestCase):
    """
    """

class TestBaseThing(TestCase):
    """
    """

suite = TestSuite([makeSuite(TestScheduler)])

if __name__ == '__main__': main()

