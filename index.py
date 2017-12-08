#!/usr/bin/env python
import pprint, datetime, sched, time
from algoliasearch import algoliasearch
from parse import drives
import xmljson
pp = pprint.PrettyPrinter(indent=4)

client = algoliasearch.Client('D3AE3TSULH', '1b36934cc0d93e04ef8f0d5f36ad7607') # This API key allows everything
algoliaSourcesIndex = client.init_index('sources')

def algoliaGetFilesIndex(organisationID):
  algoliaFilesIndex = client.init_index(organisationID + '__Files')
  return algoliaFilesIndex

def algoliaGetCardsIndex(organisationID):
  algoliaCardsIndex = client.init_index(organisationID + '__Cards')
  return algoliaCardsIndex

def addSource(data):
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
  indexFiles(accountInfo, False, True)
  return source

def indexAll():
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
  if allFiles:
    files = drives.listfiles(accountInfo)
  else:
    files = drives.listfiles(accountInfo, after=after)
  pp.pprint([f['title'] for f in files])
  pp.pprint(files)

  for f in files:
    indexFile(accountInfo, f['objectID']) # We index them again because they seem to first come in with their original names e.g. "Untitled document"

def indexFile(accountInfo, fileID):
  f = drives.getfile(accountInfo, fileID=fileID)
  pp.pprint(f)
  algoliaFilesIndex = algoliaGetFilesIndex(accountInfo['organisationID'])
  algoliaFilesIndex.add_object(f)
  indexFileContent(accountInfo, f)

def indexFileContent(accountInfo, f):
  print(f)
  # Delete all chunks from file
  params = {
    'filters': 'fileID: "' + f['objectID'] + '"'
  }
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  algoliaCardsIndex.delete_by_query('', params)

  # Create new chunks
  contentArray = drives.getContent(accountInfo, f['objectID'], True) # Should only take first one!!!
  print('contentArray', contentArray)
  cards = createCardsFromContentArray(accountInfo, contentArray, f)['allCards']
  # print(cards)
  pp.pprint(cards)


def createCardsFromContentArray(accountInfo, contentArray, f):
  print('createCardsFromContentArray')
  print('contentArray', contentArray)
  cards = []
  allCards = []
  for i, chunk in enumerate(contentArray):
    card = {
      'content': ' '.join(chunk['content']),
      'fileID': f['objectID'],
      'fileTitle': f['title'],
      'created': f['created'],
      'modified': f['modified'],
      'type': 'p',
      'index': i
    }
    if 'chunks' in chunk:
      subdata = createCardsFromContentArray(accountInfo, chunk['chunks'], f)
      subcards = subdata['cards']
      allCards += subdata['allCards']
      card['listItems'] = [c['objectID'] for c in subcards]
      card['listCards'] = [c['content'] for c in subcards]
    cards.append(card)
    allCards.append(card)
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  cardIDs = algoliaCardsIndex.add_objects(cards)
  print(cardIDs['objectIDs'])
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


# indexAll()
# indexFiles()
# indexFile('FB1p0q-c5G8Ul72nh_TACbocYbX1KwwcwavwiIG_lauJYYgC7B_L3aPaWBtfsax4t')
# indexFileContent({'objectID': 'FVNDMMXfVj99RqJMyz1xiFpk63kKA44NqCKEKimaUF1F63QxFJmvnRuuGKN2JyLXY', 'title': 'Policy Tracker for GE2017.com', 'modified': '1499418614', 'created': 'null'})


# xmlstring = open('parse/sample.xml').read()
# print(xmlstring)
# drives.xmlFindText(xmlstring)
