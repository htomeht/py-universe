#objs.py
#
#



#XXX: Write testObject, first need a Thing class.

from pubcore import Symbol

#protocols
from protocols import advise

class Thing(Symbol):
    """
    The most basic of objects
    
    """

    advise(instancesProvide=[IThing]) 

    def __init__(self, names='', pronouns=''):
        
        #synonyms and name
        self.synonyms = [str(x).lower() for x in names.split(',')]
        self.name = self.synonyms[0]

        self.pronouns = [str(x).lower() for x in pronouns.split(',')]
        
        # add synonyms to the parser's list of nouns
        for n in self.synonyms:
            if n not in pubcore.nouns: pubcore.nouns.append(n)
            

