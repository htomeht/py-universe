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
#
#   CHANGELOG
#
#   2006-07/08 TJH -    Renamed 'Symbol' to 'DynamicComponentRack' and
#                       moved it to components.py which we import to here.
#
#                       Now noun.py contains only Noun and Adjective concepts.
#
#--------------------------------------------------------------------
#

# Gettext based I18N:
# from gettext ...

def _(s):
    return s

from interfaces import *
from protocols import advise
from symbol import *

from components import DynamicComponentRack

#import locale
import types

class Noun(DynamicComponentRack):
    """
    The most basic of objects. 
    Noun doesn't provide any real methods.
    """
    advise(instancesProvide=[INoun]) 

    def __init__(self, name, adjs=()):
        DynamicComponentRack.__init__(self)

        if isinstance(name, Symbol):
            self.name = name
            
        elif isinstance(name, str):
            if hasattr(sym, name):
                self.name = getattr(sym, name)
            else:
                self.name = Symbol(name, domain=sym.NOUN, doc="Implicit Noun")
        
        if self.name.domain != sym.NOUN:
            raise ValueError("Noun must use symbol in NOUN domain. Got %s instead." % repr(self.name.domain))
        
        #synonyms and name
        self.synonyms = [x.lower() for x in names]
        self.name = self.synonyms[0]

        # add synonyms to the parser's list of nouns
        # Well we know this won't be the way to handle nouns anymore =)
        #for n in self.synonyms:
        #    if n not in pubcore.nouns: pubcore.nouns.append(n)


class Adjective(object):
    """
    PUB Object which represents adjectives.

    Combines unique symbolic concept with symbolic sense to respond to.
    Adjectives in PUB are modifiers which can be discovered by specific
    sense verbs (Look, Smell, Feel, ...) and which can be used to specify
    nouns to resolve ambiguities.
    """
    name  = None
    sense = None

    def __init__(self, name, sense=None):
        self.name  = name
        self.sense = sense

    def __repr__(self):
        return "<PUB Adjective: %s, Sense=%s>" % (str(self.name), str(self.sense))

        
