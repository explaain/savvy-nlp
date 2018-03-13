# @TODO: Sort out organisationID and the difference between organisation['objectID'] and organisation['name']

#!/usr/bin/env python
import pprint, datetime, sched, time, calendar, json, requests, random
from algoliasearch import algoliasearch
from parse import services, entityNlp
import xmljson
import firebase_admin
from firebase_admin import credentials as firebaseCredentials
from firebase_admin import auth as firebaseAuth


from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from mixpanel import Mixpanel
import CloudFlare

pp = pprint.PrettyPrinter(indent=4)
mp = Mixpanel('e3b4939c1ae819d65712679199dfce7e')
cf = CloudFlare.CloudFlare(email='jeremy@explaain.com', token='ada07cb1af04e826fa34ffecd06f954ee5e93')

# Decides whether we're in testing mode or not
Testing = False

# Decide what to print out:
toPrint = {
  'cardsCreated': False
}

# Initiate Firebase
cred = firebaseCredentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)

# Initiate Algolia
client = algoliasearch.Client('D3AE3TSULH', '1b36934cc0d93e04ef8f0d5f36ad7607') # This API key allows everything
algoliaOrgsIndex = client.init_index('organisations') if not Testing else client.init_index('-local-organisations')
algoliaSourcesIndex = client.init_index('sources')
algoliaUsersIndex = client.init_index('users')


DefaultLastModified = 0 # Temporary


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

def browseAlgolia(index, params=False):
  if params:
    return [hit for hit in index.browse_all(params)]
  else:
    return [hit for hit in index.browse_all()]

def getEntityTypes(text: str):
  try:
    entityTypes = entityNlp.getEntityTypes(text)
  except Exception as e:
    print('tried to get entities')
    print(e)
    entityTypes = []
  return entityTypes

def serveUserData(idToken: str):
  try:
    decoded_token = firebaseAuth.verify_id_token(idToken)
    print(decoded_token)
    uid = decoded_token['uid']
  except Exception as e:
    print(e)
    return False
  params = {
    'filters': 'firebase: "' + uid + '"'
  }
  res = algoliaUsersIndex.search('', params)
  if 'hits' in res and len(res['hits']):
    user = res['hits'][0]
    if '_highlightResult' in user:
      del user['_highlightResult']
    print(user)
    return user
  else:
    return False

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
  results = {
    'hits': []
  }
  numAttempts = 0
  while len(results['hits']) == 0 and numAttempts < 20:
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
    allOrgs = browseAlgolia(algoliaOrgsIndex)
    mp.track('admin', 'Organisation Setup Complete', { 'objectID': orgObjectID, 'organisationID': organisationID, 'totalOrgs': len(allOrgs) })
    print('Organisation Setup Complete', organisationID)
  else:
    mp.track('admin', 'Organisation Setup Failed', { 'organisationID': organisationID, 'error': 'No organisation with name ' + organisationID + ' found.' })
    print('Organisation Setup Failed - No organisation with name ' + organisationID + ' found.')

def setUpDomain(organisationID: str):
  dnsRecords = [
    {'name':organisationID, 'type':'A', 'content':'151.101.1.195', 'proxied': True},
    {'name':organisationID, 'type':'A', 'content':'151.101.65.195', 'proxied': True},
  ]
  for record in dnsRecords:
    zone = cf.zones.dns_records.post('1f89549d5561f64fbf1553214c85e960', data=record)
    pp.pprint(zone)
  # zones = cf.zones.dns_records.get('1f89549d5561f64fbf1553214c85e960')
  # zone = [z for z in zones if z['name'] == 'heysavvy.com']


# This was probably a one-time only thing
def updateSources():
  allSources = browseAlgolia(algoliaSourcesIndex)
  pp.pprint(allSources)
  allAccounts = kloudlessDrives.listAccounts()
  pp.pprint(allAccounts)
  updatedSources = []
  for source in allSources:
    updatedSource = [account for account in allAccounts if str(account['id']) == source['objectID']]
    if len(updatedSource):
      updatedSource = dict(updatedSource[0])
      updatedSource['objectID'] = source['objectID']
      updatedSource['organisationID'] = source['organisationID']
      updatedSource['addedBy'] = source['addedBy']
      updatedSource['superService'] = 'kloudless'
      del updatedSource['id']
      updatedSources.append(updatedSource)
      algoliaSourcesIndex.save_object(updatedSource)
  pp.pprint(updatedSources)

def addSource(data: dict):
  """This is for when a user adds a new source,
  such as connecting up their Google Drive.
  It automatically indexes all files after connecting.
  """
  organisationID = data['organisationID']
  print('data:', data)
  source = data['source']['account']
  source['objectID'] = data['source']['account']['id']
  source['organisationID'] = organisationID
  source['addedBy'] = data['source']['account']['account']
  source['superService'] = 'kloudless' # For now assumes it's kloudless
  print('source:', source)
  algoliaSourcesIndex.add_object(source)
  allSources = browseAlgolia(algoliaSourcesIndex)
  source['totalSources'] = len(allSources)
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
    numIndexed = indexFiles(accountInfo, True)
  return source

def listSources():
  return browseAlgolia(algoliaSourcesIndex)

def indexAll(includingLastXSeconds=0):
  """Indexes all files from all sources that have been updated since their own lastUpdated value"""
  sources = listSources()
  mp.track('admin', 'Beginning Global Index', {
    'accounts': sources,
    'numberOfAccounts': len(sources)
  })
  indexed = []
  for source in sources:
    print(source)
    accountID = source['accountID'] if 'accountID' in source else source['objectID']
    organisationID = source['organisationID']
    accountInfo =  source
    accountInfo['accountID'] = accountID
    num = indexFiles(accountInfo, includingLastXSeconds=includingLastXSeconds)
    indexed.append({
      'organisationID': organisationID,
      'accountID': accountID,
      'numberOfFiles': num
    })
    algoliaSourcesIndex.save_object(source)
  mp.track('admin', 'Completed Global Index', {
    'accounts': indexed,
    'numberOfAccounts': len(indexed)
  })

def indexFiles(accountInfo, allFiles=False, includingLastXSeconds=0):
  """Indexes all files from a single source that have been updated since their own lastUpdated value"""
  print('indexFiles')
  serviceData = services.getService(accountInfo=accountInfo)
  if not serviceData or 'module' not in serviceData:
    print('No module defined')
    return False
  service = serviceData['module']
  try:
    print(service)
    files = service.listFiles(accountInfo)
  except Exception as e:
    print(e)
    files = None
  if not files or not len(files):
    print('No files retrieved')
    return None
  filesTracker = {
    'indexing': [],
    'notIndexing': []
  }
  algoliaFilesIndex = algoliaGetFilesIndex(accountInfo['organisationID'])
  indexedFiles = algoliaFilesIndex.get_objects([f['objectID'] for f in files])
  # print('actualFiles')
  # pp.pprint(files)
  # print('indexedFiles')
  # pp.pprint(indexedFiles)
  for f in files:
    indexedFileArray = [iFile for iFile in indexedFiles['results'] if iFile and iFile['objectID'] == f['objectID']]
    indexedFile = indexedFileArray[0] if len(indexedFileArray) else None
    if allFiles or not indexedFile or 'modified' not in indexedFile or indexedFile['modified'] < f['modified'] or calendar.timegm(time.gmtime()) - includingLastXSeconds < f['modified']:
      filesTracker['indexing'].append({
        'title': f['title'],
        'modified': f['modified'],
        'lastIndexed': indexedFile['modified'] if indexedFile and 'modified' in indexedFile else 'Never!',
        'service': f['service'],
      })
      indexFile(accountInfo, f['objectID'], actualFile=f)
    else:
      filesTracker['notIndexing'].append({ 'title': f['title'] })
  print('indexing:')
  pp.pprint(filesTracker['indexing'])
  if not Testing and len(filesTracker['indexing']):
    other = {
      # 'onlyFilesModifiedAfter': after,
      'allFiles': allFiles,
      'numberOfFiles': len(files),
      'filesTracked': len(filesTracker['indexing']),
    }
    mp.track('admin', 'Files Indexed', {**accountInfo, **other})
  return len(files)

def indexFile(accountInfo: dict, fileID: str, actualFile=None):
  serviceData = services.getService(accountInfo=accountInfo)
  if not serviceData or 'module' not in serviceData:
    return False
  service = serviceData['module']
  if actualFile:
    f = actualFile
  else:
    try:
      f = service.getFile(accountInfo, fileID=fileID)
    except Exception as e:
      print(e)
      f = None
  if f is None:
    return False
  algoliaFilesIndex = algoliaGetFilesIndex(accountInfo['organisationID'])
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  try:
    oldFile = algoliaFilesIndex.get_object(f['objectID'])
  except Exception as e:
    print(e)
    oldFile = None
  if not Testing:
    algoliaFilesIndex.add_object(f)
  createFileCard(accountInfo, f)
  # Update service data with fileType to get service format
  serviceData = services.getService(accountInfo=accountInfo, specificFile=f)
  if 'format' in serviceData and serviceData['format']:
    print('format!')
    cardsCreated = indexFileContent(accountInfo, f)
  else:
    print('No format')
    cardsCreated = 0
  f['cardsCreated'] = cardsCreated
  notifyChanges(oldFile, f)
  if not Testing:
    mp.track('admin', 'File Indexed', f)
  print('File Indexed with ' + str(cardsCreated) + ' cards: ' + (f['title'] if 'title' in f else ''))

def indexFileContent(accountInfo, f):
  print('indexFileContent')
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  if not Testing and 'objectID' in f and len(f['objectID']): # Avoids a blank objectID deleting all cards in index
    # print(f)
    # Delete all chunks from file
    params = {
      'filters': 'type: "p" AND fileID: "' + f['objectID'] + '"'
    }
    algoliaCardsIndex.delete_by_query('', params) # Is this dangerous???

    print('Deleted')

  # Create new cards
  print('accountInfo')
  print(accountInfo)
  serviceData = services.getService(accountInfo=accountInfo, specificFile=f)
  service = serviceData['module']
  try:
    contentArray = service.getContentForCards(accountInfo, f['objectID']) # Should only take first one!!!
  except Exception as e:
    print(e)
    contentArray = None
  if not contentArray:
    return False
  cards = createCardsFromContentArray(accountInfo, contentArray, f)['allCards']
  if not Testing:
    try:
      algoliaCardsIndex.add_objects(cards)
    except Exception as e:
      print(e)
      print('Something went wrong saving cards to Algolia!')
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
    'fileType': f['fileType'] if 'fileType' in f else f['mimeType'] if 'mimeType' in f else None,
    'fileTitle': f['title'],
    'created': f['created'],
    'modified': f['modified'],
    'service': f['service'],
    'source': f['source'],
  }
  if 'description' in f and f['description']:
    card['description'] = f['description']
  if 'createdBy' in f and f['createdBy']:
    card['createdBy'] = f['createdBy']
  if 'integrationFields' in f and f['integrationFields']:
    card['integrationFields'] = f['integrationFields']
  algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
  if not Testing:
    algoliaCardsIndex.add_object(card)
    print('File Card Created!')
    pp.pprint(card)


def createCardsFromContentArray(accountInfo, contentArray, f, parentContext=[]):
  # print('createCardsFromContentArray')
  cards = []
  allCards = []
  for i, chunk in enumerate(contentArray):
    allRelevantText = ' '.join([chunk[key] for key in ['title', 'content'] if key in chunk])
    if 'cells' in chunk:
      allRelevantText += ' ' + ' '.join([cell['content'] for cell in chunk['cells']])
    entityTypes = getEntityTypes(allRelevantText)
    card = {
      'type': 'p',
      'description': chunk['content'],
      'fileID': f['objectID'],
      'fileUrl': f['url'],
      'fileType': f['fileType'] if 'fileType' in f else f['mimeType'] if 'mimeType' in f else None,
      'fileTitle': f['title'],
      'context': parentContext,
      'entityTypes': entityTypes,
      'created': f['created'],
      'modified': f['modified'],
      'index': i,
      'service': f['service'],
      'source': accountInfo['accountID'],
    }
    if 'service' in accountInfo:
      card['service'] = accountInfo['service']
    if 'superService' in accountInfo:
      card['superService'] = accountInfo['superService']
    if 'title' in chunk:
      card['title'] = chunk['title']
      if len(parentContext) > 1 and parentContext[0] == 'AGREED TERMS':
        card['title'] = 'Clause ' + card['title'] # Hack for Clauses in Contract
    for key in ['cells', 'label', 'value', 'entry']:
      if key in chunk:
        card[key] = chunk[key]
    if 'chunks' in chunk:
      context = parentContext + [chunk['content']]
      subdata = createCardsFromContentArray(accountInfo, chunk['chunks'], f, context)
      subcards = subdata['cards']
      allCards += subdata['allCards']
      card['listItems'] = [c['objectID'] for c in subcards]
      card['listCards'] = [c['description'] for c in subcards]
    cards.append(card)
    allCards.append(card)
  cardIDs = []
  # try:
    # if Testing:
  cardIDs = { 'objectIDs': [random.randint(1, 1000000000000) for c in cards] } # Use this when testing to avoid using up Algolia operations!!
    # else:
    #   algoliaCardsIndex = algoliaGetCardsIndex(accountInfo['organisationID'])
    #   cardIDs = algoliaCardsIndex.add_objects(cards)
  # except Exception as e:
  #   print('Something went wrong saving this card to Algolia:' + f['title'])
  #   print(e)
  for i, objectID in enumerate(cardIDs['objectIDs']):
    cards[i]['objectID'] = objectID
  return {
    'cards': cards, # Cards on this level
    'allCards': allCards # Cards passed up that should continue being passed
  }

def saveCard(card: dict, author:dict):
  # @TODO: Figure out whether sometimes an update will delete a field but it'll be automatically put back in
  if not author or 'organisationID' not in author or 'objectID' not in author:
    return None
  organisationID = author['organisationID']
  algoliaCardsIndex = algoliaGetCardsIndex(organisationID)
  keysToRemove = ['_highlightResult']
  for key in keysToRemove:
    if key in card:
      del(card[key])
  existingCard = None
  if 'objectID' in card:
    # Retrieve existing card
    try:
      existingCard = algoliaCardsIndex.get_object(card['objectID'])
    except Exception as e:
      print(e)
      print('objectID provided but no existing card found')
  verified = authorIsSavvy(existingCard if existingCard else card, author)
  if not verified:
    card = splitPendingCardContent(card)
  if existingCard:
    # Fill in any blanks in card from existingCard
    for key in existingCard:
      if key not in card and key != 'pendingContent':
        card[key] = existingCard[key]
    if 'pendingContent' in existingCard and existingCard['pendingContent']:
      if 'pendingContent' in card and card['pendingContent']:
        # Only replaces if card['pendingContent'] is a dict
        if card['pendingContent']:
          for key in existingCard['pendingContent']:
            if key not in card['pendingContent']:
              card['pendingContent'][key] = existingCard['pendingContent'][key]
      else:
        card['pendingContent'] = existingCard['pendingContent']
    if 'pendingContent' in card and card['pendingContent']:
      pendingKeys = [key for key in card['pendingContent']]
      for key in pendingKeys:
        if fieldsEqual(card['pendingContent'][key], existingCard[key] if key in existingCard else None):
          del(card['pendingContent'][key])
      # Allow higher users to overwrite pending changes
      if verified:
        for key in card:
          if (key not in existingCard or card[key] != existingCard[key]) and key in card['pendingContent']:
            del(card['pendingContent'][key])
  # Complete card
  else:
    existingCard = None
    card['created'] = calendar.timegm(time.gmtime())
    card['creatorID'] = author['objectID']
    if 'name' in author:
      card['creator'] = author['name']
  card['organisationID'] = organisationID
  card['modified'] = calendar.timegm(time.gmtime())
  card['modifierID'] = author['objectID']
  if 'name' in author:
    card['modifier'] = author['name']
  if not 'creatorID' in card and 'authorID' in card:
    card['creatorID'] = card['authorID']
    del(card['authorID'])

  # @TODO: Account for the fact that the service data may have updated since the last index - fetch this as well as existingCard?
  # Save to service
  if 'service' in card and card['service']:
    serviceData = services.getService(serviceName=card['service'])
    service = serviceData['module']
    if 'source' in card and card['source']:
      try:
        source = algoliaSourcesIndex.get_object(card['source'])
      except Exception as e:
        print(e)
        source = None
    else:
      sources = browseAlgolia(algoliaSourcesIndex, {
        'filters': 'organisationID:' + author['organisationID'] + ' AND service:' + card['service']
      })
      source = sources[0]
    if ('type' in card and card['type'] == 'file'):
      # @TODO: Account for the fact that the Sifter API currently doesn't let us update issues, so it always creates a new one
      try:
        serviceCard = service.saveFile(source, card)
      except Exception as e:
        print(e)
        serviceCard = {}
      # Assemble final card
      for key in serviceCard:
        card[key] = serviceCard[key]
    else:
      print('Card is a service card but type is not "file" - we don\'t support editing individual lines of files yet')
  # Save to Savvy
  print('card')
  pp.pprint(card)
  if not Testing:
    savedResult = algoliaCardsIndex.add_object(card)
    card['objectID'] = savedResult['objectID']
    mp.track(author['objectID'] if author and 'objectID' in author else 'admin', 'Card Saved', card)
  notifyChanges(existingCard, card)
  return { 'success': True, 'card': card }

def deleteCard(card, author):
  if not 'objectID':
    return { 'success': False, 'error': 'Card has no objectID' }
  if not author or 'organisationID' not in author or 'objectID' not in author:
    return { 'success': False, 'error': 'No author with correct details' }
  organisationID = author['organisationID']
  algoliaCardsIndex = algoliaGetCardsIndex(organisationID)
  try:
    existingCard = algoliaCardsIndex.get_object(card['objectID'])
  except Exception as e:
    print(e)
    existingCard = None
  verified = authorIsSavvy(existingCard, author)
  if verified:
    if 'service' in card and card['service']:
      serviceData = services.getService(serviceName=card['service'])
      service = serviceData['module']
      if 'source' in card and card['source']:
        source = algoliaSourcesIndex.get_object(card['source'])
      else:
        sources = browseAlgolia(algoliaSourcesIndex, {
          'filters': 'organisationID:' + author['organisationID'] + ' AND service:' + card['service']
        })
        source = sources[0]
      if ('type' in card and card['type'] == 'file'):
        # @TODO: Account for the fact that the Sifter API currently doesn't let us delete issues
        try:
          serviceCard = service.deleteFile(source, card)
        except Exception as e:
          print(e)
          serviceCard = {}
    try:
      algoliaCardsIndex.delete_object(card['objectID'])
      notifyChanges(card, None)
      return { 'success': True, 'card': None }
    except Exception as e:
      print(e)
      return { 'success': False, 'error': 'Couldn\'t delete card' }
  else:
    try:
      existingCard = algoliaCardsIndex.get_object(card['objectID'])
      card = dict(existingCard)
      card['pendingDelete'] = True
      algoliaCardsIndex.save_object(card)
      notifyChanges(existingCard, card)
      return { 'success': True, 'card': card }
    except Exception as e:
      return { 'success': False, 'error': 'Couldn\'t set card to be pending deletion' }

def verify(objectID: dict, author: dict, prop: str = None, approve: bool = True):
  organisationID = author['organisationID']
  algoliaCardsIndex = algoliaGetCardsIndex(organisationID)
  try:
    existingCard = algoliaCardsIndex.get_object(objectID)
  except Exception as e:
    return { 'success': False, 'error': 'Card could not be found' }
  card = dict(existingCard)

  if 'pendingContent' not in card:
    return { 'success': False, 'error': 'No pending content to verify!' }
  if not prop:
    # Verifying whole card
    if approve:
      for key in card['pendingContent']:
        card[key] = card['pendingContent'][key]
    card['pendingContent'] = None
  elif type(prop) is str:
    # Verifying card (root) property
    if prop in card['pendingContent']:
      if approve:
        card[prop] = card['pendingContent'][prop]
      card['pendingContent'][prop] = None
    else:
      return { 'success': False, 'error': 'Property ' + prop + ' is not in pending content!' }
  else:
    return { 'success': False, 'error': 'Don\'t (yet) understand how to process when prop is: ' + json.dumps(prop) }
  print('card', card)
  return saveCard(card, author)

def authorIsSavvy(card, author):
  print('Is Author Savvy?')
  pp.pprint(card)
  pp.pprint(author)
  userIsAnAdmin = ('role' in author and author['role'] == 'admin')
  print('userIsAnAdmin', userIsAnAdmin)
  cardExists = card and type(card) is dict
  print('cardExists', cardExists)
  print(type(card))
  cardHasNoTopics = 'topics' not in card or not card['topics'] or not len(card['topics'])
  print('cardHasNoTopics', cardHasNoTopics)
  authorHasACardTopic = 'topics' in author and type(author['topics']) is list and 'topics' in card and len([topic for topic in author['topics'] if topic in card['topics']])
  print('authorHasACardTopic', authorHasACardTopic)

  verified = userIsAnAdmin or (cardExists and (cardHasNoTopics or authorHasACardTopic))
  print(verified)
  return verified

def splitCardContent(card):
  nonContentKeys = ['pendingContent', 'pendingDelete', 'objectID', 'created', 'creator', 'creatorID', 'organisationID', 'type', 'fileID', 'fileUrl', 'fileType', 'fileTitle', 'service', 'source', 'verified']
  content = card
  nonContent = {}
  for key in nonContentKeys:
    if key in card:
      nonContent[key] = card[key]
    content.pop(key, None)
  return {
    'content': content,
    'nonContent': nonContent
  }

def splitPendingCardContent(card):
  cardSplit = splitCardContent(card)
  splitCard = cardSplit['nonContent']
  if 'pendingContent' not in splitCard or not splitCard['pendingContent']:
    splitCard['pendingContent'] = {}
  for key in cardSplit['content']:
    splitCard['pendingContent'][key] = cardSplit['content'][key]
  return splitCard

def fieldsEqual(a, b):
  "Returns whether a and b are equal or if they're both essentially None"
  typesOfNone = [None, '', [None], ['']]
  return a == b or (a in typesOfNone and b in typesOfNone)


def notifyChanges(oldFile, newFile):
  print('notifyChanges')
  pp.pprint(oldFile)
  pp.pprint(newFile)
  if oldFile and newFile and type(newFile) is dict and 'pendingContent' in newFile and (not oldFile or type(oldFile) is not dict or 'pendingContent' not in oldFile or oldFile['pendingContent'] != newFile['pendingContent']):
    # Changes to pendingContent
    recipient = {
      "emails": []
    }
  if newFile and type(newFile) is dict and newFile['service'] == 'sifter':
    if oldFile and type(oldFile) == 'dict':
      oldStatus = oldFile['integrationFields']['status']
      newStatus = newFile['integrationFields']['status']
      if oldStatus in ['Opened', 'Reopened'] and newStatus not in ['Opened', 'Reopened']:
        print('good!')
        # requests.post('https://savvy-api--live.herokuapp.com/notify/send', json={
        requests.post('http://localhost:5000/notify/send', json={
          "recipient": {
            "emails": [newFile['createdBy']]
          },
          "type": "CARD_UPDATED",
          "payload": {
            "message": "✅ An issue you submitted is now resolved!\n\n>*" + newFile['title'] + "*\n>" + newFile['description'][:200] + ('...' if len(newFile['description']) > 200 else '') + "\n\n_Click here to view it on Sifter: " + newFile['url'] + " _"
          }
        })



words = open('dictionaryWords.txt').read().split('\n')


# pp.pprint(saveCard({
#   'objectID': '356300620',
#   'pendingDelete': False,
#   # 'type': 'file',
#   # 'title': 'Testing Title: ' + random.choice(words),
#   # 'description': 'Testing Description: ' + random.choice(words),
#   # 'fileID': f['objectID'],
#   # 'fileUrl': f['url'],
#   # 'fileType': f['fileType'] if 'fileType' in f else f['mimeType'] if 'mimeType' in f else None,
#   # 'fileTitle': f['title'],
#   # 'created': f['created'],
#   # 'service': 'sifter',
#   # 'source': 'explaain.sifterapp.com',
#   # 'integrationFields': {
#   #   'projectID': '50455',
#   #   'priority': 'High',
#   # }
# },
# author = {
#   'objectID': '124356',
#   'name': 'Jeremy Evans',
#   'organisationID': 'explaain',
#   'role': 'member',
# }))

# pp.pprint(deleteCard({
#   'objectID': '317709421',
# },
# author = {
#   'objectID': '124356',
#   'name': 'Jeremy Evans',
#   'organisationID': 'explaain',
#   'role': 'manager',
# }))



s = sched.scheduler(time.time, time.sleep)
minsInterval = 10

def reIndex():
  indexAll()
  s.enter(60 * minsInterval, 1, reIndex)

def startIndexing():
  indexAll(includingLastXSeconds=0)
  s.enter(60 * minsInterval, 1, reIndex)
  s.run()

# indexAll()

# requests.post('https://savvy-api--live.herokuapp.com/notify/send', json={
#   "recipient": {
#     "email": "jeremy@heysavvy.com"
#   },
#   "type": "CARD_UPDATED",
#   "payload": {
#     "message": "An issue on 🐞 Sifter has been resolved! Here it is: \n\n> *This is a testing issue*\n\nClick here to view it on Sifter: https://savvy.sifterapp.com/projects/50281/issues/4314315"
#   }
# })


"""Below here is stuff for testing"""

# indexAll(includingLastXSeconds=10000)


# accountInfo = {'organisationID': 'acme', 'accountID': 288094069}
# accountInfo = {
#   "service": "zoho",
#   "organisationID": "explaain",
#   "superService": False,
#   "accountID": "savvy",
#   "token": "1461d2e158c6e83ffa4a45e4e32c9c01",
#   "email": "jeremy@heysavvy.com",
#   "objectID": "bugtracker.zoho.eu/portal/savvy"
# }
# # kloudlessDrives.listFiles(accountInfo)
#
# indexFiles(accountInfo, allFiles=True)
# accountInfo = {
#   "service": "sifter",
#   "organisationID": "explaain",
#   "superService": False,
#   "accountID": "explaain.sifterapp.com",
#   "token": "8c66dfd53afd38f2cb1548fcaac1c9e5",
#   "objectID": "explaain.sifterapp.com"
# }
# indexFiles(accountInfo)

# indexAll()
# indexFiles({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, allFiles=True)
# indexFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204',
#   'superService': 'kloudless',
# }, 'FIpeUA6-qJgZTLvISKr3n2v0BMmTqXsQN5-GkQ_yR8yOycticQbP2Trz4qdW08xsl')
# indexFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204',
#   'superService': 'kloudless',
# }, 'Ffz0GtHAtp2qbiNN-mGtZmI1dsC6Uh60QN3jJ-sOvN8dIP39UXcRkKu42D1e7Jti_')
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

# indexFile({
#   'username': 'admin',
#   'password': 'h3110w0r1d',
#   'siteDomain': 'explaain',
#   'accountID': 'https://explaain.atlassian.net/wiki/',
#   'service': 'confluence',
#   'organisationID': 'explaain',
# }, '1572866')

# xmlstring = open('parse/sample3.xml').read()
# # print(xmlstring)
# kloudlessDrives.xmlFindText(xmlstring)
