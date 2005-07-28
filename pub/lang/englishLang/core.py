# system imports
import copy

# pub imports
import pub

# protocols imports

"""
This module contains core language classes like parsers.

"""


#--------------------------------------------------------------------
#  
#

#----------------------------------------------------------------------
#    EnglishParser -- breaks a string into a command or set of commands
#
class EnglishParser:
    """
    EnglishParser:
            breaks a string into a command or set of commands
    """


    def __init__(self):
        self.words = []
        self.cmd = pub.Command()
        self.it = ''
        self.me = ''
        self.obj = obj
        self.proto = proto

    def nounWords(self,words):
        """
        given a set of words, see how many words you can lump together
        as a single noun from the beginning of the string. Thus,
            given: "give bucket of fish to bob"  we return: 0
                   "bucket of fish to bob"       ==>        3
                   "bucket to bob"               ==>        1
        """

        # the first word must be an integer, "it", or in our noun list
        if not words: return 0    # no words
        if words[0] == 'it': return 1    # "it"
        if words[0][0] == '"': return 1    # quoted string
        if pub.isInt(words[0]):    # integer
            # first word is an integer; convert to generic form
            words[0] = "#"
        if words[0]=="#" or words[0] in pub.nouns:
            # first word is in nouns; how many more words can we munch?
            a = ','.join(words)
            matches = filter(lambda x,a=a: a[:len(x)] == x, pub.nouns)
            if not matches: return 1        # (must be a number)
            # we now have a set of potential matches; find the longest
            matches.sort(lambda a,b: cmp(len(a),len(b)))
            longest = matches[len(matches)-1]
            return len(longest.split())
        return 0

    def findPrep(self,words):
        """
        print "Looking for prep in", words
        return the position of the first preposition in words,
        not looking past the first verb.
        Return -1 if no preposition is found
        """

        for i in range(0,len(words)):
            if words[i] in pub.verbs: return -1
            if words[i] in pub.preps: return i
        return -1

    def munchNouns(self,w):
        """
        starting at w, munch a set of nouns joined by conjunctions
        return the set, and remove them from self.words
        """

        if w >= len(self.words): return []
        out = []
        nounwords = self.nounWords(self.words[w:])
        while nounwords:
            if self.words[w] == 'it': out = out + self.it
            else: out.append(','.join(self.words[w:w+nounwords]))
            self.words = self.words[:w] + self.words[w+nounwords:]
            if w >= len(self.words) or self.words[w] not in pub.conjs:
                return out
            while self.words[w] in pub.conjs:
                self.words = self.words[:w] + self.words[w+1:]
            nounwords = self.nounWords(self.words[w:])
        return out

    def wordEnd(self,pStr,pStart):
        """
        return the position of the end of the word,
        given that it starts at pStart in string pStr
        """

        if pStr[pStart] == '"':
            q = pStr.find('"',pStart+1)
            if q >= 0: return q
        else:
            space = pStr.find(' ',pStart)
            comma = pStr.find(',',pStart)
            if comma < 0 or (space >= 0 and space < comma):
                if space >= 0: return space
            elif comma >= 0: return comma
        return len(pStr)

    def breakString(self,pStr):
        """
        break the string into a list of words
        - filter garbage and reduce non-quoted stuff to lower case
        - convert commas to conjunctions
        """

        w = []
        # loop through string, building list w
        wordstart = 0
        wordend = 0
        strlen = len(pStr)
        while wordstart < strlen:
            # find end of the current word
            wordend = self.wordEnd(pStr,wordstart)
            if pStr[wordstart] == '"':
                w.append(pStr[wordstart:wordend])
            else:
                # copy it into the list (unless it's garbage)
                word = pStr[wordstart:wordend].lower()
                if word:
                    if wordend < strlen and pStr[wordend] == ',':
                        if word and word not in pub.garbs: w.append(word)
                        w.append('and')
                        wordend = wordend-1
                    else:
                        if word not in pub.garbs: w.append(word)
            # repeat from the new starting point
            wordstart = wordend+1
        return w

    def parse(self,pStr=''):
        """
        Ok so let's start parsing
        first we send a pStr through the ParseCore which does most of the
        real work. 
        
        Eventually returns a list of quantal commands.
        """
        cmdlist = []
        cmdtext = pStr
        while cmdtext:
            # call the ParseCore routine, to strip one verb's worth
            cmdtext = self.parseCore(cmdtext)

            # break the multiple objects into single objects, multiple commands
            # hmm, there's gotta be a better way to do this...
            cm = Command()
            #print self.cmd
            cm.verb = self.cmd.verb
            if not self.cmd.dirobj: self.cmd.dirobj = ['']
            if not self.cmd.toobj: self.cmd.toobj = ['']
            if not self.cmd.inobj: self.cmd.inobj = ['']
            if not self.cmd.atobj: self.cmd.atobj = ['']
            if not self.cmd.withobj: self.cmd.withobj = ['']
            for a in self.cmd.dirobj:
              for b in self.cmd.toobj:
                for c in self.cmd.inobj:
                  for d in self.cmd.atobj:
                    for e in self.cmd.withobj:
                        cm.dirobj = a
                        cm.toobj = b
                        cm.inobj = c
                        cm.atobj = d
                        cm.withobj = e
                        #print cm
                        cmdlist.append(copy.copy(cm))
        # now we have a nice list of quantal commands; return it
        return cmdlist

    def parseCore(self,pStr):
        """
        Does all the namecalling, cleaning up and findind our verbs,
        prepositions and so on. 
        """
        #print "Parsing:",pStr
        self.cmd.Clear()

        # special case: check for "say" with no quotes and other shortcuts
        if pStr[0] == '"': pStr = "say "+pStr
        elif len(pStr)>5 and \
        pStr[:4].lower() == "say " and pStr[4] != '"':
            pStr = 'say "'+pStr[4:]

        # get words; strip out garbage
        self.words = self.breakString(pStr)

        # apply translations
        if self.me: pub.translations['me'] = self.me
        for i in range(0,len(self.words)):
            if pub.translations.has_key(self.words[i]):
                self.words[i] = pub.translations[self.words[i]]

        # first word should be a verb -- if not, supply 'defverb'
        w = 0
        if len(self.words)>w and self.words[w] in pub.verbs:
            self.cmd.verb = self.words[w]
            w = w + 1
        else: self.cmd.verb = 'defverb'

        # after verb: nothing, adverb, noun or conjuction
        if len(self.words) < w+1: return ''        # no more words

        # look for verb modifiers
        if self.words[w] in pub.adverbs:
            self.cmd.verb = self.cmd.verb + ' ' + self.words[w]
            self.words = self.words[:w] + self.words[w+1:]
            if w >= len(self.words): return ''

        # munch conjunctions
        while self.words[w] in pub.conjs:
            self.words = self.words[:w] + self.words[w+1:]

        # munch a direct object
        self.cmd.dirobj = self.munchNouns(w)

        # if there's another noun phrase, then it's the DO and we had IO before
        temp = self.munchNouns(w)
        if temp:
            self.cmd.toobj = self.cmd.dirobj
            self.cmd.dirobj = temp

        if self.cmd.dirobj: self.it = self.cmd.dirobj
        if len(self.words) < w+1: return ''        # no more words

        while self.words[w] in pub.preps:
            # find the object of the preposition, and assign appropriately
            objs = self.munchNouns(w+1)
            if not objs:
                pub.player.Tell("..." + self.words[w] + " WHAT?!?")
                return ''

            if self.words[w] == 'at': self.cmd.atobj = objs
            elif self.words[w] == 'in' or self.words[w] == 'into' \
              or self.words[w] == 'from': self.cmd.inobj = objs
            elif self.words[w] == 'with': self.cmd.withobj = objs
            elif self.words[w] == 'to': self.cmd.toobj = objs
            else: print "ERROR: unknown preposition " + self.words[w]

            # munch preposition
            self.words = self.words[:w] + self.words[w+1:]

            self.it = objs
            if len(self.words) < w+1: return ''    # no more words

        # look for dangling verb modifiers
        if self.words[w] in pub.adverbs:
            self.cmd.verb = self.cmd.verb + ' ' + self.words[w]
            self.words = self.words[:w] + self.words[w+1:]
            if w >= len(self.words): return ''
            # munch conjunctions
            while self.words[w] in pub.conjs:
                self.words = self.words[:w] + self.words[w+1:]

        # next word should be a verb
        if self.words[w] in pub.verbs:
            return ','.join(self.words[w:])

        # if not, something's wrong -- might be unknown word
        print 'Warning: unknown word '+self.words[w]
        return ''

        def test(self):
            """
            Test the parser
            """
            if "fish" not in pub.nouns: pub.nouns.append("fish")
            if "fish bucket" not in pub.nouns: pub.nouns.append("fish bucket")
            print "Nouns: ",pub.nouns
            print "Verbs: ",pub.verbs
            done = FALSE
            while not done:
                command = raw_input("Parser Test>")
                if command == "quit": done = TRUE
                else: print '/n'.join(map(str,self.Parse(command)))

#--------------------------------------------------------------------
# TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TE
#

class EnglishTest:
    """
    Test is used to test that lingo works.
    """


    def __init__(self):
        """"""
        
    def test(self):
        """Everything seems fine now =)"""

        print self
