from unittest import main, TestCase, TestSuite, makeSuite

import pub.pubcore as core


class TestEvent(TestCase):
    """
    Tests for Event 
    """
    def setUp(self):
        """Create some objects"""
        self.obj = core.BaseThing('shrubbery')
        self.event = core.Event(self.obj, 'self.x = 2')

    def testPerform(self):
        """check that perform really executes code"""
        self.event.Perform()
        assert self.event.x == 2

    def testRefersToObj(self):
        """check that event refers to obj"""
        assert self.event.RefersTo(self.obj) == True

    def testRefersToElse(self):
        """check that it doesn't refer to something else"""
        assert self.event.RefersTo(self.event) == False
        

class TestScheduler(TestCase):
    """
    Tests that try various things with the Scheduler. 
    """
    
    def setUp(self):
        """Create some objects used by several methods of TestScheduler."""
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

    

class TestParser(TestCase):
    """
    Run a parse test
    """

    def setUp(self):
        """create the parsing object"""
        self.par = core.Parser()
        self.str = 'We are the knights who say Ni!'

#   I'm not sure what to test on the parser yet.
        

class TestCommand(TestCase):
    """
    """

class TestVerb(TestCase):
    """
    """

class TestBaseThing(TestCase):
    """
    """

suitelist = [TestScheduler, TestEvent]
suite = TestSuite([makeSuite(suite) for suite in suitelist])

if __name__ == '__main__': main()

