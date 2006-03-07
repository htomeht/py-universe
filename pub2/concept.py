# (C)2006 Terry Hancock
#---------------------------------------------------------------------------
# concept
"""
Concept provides sets of symbols used to label concepts. These are the
international 'words' used throughout the program to communicate concepts
which are localized in the semantics module for communication with the user.

There is a module-level container namespace, called simply "sym", which you
can use to refer to Concepts. This container is completely flat -- each Concept
must have a unique name within sym, to avoid confusion.

Nevertheless, there is a tree structure of "Concept Domains", to provide
a structure to the Concepts.

There are also two types of sets of Concepts -- "Vocabulary" and "Enum".

A "Vocabulary" is an extendable set of Concepts which must share a domain.  It
can be used as a container, or you can throw away the Vocabulary and use it simply
for the side-effect of loading sym with the resulting Concepts.

You can also "clear" a Vocabulary, which will not only remove the contents of
the Vocabulary object, but also delete all Concepts from its domain in the 
sym namespace.  This is pretty violent, and should be avoided (not that it is
not strictly true that all Concepts with the same domain are in the same Vocabulary,
but they will all be scrubbed anyway).

In fact, I really only recommend using "clear" for experimentation in the interpreter,
or in tests, where you want to start over.

An "Enum" is a closed set of Concepts.  We can use these to define flags and states
throughout the program, as well as for very limited vocabularies, such as "articles"
or "declension" particles, where we want to clarify that there are no additional
possibilities. Generally you can expect program code using Enums to hard-code the
values, while Vocabularies should be extensible.  Enum is immutable.

If you mutate an object being used as a hash, you viol

Some example uses:

>>> from concept import *
>>> sym.clear()
>>> Concept('PoS', doc="Part of Speech")
<!: PoS = Part of Speech>
>>> pos = Enum(sym.PoS, {'NOUN':'Noun', 'VERB':'Verb', 'ADVB':'Adverb', 'ADJE':'Adjective', 'DECL':'Declension particle', 'PREP':'Preposotion (topological)', 'ARTL':'Article', 'CONJ':'Conjunction', 'PUNC':'Punctuation symbol'})
>>> verbs = Vocabulary(sym.VERB, ('GO', 'WALK', 'MOVE', 'LOOK', 'GET', 'PUT'), "Basic motion and action verbs")
>>> sym.GO
<!/PoS/VERB: GO = Basic motion and action verbs>

That may be a bit bulky, but we can control the verbosity:

>>> Concept.verbosity = 0
>>> sym.GO
<GO>
>>> Concept.verbosity = 1
>>> sym.GO
<VERB: GO>
>>> Concept.verbosity = 2
>>> sym.GO
<!/PoS/VERB: GO>
>>> Concept.verbosity = 3
>>> sym.GO
<!/PoS/VERB: GO = Basic motion and action verbs>

Concepts are immutable and hashable, and can be used as dictionary keys,
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

>>> Concept.verbosity = 3
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
__all__ = ['sym', 'Concept', 'Vocabulary', 'Enum']

from sets import BaseSet, Set


class _ConceptRegistry(object):
    """
    Simple registry for holding symbols. Raises an error if an overwrite is
    attempted.  Some convenience functions provided for introspection.
    """
    def __setattr__(self, name, value):
        if name=='__dict__':
            object.__setattr__(self, name, value)
        elif hasattr(self, name):
            raise AttributeError, "Attempt to overwrite symbol '%s'" % name
        elif isinstance(value, Concept):
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
        return names

    def clear(self, domain=None):
        """
        Wipe out the symbol table.
        """
        #if self._lock: raise TypeError, "Immutable"

        if domain:
            self.__dict__ = dict([(k,v) for k,v in self.__dict__.items() if k[0]=='_' and domain not in v.domains()])
        else:
            self.__dict__ = dict([(k,v) for k,v in self.__dict__.items() if k[0]=='_'])

sym = _ConceptRegistry()

class Concept(object):
    """
    Abstract marker for the concept to which a word maps.

    Concepts are used as 'labels' for objects which are represented
    by topoworld or linguistic objects. Many concepts, however, have
    no actual model object, and are used inside the semantics engine,
    possibly for disambiguation or grammatical classification.
    """
    verbosity = 3
    __lock = False
    def __init__(self, name, domain=None, doc=''):
        self.name       = name
        self.domain     = domain
        self.doc        = doc
        self.vocabulary = None
        self.__lock     = True
        sym.add(self)

    def __hash__(self):
        return hash( (self.name, self.domain) )

    def __eq__(self, other):
        if not isinstance(other, Concept):
            return False
        if self.name==other.name and self.domain==other.domain:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __cmp__(self, other):
        raise TypeError, "Symbols are unordered"

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
        elif isinstance(self.domain, Concept):
            if self.verbosity > 1:
                return '%s/%s' % (self.domain._repr_domain(), self.domain.name)
            else:
                return '%s' % self.domain.name
        else:
            return repr(self.domain)

    def domains(self):
        if self.domain is None:
            return ()
        elif isinstance(self.domain, Concept):
            return self.domain.domains() + (self.domain.name,)
        else:
            return (str(self.domain),)

    def __setattr__(self, name, value):
        if name in ('doc', 'vocabulary'):
            # These are meta-data that are not part of concept's value
            object.__setattr__(self, name, value)
        elif self.__lock:
            raise AttributeError, "Instance is locked (Immutable)." 
        elif not self.__lock and (name=='_Concept__lock' or not name[0]=='_'):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError, "(lock=%s) Name %s can't be altered." % (self.__lock, name)


class Vocabulary(BaseSet):
    """
    Base of Vocabulary and Enumeration, Abstract, do not use directly.
    """
    __slots__ = ['domain', 'doc', '_lock']

    def __new__(cls, domain, names, doc=''):
        # We use '__new__' instead of '__init__' to ensure 1:1 mapping with domains.
        self = BaseSet.__new__(cls)
        if isinstance(domain, str):
            if hasattr(sym, domain):
                domain = getattr(sym, domain)
            else:
                domain = Concept(domain, doc=doc)
                
        if not isinstance(domain, Concept):
            raise AssertionError, "Only strings and concepts accepted as vocabulary domains."
            
        existing = domain.vocabulary
        if existing is None:
            # Concept exists, but doesn't link to a vocabulary, do so now:
            domain.vocabulary = self
           
        elif isinstance(domain.vocabulary, Enum):
            # Concept is domain of Enum (closed vocabulary, can't join):
            raise TypeError, "Cannot join closed Enum %s." % repr(domain)
            
        elif isinstance(domain.vocabulary, Vocabulary):
            # If there already exists a vocabulary with this
            # domain and it is open -- join with it:
            self = domain.vocabulary
        else:
            raise AssertionError, "When is a vocabulary not a vocabulary?: %s." % repr(domain.vocabulary)
            
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
            raise KeyError, "Concept %s already in vocabulary." % key
        elif hasattr(sym, key):
            raise KeyError, "Cannot redefine existing concept %s." % repr(getattr(sym, key))
        elif isinstance(key, Concept):
            self._data[key] = True
        elif isinstance(key, str):
            self._data[Concept(key, domain=self.domain, doc=doc)] = True
        else:
            raise KeyError, "Vocabularies only hold Concepts (or string to be coerced to Concept)."

    def __repr__(self):
        return "%s('%s', %s)" % (self.__class__.__name__, str(self.domain), repr([str(s) for s in list(self)]))

    def clear(self):
        """
        Clear not only empties the vocabulary, it also removes the concepts from the registry.
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
            data = [Concept(n, self.domain, names[n] + doc) for n in names]
        elif hasattr(names, '__iter__'):
            data = [Concept(n, self.domain, doc)            for n in names]
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
                domain = Concept(domain, doc=doc)
                
        if not isinstance(domain, Concept):
            raise AssertionError, "Only strings and concepts accepted as vocabulary domains."
            
        existing = domain.vocabulary
        if existing is None:
            # Concept exists, but doesn't link to a vocabulary, do so now:
            domain.vocabulary = self
        else:
            raise TypeError, "Enum cannot join existing vocabulary domain %s." % repr(existing)
            
        self._lock = False
        self.domain = domain
        self.doc = doc
        self.update(names)
        self._lock = True
        return self


#-QA----------------------------------------------------------------------------------

# Documentation generation for concepts and domains
#
# There's no clean way to generate documentation on the Concept/Domain tree, so
# I have to implement it here.  I've thought of using a real templating system,
# such as "simpletal", but it's not in the standard library, and I hesitate to
# add the dependency for this one use. If I see more applications for it, I might
# change this:

class ConceptDocumentor(object):
    html_frame = """\
<html>
<head>
<title>PUB - Concept Tree</title>
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
<td width="10%%"><i>Concept</i></td>
<td width="90%%"><i>Description</i></td>
</tr>
%(concept_table)s
</table>
</dd>
"""
    html_concept = """\
<tr valign="top">
<td><b>%(name)s</b></td>
<td>%(doc)s</td>
</tr>
"""
    def html(self):
        domain_set = {}
        for name in sym.lookup():
            domain_set[getattr(sym, name).domains()] = 1
        domain_list = domain_set.keys()
            
        domain_list.sort()  # I think the default sort does what we want (?)
       
        mn = {'docset_body':''}
        for domain_path in domain_list:
            fmt = {}

            if len(domain_path)==0:
                names = sym.lookup(domain='!')
            else:
                domain = getattr(sym, domain_path[-1])
                names = sym.lookup(domain=domain)

            names.sort()
            concepts = [getattr(sym, n) for n in names]
            
            fmt['concept_table'] = ''.join([self.html_concept % {'name':c.name, 'doc':c.doc}
                                            for c in concepts])
            if len(concepts)==0:
                fmt['domain_path'] = 'EMPTY DOMAIN?'
            else:
                fmt['domain_path'] = concepts[0]._repr_domain()
           
            mn['docset_body'] += self.html_domain % fmt

        return self.html_frame % mn 


# Test with doctest module
def _test():
    import doctest
    doctest.testmod()
if __name__ == "__main__":
    _test()
