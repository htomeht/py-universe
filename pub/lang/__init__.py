# pub.lang
#
# module provides an interface to all languages supported by pub.

# system imports
import os, os.path

# pub imports
import pub

#protocols imports

from protocols import adapt

#--------------------------------------------------------------------


def getListing(dir=None):
    """
    a function that returns a generator of language modules.
    Each item returned consists of a language name and a module.
    """
    
    lang = pub.interfaces.ILangMod
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
                yield i.name, i


# create language modules dictionary
mods = {}
for name, module in getListing():
    mods[name] = module
