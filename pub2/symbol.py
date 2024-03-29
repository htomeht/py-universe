# (C)2006 Terry Hancock
#---------------------------------------------------------------------------
# symbol
"""
Symbol provides sets of symbols used to label concepts. These are the
international 'words' used throughout the program to communicate concepts
which are localized in the semantics module for communication with the user.

There is a module-level container namespace, called simply "sym", which you
can use to refer to Symbols. This container is completely flat -- each Symbol
must have a unique name within sym, to avoid confusion.

Nevertheless, there is a tree structure of "Symbol Domains", to provide
a structure to the Symbols.

There are also two types of sets of Symbols -- "Vocabulary" and "Enum".

A "Vocabulary" is an extendable set of Symbols which must share a domain.  It
can be used as a container, or you can throw away the Vocabulary and use it simply
for the side-effect of loading sym with the resulting Symbols.

You can also "clear" a Vocabulary, which will not only remove the contents of
the Vocabulary object, but also delete all Symbols from its domain in the 
sym namespace.  This is pretty violent, and should be avoided (not that it is
not strictly true that all Symbols with the same domain are in the same Vocabulary,
but they will all be scrubbed anyway).

In fact, I really only recommend using "clear" for experimentation in the interpreter,
or in tests, where you want to start over.

An "Enum" is a closed set of Symbols.  We can use these to define flags and states
throughout the program, as well as for very limited vocabularies, such as "articles"
or "declension" particles, where we want to clarify that there are no additional
possibilities. Generally you can expect program code using Enums to hard-code the
values, while Vocabularies should be extensible.  Enum is immutable.

If you mutate an object being used as a hash, you violate assumptions of the module.

Some example uses:

>>> from concepts import *
>>> sym.clear()
>>> Symbol('PoS', doc="Part of Speech")
<!: PoS = Part of Speech>
>>> pos = Enum(sym.PoS, {'NOUN':'Noun', 'VERB':'Verb', 'ADVB':'Adverb', 'ADJE':'Adjective', 'DECL':'Declension particle', 'PREP':'Preposotion (topological)', 'ARTL':'Article', 'CONJ':'Conjunction', 'PUNC':'Punctuation symbol'})
>>> verbs = Vocabulary(sym.VERB, ('GO', 'WALK', 'MOVE', 'LOOK', 'GET', 'PUT'), "Basic motion and action verbs")
>>> sym.GO
<!/PoS/VERB: GO = Basic motion and action verbs>

That may be a bit bulky, but we can control the verbosity:

>>> Symbol.verbosity = 0
>>> sym.GO
<GO>
>>> Symbol.verbosity = 1
>>> sym.GO
<VERB: GO>
>>> Symbol.verbosity = 2
>>> sym.GO
<!/PoS/VERB: GO>
>>> Symbol.verbosity = 3
>>> sym.GO
<!/PoS/VERB: GO = Basic motion and action verbs>

Symbols are immutable and hashable, and can be used as dictionary keys,
labels, etc. -- anywhere you might use an int or a string object:

>>> spam = {}
>>> sym.VERB
<!/PoS: VERB = Verb>
>>> spam[sym.VERB] = 1
>>> spam
{<!/PoS: VERB = Verb>: 1}

Enum sets can also be used as dictionary keys:

>>> spam = {}
>>> spam[pos] = 1
>>> spam
{Enum('PoS', ['PREP', 'PUNC', 'NOUN', 'ARTL', 'ADJE', 'DECL', 'CONJ', 'ADVB', 'VERB']): 1}

Nor can you add elements to an Enum -- it is a closed set:

>>> PoS['GARB'] = 1
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
NameError: name 'PoS' is not defined
>>> PoS.add('GARB')
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
NameError: name 'PoS' is not defined

But Vocabularies are mutable sets, so they can't be used as keys:

>>> spam = {}
>>> spam[verbs] = 1
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
  File "symbols.py", line 196, in __hash__
    raise TypeError, "Cannot hash (mutable) vocabulary"
TypeError: Cannot hash (mutable) vocabulary
>>>

But you can extend them:

>>> verbs.add("RUN", "Advanced motion verb")
>>> verbs.add("SWIM", "Move through the water")
>>> verbs.add("FLY", "Like a bird")
>>> verbs
Vocabulary('VERB', ['SWIM', 'WALK', 'PUT', 'GET', 'MOVE', 'GO', 'RUN', 'FLY', 'LOOK'])

Not that with this method, we gave the verbs individual doc strings:

>>> Symbol.verbosity = 3
>>> sym.SWIM
<!/PoS/VERB: SWIM = Move through the water>
>>> sym.FLY
<!/PoS/VERB: FLY = Like a bird>

Unlike the originals which used just the one string:

>>> sym.GO
<!/PoS/VERB: GO = Basic motion and action verbs>
>>> sym.WALK
<!/PoS/VERB: WALK = Basic motion and action verbs>

But that's just a shortcut. We could've defined verbs with unique strings if
we used a dictionary instead of a sequence to initialize the vocabulary --
in that case, the dictionary values are the doc strings. Observe:

>>> nouns = Vocabulary(sym.NOUN, { 'TREE':"Large woody plant", 'CACTUS':"Prickly desert plant", 'GRASS':"Blade-leafed ground cover"})
>>> nouns
Vocabulary('NOUN', ['GRASS', 'CACTUS', 'TREE'])
>>> sym.GRASS
<!/PoS/NOUN: GRASS = Blade-leafed ground cover>
>>> sym.CACTUS
<!/PoS/NOUN: CACTUS = Prickly desert plant>
>>> sym.TREE
<!/PoS/NOUN: TREE = Large woody plant>

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


__all__ = ['sym', 'Symbol', 'Vocabulary', 'Enum', 'Vague', 'VagueConcept', 'VagueDomain']

from sets import BaseSet, Set
from vague import *


class _SymbolRegistry(object):
    """
    Simple registry for holding symbols. Raises an error if an overwrite is
    attempted.  Some convenience functions provided for introspection.
    """
    def __setattr__(self, name, value):
        if name=='__dict__':
            object.__setattr__(self, name, value)
        elif hasattr(self, name):
            raise AttributeError, "Attempt to overwrite symbol '%s'" % name
        elif isinstance(value, Symbol):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError, "Symbol registry only holds Symbols."

    def __len__(self):
        return len([n for n in self.__dict__ if n[0]!='_'])

    def __repr__(self):
        return '<Symbol Registry: %d symbols defined>' % len(self)

    def add(self, symbol):
        setattr(self, symbol.name, symbol)

    def lookup(self, domain=None, match=''):
        names = []
        for name in self.__dict__:
            if name[0]!='_':
                if ((not domain or self.__dict__[name].domain==domain) or
                            (domain=='!' and self.__dict__[name].domain==None)):
                    if name[:len(match)]==match:
                        names.append(name)

        # 2006-06/27: change to return symbols instead of names:
        return [getattr(self, name) for name in names]

    def clear(self, domain=None):
        """
        Wipe out the symbol table.
        """
        #if self._lock: raise TypeError, "Immutable"

        if domain:
            self.__dict__ = dict([(k,v) for k,v in self.__dict__.items() if k[0]=='_' and domain not in v.domains()])
        else:
            self.__dict__ = dict([(k,v) for k,v in self.__dict__.items() if k[0]=='_'])

# We probably want to put the actual symbol registry into the persistant database?
# We also need to cope better with non-conflicting re-definitions
sym = _SymbolRegistry()

class Symbol(object):
    """
    Abstract marker for the symbol to which a word maps.

    Symbols are used as 'labels' for objects which are represented
    by topoworld or linguistic objects. Many symbols, however, have
    no actual model object, and are used inside the semantics engine,
    possibly for disambiguation or grammatical classification.
    """
    verbosity = 3
    __lock = False
    def __init__(self, name, domain=None, doc=''):
        if isinstance(domain, str):
            if hasattr(sym, domain):
                domain = getattr(sym, domain)
            else:
                domain = Symbol(domain, doc=doc)
                
        if domain and not isinstance(domain, Symbol):
            raise ValueError, "Only strings and symbols accepted as symbol domain."
            
        if not isinstance(name, str):
            raise ValueError("Symbol name should be a string (and valid identifier)")
 
        self.name       = name
        self.domain     = domain
        self.doc        = doc
        self.vocabulary = None
        self.__lock     = True
        sym.add(self)

    def __hash__(self):
        return hash( (self.name, self.domain) )

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        if self.name==other.name and self.domain==other.domain:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        return cmp(self.name, other.name)
        #raise TypeError, "Symbols are unordered"

    def __str__(self):
        return self.name
        
    def __repr__(self):
        if self.verbosity >= 3 and self.doc:
            return "<%s: %s = %s>" % (self._repr_domain(), self.name, self.doc)
        elif self.verbosity > 0:
            return "<%s: %s>"  % (self._repr_domain(), self.name)
        else:
            return "<%s>" % self.name

    def _repr_domain(self):
        # Recurse up domain tree to collect full domain path
        if self.domain is None:
            return '!'
        elif isinstance(self.domain, Symbol):
            if self.verbosity > 1:
                return '%s/%s' % (self.domain._repr_domain(), self.domain.name)
            else:
                return '%s' % self.domain.name
        else:
            return repr(self.domain)

    def domains(self):
        if self.domain is None:
            return ()
        elif isinstance(self.domain, Symbol):
            return self.domain.domains() + (self.domain.name,)
        else:
            return (str(self.domain),)

    def __setattr__(self, name, value):
        if name in ('doc', 'vocabulary'):
            # These are meta-data that are not part of symbol's value
            object.__setattr__(self, name, value)
        elif self.__lock:
            raise AttributeError, "Instance is locked (Immutable)." 
        elif not self.__lock and (name=='_Symbol__lock' or not name[0]=='_'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError, "(lock=%s) Name %s can't be altered." % (self.__lock, name)


class Vocabulary(BaseSet):
    """
    Vocabulary or mutable enumeration.
    """
    __slots__ = ['domain', 'doc', '_lock']

    def __new__(cls, domain, names, doc=''):
        # We use '__new__' instead of '__init__' to ensure 1:1 mapping with domains.
        self = BaseSet.__new__(cls)
        if isinstance(domain, str):
            if hasattr(sym, domain):
                domain = getattr(sym, domain)
            else:
                domain = Symbol(domain, doc=doc)
                
        if not isinstance(domain, Symbol):
            raise AssertionError, "Only strings and symbols accepted as vocabulary domains."
            
        existing = domain.vocabulary
        if existing is None:
            # Symbol exists, but doesn't link to a vocabulary, do so now:
            domain.vocabulary = self
           
        elif isinstance(domain.vocabulary, Enum):
            # Symbol is domain of Enum (closed vocabulary, can't join):
            raise TypeError, "Cannot join closed Enum %s." % repr(domain)
            
        elif isinstance(domain.vocabulary, Vocabulary):
            # If there already exists a vocabulary with this
            # domain and it is open -- join with it:
            self = domain.vocabulary
        else:
            raise AssertionError, "When is a vocabulary not a Vocabulary?: %s." % repr(domain.vocabulary)
            
        self._lock = False
        self.domain = domain
        self.doc = doc
        self.update(names)            
        
        return self
        
    def __init__(self, *args, **kw):
        # See __new__
        pass

    def __hash__(self):
        if self._lock:
            return hash((self.domain, BaseSet.__hash__(self) ))
        else:
            raise TypeError, "Cannot hash (mutable) vocabulary"

    def __setattr__(self, name, value):
        if name in ('_lock', 'doc'): # Mutable attributes can always be changed and don't affect hash
            BaseSet.__setattr__(self, name, value)
        elif self._lock:  # lock mechanism "politely immutable"
            raise AttributeError, "Instance is locked (Immutable)."
        else:  # if unlocked, can set anything.
            BaseSet.__setattr__(self, name, value)

    def __setitem__(self, key, doc):
        if self._lock: raise TypeError, "Immutable"

        if not isinstance(doc, str):
            doc = self.doc
        if key in self._data:
            raise KeyError, "Symbol %s already in vocabulary." % key
        elif hasattr(sym, key):
            raise KeyError, "Cannot redefine existing symbol %s." % repr(getattr(sym, key))
        elif isinstance(key, Symbol):
            self._data[key] = True
        elif isinstance(key, str):
            self._data[Symbol(key, domain=self.domain, doc=doc)] = True
        else:
            raise KeyError, "Vocabularies only hold Symbols (or string to be coerced to Symbol)."

    def __repr__(self):
        return "%s('%s', %s)" % (self.__class__.__name__, str(self.domain), repr([str(s) for s in list(self)]))

    def clear(self):
        """
        Clear not only empties the vocabulary, it also removes the symbols from the registry.
        """
        sym.clear(self.domain)
        self._data = {}

    def add(self, key, doc):
        # We don't bother to check the lock, because __setitem__ does.
        self[key] = doc

    def update(self, names, doc=None):
        """
        Update the list of names.
        """
        if self._lock: raise TypeError, "Immutable"

        if not doc:
            doc = self.doc
        
        if type(names)==dict:
            data = [Symbol(n, self.domain, names[n] + doc) for n in names]
        elif hasattr(names, '__iter__'):
            data = [Symbol(n, self.domain, doc)            for n in names]
        else:
            raise ValueError, "Vocabulary words must be in a collection object."

        self._data = {}
        if data is not None:
            self._update(data)


class Enum(Vocabulary):
    """
    An enum is an immutable set of symbols, or a closed vocabulary.
    """
    #
    # The only implementation differences for Enum from Vocabulary is that 
    # Enum has a different name, and the _lock is triggered. In particular,
    # it *is* possible (but unwise) to unlock an Enum.  Also, because
    # Enum's hash does not include the doc string, you can change the
    # doc string.
    #
    __slots__ = []
    def __new__(cls, domain, names, doc=''):
        # I hate pasting code, but there are several small changes from Vocabulary here
        self = BaseSet.__new__(cls)
        if isinstance(domain, str):
            if hasattr(sym, domain):
                domain = getattr(sym, domain)
            else:
                domain = Symbol(domain, doc=doc)
                
        if not isinstance(domain, Symbol):
            raise AssertionError, "Only strings and symbols accepted as vocabulary domains."
            
        existing = domain.vocabulary
        if existing is None:
            # Symbol exists, but doesn't link to a vocabulary, do so now:
            domain.vocabulary = self
        else:
            raise TypeError, "Enum cannot join existing vocabulary domain %s." % repr(existing)
            
        self._lock = False
        self.domain = domain
        self.doc = doc
        self.update(names)
        self._lock = True
        return self

# The remaining symbols in this module are "uncounted"/"non-enumerated" symbols
# (Strictly speaking even "floating point" numbers are "countable" on a computer,
# since there is a finite resolution and a finite range -- but it's best to treat
# them as uncounted real valued numbers. These symbols have the same type of
# behavior.

class VagueConcept(Vague, Symbol):
    """
    A Vague Concept occupies a domain, just as a Symbol does,
    and represents abstract knowledge. However, the value of a
    VagueConcept is not a member of an open or closed countable
    set, but rather, a point on the vague interval [-1,1].

    Therefore, we don't check VagueConcepts into the symbol
    registry (there's essentially an infinity of them, so it
    would get very unwieldy).  But we do check in their domains,
    and the vocabulary of VagueConcept domains will at least
    be given a marker class which can do a membership test.

    In PUB, of course, we only use this class for Adverbs,
    so you should see that class for specifics.
    """

    domain = None
    def __init__(self, value, domain=None):
        if isinstance(domain, str):
            if hasattr(sym, domain):
                domain = getattr(sym, domain)
            else:
                domain = Symbol(domain, doc=doc)
                
        if domain and not isinstance(domain, Symbol):
            raise ValueError, "Only strings and symbols accepted as symbol domain."
            
        if not isinstance(value, float) and not isinstance(value, Vague):
            raise ValueError("VagueConcept value must be a float or Vague")

        if not domain: domain = None

        self._data      = self._coerce(value)
        self.domain     = domain
        self.vocabulary = None
        self.__lock     = True
        
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "<%s:%7.4fv>" % (self._repr_domain(), self._data)

    def __hash__(self):
        return hash((self._data, self.domain))

    def __eq__(self, other):
        # Delete rich-compare properties of Symbol, so comparisons
        # will fall-through to Vague's __cmp__
        return NotImplemented

    def __ne__(self, other):
        # Delete rich-compare properties of Symbol, so comparisons
        # will fall-through to Vague's __cmp__
        return NotImplemented

class VagueDomain(object):
    """
    VagueDomain represents the 'vocabulary' of a domain with
    VagueConcepts in it.

    This is mostly a marker class, but we can test for validity
    of membership (an object must be a VagueConcept instance
    and have a matching domain to be considered a member).

    Since VagueDomains have an uncountably infinite number of
    members (technically this isn't true, because we don't really
    have "real numbers", but it's close enough for practical
    purposes), it would be silly to list all possible members,
    so representations use a rule-based notation.
    """
    domain = None
    def __init__(self, domain, doc=""):
        if isinstance(domain, str):
            if hasattr(sym, domain):
                domain = getattr(sym, domain)
            else:
                domain = Symbol(domain, doc=doc)
                
        if not isinstance(domain, Symbol):
            raise AssertionError, "Only strings and symbols accepted as vocabulary domains."
            
        existing = domain.vocabulary
        if existing is None:
            # Symbol exists, but doesn't link to a vocabulary, do so now:
            domain.vocabulary = self
        else:
            raise TypeError, "VagueDomain cannot join existing vocabulary domain %s." % repr(existing)
            
        self._lock = False
        self.domain = domain
        self.doc    = doc
        self._lock = True
        
    def __repr__(self):
        return "VagueDomain(%s)" % repr(self.domain)

    def __str__(self):
        return "<VagueDomain %s: x in [-1,1]>" % repr(self.domain)

    def __contains__(self, obj):
        """
        Containment test is rule-based.
        """
        if isinstance(obj, VagueConcept) and obj.domain==self.domain:
            return True
        else:
            return False

    def __len__(self):
        return 0

    def __nonzero__(self):
        return True
    
    
#-QA----------------------------------------------------------------------------------

# Documentation generation for symbols and domains
#
# There's no clean way to generate documentation on the Symbol/Domain tree, so
# I have to implement it here.  I've thought of using a real templating system,
# such as "simpletal", but it's not in the standard library, and I hesitate to
# add the dependency for this one use. If I see more applications for it, I might
# change this:

class SymbolDocumentor(object):
    html_frame = """\
<html>
<head>
<title>PUB - Symbol Tree</title>
<link rel="stylesheet" href="epydoc.css" type="text/css"></link>
</head>
<body bgcolor="white" text="black" link="blue" vlink="#204080" alink="#204080">
<h5><a href="../epydoc/index.html">Back to Developer's Index</a></h5>
<dl>
%(docset_body)s
</dl>
</body>
</html>
"""
    html_domain = """\
<dt><b>%(domain_path)s</b></dt>
<dd>
<table width="90%%" cellpadding="2" cellspacing="4" border="0" cols="2">
<tr valign="top">
<td width="10%%"><i>Symbol</i></td>
<td width="90%%"><i>Description</i></td>
</tr>
%(symbol_table)s
</table>
</dd>
"""
    html_symbol = """\
<tr valign="top">
<td><b>%(name)s</b></td>
<td>%(doc)s</td>
</tr>
"""
    def html(self):
        domain_set = {}
        for symbol in sym.lookup():
            domain_set[symbol.domains()] = 1
        domain_list = domain_set.keys()
            
        domain_list.sort()  # I think the default sort does what we want (?)
       
        mn = {'docset_body':''}
        for domain_path in domain_list:
            fmt = {}

            if len(domain_path)==0:
                symbols = sym.lookup(domain='!')
            else:
                domain = getattr(sym, domain_path[-1])
                symbols = sym.lookup(domain=domain)

            #symbols = [getattr(sym, n) for n in symbols]
            
            fmt['symbol_table'] = ''.join([self.html_symbol % {'name':c.name, 'doc':c.doc}
                                            for c in symbols])
            if len(symbols)==0:
                fmt['domain_path'] = 'EMPTY DOMAIN?'
            else:
                fmt['domain_path'] = symbols[0]._repr_domain()
           
            mn['docset_body'] += self.html_domain % fmt

        return self.html_frame % mn 


# Test with doctest module
def _test():
    import doctest
    doctest.testmod()
if __name__ == "__main__":
    _test()
