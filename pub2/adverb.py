#   (C)2006 Terry Hancock
#    adverb
"""
Adverbs are modifiers for verb actions. We model them as numerical values
in specific "domains" -- each domain contains a set of adverbs with meanings
which are translated as a float between -1 and +1.  The verb code decides
what to do with the number: generally, this modifier will be passed on to
the direct and indirect objects, whose verb methods may opt to react differently
according to the adverb.

A simple example: "hit nail" implies a neutral adverb (value 0), but
"hit nail gently", "hit nail hard", and "hit nail very hard" may, for
example result in adverbial values (-0.5) and (+0.5) respectively.  The nail
object may decide not to change its state (resist being driven in) if
intensity < -0.3 or to *break* if intensity > +0.6.

Thus, the player's choice of adverb can affect the outcome of an action,
and the designer has more flexibility.
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

import locale

class AdverbDomain(dict):
    """
    A collection of adverbs which modify the same property of a verb.

    Shortcuts are provided for common inversions and to build an array of
    variations on a single adverb using modifiers. These should be localizable,
    but if for some reason they are not flexible enough, it is always possible
    to simply use explicit sets of adverbs (it's just a shortcut, the effect
    is the same).
    """
    
    # FIXME: localization
    _std_modifiers = locale.StdAdverbModifiers
    _std_inversion = locale.StdAdverbInversion
    
    def __init__(self, A, B=None):
        self.define_adverbs(A, B)

    def define_adverbs(self, A, B=None, stretch=1.0, pan=0.0):
        """
        Add a group of adverbs to this domain.

        Note that this is separated from the __init__ so you can group more than one collection
        of adverbs into the same range.

        @param stretch: allows you to expand or shrink the range of meaning relative to the base adverbs
        @param pan: allows you to push the range of meaning towards either extreme.
        """
    
        if type(A) == type({}):
            # Dictionary specified, define ranges explicitly
            for adverb in A.keys():
                self[adverb] = A[adverb]*stretch + pan

                # stops
                if self[adverb]>1.0:    self[adverb]=1.0
                elif self[adverb]<-1.0: self[adverb]=-1.0
            
        if type(A) == type(''):
            # Construct a standard modified set from one word or two antonyms

            # If only one word is specified, call other "not X"
            if not B:
                B = self._std_inversion % A
            elif not A:
                A = self._std_inversion % B

            # We accept shorthand for "un-", "non--", "in-" etc with a dash (dash is removed)
            # Note that, e.g.: "non-", "standard" gets you "nonstandard", 
            #                  while "not--" gets you "non-standard"
            
            if B[-1]=='-':   B = B[:-1] + A
            elif A[-1]=='-': A = A[:-1] + B

            # OR we can accept suffixes. I don't think this happens in English, but
            # it could be used with "-kune" in Japanese, for example (?)

            if B[0]=='-':   B = A + B[1:]
            elif A[0]=='-': A = B + A[1:]

            words = {'A':A, 'B':B}
            for modifier in self._std_modifiers.keys():
                key = modifier % words
                self[key] = self._std_modifiers[modifier]*stretch + pan

                # stops
                if self[key] > 1.0:    self[key]==1.0
                elif self[key] < -1.0: self[key]=-1.0



# Should be in another module, for localization reasons
#  Some simple adverb domains as examples:

INTENSITY  = AdverbDomain("gently", "hard")
INTENSITY.define_adverbs("", "violently", stretch=0.8, pan=0.2)

POLITENESS = AdverbDomain("", "nicely")
POLITENESS.define_adverbs("politely", "rudely")
POLITENESS.define_adverbs({"pointedly":-0.1, "surreptitiously":+0.9, "circumspectly":+0.87})


