from nltk import word_tokenize, pos_tag, ne_chunk

def getEntityTypes(text: str = ''):
  # print('getEntityTypes', text)
  chunks = ne_chunk(pos_tag(word_tokenize(text)))
  entities = []
  for chunk in chunks:
    try:
      entity = chunk.label()
    except Exception as e:
      entity = None
    if entity and entity not in ['GPE']:
    # if entity and entity not in entities:
      entities.append(entity)
  # print(entities)
  return entities

# print(getEntityTypes('testing this is Jeremy'))
