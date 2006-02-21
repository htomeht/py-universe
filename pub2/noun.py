# (C) 1996 Joe Strout, 2004 Gabriel Jagenstedt, 2006 Terry Hancock
#   noun
"""
Base classes for all nouns and noun registry.
"""

#objs.py
#
#
#--------------------------------------------------------------------
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

# Gettext based I18N:
# from gettext ...

def _(s):
    return s

from interfaces import *
from protocols import advise

import locale


import types

#----------------------------------------------------------------------
# Symbol -- Base class for nouns and components -- used by the
#           component based object system
#
class Symbol:
    """
    Symbol:
        Base class of componets and nouns/things.
        It contains methods and variables to handle components 
        mostly.
    """

    advise(instancesProvide=[ISymbol])

    def __init__(self):
        
        self._components = [] # PRIVATE variable
                              # a list of classes or instances
                              # that should be added to the object when
                              # initialized.

        self.components = [] # a list that contains references 
                             # to components after it has been initialized.
                             # this is the variable that the outside uses.
        
        self.addComponents(self._components) # Add the components
            

    def addComponents(self,com):
        """
        method that adds components to the components list.
        checks three possible ways it can be called, with either a list, a class
        or an instance. Only when called with an instance does the component get
        added to the list, in other cases it's converted into an instance and
        resent to addComponents
        """

        
        if com:

            if type(com) == types.ListType:
                for each in com: self.addComponents(each)
                
            elif type(com) == types.ClassType: 
                self.addComponents(com())

            elif type(com) == types.InstanceType and isinstance(com, Symbol): 
                self.components.append(com)
            
            else: raise TypeError('Must be of type List, Class or Instance')

        # there might well be more issues to deal with but this is a start.

    def delComponents(self,com):
        """
        Can be called in the same way as addComponents, with a list, class or
        instance. However dealing with deleting componets is a bit harder.
        When given a list the list is looped through and calls to delComponents
        are made.
        When given a class all classinstances are deleted.
        When given an instance just that instance is removed.        
        """

        if com:

            if type(com) == types.ListType: 
                for each in com: self.delComponents(each)

            elif type(com) == types.ClassType: 
                delete = []
                for item in self.components:
                    if item.__class__ == com:
                        delete.append(item)

                #delete all occurences of the class
                for item in delete:
                    self.components.remove(item)
                del delete        

            elif type(com) == types.InstanceType: 
                if com in self.components:
                    self.components.remove(com)
            
            else: raise TypeError('Must be of type List, Class or Instance')

class Noun(Symbol):
    """
    The most basic of objects. 
    Noun doesn't provide any real methods.
    """

    advise(instancesProvide=[INoun]) 

    def __init__(self, names=[]):
        Symbol.__init__(self)       
        
        #synonyms and name
        self.synonyms = [x.lower() for x in names]
        self.name = self.synonyms[0]

        # add synonyms to the parser's list of nouns
        # Well we know this won't be the way to handle nouns anymore =)
        #for n in self.synonyms:
        #    if n not in pubcore.nouns: pubcore.nouns.append(n)
        
