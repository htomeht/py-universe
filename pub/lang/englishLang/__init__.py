from protocols import advise

from pub.interfaces import ILang, IEnglish 

import adapters

advise(moduleProvides=[ILang])

name = 'english'

class English:
    """
    Provides IEnglish.
    """

    advise(instancesProvide=[IEnglish])

def initiate():
    """
    return a language. 
    """

    return English()
