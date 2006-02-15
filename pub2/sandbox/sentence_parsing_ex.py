verb_words = ('hit', 'walk', 'talk', 'use', 'get')
noun_words = ('nail', 'hammer', 'book', 'broom', 'broom closet')
adje_words = ('red', 'blue', 'old', 'new', 'shiny', 'rusty')
decl_words = ('to', 'from', 'towards', 'away from', 'using', 'with')
prep_words = ('on', 'in', 'over', 'under', 'below', 'beneath', 'behind', 'in front of')
arti_words = ('a', 'the')
advb_words = ('quickly', 'slowly', 'lightly', 'heavily', 'strongly', 'weakly')
conj_words = (',', '&', 'and', 'then')

def classify_vocabulary():
    vocabulary = {}
    sources = { 'V':verb_words,
                'A':advb_words,
                'N':noun_words,
                'a':adje_words,
                'd':decl_words,
                'p':prep_words,
                't':arti_words,
                'x':conj_words  }
    for code, source in sources.items():
        for word in source:
            # print "ADDING WORD: %s -> %s" % (word,code)
            if not vocabulary.has_key(word):
                vocabulary[word]=[code, '', []]
            else:
                vocabulary[word][0] += code
            partials = word.split()
            if len(partials)>1:
                for partial in partials:
                    # print "ADDING PARTIAL: %s -> %s" % (partial,code)
                    if not vocabulary.has_key(partial):
                        vocabulary[partial]=['', code, [word]]
                    else:
                        vocabulary[partial][1] += code
                        vocabulary[partial][2].append(word)
    return vocabulary

c_voc = classify_vocabulary()

partials_words = [w for w,c in c_voc.items() if c[1]]

for word in partials_words:
    print word, c_voc[word]
             
classify_vocabulary()

def classify_words(sentence_words):
    """
    Create a classifier string object which can be used to find part-of-speech
    patterns in a sentence.
    """
    classifier = []
    for i, word in sentence_words:
        c = ''
        if   word in verb_words: c += 'V'
        elif word in advb_words: c += 'A'
        elif word in noun_words: c += 'N'
        elif word in adje_words: c += 'a'
        elif word in decl_words: c += 'd'
        elif word in prep_words: c += 'p'
        elif word in conj_words: c += 'x'
        elif word in artl_words: c += 't'
        classifier.append("<%3.3d|%s>" % (i, c))
        
    return ' '.join(classifier)

recog_words = dict([(c,r'(<(\d\d\d)\|\w*%s\w*>)' % c) for c in "VANadpxt"])

noun_phrase = r"(%(p)s|%(d)s)?%(t)s?%(a)s*%(N)s" % recog_words


