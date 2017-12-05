#!/usr/bin/env python
import re, io, pprint, itertools, zipfile, json, untangle
from collections import OrderedDict
import xmljson
from xmljson import parker, Parker
# bf = BadgerFish(dict_type=OrderedDict)
from xml.etree.ElementTree import fromstring
pp = pprint.PrettyPrinter(indent=1)

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
      xml = xmlFindText(xmlContent)
      print('xml', xml)
      return xml
      # reg = re.findall('>([^<>]*)<', xmlContent)
      # contentArray = [r for r in reg if len(r) > 0 and r != '\r']
      # if asArray:
      #   return contentArray
      # else:
      #   content = ' '.join(contentArray)
      #   return content
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

# def xmlFindText(xmlContent):
#   obj = json.loads(json.dumps(parker.data(fromstring(xmlContent))).replace('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}',''))
#   pp.pprint(obj)
#   textArray = []
#   ongoingCounter = []
#   xmlSearchTextInChildren(obj, None, 0, textArray, ongoingCounter)
#   print('textArray')
#   pp.pprint(textArray)
#
#   # For comparison:
#   reg = re.findall('>([^<>]*)<', xmlContent)
#   # print([r for r in reg if len(r) > 0 and r != '\r'])

# def xmlSearchTextInChildren(obj, parentKeyOrItem, level, arrayPassedDown, ongoingCounter):
#   # print(level)
#   try:
#     for keyOrItem in obj:
#       # print('level:', level, ', keyOrItem:', keyOrItem)
#
#       if keyOrItem == '$':
#         ongoingCounter.append(len(ongoingCounter))
#         print({level: obj[keyOrItem]})
#         arrayPassedDown.append({level: obj[keyOrItem]})
#       if parentKeyOrItem == 'p':
#         arrayPassedDown = []
#       nextObj = keyOrItem if isinstance(keyOrItem, dict) or isinstance(keyOrItem, list) else (obj[keyOrItem] if isinstance(obj, dict) else None)
#       # print('nextObj', nextObj)
#       if isinstance(nextObj, dict) or isinstance(nextObj, list):
#         print(ongoingCounter, keyOrItem)
#         xmlSearchTextInChildren(nextObj, keyOrItem, level + 1, arrayPassedDown, ongoingCounter)
#       # else:
#       #   print('stopped')
#
#       if parentKeyOrItem == 'p':
#         textArray = arrayPassedDown
#         print('textArray1')
#         pp.pprint(textArray)
#   except Exception as e:
#     print(e)


def xmlFindText(xmlContent):
  xml = untangle.parse(xmlContent)
  textArray = []
  ongoingCounter = []
  xmlSearchTextInChildren(xml, 0, textArray, ongoingCounter, { 'parFormatting': False, 'hyperlink': False })
  textArray = [chunk for chunk in textArray if len(chunk['content'])]
  print('textArray')
  pp.pprint(textArray)
  chunkHierarchy = getChunkHierarchy(textArray)
  pp.pprint(chunkHierarchy)
  return chunkHierarchy

def xmlSearchTextInChildren(xml, level, dataPassedDown, ongoingCounter, context):
  children = xml.__dict__['children'] or xml['children']
  spacing = ''.join([' ' for l in range(level)])
  if children is not None:
    for child in children:
      child.context = dict(context) # Is NOT a deep copy
    for i, child in enumerate(children):
      print(spacing, child)
      if child._name == 'w_p':
        chunkData = {
          'content': [],
          'ranking': 0
        }
      else:
        chunkData = dataPassedDown

      if 'cdata' in child.__dict__ and child.__dict__['cdata'] and not child.__dict__['cdata'].isspace() and child._name != 'w_instrText':
        dataPassedDown['content'].append(child.__dict__['cdata'].strip())
        if child.context['hyperlink']:
          dataPassedDown['content'][-1] = '[' + dataPassedDown['content'][-1] + '](' + child.context['hyperlink'] + ')'
      if child._name == 'w_pPr':
        child.context['parFormatting'] = True
      if child.context['parFormatting']:
        dataPassedDown['ranking'] += getRanking(child)
      if hasattr(child, 'w_instrText') and 'cdata' in child.w_instrText.__dict__ and 'HYPERLINK' in child.w_instrText.__dict__['cdata'] and i < len(children) - 1:
        p = re.compile('HYPERLINK \"(.*)\"')
        children[i+1].context['hyperlink'] = p.search(child.w_instrText.__dict__['cdata']).group(1)
      try:
        xmlSearchTextInChildren(child, level + 1, chunkData, ongoingCounter, child.context)
      except Exception as e:
        print(e)
      if child._name == 'w_p':
        dataPassedDown.append(chunkData)


def getRanking(el):
  ranking = 0
  if el._name == 'w_numPr':
    ranking = -10
  if el._name == 'w_sz': # Doesn't appear to work on headings?
    ranking = int(el._attributes['w:val'])
  if el._name == 'w_pStyle':
    print('w_pStyle w_pStyle')
    style = el._attributes['w:val']
    styles = {
      'Heading1': 400,
      'Heading2': 300,
      'Heading3': 200,
      'Heading4': 100,
      'Heading5': 60,
      'Heading6': 40
    }
    print('style', style)
    if style in styles:
      ranking = styles[style]
  if el._name == 'w_b' and el._attributes['w:val'] == '1':
    ranking = 10
  return ranking

def getChunkHierarchy(textArray):
  print('getChunkHierarchy')
  print(textArray)
  chunks = []
  base = 0
  for i, chunk in enumerate(textArray):
    print(chunk['ranking'])
    if chunk['ranking'] >= textArray[base]['ranking'] and i > 0:
      print('go!!', base+1, i)
      if textArray[i-1]['ranking'] == chunk['ranking']:
        chunks.append(textArray[i-1])
      else:
        print(textArray[base+1:i])
        myChunk = textArray[base]
        myChunk['chunks'] = getChunkHierarchy(textArray[base+1:i])
        chunks.append(myChunk)
      base = i
    if i == len(textArray)-1:
      print('end!!', base+1, i)
      if textArray[i]['ranking'] == textArray[base]['ranking']:
        chunks.append(textArray[i])
      else:
        print(textArray[base+1:])
        myChunk = textArray[base]
        myChunk['chunks'] = getChunkHierarchy(textArray[base+1:])
        chunks.append(myChunk)
    # if chunk['ranking'] < baseRanking and base == 0:
    #   base = i
  # if len(chunks) == 0:
  #   chunks = textArray
  return chunks



# search('', '', 'savvy')
# getContent('', '', 'FvsojaQrWWSNvuxbjS_hrw_fEVkEY8ykbb5kJh_cB-C_l-zw9ZnOEXZsq9HIp15dD')
# getContent('', '', 'FyjC21jL7Hy3j55_Ek-d5U_oSk3pt4e7zjAq30HGyD7MoWBYhUjgktG9t6aCzfkce')
