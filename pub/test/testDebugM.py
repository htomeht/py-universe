from unittest import main, TestCase, TestSuite, makeSuite
from os import system
from os.path import join as pathjoin, split as pathsplit, dirname, abspath
from sys import argv, path as pythonpath 

import pub.debug

pubdir = abspath(dirname(argv[0]))
gamesdir = pathjoin(pubdir, 'games')
testdir = pathjoin(pubdir, 'test')
PYTHONPATH = pathsplit(pubdir)[0]
pythonpath.insert(0, PYTHONPATH)


def runtest(name, gamepath, makeoutput):
    """
    This is basicly the same function that we have in test.py used
    to run integration tests with one small difference.
    I've removed the code to delete a save.
    """
    inputfile = pathjoin(testdir, '%s-input' % name)
    outputfile = pathjoin(testdir, '%s-output' % name)
    if makeoutput: testfile = outputfile
    else: testfile = pathjoin(testdir, '%s-testout' % name)
    system('PYTHONPATH=%s PUBTESTING=true python %s <%s >%s' % (PYTHONPATH,
        gamepath, inputfile, testfile))
    if makeoutput: return
    system('diff %s %s' % (outputfile, testfile))
    system('rm %s' % testfile)

if len(argv)>1: makeoutput = argv[1]=='makeoutput'
else: makeoutput = False


class TestDebugVerbs(TestCase):
    """Test if our debugging verbs do what we expect
    """
    def testVerbs(self):
        """For the case of testing debugging verbs we use
        gredgar, we could just as well use any other game. 
        """
        
        pubdemo= pathjoin(pubdir, 'pubdemo.py')           
        runtest('debug', pubdemo, makeoutput)
        


suite = TestSuite([makeSuite(TestDebugVerbs)])

if __name__ == '__main__': main()
