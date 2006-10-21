# components.py    contains components for pub            04/10/22 GJ
#
#   Copyright (C) 2004 Gabriel Jagenstedt
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
#  CHANGELOG
#
#   2006-07/08 TJH - Changed 'Symbol' to 'DynamicComponentRack' and
#                   moved it into components.py
#
#
#--------------------------------------------------------------------
""" 
This module provides components that are made into parts of an object. 
Add these components or instances thereof to objs with:
obj.addComponents(compo)
"""

# system imports

# pub imports
import pub

from interfaces import *
import defaults as d

# protocols imports
from protocols import advise


class DynamicComponentRack(object):
    """
    Base class of objects which use the dynamic components design.

    Currently this is the base class for Noun only, which is why it's
    in this file. It allows components to be defined dynamically,

    It is also the base class for Component.
    """

    advise(instancesProvide=[IDynamicComponentRack])

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

            elif type(com) == types.InstanceType \
            and isinstance(com, DynamicComponentRack): 
                self.components.append(com)
                com(self) # This registers the component with self.
                 self.addComponents(com.components) 
                # Add everything that this component provides.
                
            else: raise TypeError('Must be of type List, Class or Instance')

        # there might well be more issues to deal with but this is a start.

    def __iadd__(self, other):
        """
        Synonym to provide n += components syntax.
        """
        self.addComponents(other)

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

            if type(com) == list: 
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
                    self.delComponents(com.components)
                    # Remove everything provided by the component. 
            
            else: raise TypeError('Must be of type List, Class or Instance')

        def __isub__(self, other):
            """
            Synonym to provide simpler n -= components
            """
            self.delComponents(other)

        def extend(self,meth,component):
            """
            Extends the Object to enable dispatching methods.
            """

            if type(meth) == list:
                for x in meth:
                    extend(meth)

            if type(meth) == str:
                if not meth in dir(self)
                    exec """

@dispatch.generic()
def %(m)s(self,cmd): pass
self.%(m)s = %(m)s
""" % {'m':meth}
                    
            else : raise TypeError, "Must be of type List or String."
                

#---------------------------------------------------------------------
class Component(DynamicComponentRack):
    """
    Component is the base class for all components it holds basic 
    functionality for dealing with composites. However there is 
    currently nothing that differs between DynamicComponentRack and Component.
    """

    advise(instancesProvide=[IDynamicComponentRack])

    def __init__(self):
        DynamicComponentRack.__init__(self)
        
        check = "and self.components.__contains__(c)"


######################################################################
#
#
class TestComponent(Component):
    """A TestComopnent. Used to check adation and stuff."""

    advise(instancesProvide=[ITest])
    def __init__(self):
        Component.__init__(self)    

        self.methods = ['test']

        self(self)

    def __call__(self,parent):

        parent.extentd(self.methods)

        @parent.test.when("cmd is 'test'")
        def test(self,cmd,c=self):
            print 'Testing finished.'
