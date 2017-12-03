#!/usr/bin/env python
import re, io, pprint, itertools, zipfile
pp = pprint.PrettyPrinter(indent=4)

import kloudless
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')
account = kloudless.Account.all()[0]

def getContent(organisationID, user, fileID, asArray=False):
  kfile = account.files.retrieve(fileID)
  content = kfile.contents().content
  try:
    z = zipfile.ZipFile(io.BytesIO(content))
    fileList = z.infolist()
    docs = [f for f in fileList if f.filename == 'word/document.xml']
    if len(docs):
      doc = docs[0]
      xmlContent = z.read(doc).decode('utf-8')
      print(xmlContent)
      reg = re.findall('>([^<>]*)<', xmlContent)
      contentArray = [r for r in reg if len(r) > 0 and r != '\r']
      if asArray:
        return contentArray
      else:
        content = ' '.join(contentArray)
        return content
    else:
      return ''
    pass
  except Exception as e:
    return ''

def search(organisationID, user, query):
  print(query)
  queries = query.split()[:8] # Max 8 words
  split = lambda A, n=2: [' '.join(str(x) for x in A[i:i+n]) for i in range(0, len(A), n)]
  queries = split(queries)
  print('\n\nqueries\n', queries)
  allResultsLists = list(map(lambda x: account.search.all(q=x), queries))
  files = []
  for resultsList in allResultsLists:
    for result in resultsList:
      if not any(f['id'] == result['id'] for f in files):
        files.append(result)
  pp.pprint('\n\nfiles:\n' + '\n'.join(list(map(lambda x: x['name'], files))))
  # pp.pprint(list(map(lambda x: x['name'], files)))
  # pp.pprint(files)
  cards = list(map(fileToCard, files))
  return cards

def listfiles(organisationID, user, after, number=100):
  print(after)
  recent = account.recent.all(page_size=number, after=after)
  pp.pprint(len(recent))
  pp.pprint('files:' + '\n'.join(list(map(lambda x: x['name'], recent))))
  files = [fileToAlgolia(f) for f in recent]
  return files

def getfile(organisationID, user, fileID):
  f = account.files.retrieve(id=fileID)
  print('file:')
  pp.pprint(f)
  return fileToAlgolia(f)

def fileToAlgolia(f):
  print(f)
  return {
    'objectID': f['id'],
    'url': 'https://docs.google.com/document/d/' + f['raw_id'],
    'mimeType': f['mime_type'],
    'title': f['name'],
    'created': f['created'],
    'modified': f['modified'],
  }

def fileToCard(f):
  name = f['name']
  card = {
    'card': {
      'content': {},
      'file': {
        'id': f['id'],
        'url': 'https://docs.google.com/document/d/' + f['raw_id'], # Only works for docs currently
        'title': f['name'],
        'folder': 'Google Drive'
      },
      'objectID': f['id'][:12],
      'highlight': True
    }
  }
  return card

# search('', '', 'savvy')


# getContent('', '', 'FvsojaQrWWSNvuxbjS_hrw_fEVkEY8ykbb5kJh_cB-C_l-zw9ZnOEXZsq9HIp15dD')
# getContent('', '', 'FyjC21jL7Hy3j55_Ek-d5U_oSk3pt4e7zjAq30HGyD7MoWBYhUjgktG9t6aCzfkce')
