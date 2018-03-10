from nltk import word_tokenize, pos_tag, ne_chunk
sentence = "Mark and John are working at Google."
print(ne_chunk(pos_tag(word_tokenize(sentence))))
"""
(S
(PERSON Mark/NNP)
and/CC
(PERSON John/NNP)
are/VBP
working/VBG
at/IN
(ORGANIZATION Google/NNP)
./.)
"""
