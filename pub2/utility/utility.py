#   utility
"""
Collection of convenience functions used throughout the code.
"""
#    pubcore.py                                           6/01/98 JJS
#
#   Copyright (C) 1998 Joe Strout 
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
#
#   2002-5/10:
#    Terry Hancock
#       Added doc strings based on comments/code.
#
#   2004-21/01
#    Gabriel J
#       Went through the code adding more doc strings
#       Most based on curent comments but some on own experience
#
#   2004-22/10: 
#    Gabriel J
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
NOTE: Don't mess with this module unless you know what you're doing!

A number of utility functions. I'm a little
disturbed by things like "cap" which simply call
Python library functions -- not sure that we need
such a wrapper, as it likely increases the learning
curve for working with the code. (?)  On the other
hand, if used frequently enough, it might clarify
the code. If so, we need to add comments to define
what these things do.
"""
#----------------------------------------------------------------------

# system imports

import string
import types
import copy
import random
import re

# pub imports

import pub
from interfaces import IDynamicComponentRack, ILangMod 
import adapters
from constants import *


# protocols imports

from protocols import adapt, advise

#--------------------------------------------------------------------

cap = string.capitalize # function to capitalize a string

def isString(x):
    """
    function to determine whether something is a string
    """
    return type(x) == type('')

def isInstance(x):
    """
    function to determine whether it's an Instance
    """
    return type(x) == types.InstanceType

def isInt(x):
    """
    function to determine whether it's a number, or interpretable as one
    """
    try:
       string.atoi(x)
       return TRUE
    except: return type(x) == type(1)

def toInt(x):
    """
    function to force it to be a number
    """
    if isInt(x): return x
    try: return string.atoi(x)
    except: return 0


def stripPunctuation(str):
    """
    function to strip commas and periods from a string
    """
    for char in ",.!?": 
        str = str.replace(char, '')
    return str

#--------------------------------------------------------------------
# chainLinker -- Used by the component driven object system
#
def chainLinker(obj, proto, default=None):
    """
    A function that generates a chain
    used by, for instance invoke to get at all verb methods in an object.
    We can add more functionality here but it's probably best to keep it to 
    a minimum.

    obj can be either a list or something that provides IDynamicComponentRack.
    """
    
    # First loop through the obj to see if it has any components
    if type(obj) == type([]):
        for item in obj:
            adapted = adapt(item, IDynamicComponentRack, None)
            if adapted is not None:
                for com in adapted.components:
                    for adapted in chainLinker(com, proto):
                        yield adapted
    # Second try to adapt those components to the relevant protocol
    # This is the function that builds the chain even though it get's 
    # passed through the above.
    else:
        adapted = adapt(obj, proto, None)
        if adapted is not None:
            yield adapted
    
    # Third add a default method.
    if default is not None:
        yield default

            
#--------------------------------------------------------------------
# invoke -- used by the component driven object system
#
def invoke(obj, proto, meth, cmd=None, output=True):
    """
    invoke is used to run methods in an objects components that can be adapted
    to a interface of choice. It can also be used to generate output based on
    cmd, or to suppress it.

    Note: invoke is only used for verb methods. If you want to access other
    methods in other ways use chainLinker or other functions that might be
    provided.

    calling invoke without a cmd gives different responses depending on the
    actuall method called. All methods should be able to handle None as value.
    Mostly it will result in either an error or immediate execution.
    like: invoke(door, IOpen, 'open') will try to set the doors isOpen=True
    """
    room = obtain(obj,ILocatable).getRoom()
    actor = cmd.actor or None
    chain = chainLinker([obj,room,actor], proto) 
    # link a chain of methods in components 
    try: first = chain.next()
    except StopIteration: 
        # The method can't be found on the object, return an error
        raise pub.errors.ComponentError, "No such component can be found"
    
    try: getattr(first,meth)(chain,cmd)
    except StopIteration: # Check for the end of the chain.
                          # This means that the command was successful
                          
        if not output: raise pub.errors.NoOutput
        else: 
            return True # Tells the caller it has finished processing
                        # and that it was succesfull.
    
#--------------------------------------------------------------------
# lingo -- a language finder
#
def lingo(lang, cls, args = []):
    """
    method to access a couple of dictionaries and dig out a language
    and subsequently a specific class.

    lang should be a string like 'english' or 'swedish'
    cls should be a string containing something like 'parser' 
    """

    try: temp = pub.lang.mods[lang.lower()] # a language module
    except KeyError: raise pub.errors.PubError, "Language doesn't exist."

    if adapt(temp, ILangMod, None) != None: 
        try: out = temp.get[cls.lower()] # get the named class
        except KeyError: raise pub.errors.PubError, "Can't find class"
    
        return out(*args) # if args is not empty args will be passed. 


#--------------------------------------------------------------------
# obtain -- used by the component driven object system
#
def obtain(obj,proto,default=None):
    """
    Minimal interface to chainLinker that simply finds out if an object has a
    component that matches the protocol and returns it. If there are more or
    less than one an error is raised.
    """
    
    adapted = adapt(obj, IDynamicComponentRack, default)  
    if adapted is not None: 
        for com in adapted.components:
            com = adapt(com, proto, None)
            if com is not None: # The first match is returned
                return com 
            else: return False
                        
    else: return False
