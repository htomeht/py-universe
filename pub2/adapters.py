# adapters.py    contains adapters                        04/10/22 GJ
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

#--------------------------------------------------------------------
# CHANGELOG
#
#   2004-22/10: Gabriel Jagenstedt
#       Cleaned up and inserted a copyright notice
#--------------------------------------------------------------------
"""
Adapters for PUB

Contains ,
"""

# standard imports

# pub imports
import interfaces
#import pub.lang

# protocols imports
from protocols import advise

#--------------------------------------------------------------------
#
#class StrLangAdapter:
#    """
#    Adapter that evaluates a string as a language name into a languageinstance
#    """
#
#    advise(instancesProvide=[interfaces.ILang], asAdapterForTypes=[str])
#
#    def __init__(self, obj, proto):
#        self.langstr = obj
#       
#        
#    def initiate(self):
#        """
#        method to translate a string into a language. 
#        """
#
#        for lang in pub.lang.getListing():
#            if lang.name.lower() == self.langstr.lower():
#                #pub.language = lang 
#                # set this language as current language 
#                # this way next time we adapt we won't need to evaluate.
#                
#                return lang.initiate()
#
#        # No such language found
#        raise pub.errors.LanguageError, "Can't find specified language"
#
#        
#--------------------------------------------------------------------
