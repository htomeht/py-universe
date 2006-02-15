# Game engine localization

# This is a set of ideas about localization, showing some examples to drive decisions
# about the localization model.
#
# Internationalizing an IF engine is not as simple as internationalizing a normal
# program with fully-written messages. An IF engine has to actually generate sentences
# from linguistic atoms (words, morphemes, endings, etc).  This is probably not at
# all feasible to do in a fully natural way!
#
# But we only require basic comprehension, and we work in a very limited domain of
# expressions.  Hence the internationalization effort needs to be driven by the specific
# needs of the engine, and not some grand concept of formalizing entire languages!
#
# Remember that the IF engine only parses *commands* from the player, then *reports*
# events as they happen. It only uses simple sentences, though it can understand *some*
# compound commands by a simple expedient of extracting simple sentences with conjunction
# markers which are all treated the same way.
#
# Obviously much subtlety is lost!  Not in translation from "Language X" to "English",
# but in translation from "Language X" to "IF-ese".
#
# 

inflections = ('subj', 'dobj', 'iobj', 'poss')  # Driven by use in the engine
                                                # The IF engine isn't smart enough to distinguish
                                                # more cases, so don't mess with them.

# Anything smarter than these cases can be fixed in the sentence() function.

you = ('you', 'you', 'you', 'your')             #  English (very degenerate)
you = ('tu',  'ti',  'ti',  'tu')               #  Spanish
you = ('anata', 'anata', 'anata', 'anata')      #  Japanese (fully degenerate! Note that the "no" can
                                                #  be added by the sentence generator).

#question words
who, what, which, whichway, where, when, how, howmuch, why = (
    'who', 'what', 'which', 'which way', 'where', 'when', 'how', 'how much', 'why')

who, what, which, whichway, where, when, how, howmuch, why = (
    'dare', 'nani', 'dore', 'dochira', 'doko', 'nan ji', 'dou', '?', 'naze')    #jp

who, what, which, whichway, where, when, how, howmuch, why = (
    'quien', 'que', 'quel', 'a donde', 'donde', 'cuando', 'como', 'cuanto', 'porque') #es
    
#relative locations (in room, in inventory, in other room or inside container)
# e.g. "you see no keys *here*"
#
here, there, overthere = ('here', 'there', 'there')
here, there, overthere = ('aqui', 'alli',  'alli')  #es  (3rd is wrong?)
here, there, overthere = ('kore', 'sore',  'are')   #jp

#indefinites
some, something, someone, somewhere = (
    'some', 'something', 'someone', 'somewhere')

some, something, someone, somewhere = (
    'de', "quelqu'un", "quelqu'on", "quel place") #fr (sort of)

some, something, someone, somewhere = (
    'algun', 'alguno', 'alguien', 'adonde')   #es (sort of)

some, something, someone, somewhere = (
    '', 'nani', 'dare', 'doko')         #jp





class _irregular:
    """
    Name space for various irregular forms (used for lookup).

    NOTE: Don't try to list every irregular word in the language!
          Start with this empty, and add words as needed from other parts.

    Please note that this class is private to locale.py. The code uses
    provided helper functions.  Some localizations may need to change some
    definitions in here (for example, more complex pluralization cases in
    some Slavic languages?  Counters in Japanese?)    
    """
    plural = {  'sheep':'sheep',        # Stupid examples, but you get the idea.
                'tooth':'teeth',
                }

    # conjugation: we're only interested in present tense imperative, 2nd person singular,
    #               3rd person singular (inanimate), 3rd person singular (animate)
    #
    #               We use the first form in understanding the player's typed commands.
    #               The second is used to describe the player's action as it is done.
    #               The third is used if the subject is a non-player, non-character, thing
    #               The fourth is used for "agent" or "character" objects (subclasses of "Person")
    #
    #               This doesn't matter for verbs in English, but it may in some languages
    #               like Japanese that require some kind of honorific treatment for people.
    #
    #               Animals and machines are edge cases: but the *game designer* chooses which
    #               class to put them in.
    #
    tense        = { 'be':('be', 'are', 'is', 'is'),         # Again, I'm not sure we need these verbs
                     'do':('do', 'do',  'does', 'does')}     # (except "are" is likely to be used in
                                                            # the sense of "are located").

    # inflection:  we only use nouns in 3 places: the subject of a sentence, the direct object,
    #               and the indirect object of the sentence.  Since we use a marker to distinguish
    #               the particular varieties of indirect object (and most languages use either a
    #               word or a regular word-ending for this), the sentence() function is the only
    #               place to do anything smarter than that.

    inflection = { 'I': ('I', 'me', 'me') }     # Not really needed
                                                # I can't think of any *real* examples of this.
                                                
    # the inflections in Japanese don't count, because they are regular, and are actually
    # provided by separate words, so there's no reason to put them here.

A_THE, A_A, A_X = range(3)


class noun_class(list): # English doesn't need this, but Spanish, French, German, and Swahili all do
    nouns = ()
    the   = 'the'       # "specified"
    thes  = 'the'
    a     = 'a'         # "example"
    as    = 'as'
    x     = ''          # "unspecified"

N = noun_class(list)    # English has only one (except for pronouns)

F = noun_class(list)    # Romance languages have two "genders" for nouns (French)
F.the  = 'la'
F.thes = 'les'
F.a    = 'une'
F.as   = 'de'

M = noun_class(list)
M.the  = 'le'
M.thes = 'les'
M.a    = 'un'
M.as   = 'de'

                        # Swahili has (IIRC) 8 different classes of nouns -- nothing to do with
                        # gender, but they take different plural forms, etc.
                        # I mention this, because it underscores the need for a general facillity
                        # for noun classes.

class verb_class(list): # Once again, not needed by English, but Spanish and French need it
    verbs = ()

class noun_class(list):
    """
    Represents a group of nouns having the same grammatical behavior, such
    as gender in Romance languages, or noun classes in Bantu languages.

    Irregular nouns can be placed in a class of their own.
    """
    def __call__(self, article=None, number=1, inflection=NOM):
  
def possessive(owner, thing):
    """
    Express that thing is owned by owner (or belongs to, is specific to, etc).
    """
    if owner == you:
        return "%s %s" % (you[3],str(thing))
    else:
        return "%s's %s" % (str(owner), str(thing))

def pluralize(thing, number):       # English
    """
    Express the plural of thing with given number.
    """
    if number!=0 and number>1:
        if thing == you:
            return "you"
        elif str(thing) in _irregular.plural.keys():
            return _irregular.plural[str(thing)]
        elif str(thing)[-1]=='s':
            return str(thing) + 'es'
        else:
            return str(thing) + 's'
    else:
        return str(thing)

def _counter(thing, number):
    """
    Japanese counter code (may be used by sentence()).
    """
    ctr = noun[str(thing)].counter
    ctr_base = counters[ctr].base
    return "%s%s" % (ctr_base, ctr, str(thing))

# Okay, that might not really be best -- most of the time plurals aren't noted in Japanese
# but sentence() will probably only call this when it's really necessary to know. (???)

# Otherwise, we could just use a simpler:

def pluralize(thing, number):
    return str(thing)

# Since most of the time, we only need that.
        
def inflect(pos, noun):                                 
    """
    only irregular cases in English
    inlection is normally fully degenerate
    """
    i = ['subj', 'dobj', 'iobj'].index(pos)
    if str(noun) in _irregular.inflections.keys():
        return _irregular.inflections[str(noun)][i]
    else:
        return str(noun)

def inflect(pos, noun):
    """
    Japanese never inflects noun structure -- sentence adds particles in
    a completely regular way to indicate noun position.  This applies
    even to pronouns.
    """
    return str(noun)


def conjugate(subject, verb, tense=config.PRESENT):
    """
    In English conjugation is nearly degenerate -- only 3rd person singular differs,
    except for a very small number of irregular verbs (mainly "to be").
    """
    if str(verb) in _irregular.conjugation.keys():
    
    if tense==config.IMPERATIVE:
        return str(verb)

    if subject.number==0 or subject.number > 1:
        return str(verb)
    else:
        return str(verb) + 's'

def quote(text):
    """
    Mark text as a literal quotation.
    """
    return '"%s"' % text

def quote(text)
    """
    Japanese (Romaji) -- Kana version should use correct unicode Japanese quotation marks of course.
    """
    return '"%s" to' % text
    

def sentence(   subj=None,
                verb=None,
                dobj=None,
                advb=None,
                iobj={},
                tense=config.PRESENT):
    """
    English language prototype.

    Build a sentence using locale information, and the basic parts of speech that
    need to be communicated. 
    
    Parts of speech will either be None (in which case they are unspecified by the
    IF engine, and should not be used at all), or they are objects, with interfaces
    as specified below.  Note that strings are not used, because sentence may need
    to interrogate objects for regular or irregular inflections, conjugations, or
    other language-specific grammar requirements.

    Default is plain present tense because most common use of sentence is to generate
    descriptions of your actions as they happen (normally imperative tense is understood
    by the IF engine, not generated -- but there may be exceptions from non-player
    agent objects, so it is provided.

    @param subj: pair with specifier (for articles) and noun object implementing INoun.
    @param verb: object implementing IVerb.
    @param dobj: pair with specifier and noun implementing INoun
    @param iobj: dictionary whose keys are prepositions, and values noun-pairs as with subj and dobj.
    @param tense: constant identifying tense, either config.PRESENT or config.IMPERATIVE.
    """
    if verb: s_verb = conjugate(subj[1], verb, tense)
    if subj: s_subj = "%s %s" % (str(subj[0]), str(subj[1]))
    if dobj: s_dobj = "%s %s" % (str(dobj[0]), str(dobj[1]))
    if advb: s_advb = str(advb)
    
    if iobj:
        s_iobj = " ".join(["%s %s %s" % (str(p), str(n[0]), str(n[1])) for p,n in iobj.items()]

    if tense == config.IMPERATIVE:
        s_subj = ''

    return (" ".join([w for w in [s_subj, s_verb, s_dobj, iobj, advb] if w])).capitalize() + '.'
    

def sentence( subj=None,
              verb=None,
              dobj=None,
              advb=None,
              iobj={},
              tense=config.PRESENT):
    """
    Japanese version (romaji, obviously).
    """

    if verb: s_verb = conjugate(subj[1], verb, tense)   # Only tense matters though.
    if subj: s_subj = "%s ga" % str(subj[1])        # or "wa"?

    if isinstance(dobj, quotation):
        s_dobj = quote(str(quotation))
    else:
        s_dobj = "%s wo" % str(dobj[1])

    if advb: s_advb = str(advb)

    if subj == locale.you:      # Always omit player character noun phrase.
        s_subj = ''
    
    if iobj:
        s_iobj = " ".join(["%s %s" % (str(n[1]), str(p)) for p,n in iobj.items()]

    # Note that capitalization and spacing is only used because this is romaji,
    # Unicode version would use kanji and hiragana, without spacing, and end in a maru.
    
    return (" ".join([w for w in [s_subj, s_verb, s_dobj, iobj, advb] if w])).capitalize() + '.'


# This is the nouns translation table for the IF engine and built-ins:
#
#                        NAME: (XLTN, NOUNCLASS, EXTENDED),
noun_vocabulary = {     'pen': ('pluma', n_F, "pluma para escrire"),   # A regular noun, "feminine" class.
                        'you': ('tu', pronoun(inflections=('tu', 'te', 'ti', 'tu')), ''), # (irregular) pronoun
                        'cat': ('gato', n_M_, '')
                        }  #  es example

# NOUNCLASS provides the means to:
#
#   1) Interpret article modifiers: A, THE, None, ABSTRACT, PERSON, ANIMATE
#   2) Pluralize correctly based on literal number
#       (Special values: -1=collective, -2=plural(unknown number), -1000=uncountable)
#   3) Correctly apply declension
#


