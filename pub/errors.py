#errors.py
#
# pub.errors
# Contains the pub error system.


class PubError(Exception): # Basic pub error class subclass this to create more
                           # specific exceptions.


    """
    ObjError
    StateError
    InventoryError
    DestinationError
    SizeError
    TargetError
    """
    pass


class BailOutError(PubError): # exeption to raise to bail out of current
    pass                      # stack frame (used when restorin etc.)


class ComponentError(PubError): # exception to raise when components act up.
    pass                        # iow don't exist and the like.

class LanguageError(PubError): # exception raised when a language can't be 
    pass                       # found
