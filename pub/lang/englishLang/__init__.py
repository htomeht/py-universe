from protocols import advise

from pub.interfaces import ILang, IEnglish 


advise(moduleProvides=[ILang, IEnglish])

name = 'english'

#def initiate():
#    """
#    function to return the current module.
#    """
#
#    if __name__ != '__main__': return __import__(__name__) 
#    else: return None
