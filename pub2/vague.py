# (C)2006 Terry Hancock
#--------------------------------------------------------
# vague
"""
Define a very simple saturating vague number.

Vague numbers represent spectra of meaning, such as we use
with adverbs (is "few" less or more than "several"?). These
are used to represent fuzzy shades of meaning.

In Python Universe Builder, we use vague numbers to define
the meanings of adverbs and to distinguish fine differences
in verbs which are otherwise synonyms.

In what language but Python could you write about a "precise
mathematical description of vagueness"? It seems terribly
appropriate to me. ;-)
"""
# GPL v2+ grant/disclaimer

from math import *

class Vague(object):
    """
    Vague number.

    By default, it's defined on the range -1.0 to 1.0, and uses a bivalent sigmoid
    as its "transfer" or "saturation" function.  I've added a nudge ("epsilon") to avoid 
    problems with series of small values converging on values below 1.0 (or above -1.0).

    This keeps the following statements true:
    
    Zero remains an identity (we use "o" as a vague zero, defined in this module):
    
    >>> o
    Vague(0.0)
    >>> d = Vague(0.1)
    >>> d
    Vague(0.10000000000000001)
    >>> d + o
    Vague(0.10000000000000001)
    >>> o + d
    Vague(0.10000000000000001)
    >>> d + o + o + o
    Vague(0.10000000000000001)
    >>> o + o + o + d
    Vague(0.10000000000000001)

    If:
        a > 0
        b > 0
        c = a + b
    Then:
        c > a and c > b

    As long as a and b are above a minimum "epsilon" value
    (currently hard-coded to 0.00001):

    >>> a = Vague(0.2)
    >>> b = Vague(0.001)
    >>> c = a + b
    >>> c
    Vague(0.20001000000000002)

    The same principle works on the negative side:

    >>> e = -a
    >>> f = -b
    >>> g = e + f
    >>> g
    Vague(-0.20001000000000002)

    However, be aware that vague addition is commutative, but NOT associative:

    >>> b + b + a
    Vague(0.20001000000000002)
    >>> a + b + b
    Vague(0.20002000000000003)
    >>> b + a + b
    Vague(0.20002000000000003)

    Some unary operations are defined:
    
    >>> a = Vague(0.2)
    >>> a
    Vague(0.20000000000000001)

    Amelioration brings a vague concept closer to zero.  Ameliorative combining
    adverbs might be "slightly":

    >>> -a
    Vague(0.10000000000000001)

    Exacerbation pushes a vague concept further from zero. Exacerbative combining
    adverbs include "very", "extremely", etc:

    >>> +a
    Vague(0.37995896225522502)

    Negation or Inversion flips the sign (same as unary minus on float or logical
    not on boolean):

    >>> ~a
    Vague(-0.20000000000000001)

    Subtraction is implemented by inverting the second vague:

    >>> a - d
    Vague(0.099667994624955902)
    >>> a + (~d)
    Vague(0.099667994624955902)
    >>> a - d == a + (~d)
    True

    Multiplication in the sense of multiple addition is defined with
    integers, using the % operator:

    >>> d + d + d
    Vague(0.28892800385551548)
    >>> 3%d
    Vague(0.28892800385551548)
    >>> d + d + d == 3%d
    True
    """
    minimum  = -1.0
    maximum  =  1.0
    __lock   =  False
    
    def __init__(self, value):
        self._data  = self._clip(float(value))
        self.__lock = True

    def __setattr__(self, name, value):
        if not self.__lock:
            object.__setattr__(self, name, value)
        else:
            raise TypeError("Immutable")

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, float.__repr__(self._data))

    def __str__(self):
        return "%7.4fv" % self._data
        
    # Utilities

    def _clip(self, f):
        "Make sure that float f is clipped to [-1,1] interval"
        if   f >  self.maximum: f = self.maximum
        elif f <  self.minimum: f = self.minimum
        return f

    def _saturate(self, f):
        return 2/(1+exp(-2*f))-1

    def _coerce(self, f):
        "Coerce f to Vague or raise error"
        if isinstance(f, Vague):
            return f
        elif type(f) in (float, long, int) and -1.0 <= f <= 1.0:
            return Vague(f)
        else:
            raise ValueError("Not coerceable or out of [-1,1] domain, value = %s" % repr(f))

    # Math rules for vague numbers

    def __hash__(self):
        return hash(self._data)

    def __cmp__(self, other):
        return cmp(self._data, other._data)

    def __float__(self):
        "Coersion to float, just exposes the _data element"
        return self._data

    def __int__(self):
        """
        Coersion to integer

        Rounds (if it had usual integer-truncation it would always return zero).
        """
        if   self._data < -0.5: return -1
        elif self._data >  0.5: return  1
        else:                   return  0
        
    def __add__(self, other):
        "Add applies saturation function to result of addition, result stays in [-1,1]"
        other = self._coerce(other)
        epsilon = 0.00001
        r = self._saturate(self._data + other._data)
        if abs(self._data) < epsilon:
            return Vague(self._clip(other._data))
        elif abs(other._data) < epsilon:
            return Vague(self._clip(self._data))
        #
        # TODO: This seems like a kludge to cover up a mathematical misunderstanding
        #        Is there a more elegant solution?
        #
        # In order to avoid convergence within the interval, we ensure that adding
        # positive values always increases the result (up to the threshold) and
        # likewise for both negative. if calculation is a difference, the saturation
        # function has no such negative effect.
        if other._data >= 0.0 and self._data >= 0.0:
            r = max((r, self._data, other._data)) + epsilon
        elif other._data <= 0.0 and self._data < 0.0:
            r = min((r, self._data, other._data)) - epsilon
        return Vague(self._clip(r))

    def __radd__(self, other):
        return self.__add__(other)

    def __invert__(self):
        "Reverse the meaning of vague."
        return Vague(-self._data)

    def __neg__(self):
        """
        Amelioration

        Softens the impact of the vague number (closer to 0).
        """
        return Vague(self._data*0.5)

    def __pos__(self):
        """
        Exacerbation

        Increases the impact of the vague number (further from 0).
        """
        return self + self

    def __sub__(self, other):
        "Flips other, then uses same rule as add"
        return self + (~other)

    def __rsub__(self, other):
        return (~self).__add__(other)

    def __mod__(self, other):
        """
        Special case for integer multiple sum

        This is mostly useful for testing. I don't
        think we have any production use for it.
        I used it a lot to explore pathological convergence
        problems though, so it's handy to have.
        """
        if type(other) == int:
            if other < 0:
                r0 = -self
                N  = -other
            else:
                r0 =  self
                N  =  other
            r = r0
            for i in range(N-1):
                r = r + r0
        else:
            raise TypeError("Don't know what to do with %s" % repr(type(other)) )
        return r

    def __rmod__(self, other):
        return self.__mul__(other)
                

# Some useful constants:
o = zero = Vague(0)
I = Vague(1)

