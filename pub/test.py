#!/usr/bin/env python

from os import system
from os.path import dirname, join as pathjoin, split as pathsplit, abspath
from sys import path as pythonpath, argv, exit

#Establish some useful global variables.
#
#We assume that this program is located in the root directory of
#the instance of the pub package that we are testing.  Given
#that assumption, we find everything else by building paths.
#relative to that root.
#
pubdir = abspath(dirname(argv[0]))
pythonpath = pathsplit(pubdir)[0]
testdir = pathjoin(pubdir, 'test')
gamesdir = pathjoin(pubdir, 'games')

#This routine will run a particular test game and diff the output.
def runtest(name, gamepath, makeoutput):
    inputfile = pathjoin(testdir, '%s-input' % name)
    outputfile = pathjoin(testdir, '%s-output' % name)
    if makeoutput: testfile = outputfile
    else: testfile = pathjoin(testdir, '%s-testout' % name)
    system('PYTHONPATH=%s PUBTESTING=true python %s <%s >%s' % (pythonpath,
        gamepath, inputfile, testfile))
    system('rm pub.dat')
    if makeoutput: return
    system('diff %s %s' % (outputfile, testfile))
    system('rm %s' % testfile)


### Main program ###

#Set a flag if this is a run to generate the output files.
if len(argv)>1: makeoutput = argv[1]=='makeoutput'
else: makeoutput = False

#pubdemo test
pubdemo = pathjoin(pubdir, 'pubdemo.py')
runtest('pubdemo', pubdemo, makeoutput)

#Gredgar
gredgar = pathjoin(gamesdir, 'gredgar.py')
runtest('gredgar', gredgar, makeoutput)