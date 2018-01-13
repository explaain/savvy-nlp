#!/usr/bin/env python
import pprint, datetime, sched, time
from random import *
from algoliasearch import algoliasearch
from parse import drives
import xmljson
from mixpanel import Mixpanel

pp = pprint.PrettyPrinter(indent=4)
mp = Mixpanel('e3b4939c1ae819d65712679199dfce7e')

# Decides whether we're in testing mode or not
Testing = False

# Decide what to print out:
toPrint = {
  'cardsCreated': True
}


client = algoliasearch.Client('D3AE3TSULH', '1b36934cc0d93e04ef8f0d5f36ad7607') # This API key allows everything
algoliaSourcesIndex = client.init_index('sources')
algoliaOrgsIndex = client.init_index('organisations') if not Testing else client.init_index('-local-organisations')


def algoliaGetFilesIndexName(organisationID: str):
  return organisationID + '__Files'
def algoliaGetCardsIndexName(organisationID: str):
  return organisationID + '__Cards'
def algoliaGetFilesIndex(organisationID: str):
  algoliaFilesIndex = client.init_index(algoliaGetFilesIndexName(organisationID))
  return algoliaFilesIndex
def algoliaGetCardsIndex(organisationID: str):
  algoliaCardsIndex = client.init_index(algoliaGetCardsIndexName(organisationID))
  return algoliaCardsIndex

def setUpOrg(organisationID: str):
  """For now this just sets up Cards and Files Algolia Indices,
  Creates algoliaApiKey and saves this to organisations index
  """
  print('Setting Up Organisation', organisationID)
  mp.track('admin', 'Setting Up Organisation', { 'organisationID': organisationID })
  filesSettings = algoliaGetFilesIndex('explaain').get_settings()
  cardsSettings = algoliaGetCardsIndex('explaain').get_settings()
  print(filesSettings)
  print(cardsSettings)
  algoliaGetFilesIndex(organisationID).set_settings(filesSettings) # Probably worth making this happen every reindex for all other indices for when explaain__Cards and explaain__Files settigns get updated
  algoliaGetCardsIndex(organisationID).set_settings(cardsSettings)
  apiKeyParams = {
    'acl': ['search', 'browse', 'addObject', 'deleteObject'],
    'indexes': [organisationID + '__*'],
    'description': 'Access only for organisation ' + organisationID
  }
  print('apiKeyParams', apiKeyParams)
  algoliaApiKey = client.add_api_key(apiKeyParams)
  print('algoliaApiKey', algoliaApiKey)
  searchParams = {
    'filters': 'name: "' + organisationID + '"'
  }
  results = {}
  numAttempts = 0
  while results['hits'] == 0 and numAttempts < 20:
    time.sleep(5)
    numAttempts += 1
    results = algoliaOrgsIndex.search('', searchParams)
  if len(results['hits']):
    orgObjectID = results['hits'][0]['objectID']
    print('orgObjectID', orgObjectID)
    res = algoliaOrgsIndex.partial_update_object({
      'objectID': orgObjectID,
      'algolia': {
        'apiKey': algoliaApiKey['key']
      }
    })
    print(res)
    mp.track('admin', 'Organisation Setup Complete', { 'organisationID': organisationID })
    print('Organisation Setup Complete', organisationID)
  else:
    mp.track('admin', 'Organisation Setup Failed', { 'organisationID': organisationID, 'error': 'No organisation with name ' + organisationID + ' found.' })
    print('Organisation Setup Failed - No organisation with name ' + organisationID + ' found.')

def addSource(data: dict):
  """This is for when a user adds a new source,
  such as connecting up their Google Drive.
  It automatically indexes all files after connecting.
  """
  organisationID = data['organisationID']
  print('data:', data)
  source = {
    'objectID': data['source']['account']['id'],
    'organisationID': organisationID,
    'addedBy': data['source']['account']['account']
  }
  print('source:', source)
  algoliaSourcesIndex.add_object(source)

  mp.track('admin', 'Source Added', source)

  # Index all files from source
  accountInfo = {
    'organisationID': organisationID,
    'accountID': source['objectID']
  }

  # If either Algolia Indices doesn't exist then create them, create algoliaApiKey and add this to organisations index
  indices = client.list_indexes()
  if not any(i['name'] == algoliaGetFilesIndexName(organisationID) for i in indices['items']) or not any(i['name'] == algoliaGetCardsIndexName(organisationID) for i in indices['items']):
    setUpOrg(organisationID)

  numIndexed = 0
  numAttempts = 0
  while numIndexed == 0 and numAttempts < 20:
    time.sleep(10)
    numAttempts += 1
    numIndexed = indexFiles(accountInfo, False, True)
  return source

def indexAll():
  """Indexes all files since last memory update""" # Currently, all sources had the same Last Update Time stored
  accounts = drives.listAccounts()
  memory = open('memory.txt','r')
  lastRefreshTime = datetime.datetime.strptime(memory.read().splitlines()[0], '%Y-%m-%d %H:%M:%S.%f')
  print(lastRefreshTime)
  thisRefreshTime = str(datetime.datetime.now())
  mp.track('admin', 'Beginning Global Index', {
    'lastRefreshTime': lastRefreshTime,
    'thisRefreshTime': thisRefreshTime,
    'accounts': accounts,
    'numberOfAccounts': len(accounts)
  })
  indexed = []
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
      num = indexFiles(accountInfo, after=lastRefreshTime)
      indexed.append({
        'organisationID': organisationID,
        'accountID': accountID,
        'numberOfFiles': num
      })
  memory = open('memory.txt','w') # Happens now so that incomplete indexing doesn't overwrite lastRefreshTime
  memory.write(thisRefreshTime)
  mp.track('admin', 'Completed Global Index', {
    'lastRefreshTime': lastRefreshTime,
    'thisRefreshTime': thisRefreshTime,
    'accounts': indexed,
    'numberOfAccounts': len(indexed)
  })

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
  if len(files):
    other = {
      'onlyFilesModifiedAfter': after,
      'allFiles': allFiles,
      'numberOfFiles': len(files)
    }
    mp.track('admin', 'Files Indexed', {**accountInfo, **other})
  return len(files)

def indexFile(accountInfo, fileID: str):
  f = drives.getFile(accountInfo, fileID=fileID)
  if f is not None:
    algoliaFilesIndex = algoliaGetFilesIndex(accountInfo['organisationID'])
    algoliaFilesIndex.add_object(f)
    createFileCard(accountInfo, f)
    cardsCreated = 0
    if f['mimeType'] in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
      cardsCreated = indexFileContent(accountInfo, f)
    else:
      if 'doc' in f['mimeType']:
        print('"doc" was found in:', f['mimeType'])
    other = { 'cardsCreated': cardsCreated }
    mp.track('admin', 'File Indexed', {**f, **other})

def indexFileContent(accountInfo, f):
  if not Testing:
    print(f)
    # Delete all chunks from file
    params = {
      'filters': 'type: "p" AND fileID: "' + f['objectID'] + '"'
    }
    algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
    algoliaCardsIndex.delete_by_query('', params) # Is this dangerous???

    print('Deleted')

  # Create new cards
  contentArray = drives.getContent(accountInfo, f['objectID']) # Should only take first one!!!
  cards = createCardsFromContentArray(accountInfo, contentArray, f)['allCards']
  print('Number of Cards:', len(cards))
  if toPrint['cardsCreated']:
    pp.pprint(cards)
  return len(cards)

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
  if not Testing:
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

# accountInfo = {'organisationID': 'acme', 'accountID': 288094069}
# indexFiles(accountInfo, False, True)

# indexAll()
# indexFiles({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, allFiles=True, after=None)
# indexFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'FZFSR0chh4O89xJ-70HfseeFyz6MoRQK5VyJ2tkGFGbbHEh6tlaXdsXyZ6r0SHfG7')
# indexFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'J13B2DLXBLT8HsALzNTfviaXVscPNm5RtgnSv_KPbZgSMJAe0vNj5M5ipz')
# indexFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'F88bWIq-LWUFA72bVPTHSBrJni_zNfEufrlqw8Hc--DkNBTM4u7InvdV8JcVurbpT')
# indexFile({
#   'organisationID': 'askporter',
#   'accountID': '284151319'
# }, 'FtORrzfQkKOM6NOR_ZgkDcBmP258Sne-HAMXW32x2F29Xr1VGyK2JKsqCq0eu704P')
# indexFileContent({'objectID': 'FVNDMMXfVj99RqJMyz1xiFpk63kKA44NqCKEKimaUF1F63QxFJmvnRuuGKN2JyLXY', 'title': 'Policy Tracker for GE2017.com', 'modified': '1499418614', 'created': 'null'})


# xmlstring = open('parse/sample3.xml').read()
# # print(xmlstring)
# drives.xmlFindText(xmlstring)
