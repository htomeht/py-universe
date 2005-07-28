#    picklemod.py                                         8/26/96 JJS
#
#   Copyright (C) 1996 Joe Strout 
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# CHANGELOG
#   2004-22/10: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
This module pickles entire modules.  Handy when you're trying
to save/restore the state of a program which uses many module-
level variables.  Use it as follows:

picklemod.save( somefile, module1, module2, ...)
...
picklemod.restore( somefile, module1, module2, ...)

Note that you can't save the module from which these calls
are made; if you figure out how to do this, let me know!
"""
#----------------------------------------------------------------------

# system imports
from types import *
import cPickle

# pub imports

# protocols imports


#--------------------------------------------------------------------

exclude = [ModuleType, FunctionType, ClassType, BuiltinFunctionType,
       BuiltinMethodType, CodeType, FileType ]

#--------------------------------------------------------------------
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
