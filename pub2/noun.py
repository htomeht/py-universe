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

        
        if com and type(com) == types.ListType:
            for each in com: self.addComponents(each)
            
        if type(com) == types.ClassType: 
            self.addComponents(com())

        if type(com) == types.InstanceType and isinstance(com, Symbol): 
            self.components.append(com)
        
        else: raise TypeError('%com must be of type List, Class or Instance')

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

        if type(com) == types.ListType: 
            for each in com: self.delComponents(each)

        if type(com) == types.ClassType: 
            delete = []
            for item in self.components:
                if item.__class__ == com:
                    delete.append(item)

            #delete all occurences of the class
            for item in delete:
                self.components.remove(item)
            del delete        

        if type(com) == types.InstanceType: 
            if com in self.components:
                self.components.remove(com)
            

        else: raise TypeError('%com must be  of type List, Class or Instance')



#----------------------------------------------------------------------
# Noun -- base class of any noun in the game
#
class Noun:
    """
    Noun:
        base class of any noun in the game
    """
        
    # initialization method
    def __init__(self, pName=''):
        #self.a = locale.nouns[self.name].a    # article to use for 'a'
        #self.the = locale.nouns[self.name].the    # article to use for 'the'

        locale.register(locale.NOUN, self.name)

        self.blind = FALSE    # if TRUE, can't see anything
        self.container = None    # its location
        self.defverb = None    # no default verb
        self.desc = ''   # description
        self.initialDesc = ''    # desc, before it's moved (if different)
        self.initialNote = ''    # note, before it's moved (if different)
        self.invisible = 0    # invisibilty level (0 = plainly visible)
        self.invisName = locale.something    # perceived "name" when invisible
        self.light = 0    # light given off (100 = sunlight)
        self.listening = FALSE    # wants Tell() calls?
        self.listLine = ''    # line to print in contents list
        self.name = string.split(pName,',')[0]    # main name
        self.note = ''    # line to print in room contents (if nonstandard)
        self.salient = TRUE    # show in room contents list?
        self.seesDark = 0    # bonus to room light when this is seeing
        self.seesInvisible = 0    # invisibility level which this can see
        self.size = 10    # size (100=human)
        self.synonyms = string.split(string.lower(pName),',')
        self.the = locale.nouns[self.name].the    # article to use for 'the'
        
        # special initialization
        self.desc = _('It looks like an ordinary %s.') % self.name

        # add names to the parser's list of nouns
        for n in self.synonyms:
            if n not in nouns: nouns.append(n)

    
    def __getinitargs__(self):
        """
        get arguments (used by copy.copy)
        """
        return (string.join(self.synonyms,','),)
 
    
    def GetName(self, article=0, pLooker=None):
        """
        get name
        """
        # FIXME: This belongs in locale, because it's highly language dependent.
        #           should make a call into locale.
        #
        if pLooker and not pLooker.CanSee(self):
            if article==The or article==A: return cap(self.invisName)
            return self.invisName
        if not article: return self.name
        if article==the: return self.the + ' ' + self.name
        if article==a: return self.a + ' ' + self.name
        if article==The: return cap(self.the) + ' ' + self.name
        if article==A: return cap(self.a) + ' ' + self.name
        return self.name

    
    def __call__(self,article=0,pLooker=None):
        """
        allow treating an object like a function,
        as a shorthand for GetName
        """
        return self.GetName(article,pLooker)

    
    def NameMatch(self, pName):
        """
        check for a name match
        """
        return pName in self.synonyms


    def GetNote(self):
        """
        get note (for when listing the contents of a room)
        """
        if self.initialNote: return self.initialNote
        if self.note: return self.note
        #This is a nasty hack.  Doing it without a hack will touch
        #a lot more code, though, so I'm doing it this way for now.
        from os import environ
        if environ.get('PUBTESTING')=='true':
            return 'There is ' + self(a) + ' here.'
        #End hack.
        #return (random.choice( ['You see %s lying here.',
        #                       '%s is lying here.',
        #                       'There is %s here.'] ) % self(locale.A)).capitalize()

        return locale.sentence(locale.you, 'see', self(a), locale.here)
        
                
    
    def GetDesc(self,pDepth=0):
        """
        get description
        """
        if self.initialDesc: return self.initialDesc
        return self.desc

    
    def GetRoom(self):
        """
        get room (not just any container, but the first ROOM container)
        """
        cont = self
        while cont and not hasattr(cont,'ComputeTotalLight'):
            cont = cont.container
        return cont

    
    def GetListLine(self): 
        """
        get line to be printed in a list of items (e.g., for inventory)
        when an item should have a listline you either have to write it
        like so:
            '  - a shrubbery of sorts' or
            self.Getname(a) + ' of sorts' if the main name is shrubbery.
        """
        if self.listLine: return self.listLine        
        return '   - ' + self.GetName(a)


    def CanSee(self, pWhat):
        """
        can we see the given object? (assuming it's present)
        """
        # if we're blind, automatically return FALSE
        if self.blind: return FALSE

        # figure effect of lighting and night vision...

        effectiveLight = self.GetRoom().light + self.seesDark
        # anything which gives off light can always be seen
        # (unless it's the room itself)
        if pWhat.light > 0 and pWhat != self.container:
            effectiveLight = 100

            # figure effect of invisibility and counter-invisibility vision...

        visible = 1 - pWhat.invisible + self.seesInvisible
            
        # return TRUE only if both light and visibility are good
            
        return effectiveLight > 20 and visible > 0


    def CanContain(self, pWhat): 
        """
        can we contain something?
        """
        return FALSE
    

    def Tell(self, pWhat,pCmd=None):
        """
        let the object hear something
        
        by default, do nothing
        the pCmd parameter allows substitution of various
        object names, depending on whether this object can see 'em
        """
        return

    # checks, before and after this object is used as the object of a command
    
    def PreObj(self, cmd): return OK

    def PostObj(self, cmd): return OK

    # checks before and after this object is moved
    def PreMove(self):
        self.GetRoom().ComputeTotalLight()
        return OK
    
    def PostMove(self):
        self.GetRoom().ComputeTotalLight()
        return OK
    
    def MoveTo(self, pWhere):
        """
        move objects to destination in pWhere if checks pass

        if the destination is 'TRASH' delete object
        """
        if pWhere == 'TRASH': 
            if self.container: 
                self.container.contents.remove(self)
                del self
                return CANCEL 
        if not pWhere.CanContain(self) \
        or not self.PreMove():
            return CANCEL
        pWhere.ContainNoCheck(self)
        self.PostMove()
        return OK
                    

#XXX: Write testObject, first need a Thing class.

#from pubcore import Symbol

#protocols
from protocols import advise

class Thing(Symbol):
    """
    The most basic of objects
    
    """

    #FIXME: There is no IThing, nor INoun, which is probably what it should become.
    #advise(instancesProvide=[IThing]) 

    def __init__(self, names='', pronouns=''):
        
        #synonyms and name
        self.synonyms = [str(x).lower() for x in names.split(',')]
        self.name = self.synonyms[0]

        self.pronouns = [str(x).lower() for x in pronouns.split(',')]
        
        # add synonyms to the parser's list of nouns
        for n in self.synonyms:
            if n not in pubcore.nouns: pubcore.nouns.append(n)
            

