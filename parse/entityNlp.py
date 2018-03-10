from nltk import word_tokenize, pos_tag, ne_chunk
sentence = "Mark and John are working at Google."
# chunks = ne_chunk(pos_tag(word_tokenize(sentence)))
# print(chunks)
# print(chunks[0].label())
# print(chunks[0].leaves())
# print(chunks[0][0])
# print(chunks[1])

def getEntityTypes(text: str = ''):
  print('getEntityTypes', text)
  chunks = ne_chunk(pos_tag(word_tokenize(text)))
  entities = []
  for chunk in chunks:
    print(chunk)
    try:
      entity = chunk.label()
    except Exception as e:
      entity = None
    if entity:
    # if entity and entity not in entities:
      entities.append(entity)
  # print(entities)
  return entities

print(getEntityTypes('testing this is Jeremy'))
