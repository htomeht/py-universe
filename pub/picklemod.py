#    picklemod.py                8/26/96 JJS
#
#    This module pickles entire modules.  Handy when you're trying
#    to save/restore the state of a program which uses many module-
#    level variables.  Use it as follows:
#
#    picklemod.save( somefile, module1, module2, ...)
#        ...
#    picklemod.restore( somefile, module1, module2, ...)
#
#    Note that you can't save the module from which these calls
#    are made; if you figure out how to do this, let me know!
#----------------------------------------------------------------------

from types import *
import cPickle

exclude = [ModuleType, FunctionType, ClassType, BuiltinFunctionType,
       BuiltinMethodType, CodeType, FileType ]

def modvars(module):
    mdict = module.__dict__
    li = []
    for name, value in mdict.items():
        t = type(value)
        if t not in exclude and name[:2] != '__':
            li.append((name, value))
    return li

def save( f, *pModules ):
    p = cPickle.Pickler(f)
    for mod in pModules:
        p.dump( modvars(mod) )

def restore( f, *pModules ):
    u = cPickle.Unpickler(f)
    for mod in pModules:
        relist = u.load()
        for (name, value) in relist:
            setattr(mod, name, value)
