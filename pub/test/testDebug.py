from unittest import main, TestCase, TestSuite, makeSuite
import pub


class TestDebug(TestCase):

    
    def setUp(self):
        #this is one reason global variables are a bad idea:
        #they make unit testing difficult.
        reload(pub)

    def testDebugOn(self):
        self.failIf(pub.debugging)
        pub.Debugging()
        self.failUnless(pub.debugging)

    def testDebugOnLower(self):
        self.failIf(pub.debugging)
        pub.Debugging('on')
        self.failUnless(pub.debugging)

    def testDebugOnUpper(self):
        self.failIf(pub.debugging)
        pub.Debugging('ON')
        self.failUnless(pub.debugging)

    def testDebugOnMixed(self):
        self.failIf(pub.debugging)
        pub.Debugging('On')
        self.failUnless(pub.debugging)

    def testDebugOff(self):
        self.failIf(pub.debugging)
        pub.Debugging('off')
        self.failIf(pub.debugging)

    def testDebugOnOffLower(self):
        self.failIf(pub.debugging)
        pub.Debugging('on')
        self.failUnless(pub.debugging)
        pub.Debugging('off')
        self.failIf(pub.debugging)

    def testDebugOnOffUpper(self):
        self.failIf(pub.debugging)
        pub.Debugging('on')
        self.failUnless(pub.debugging)
        pub.Debugging('OFF')
        self.failIf(pub.debugging)        

    def testDebugOnOffMixed(self):
        self.failIf(pub.debugging)
        pub.Debugging('on')
        self.failUnless(pub.debugging)
        pub.Debugging('Off')
        self.failIf(pub.debugging)        


suitelist = []
suite = TestSuite([makeSuite(suite) for suite in suitelist])

if __name__ == '__main__': main()
