#I18N/L14N notation in PUB:

#How about single-letter functions for:

# Part-of-Speech symbols:
Noun, Verb, Advb, Adje, Decl, Prep, Artl, Conj, Punc = range(9)

PoS_hint_inv =  {   Noun: ('noun',          'n',                    'N'),
                    Verb: ('verb',          'vb',                   'V'),
                    Adje: ('adjective',     'adje', 'adj',          'a'),
                    Advb: ('adverb',        'advb', 'adv',          'A'),
                    Artl: ('article',       'artl', 'art',          't'),
                    Prep: ('preposition',   'prep', 'prp',          'p'),
                    Decl: ('declension',    'decl', 'dec',          'd'),
                    Conj: ('conjunction',   'conj', 'con',          'c'),
                    Punc: ('punctuation',   'punct', 'pnct', 'punc','.'),
                    }
# Invert multi-map interprets hints:
PoS_hint = dict(sum( [[(h,pos) for h in hints] for pos,hints in PoS_hint_inv.items()],[])

PoS_precedence = (Noun, Verb, Advb, Adje, Decl, Prep, Artl, Conj, Punc)

def read_pos_hint(hint):
    if len(hint)>1:
        hint = hint.lower()
    return PoS_hint[hint]

def I(word, hint=None):
    """
    Internationalize a vocabulary word from a game.

    If given, the part-of-speech hint will ensure that
    the correct word is found (otherwise, the precedence
    order will be used to find the first match).
    """
    try:
        if not hint:
            for pos in PoS_precedence:
                symbol = locale.original.Vocabulary.i18n(word, pos)
        else:
            symbol = locale.original.Vocabulary.i18n(word,read_pos_hint(hint))
    except WordNotInVocabulary:    
        locale.original.log_missing_word(word, hint)
    return symbol

