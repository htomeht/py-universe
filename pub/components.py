#XXX: Write a testComponent, needs a Component class first.

from pubcore import Symbol
from interfaces import *

from protocols import advise

class Component(Symbol):
    """
    Component is the base class for all components it holds basic 
    functionality for dealing with composites.
    """

    advise(instancesProvide=[ISymbol])
    

#--------------------------------------------------------------------
class Ask(Component):
    """
    A simple ask component that provides IAskL. If you want an object to
    be able to respond to questions.
    """
        
    advise(instancesProvide = [IAskL])

    def __init__(self, obj, proto):
        self.obj = obj
        
    def ask(self, chain, cmd):
        """takes a chain object and a command object"""

        
    
