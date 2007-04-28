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

from math import *
from bisect import bisect
import operator

class Vague(object):
    """
    Vague number.

    Vague numbers represent flexible linguistic concepts of scale or degree.
    They are similar to fuzzy logic truth values, but have a valence, so they
    are defined over the interval [-1,+1].

    All valid mathematical operators must keep their results in this range,
    "saturating" as they approach the limits.
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
        """
        Make sure that float f is clipped to [-1,1] interval
        """
        if   f >  self.maximum: f = self.maximum
        elif f <  self.minimum: f = self.minimum
        return f

    def _saturate(self, f):
        """
        Saturation function maps out of domain values into domain, smoothly.
        
        I use a bivalent sigmoid as the "transfer" or "saturation" function.  I've
        added a nudge ("epsilon") to avoid problems with series of small values
        converging on values below 1.0 (or above -1.0).

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
        """
        return 2/(1+exp(-2*f))-1

    def _coerce(self, f):
        """
        Coerce f to Vague or raise error
        """
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
        other = self._coerce(other)
        return cmp(self._data, other._data)

    def __abs__(self):
        return Vague(abs(self._data))

    def __float__(self):
        """
        Coersion to float, just exposes the _data element
        """
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
        """
        Add applies saturation function to result of addition, result stays in [-1,1]
        
        Saturating "Vague Addition":

        As long as a and b are above a minimum "epsilon" value
        (currently hard-coded to 0.00001):

        >>> a = Vague(0.2)
        >>> b = Vague(0.001)
        >>> c = a + b
        >>> c
        Vague(0.20001000000000002)

        The same principle works on the negative side:

        >>> e = ~a
        >>> f = ~b
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
        """
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
        other = self._coerce(other)
        return self.__add__(other)

    def __invert__(self):
        """
        Reverse the meaning of vague.

        Negation or Inversion flips the sign (same as unary minus on float or logical
        not on boolean):
        
        >>> a = Vague(0.2)
        >>> a
        Vague(0.20000000000000001)
        >>> ~a
        Vague(-0.20000000000000001)
        """
        return Vague(-self._data)

    def __neg__(self):
        """
        Amelioration

        Softens the impact of the vague number (closer to 0).
        
        Amelioration brings a vague concept closer to zero.  Ameliorative combining
        adverbs might be "slightly":
        
        >>> a = Vague(0.2)
        >>> a
        Vague(0.20000000000000001)
        >>> -a
        Vague(0.10000000000000001)
        """
        return Vague(self._data*0.5)

    def __pos__(self):
        """
        Exacerbation

        Increases the impact of the vague number (further from 0).

        Exacerbation pushes a vague concept further from zero. Exacerbative combining
        adverbs include "very", "extremely", etc:
        
        >>> a = Vague(0.2)
        >>> a
        Vague(0.20000000000000001)
        >>> +a
        Vague(0.37995896225522502)
        """
        return self + self

    def __sub__(self, other):
        """
        Flips other, then uses same rule as add

        Subtraction is implemented by inverting the second vague:
        >>> a = Vague(0.2)
        >>> a
        Vague(0.20000000000000001)
        >>> d = Vague(0.1)
        >>> d
        Vague(0.10000000000000001)
        >>> a - d
        Vague(0.099667994624955902)
        >>> a + (~d)
        Vague(0.099667994624955902)
        >>> a - d == a + (~d)
        True
        """
        other = self._coerce(other)
        return self + (~other)

    def __rsub__(self, other):
        other = self._coerce(other)
        return (~self).__add__(other)

    def __mod__(self, other):
        """
        Special case for integer multiple sum

        This is mostly useful for testing. I don't
        think we have any production use for it.
        I used it a lot to explore pathological convergence
        problems though, so it's handy to have.

        Multiplication in the sense of multiple addition is defined with
        integers, using the % operator:

        >>> d = Vague(0.1)
        >>> d
        Vague(0.10000000000000001)
        >>> d + d + d
        Vague(0.28892800385551548)
        >>> 3%d
        Vague(0.28892800385551548)
        >>> d + d + d == 3%d
        True
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
        return self.__mod__(other)  # FIXME: does this make sense for Vague numbers?

    def __mul__(self, other):
        """
        'Combination'

        In PUB, we use this operation to express the effect of combining adverbs on
        adverbs (in principle, it could apply to adjectives as well).

        C = A * B    

        For A ==+0.5:       B is unchanged
        For A ==-0.5:       B is negated (flips sign)
        (FIXME: these requirements are not yet met by this design)
        
        For A in [+0.0,+0.5): ameliorates B  (pushes closer to 0.0)
        For A in (+0.5,+1.0]: exacerbates B  (pushes away from 0.0)
        For A in (-0.5,-0.0): ameliorates B  (pushes closer to 0.0) and negates (flips sign)
        For A in [-1.0,-0.5): exacerbates B  (pushes away from 0.0) and negates (flips sign)
        (These currently do work)

        It turns out that saturated doubled multiplication does this fairly well. It
        also has the benefit of being commutative, so we don't have to worry about
        which of A or B is the combining adverb (and hence, we don't have to worry
        about the order in adverbial expressions). 
        """
        # FIXME: combination math below doesn't quite fit the spec above
        #        (it fails to meet the identity requirements due to the
        #         effects of the saturation function)
        # FIXME: test Vague multiplication / 'combination'
        other = self._coerce(other)
        
        # The pivot is chosen (by substituting into the saturation function,
        # to put the Vague multiplicative identity at exactly Vague(0.5):
        # pivot = -2. * log(1./3)

        r = self._saturate(2 * self._data * other._data)
        return Vague(self._clip(r))        
                

# Some useful constants:
o = zero = Vague(0)
I = Vague(1)


class SparseVector(dict):
    """
    SparseVector is a numerical aggregate type with math defined.

    It has an undefined dimensionality, with all unspecified elements set to a default value.
    The actual element math is determined by the numerical type of the values, and the
    keys can be any hashable objects. Actually implemented as a dictionary.

    Use: we use SparseVector of Vague to represent adverbial state

    Tests:

    >>> a = {'COMBINING':Vague(0.200), 'INTENSITY':Vague(-0.300), 'POLITENESS':Vague(0.400)}
    >>> b = {'COMBINING':Vague(-0.100), 'INTENSITY':Vague(0.200), 'POLITENESS':Vague(-0.200)}
    >>> A = SparseVector(a, default = Vague(0.0))
    >>> B = SparseVector(b, default = Vague(0.0))
    >>> A + B
    SparseVector({'POLITENESS': Vague(0.19737532022490401), 'INTENSITY': Vague(-0.09966799462495568), 'COMBINING': Vague(0.099667994624955902)}, default=Vague(0.0))
    
    >>> A.apply(float)
    >>> B.apply(float)
    >>> A + B
    SparseVector({'POLITENESS': 0.20000000000000001, 'INTENSITY': -0.099999999999999978, 'COMBINING': 0.10000000000000001}, default=0.0)
    >>> A - B
    SparseVector({'POLITENESS': 0.60000000000000009, 'INTENSITY': -0.5, 'COMBINING': 0.30000000000000004}, default=0.0)
    >>> A * B
    -0.16000000000000003
    >>> A % B
    SparseVector({'POLITENESS': -0.080000000000000016, 'INTENSITY': -0.059999999999999998, 'COMBINING': -0.020000000000000004}, default=0.0)
    >>> A % A
    SparseVector({'POLITENESS': 0.16000000000000003, 'INTENSITY': 0.089999999999999997, 'COMBINING': 0.040000000000000008}, default=0.0)
    >>> A * A
    0.29000000000000004
    >>> A ** 2
    0.29000000000000004
    >>> abs(A)
    0.53851648071345048
    >>> A ** 1
    0.53851648071345048

    >>> A * 2
    SparseVector({'POLITENESS': 0.80000000000000004, 'INTENSITY': -0.59999999999999998, 'COMBINING': 0.40000000000000002}, default=0.0)
    >>> 2 * A
    SparseVector({'POLITENESS': 0.80000000000000004, 'INTENSITY': -0.59999999999999998, 'COMBINING': 0.40000000000000002}, default=0.0)
    

    """
    default = 0.0
    
    def __init__(self, items=None, default=0.0):
        if items:
            self.update(items)
        self.default = default

    def __repr__(self):
        return "SparseVector(%s, default=%s)" % (dict.__repr__(self), repr(self.default))

    def __getitem__(self, key):
        return self.get(key, self.default)

    def apply(self, func):
        """
        Apply a function to each value (in place).
        Can be used to change type, if 'func' is a type built-in.
        """
        for key in self.keys():
            self[key] = func(self[key])
        self.default = func(self.default)

    def applied(self, func):
        """
        Functional variant of apply, makes a copy.
        """
        result = SparseVector(default=self.default)
        result.update(self)
        result.apply(func)
        return result

    def _operate(self, other, operator):
        K1 = self.keys()
        K2 = other.keys()
        keys = set(K1 + K2)

        default = operator(self.default, other.default)
        
        result = SparseVector(default=default)
        for key in keys:
            result[key] = operator(self.get(key, self.default), other.get(key, self.default))

        return result

    def __eq__(self, other):
        if (self-other)**2 == 0.0:
            # Note that we don't tolerate error here (this is not the recommended equality test
            # for floating point elements!)
            return True
        else:
            return False
  
    def __add__(self, other):
        return self._operate(other, operator.add)

    def __sub__(self, other):
        return self._operate(other, operator.sub)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __mul__(self, other):
        """
        Dot product or Scalar multiplication.

        If 'other' is another SparseVector, the result is a dot product.

        If 'other' is a scalar number, the result is scalar multiplication
        (that is, the magnitude is multiplied by the scalar, while the
        direction is unchanged).
        """
        if hasattr(other, '__iter__'):
            result = self._operate(other, operator.mul)
            return sum(result.values(), result.default)
        else:
            # scalar multiplication
            result = SparseVector(default=self.default)
            for key in self.keys():
                result[key] = self[key] * other
            result.default = self.default * other
            return result

    def __rmul__(self, other):
        return self.__mul__(other)

    def __mod__(self, other):
        """
        Component-wise product.

        There is no real cross-product for undefined dimensional vectors.
        """
        return self._operate(other, operator.mul)

    def __abs__(self):
        """
        Magnitude
        """
        return sqrt(self * self)

    def __pow__(self, exp):
        """
        Power of magnitude.
        """
        # Probably gratuitous optimization, but I thought we should avoid
        # the sqrt for the most common use (as in a chi-squared calculation)
        if exp==2:
            return self * self
        else:
            square = self * self
            halfexp = float(exp) / 2
            return square ** halfexp


def table_lookup(value, table, direction=None):
    """
    Pick the nearest match from a list of tuples, where table[0] is the value column.
    
    Example:

    >>> table = [ (-0.100, 'A'), (+0.400,'B'), (+0.200, 'C'), (-0.800,'D'), (+0.500,'E'), (+0.900, 'F')]
    >>> table_lookup(-0.656, table)
    (-0.80000000000000004, 'D')
    >>> table_lookup(0.356, table)
    (0.40000000000000002, 'B')
    >>> table_lookup(0.256, table)
    (0.20000000000000001, 'C')
    >>> table_lookup(0.356, table, -1)
    (0.20000000000000001, 'C')
    >>> table_lookup(0.256, table, +1)
    (0.40000000000000002, 'B')
    """
    table.sort()
    keys = [float(row[0]) for row in table]
    above = min((bisect(keys, value), len(table)-1))
    below = max((above - 1, 0))
    if direction==1:
        index = above
    elif direction==-1:
        index = below
    elif value-keys[below] < keys[above]-value:
        index = below
    else:
        index = above
    return table[index]

# Unit test:
# (just run the module to test, with "-v" if you want a report even if it passes)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

