#!/usr/bin/env python

from os import system, listdir
from os.path import join as pathjoin, split as pathsplit, dirname, abspath
from sys import path as pythonpath, argv, exit

#Establish some useful global variables.
#
#We assume that this program is located in the root directory of
#the instance of the pub package that we are testing.  Given
#that assumption, we find everything else by building paths.
#relative to that root.
#
pubdir = abspath(dirname(argv[0]))
PYTHONPATH = pathsplit(pubdir)[0]
pythonpath.insert(0, PYTHONPATH)
testdir = pathjoin(pubdir, 'test')
gamesdir = pathjoin(pubdir, 'games')

#This routine will run a particular test game and diff the output.
def runtest(name, gamepath, makeoutput):
    inputfile = pathjoin(testdir, '%s-input' % name)
    outputfile = pathjoin(testdir, '%s-output' % name)
    if makeoutput: testfile = outputfile
    else: testfile = pathjoin(testdir, '%s-testout' % name)
    system('PYTHONPATH=%s PUBTESTING=true python pubrun %s <%s >%s' % (PYTHONPATH,
        gamepath, inputfile, testfile))
    system('rm pub.dat')
    if makeoutput: return
    system("sed -e 's/0x.*c//' %s > diff1" % testfile)
    system("sed -e 's/0x.*c//' %s > diff2" % outputfile)
#    system('diff %s %s' % (outputfile, testfile))
    system('diff diff1 diff2')
    system('rm %s diff1 diff2' % testfile)


### Main program ###

#Set a flag if this is a run to generate the output files.
if len(argv)>1: makeoutput = argv[1]=='makeoutput'
else: makeoutput = False

#First, run the unit tests.
from unittest import TextTestRunner, TestSuite 
tests = TestSuite()
for candidate in listdir(testdir):
    print candidate
    if candidate[:4] == 'test' and candidate[-3:]=='.py':
        print candidate
        modname = candidate[:-3]
        testmod = __import__('pub.test.%s' % modname)
        repr(getattr(testmod.test,modname))
        tests.addTest(getattr(testmod.test,modname).suite)
TextTestRunner().run(tests)
print
print

#Check for tabs.
print "Checking for tabs in python source files.  Output is bad:"
system('grep "\t" *.py')
print "Done looking for tabs.\n\n"


#Now run the integration tests.
print "Running Integration Tests.  No output is good output:"

#pubdemo test
pubdemo = pathjoin(pubdir, 'pubdemo.py')
runtest('pubdemo', pubdemo, makeoutput)

#Gredgar
gredgar = pathjoin(gamesdir, 'gredgar.py')
runtest('gredgar', gredgar, makeoutput)

#Debugging test
debug = pathjoin(pubdir, 'pubdemo.py')
runtest('debug', debug + ' -d', makeoutput)


print "\nTesting Complete."
