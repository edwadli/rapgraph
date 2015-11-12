
from nltk.corpus import cmudict
_DEBUG_ = False
# the basis of rhyme
transcr = cmudict.dict()
_NULL_ = '_NULL_'
phs = 'AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH\
    IY JH K L M N NG OW OY P R S SH T TH UH UW V W Y Z'.split()
phs_vowels = set('AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW'.split())


def tokenizeVerse(verse):
    # preprocessing
    verse = verse.strip().lower()
    # remove all symbols except letters, space, apostrophe
    accepted_chars = set('abcdefghijklmnopqrstuvwxyz \'\n')
    verse = ''.join(filter(accepted_chars.__contains__, verse))
    # separate string into lines
    lines = verse.split('\n')

    vocab = set()
    # build nested tokenized string
    verse_nested = []
    for line in lines:
        # separate each line into words
        words = line.split()
        verse_nested.append(words)
        # add word into vocabulary
        for word in words:
            vocab.add(word)
    return verse_nested, vocab


def phonemes(words):
    phonemes = {}
    for word in words:
        # get possible pronunciations from dict
        possible_pronunciations =  transcr.get(word, [[_NULL_]])
        if word not in transcr:
            # TODO: generate a guess on the pronunciation
            pass
        # strip out emphasis on vowels
        for pronunciation in possible_pronunciations:
            for i in range(len(pronunciation)):
                pronunciation[i] = ''.join(c for c in pronunciation[i] if not c.isdigit())
        # remove repeats
        possible_pronunciations = list(set([tuple(p) for p in possible_pronunciations]))
        phonemes[word] = possible_pronunciations
    return phonemes


def allPhonemePermutations(line, phoneme_dict, pos=0):
    if pos >= len(line):
        return []
    else:
        tail_permutations = allPhonemePermutations(line, phoneme_dict, pos+1)
        # cons all possible head word pronunciations
        all_permutations = []
        
        # helpful DEBUG warning message
        if _DEBUG_ and len(phoneme_dict[line[pos]]) > 2:
               print "Many Pronunciations Warning: " + line[pos]
               print phoneme_dict[line[pos]]
        
        for head_pronunciation in phoneme_dict[line[pos]]:
            # tag each phoneme with their word for later reconstruction
            head = [(phoneme, pos) for phoneme in head_pronunciation]
            if tail_permutations:
                for tail in tail_permutations:
                    all_permutations.append(head + tail)
            else:
                all_permutations.append(head)
        return all_permutations

def phonemeSimilarity(ph_a, ph_b):
    # Heuristic phoneme rhyming similarity in range [0, 1]    
    relative_score = 0.
    if ph_a == _NULL_ or ph_b == _NULL_:
        return 0.
    if ph_a == ph_b:
        # rhyme
        relative_score = 1.
    elif ph_a in phs_vowels:
        if ph_b in phs_vowels:
            # both vowels, likely to rhyme
            relative_score = 0.3
    elif ph_b not in phs_vowels:
        # both consonants, could help rhyme
        relative_score = 0.05
    return relative_score
    
    

def alignPhonemeSequences(a_seq, b_seq):
    # Smith-Waterman alignment with custom phoneme similarity scoring
    GAP_PENALTY = -1.
    MIN_SCORE = -10.
    MAX_SCORE = 10.
    score_range = MAX_SCORE - MIN_SCORE
    
    width = len(a_seq)+1
    height = len(b_seq)+1
    H = [[0] * width for i in range(height)]

    # Run the DP alg
    for row in range(1,height):
        for col in range(1,width):
            relative_score = phonemeSimilarity(a_seq[col-1], b_seq[row-1])
            align = H[row-1][col-1] + relative_score * score_range + MIN_SCORE
            deletion = H[row-1][col] + GAP_PENALTY
            insertion = H[row][col-1] + GAP_PENALTY
            H[row][col] = max(0, align, deletion, insertion)

    # extract the solution
    # find max value in H
    max_value = 0
    max_row = None
    max_col = None
    for row in range(height):
        for col in range(width):
            if H[row][col] >= max_value:
                max_value = H[row][col]
                max_row = row
                max_col = col
    # find path up/left/upleft
    # upleft = align (need to check if match or mismatch)
    # up = deletion in a_seq
    # left = insertion in a_seq
    alignment = []
    while max_row > 0 and max_col > 0:
        corner = H[max_row-1][max_col-1]
        up = H[max_row-1][max_col]
        left = H[max_row][max_col-1]
        
        if left>corner and left>up:
            max_col -= 1
        elif up>corner and up>left:
            max_row -= 1
        else: # corner>up and corner>left
            max_row -= 1
            max_col -= 1
            if phonemeSimilarity(a_seq[max_col], b_seq[max_row]) > 0.5:
                alignment.append((max_col, max_row))
        
    return max_value, alignment


def alignRhyme(line_a, line_b, phoneme_dict):
    # get all possible ways to pronounce the line
    possible_a_seqs = allPhonemePermutations(line_a, phoneme_dict)
    possible_b_seqs = allPhonemePermutations(line_b, phoneme_dict)
    # select best alignment of these permutations
    max_score = float('-inf')
    best_alignment = []
    best_a = None
    best_b = None
    for a_seq in possible_a_seqs:
        for b_seq in possible_b_seqs:
            score, alignment = alignPhonemeSequences([p[0] for p in a_seq], [p[0] for p in b_seq])
            if score >= max_score:
                max_score = score
                best_alignment = alignment
                best_a = a_seq
                best_b = b_seq
    # convert from alignment between phonemes to alignment between words
    rhyme_alignment = {}
    for (i_a, i_b) in best_alignment:
        i_word_a = best_a[i_a][1]
        i_word_b = best_b[i_b][1]
        word_pair = (i_word_a, i_word_b)
        if word_pair not in rhyme_alignment:
            rhyme_alignment[word_pair] = 0
        rhyme_alignment[word_pair] += 1
    rhyme_alignment = [(pair[0], pair[1], rhyme_alignment[pair]) for pair in rhyme_alignment]
    return rhyme_alignment


def wordLinks(verse):
    verse_nested, vocab = tokenizeVerse(verse)
    phoneme_dict = phonemes(vocab)
    # get build rhyming graph: words=nodes, rhymes=edges
    word_links = []
    if len(verse_nested) > 1:
        prev_line = verse_nested[0]
        for i in range(1, len(verse_nested)):
            curr_line = verse_nested[i]
            # get rhyme alignment for these two lines
            rhyme_alignment = alignRhyme(prev_line, curr_line, phoneme_dict)
            word_links.append(rhyme_alignment)
            # shift for next iteration
            prev_line = curr_line
        
    return verse_nested, word_links, phoneme_dict

def inlineRhyme(line, phoneme_dict):
    # greedy forward pass
    links = []
    for pos in range(len(line)-1):
        word = line[pos]
        # note that this method doesnt capture all multiword rhymes
        # we can capture a little more if we also do a backward pass
        alignment = alignRhyme([word], line[pos+1:], phoneme_dict)
        links += [(pos_a+pos, pos_b+pos+1,wt) for (pos_a, pos_b, wt) in alignment if wt > 1]
    return links

def analyzeRap(verse):
    # get rhyme graph
    verse_nested, word_links, phoneme_dict = wordLinks(verse)
    inline_links = [inlineRhyme(line, phoneme_dict) for line in verse_nested]
    # save to beaker
    beaker = {}
    beaker['words'] = verse_nested # list of list of words
    beaker['rhymes'] = word_links # list of list of (wordindex, wordindex, multiplicity)
    beaker['inlines'] = inline_links # list of list of (wordindex, wordindex, weight)
    return beaker

def incrementalAnalyzeRap(verse):
    # yield partial results line by line
    verse_nested, vocab = tokenizeVerse(verse)
    phoneme_dict = phonemes(vocab)

    prev_line = []
    for i in range(len(verse_nested)):
        curr_line = verse_nested[i]
        # get rhyme alignment for these two lines
        rhyme_alignment = alignRhyme(prev_line, curr_line, phoneme_dict)
        # get inline rhyme alignment for the current line
        inline_alignment = inlineRhyme(curr_line, phoneme_dict)
        # yield result for that line of the verse
        yield {
            'words': curr_line,
            'rhymes': rhyme_alignment,
            'inlines': inline_alignment
        }
        # shift for next iteration
        prev_line = curr_line
