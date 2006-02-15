# (C) 2006 Terry Hancock
# PUB Engine Locale: fr
"""
Generic US English engine locale for Python Universe Builder
"""
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

### SENTENCE ########################################################
# DON'T CHANGE THE NEXT LINE!
(subject, verb, direct_object, preposition, indirect_object, adverb) = range(6)

# CHANGE *THIS* LINE:
StdSentenceOrder = (subject, 
                    verb, 
                    direct_object,
                    preposition,
                    indirect_object,
                    adverb)

    # Change to reflect the most natural sentence order. Bear in mind that in
    # some languages, "prep" may be glossed as a declension particle or
    # ending.

    # Yes, I'm very much aware that sentences can be more complicated, 
    # but this is the form that sentences given to the parser will
    # have to take. It can sound stilted, but has to make sense.

#####################################################################



### NOUNS ###########################################################
#Individual nouns should generally be localized in the Game locale.

noun_groups  = ('N',)  # English has only one regular class of nouns

# Pluralization

def pluralize(noun, number):
    if number==0 or number>1:
        if noun[-1]=='s':
            return noun + 'es'
        else:
            return noun + 's'
    else:
        return noun

        # FIXME: I think we're going to have to be smarter than this
        # to handle languages like Chinese and Japanese which require
        # 'counters' and explicit/implicit number

        # English collective nouns and irregular plurals will be handled
        # within each noun definition

# Articles

article_the = "the %s"
article_a   = "a %s"

# FIXME:
# This makes sense only in European languages, and even so, usage varies 
# a lot (e.g. "Love" vs "L'Amour" as abstract subject). For now, we ignore
# the usage differences, and languages without articles should define both
# as "%s" and move on

# Declension (only makes sense in some languages)
# see also "Prepositions"
# Note that nouns may override, so this is fall-back or 'regular' declension
#
# N is the noun (or its base form)
# P is the "preposition", "particle", "prefix", or "suffix" which
# marks the relationship of the noun to the verb or the role of the
# noun in the sentence. PUB only knows about "subj" and "dobj" implicitly,
# and depends on the verb and noun to know what the preposition means
# in context -- thus "indirect object" may represent more than one
# possible declension -- if this can be constructed by attaching one of
# several standard endings, then this is the means.

# In English, subj and dobj take no special endings or declension marks,
# so they are only distinguishable by word order.  The meaning of
# the "indirect object" is a noun with a declension determined by the
# preposition.

declension = {  'subj': '%(N)s',
                'dobj': '%(N)s',
                'iobj': '%(P)s %(N)s' }

# Special abstract nouns

adj_specifying  = '%(A)s %(N)s'
adj_descriptive = '%(N)s %(A)s'

inventory = ('inventory',)

# Adjectives -- note that these are adjective forms! Many of these
# are nouns in English too, but these will be used in modifiers (as
# in "one red box" or "switch is on").

adj_state = ('on', 'off')

# FIXME: do we really need colors?  Maybe these should be in game locales
adj_color = { 'black': 'black',
              'white': 'white',
              'gray':  'gray',
              'brown': 'brown',
              'red':   'red',
              'blue':  'blue',
              'green': 'green'}

adj_number = ('one', 'two',   'three', 'four', 'five', 
              'six', 'seven', 'eight', 'nine', 'ten')

adj_size   = ('smallest', 'smaller', 'small', 'large', 'larger', 'largest')


#####################################################################


### PREPOSITIONS ####################################################
# What we call 'prepositions' in English may be replaced by declension
# particles in some other languages. The point is, these determine the
# relationship of a noun to an action.

# Prepositions are among the hardest words to translate, so I'm trying
# to be very explicit and literal here.  The use of prepositions in
# PUB is to indicate the relationship of various "indirect object" nouns
# to the verbs acting on them -- so keep this in mind when translating.

# Containment
within = ('in', 'within')
    # Means object is contained within another object
    # DO NOT USE 'on' to mean 'in' in English!  Per-noun irregularities
    # can be resolved in the noun locale (e.g. the Noun "airplane" will
    # redefine 'on' as a synonym for 'in', removing it from the "on" list).

# Spatial relationships

# Almost every language has some support for adjacency in the form of
# a "cube model" -- objects having six sides: top/bottom, front/back,
# left/right. In addition, there is usually something indicating distance
# without being specific, and gravity implies attachment to top (supporting).

on    = ('on', 'upon', 'on top of')    # Touching / supported-by
top   = ('above', 'over')              # Not touching

bottom= ('under', 'below', 'beneath')  

front = ('in front of',)
back  = ('in back of',) #?

side  = ('beside', 'near')
left  = ('to the left of',)
right = ('to the right of',)

# Anything more specific will be have to be associated with individual nouns
# (e.g. on top shelf of)

# Tool-use

using   = ('using', 'with')
tool_on = ('on', 'upon', 'against')
target  = ('towards', 'to')

#####################################################################


### VERBS ###########################################################

#####################################################################


### ADVERBS #########################################################

StdAdverbModifiers = {  'extremely %(A)s':  -0.7,
                        'very %(A)s':       -0.5,
                        '%(A)s':            -0.3,
                        '':                  0.0,
                        '%(B)s':             0.3,
                        'very %(B)s':        0.5,
                        'extremely %(B)s':   0.7 }
                        
# 'A' and 'B' are adverbs with opposite meanings.  They may be
# constructed by using a standard inversion form for either A or B,
# or they may be explicit opposites.

StdAdverbInversion = "not %s"

# Standard (fall back) inversion form. This is only used if no
# inverse form is given for 'A' or 'B' in StdAdverbModifiers.

#####################################################################
