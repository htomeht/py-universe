# adapters for pub

import interfaces
import pub.lang

from protocols import advise

#--------------------------------------------------------------------
class StrLangAdapter:
    """
    Adapter that evaluates a string as a language name into a languageinstance
    """

    advise(instancesProvide=[interfaces.ILang], asAdapterForTypes=[str])

    def __init__(self, obj, proto):
        self.langstr = obj
       
        
    def initiate(self):
        """
        method to translate a string into a language. 
        """

        for lang in pub.lang.getListing():
            if lang.name.lower() == self.langstr.lower():
                #pub.language = lang 
                # set this language as current language 
                # this way next time we adapt we won't need to evaluate.
                
                return lang

        # No such language found
        raise pub.errors.LanguageError, "Can't find specified language"

        
#--------------------------------------------------------------------
