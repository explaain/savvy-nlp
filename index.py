#!/usr/bin/env python
import pprint, datetime, sched, time
from random import *
from algoliasearch import algoliasearch
from parse import drives
import xmljson
pp = pprint.PrettyPrinter(indent=4)

# Decides whether we're in testing mode or not
Testing = False

# Decide what to print out:
toPrint = {
  'cardsCreated': True
}

client = algoliasearch.Client('D3AE3TSULH', '1b36934cc0d93e04ef8f0d5f36ad7607') # This API key allows everything
algoliaSourcesIndex = client.init_index('sources')

def algoliaGetFilesIndex(organisationID: str):
  algoliaFilesIndex = client.init_index(organisationID + '__Files')
  return algoliaFilesIndex

def algoliaGetCardsIndex(organisationID: str):
  algoliaCardsIndex = client.init_index(organisationID + '__Cards')
  return algoliaCardsIndex

def addSource(data: dict):
  """This is for when a user adds a new source,
  such as connecting up their Google Drive.
  It automatically indexes all files after connecting.
  """

  print('data:', data)
  source = {
    'objectID': data['source']['account']['id'],
    'organisationID': data['organisationID'],
    'addedBy': data['source']['account']['account']
  }
  print('source:', source)
  algoliaSourcesIndex.add_object(source)

  # Index all files from source
  accountInfo = {
    'organisationID': source['organisationID'],
    'accountID': source['objectID']
  }
  time.sleep(5)
  indexFiles(accountInfo, False, True)
  return source

def indexAll():
  """Indexes all files since last memory update""" # Currently, all sources had the same Last Update Time stored
  accounts = drives.listAccounts()
  memory = open('memory.txt','r')
  lastRefreshTime = datetime.datetime.strptime(memory.read().splitlines()[0], '%Y-%m-%d %H:%M:%S.%f')
  print(lastRefreshTime)
  thisRefreshTime = str(datetime.datetime.now())
  for account in accounts:
    print(account)
    accountID = account['id']
    source = False
    try:
      source = algoliaSourcesIndex.getObject(accountID)
    except Exception as e:
      print('Couldn\'t find Algolia record for this source - skipping.', e)
    if source:
      organisationID = source['organisationID']
      accountInfo = {
        'organisationID': organisationID,
        'accountID': accountID
      }
      indexFiles(accountInfo, after=lastRefreshTime)
  memory = open('memory.txt','w') # Happens now so that incomplete indexing doesn't overwrite lastRefreshTime
  memory.write(thisRefreshTime)

def indexFiles(accountInfo, after, allFiles=False):
  """Indexes files from a query based on criteria given"""
  print(accountInfo)
  print(after)
  print(allFiles)
  if allFiles:
    print('Mytest 1')
    files = drives.listFiles(accountInfo)
  else:
    files = drives.listFiles(accountInfo, after=after)
  pp.pprint([f['title'] for f in files])
  pp.pprint(files)

  for f in files:
    indexFile(accountInfo, f['objectID']) # We index them again because they seem to first come in with their original names e.g. "Untitled document"

def indexFile(accountInfo, fileID: str):
  f = drives.getFile(accountInfo, fileID=fileID)
  if f is not None:
    print('Not None')
    # pp.pprint(f)
    algoliaFilesIndex = algoliaGetFilesIndex(accountInfo['organisationID'])
    algoliaFilesIndex.add_object(f)
    createFileCard(accountInfo, f)
    if f['mimeType'] in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
      indexFileContent(accountInfo, f)
    else:
      if 'doc' in f['mimeType']:
        print('"doc" was found in:', f['mimeType'])

def indexFileContent(accountInfo, f):
  print(f)
  # Delete all chunks from file
  params = {
    'filters': 'type: "p" AND fileID: "' + f['objectID'] + '"'
  }
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  algoliaCardsIndex.delete_by_query('', params) # Is this dangerous???

  print('Deleted')

  # Create new cards
  contentArray = drives.getContent(accountInfo, f['objectID'], True) # Should only take first one!!!
  cards = createCardsFromContentArray(accountInfo, contentArray, f)['allCards']
  print('Number of Cards:', len(cards))
  if toPrint['cardsCreated']:
    pp.pprint(cards)

def createFileCard(accountInfo, f):
  card = {
    'type': 'file',
    'objectID': f['objectID'],
    'title': f['title'],
    'fileID': f['objectID'],
    'fileUrl': f['url'],
    'fileType': f['mimeType'],
    'fileTitle': f['title'],
    'created': f['created'],
    'modified': f['modified'],
  }
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  algoliaCardsIndex.add_object(card)
  print('File Card Created!')
  pp.pprint(card)


def createCardsFromContentArray(accountInfo, contentArray, f, parentContext=[]):
  # print('createCardsFromContentArray')
  # print('contentArray', contentArray)
  cards = []
  allCards = []
  for i, chunk in enumerate(contentArray):
    card = {
      'type': 'p',
      'content': chunk['content'],
      'fileID': f['objectID'],
      'fileUrl': f['url'],
      'fileType': f['mimeType'],
      'fileTitle': f['title'],
      'context': parentContext,
      'created': f['created'],
      'modified': f['modified'],
      'index': i
    }
    if 'title' in chunk:
      card['title'] = chunk['title']
      if len(parentContext) > 1 and parentContext[0] == 'AGREED TERMS':
        card['title'] = 'Clause ' + card['title'] # Hack for Clauses in Contract
    if 'chunks' in chunk:
      context = parentContext + [chunk['content']]
      subdata = createCardsFromContentArray(accountInfo, chunk['chunks'], f, context)
      subcards = subdata['cards']
      allCards += subdata['allCards']
      card['listItems'] = [c['objectID'] for c in subcards]
      card['listCards'] = [c['content'] for c in subcards]
    cards.append(card)
    allCards.append(card)
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  cardIDs = []
  try:
    if Testing:
      cardIDs = { 'objectIDs': [randint(1, 1000000000000) for c in cards] } # Use this when testing to avoid using up Algolia operations!!
    else:
      cardIDs = algoliaCardsIndex.add_objects(cards)
  except Exception as e:
    print('Something went wrong saving this card to Algolia:' + f['title'])
    print(e)
  # print(cardIDs['objectIDs'])
  for i, objectID in enumerate(cardIDs['objectIDs']):
    cards[i]['objectID'] = objectID
  return {
    'cards': cards, # Cards on this level
    'allCards': allCards # Cards passed up that should continue being passed
  }


s = sched.scheduler(time.time, time.sleep)
minsInterval = 10

def reIndex():
  indexAll()
  s.enter(60 * minsInterval, 1, reIndex)

def startIndexing():
  indexAll()
  s.enter(60 * minsInterval, 1, reIndex)
  s.run()



"""Below here is stuff for testing"""

# accountInfo = {
#   'accountID': '284119499',
#   'organisationID': 'tickbox'
# }
# indexFiles(accountInfo, False, True)

# indexAll()
# indexFiles({
#   'organisationID': 'askporter',
#   'accountID': '284151319'
# }, allFiles=True, after=None)
# indexFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'FrgFloBV1hJZbWdgYDHIX9d6fL8IfaJ1lQzMiov53_HFhS7IKTeNrexpdc2xUbeYi')
# indexFile({
#   'organisationID': 'askporter',
#   'accountID': '284151319'
# }, 'FtORrzfQkKOM6NOR_ZgkDcBmP258Sne-HAMXW32x2F29Xr1VGyK2JKsqCq0eu704P')
# indexFileContent({'objectID': 'FVNDMMXfVj99RqJMyz1xiFpk63kKA44NqCKEKimaUF1F63QxFJmvnRuuGKN2JyLXY', 'title': 'Policy Tracker for GE2017.com', 'modified': '1499418614', 'created': 'null'})


# xmlstring = open('parse/sample3.xml').read()
# # print(xmlstring)
# drives.xmlFindText(xmlstring)
