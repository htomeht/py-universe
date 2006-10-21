# Defines components relating to agent behaviour, talking, reasoning and such.

from protocols import Interface, advise

import pub.error

#---------------------------------------------------------------------
# Asking  Interface 
# 
class IAskL(Interface):
    """
    provides an interface to asking the components owner.
    """

    def ask(chain,cmd):
        """Method to ask the being about a given subject."""


class Askable(Component):
    """
    A simple ask component that provides IAskL. If you want an object to
    be able to respond to questions. 
    """
        
    advise(instancesProvide = [IAskL])

    def __init__(self):
        Component.__init__(self)
        self.methods = ['ask']

        # Ask specifics 
        self.answers = {} # A dictionary with queries and answers

        self.__call__(self)
        
    def __call__(self,parent):
        """Register methods to parent."""
        
        parent.extend(self.methods, self)
                
        #-------------------------------------------------------------
        # Ask methods

        @parent.ask.when("c.answers.__contains__(cmd.aboutobj) %s" % self.check)
        def ask(self, cmd, c=self):

            cmd.tell(answer = c.answers[cmd.aboutobj])

        @parent.ask.before("not c.answers.__contains__(cmd.aboutobj) %s"\
        % self.check)
        def ask_fail_no_answer(self,cmd,c=self):
            
            raise pub.errors.NoAnswer

        #
        #-------------------------------------------------------------

# End Asking Interface
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Receiving Interface
#
class IReceiveL(Interface):
    """
    Provides receive method.
    This only matters when the receiver can react on being
    given something.
    """

    def receive(chain,cmd):
        """Method that listens for receive events"""

#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Talking Interface
#
class ITalkL(Interface):
    """ Provides the talk listener interface."""

    def talk(chain,cmd):
        """Method listening for talk events."""

class Talkable(Component):
    """
    Used to provide a talk interface. May be used to simplify 
    problem solving in place of ask and tell.
    """
        
    advise(instancesProvide = [ITalkL])

    def __init__(self):
        Component.__init__(self)
        self.methods = ['talk']

        # Talk specifics 
        self.answers = []

        self.__call__(self)
        
    def __call__(self,parent):
        """Register methods to parent."""
        
        parent.extend(self.methods, self)
                
        #-------------------------------------------------------------
        # Talk methods

        @parent.talk.when("c.answers %s" % self.check)
        def talk(self, cmd, c=self):

            cmd.tell(answer = c.answer[0]
            if c.answer.length > 1:
                c.answer = c.answer[1:]

        @parent.talk.before("not c.answers %s"\
        % self.check)
        def talk_fail_no_answer(self,cmd,c=self):
            
            raise pub.errors.NoAnswer

        #
        #-------------------------------------------------------------


#
#---------------------------------------------------------------------

#---------------------------------------------------------------------
# Telling Interface
#
class ITellL(Interface):
    """
    Provides tell method.
    """

    def tell(chain,cmd):
        """
        Method to tell the being about something. Usually used by cmd.tell
        to let a player know what has happened after a command was executed.
        """

class Tellable(Component):
    """"""

    advise(InstancesProvide = [ITellL]

    def __init__(self):
        """"""
        Component.__init__(self)

        self.methods = ['tell']

        self.__call__(self)

    def __call__(self,parent):
        
        parent.extend(self.methods)

        #-------------------------------------------------------------
        # Tell methods 
        
        @parent.tell.when("True %s" %s self.check)
        def tell(self,cmd,c=self):
            """
            This would likely be seen as a metaclass of
            sorts. Creating a general Tellable class would most likely
            just send information from the tell to a parser. In the case
            of an agent this parser could make it possible to react on 
            actions.
            """
            continue

        #
        #-------------------------------------------------------------


#
#---------------------------------------------------------------------

