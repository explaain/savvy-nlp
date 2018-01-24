#!/usr/bin/env python
import re, io, pprint, itertools, zipfile, untangle
from collections import OrderedDict
import xmljson
import urllib
from xmljson import parker, Parker
# bf = BadgerFish(dict_type=OrderedDict)
from xml.etree.ElementTree import fromstring
pp = pprint.PrettyPrinter(indent=1, width=160)

import kloudless
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

# Decide what to print out:
toPrint = {
  'fileList': True,
  'xmlString': False,
  'elements': False,
  'arrayOfPars': False,
  'justScores': False,
  'hierarchies': False,
  'hierarchyText': True
}


def listAccounts():
  accounts = kloudless.Account.all()
  return accounts

def getAccount(accountID):
  account = kloudless.Account(id=accountID)
  return account



def listFiles(accountInfo, after=False, number=500):
  account = getAccount(accountInfo['accountID'])
  recent = []
  if after:
    recent = account.recent.all(page_size=number, after=after)
  else:
    recent = account.recent.all(page_size=number)
  print('Number of Files:', len(recent))
  print('files: ', '\n'.join(list(map(lambda x: x['name'], recent))))
  files = [fileToAlgolia(f, accountInfo) for f in recent]
  return files

def getFile(accountInfo, fileID):
  account = getAccount(accountInfo['accountID'])
  f = {}
  try:
    f = account.files.retrieve(id=fileID)
    # Starting to add author info but need to fix permissions issue - team admin access?
    # print("f['owner']['id']", f['owner']['id'])
    # author = account.users.retrieve(id=f['owner']['id'])
    f = fileToAlgolia(f, accountInfo)
    print('file:')
    pp.pprint(f)
  except Exception as e:
    f = None
    print('Error getting file: "' + fileID + '"', e)
  return f

def getFileUrl(id, fileType):
  roots = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'https://docs.google.com/document/d/',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'https://docs.google.com/spreadsheets/d/',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'https://docs.google.com/presentation/d/',
    # 'application/pdf': 'https://drive.google.com/file/d/'
  }
  return (roots[fileType] if fileType in roots else 'https://drive.google.com/file/d/') + id

def fileToAlgolia(f, accountInfo):
  print('fileToAlgolia')
  print(f)
  pp.pprint(accountInfo)
  return {
    'objectID': f['id'],
    'url': getFileUrl(f['raw_id'], f['mime_type']),
    'rawID': f['raw_id'],
    'mimeType': f['mime_type'],
    'title': f['name'],
    'created': f['created'],
    'modified': f['modified'],
    'source': accountInfo['accountID']
  }

def fileToCard(f):
  name = f['name']
  card = {
    'card': {
      'content': {},
      'file': {
        'id': f['id'],
        'url': getFileUrl(f['raw_id'], f['mime_type']),
        'title': f['name'],
        'folder': 'Google Drive'
      },
      'objectID': f['id'][:12],
      'highlight': True
    }
  }
  return card

def getContent(accountInfo, fileID):
  fileData = getFile(accountInfo, fileID)
  if fileData:
    if fileData['mimeType'] == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      try:
        xmlContent = extractRawXMLContent(accountInfo, fileID)
        chunkHierarchy = xmlFindText(xmlContent)
        return chunkHierarchy
        pass
      except Exception as e:
        print(e)
        return ''
    elif fileData['mimeType'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
      csvContent = extractRawContent(accountInfo, fileData['rawID'], 'text/csv')
      contentArray = getCsvContentArray(csvContent)
      print(contentArray)
      return contentArray
  else:
    return None


def extractRawXMLContent(accountInfo, fileID):
  account = getAccount(accountInfo['accountID'])
  kfile = account.files.retrieve(fileID)
  content = kfile.contents().content
  z = zipfile.ZipFile(io.BytesIO(content))
  fileList = z.infolist()
  if toPrint['fileList']:
    pp.pprint(fileList)
  docs = [f for f in fileList if f.filename == 'word/document.xml'] # or f.filename == 'word/numbering.xml'] # or f.filename == 'word/styles.xml' or f.filename == 'word/setting.xml' or f.filename == 'word/theme1.xml' or f.filename == 'word/document.xml.rels'] # or 'xl' in f.filename]
  print(len(docs))
  xmlContent = []
  for doc in docs:
    xmlContent.append(z.read(doc).decode('utf-8'))
    if toPrint['xmlString']:
      print('join(xmlContent)')
      print(''.join(xmlContent))
  if len(xmlContent):
    return xmlContent[0]
  else:
    return ''

def xmlFindText(xmlContent):
  xml = untangle.parse(xmlContent)
  textArray = []
  ongoingCounter = []
  xmlSearchTextInChildren(xml, 0, textArray, ongoingCounter, { 'parFormatting': False, 'hyperlink': False })
  for t in textArray:
    t['ranking'] = sum(t['allRankings'].values())
  textArray = [chunk for chunk in textArray if len(chunk['content'])]
  if toPrint['arrayOfPars']:
    pp.pprint(textArray)
  if toPrint['justScores']:
    for t in textArray:
      print(t['ranking'], t['content'])
  chunkHierarchy = getChunkHierarchy(textArray)
  chunkHierarchy = completeContent(chunkHierarchy)
  if toPrint['hierarchies']:
    pp.pprint(chunkHierarchy)
  if toPrint['hierarchyText']:
    print(chunksToPrint(chunkHierarchy, 0))
  return chunkHierarchy

def chunksToPrint(chunks, layer = 0):
  printArray = []
  for chunk in chunks:
    content = ''.join(chunk['content'])
    content = content[:80] + '...' if len(content) > 80 else content
    if 'title' in chunk:
      content = chunk['title'] + ': ' + content
    printArray += [('    ' * layer) + content]
    if 'chunks' in chunk:
      printArray += chunksToPrint(chunk['chunks'], layer + 1)
  return printArray

def xmlSearchTextInChildren(xml, level, dataPassedDown, ongoingCounter, context):
  children = xml.__dict__['children'] or xml['children']
  spacing = ''.join([' ' for l in range(level)])
  if children is not None:
    for child in children:
      child.context = dict(context) # Is NOT a deep copy
    for i, child in enumerate(children):
      if toPrint['elements']:
        print(spacing, child)
      if child._name == 'w_p':
        chunkData = {
          'content': [],
          'allRankings': {},
          'otherContext': {}
        }
      else:
        chunkData = dataPassedDown
      if child._name == 'w_tbl':
        child.context['table'] = True
      if 'cdata' in child.__dict__ and child.__dict__['cdata'] and not child.__dict__['cdata'].isspace() and child._name != 'w_instrText':
        dataPassedDown['content'].append(child.__dict__['cdata'].strip())
        if child.context['hyperlink']:
          dataPassedDown['content'][-1] = '[' + dataPassedDown['content'][-1] + '](' + child.context['hyperlink'] + ')'
      if child._name == 'w_numPr':
        chunkData['otherContext']['numbered'] = True
      if child._name == 'w_pPr':
        child.context['parFormatting'] = True
      if child.context['parFormatting']:
        ranking = getRanking(child)
        if sum(ranking.values()) != 0:
          dataPassedDown['allRankings'] = {**dataPassedDown['allRankings'], **ranking}
      if hasattr(child, 'w_instrText') and 'cdata' in child.w_instrText.__dict__ and 'HYPERLINK' in child.w_instrText.__dict__['cdata'] and i < len(children) - 1:
        p = re.compile('HYPERLINK \"(.*)\"')
        children[i+1].context['hyperlink'] = p.search(child.w_instrText.__dict__['cdata']).group(1)
      try:
        xmlSearchTextInChildren(child, level + 1, chunkData, ongoingCounter, child.context)
      except Exception as e:
        print(e)
      if child._name == 'w_p':
        for prop in ['w_sz']:
          if prop not in chunkData['allRankings'] and len(dataPassedDown) and prop in dataPassedDown[-1]['allRankings']:
            chunkData['allRankings'][prop] = dataPassedDown[-1]['allRankings'][prop]
        dataPassedDown.append(chunkData)


def getRanking(el):
  ranking = 0
  if 'table' in el.context:
    ranking = -40 # Hack for the Contract doc
  if el._name == 'w_numPr':
    ranking = -10
  if el._name == 'w_numId' and el._attributes['w:val'] == "8": # Purely a hack for Contract doc
    ranking = 11
  if el._name == 'w_ilvl':
    ranking = -10 * int(el._attributes['w:val'])
  if el._name == 'w_ind':
    ranking = -1 * int(el._attributes['w:left']) / 20
  if el._name == 'w_sz':
    ranking = int(el._attributes['w:val'])
  if el._name == 'w_pStyle':
    style = el._attributes['w:val']
    styles = {
      'Title': 800,
      'Subtitle': 600,
      'Heading1': 400,
      'Heading2': 300,
      'Heading3': 200,
      'Heading4': 100,
      'Heading5': 60,
      'Heading6': 40
    }
    if style in styles:
      ranking = styles[style]
  if el._name == 'w_b' and el._attributes['w:val'] == '1':
    ranking = 10
  return {
    el._name: ranking
  }

def getChunkHierarchy(textArray):
  chunks = []
  base = 0
  for i, chunk in enumerate(textArray):
    if chunk['ranking'] >= textArray[base]['ranking'] and i > 0:
      if textArray[i-1]['ranking'] == chunk['ranking']:
        chunks.append(textArray[i-1])
      else:
        myChunk = textArray[base]
        myChunk['chunks'] = getChunkHierarchy(textArray[base+1:i])
        chunks.append(myChunk)
      base = i
    if i == len(textArray)-1:
      if textArray[i]['ranking'] == textArray[base]['ranking']:
        chunks.append(textArray[i])
      else:
        myChunk = textArray[base]
        myChunk['chunks'] = getChunkHierarchy(textArray[base+1:])
        chunks.append(myChunk)
    # if chunk['ranking'] < baseRanking and base == 0:
    #   base = i
  # if len(chunks) == 0:
  #   chunks = textArray
  return chunks

# Joins content arrays and adds numbering
def completeContent(chunks, parentNumber=False):
  for i, chunk in enumerate(chunks):
    chunk['content'] = ' '.join(chunk['content'])
    number = parentNumber
    if 'numbered' in chunk['otherContext']:
      number = (str(number) + '.' if number else '') + str(i + 1)
      chunk['title'] = number # + ' ' + chunk['content']
    if 'chunks' in chunk:
      chunk['chunks'] = completeContent(chunk['chunks'], number)
  return chunks

def extractRawContent(accountInfo, rawID, format):
  account = getAccount(accountInfo['accountID'])
  res = account.raw(raw_uri='/drive/v2/files/' + rawID + '/export?mimeType=' + urllib.parse.quote_plus(format), raw_method='GET')
  content = res.content.decode("utf-8")
  print(content)
  return content

def getCsvContentArray(csvContent):
  split = csvContent.split('\r\n')
  print(split)
  firstRow = split[0].split(',')
  contents = [ '\n'.join([(addColon(firstRow[i]) + ' ' + cell) for i, cell in enumerate(row.split(',')) if len(cell)]) for row in split[1:] ]
  print(contents)
  contentArray = [{'content': content, 'allRankings': {}, 'otherContext': {}, 'ranking': 0} for content in contents]
  return contentArray

def addColon(text):
  return text + ':' if not text.endswith(':') else text


# getContent({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'Fuaa5Yz9jDnCPgHNeoPGcIznjrdc80OsWyL97CFoAUM1x8LQQCI6EMAZKz0-vxZaT')


"""Below here is functions no longer used"""

def search(accountInfo, query):
  account = getAccount(accountInfo['accountID'])
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


"""Below here is stuff for testing"""

# search('', '', 'savvy')
# getContent('', '', 'FvsojaQrWWSNvuxbjS_hrw_fEVkEY8ykbb5kJh_cB-C_l-zw9ZnOEXZsq9HIp15dD')
# getContent('', '', 'FyjC21jL7Hy3j55_Ek-d5U_oSk3pt4e7zjAq30HGyD7MoWBYhUjgktG9t6aCzfkce')
