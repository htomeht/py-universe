#pub.langs

import pub

import os, os.path

from protocols import adapt


def getListing(dir=None):
    """
    a function that returns a generator of language modules.
    """
    
    lang = pub.interfaces.ILang
    if dir == None: 
        
        pubdir = os.path.split(os.path.abspath(pub.__file__))[0]
        dir = os.path.join(pubdir, "lang/")
        if pub.debugging: print dir
    
    dirlist = os.walk(dir).next()[1] # a list of dirs
    if pub.debugging: print dirlist

    
    for item in dirlist:
        if pub.debugging: print item
        if item[-4:] == 'Lang':
            x = "pub/lang/"+item
            if pub.debugging: print x
            i = adapt(__import__(x, globals, locals), lang, None)

            if i != None:
                if pub.debugging: print i
                yield i


#listing = [item for item in getListing()]
