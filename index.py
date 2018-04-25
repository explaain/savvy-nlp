#!/usr/bin/env python
import pprint, os, datetime, sched, time, calendar, json, requests, random, difflib, traceback, sys, db, re
from raven import Client as SentryClient
from parse import services, entityNlp
import xmljson
import firebase_admin
import track
from firebase_admin import credentials as firebaseCredentials
from firebase_admin import auth as firebaseAuth
from google.cloud import storage as google_storage
from algoliasearch import algoliasearch



from oauth2client import client as googleClient

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from mixpanel import Mixpanel
import CloudFlare

GOOGLE_CLIENT_SECRET_FILE = 'google_connect_client_secret.json'

algoliaClient = algoliasearch.Client('D3AE3TSULH', '1b36934cc0d93e04ef8f0d5f36ad7607') # This API key allows everything

pp = pprint.PrettyPrinter(indent=4, width=160)
sentry = SentryClient(
  'https://9a0228c8fde2404c9ccd6063e6b02b4c:d77e32d1f5b64f07ba77bda52adbd70e@sentry.io/1004428',
  environment = 'local' if 'HOME' in os.environ and os.environ['HOME'] == '/Users/jeremy' else 'production')
mp = Mixpanel('e3b4939c1ae819d65712679199dfce7e')
cf = CloudFlare.CloudFlare(email='jeremy@explaain.com', token='ada07cb1af04e826fa34ffecd06f954ee5e93')

google_storage_client = google_storage.Client.from_service_account_json(
        'google-cloud-platform-Savvy-credentials.json')
google_bucket = google_storage_client.get_bucket('savvy')

# Decides whether we're in testing mode or not
Testing = False

ForceOverwrite = False

# Decide what to print out:
toPrint = {
  'cardsCreated': False
}

# Initiate Firebase
cred = firebaseCredentials.Certificate('serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)

def getEntityTypes(text: str):
  try:
    entityTypes = entityNlp.getEntityTypes(text)
  except Exception as e:
    print('tried to get entities')
    traceback.print_exc(file=sys.stdout)
    entityTypes = []
  return entityTypes

def serveUserData(idToken: str):
  """ Returns user data from our Database (Algolia),
  once the user has logged in through Firebase (if it can't verify user token it gives up immediately).
  Currently only called from frontend in (auth.js)
  """
  firebaseUid = None
  try:
    firebase_user = firebaseAuth.verify_id_token(idToken)
    print(firebase_user)
    firebaseUid = firebase_user['uid']
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    sentry.captureException()
    return False
  if not firebaseUid or not len(firebaseUid):
    print('Blank firebaseUid - aborting for security reasons!')
    sentry.captureMessage('Blank firebaseUid - aborting for security reasons!', extra={
      'user': firebase_user,
    })
    return False
  params = {
    'filters': 'firebase: "' + firebaseUid + '"'
  }
  # res1 = db.Users().get(firebaseUid)
  # res = { 'hits': [res1] }
  # @TODO: This should happen by filtering in the search, not by returning everything then filtering
  # all_users = db.Users().browse()
  # pp.pprint(all_users)
  # if not all_users or not len(all_users):
  #   print('Couldn\'t fetch users from ElasticSearch!')
  #   sentry.captureMessage('Couldn\'t fetch users from ElasticSearch!', extra={
  #     'all_users': all_users,
  #     'firebaseUid': firebaseUid,
  #     'firebase_user': firebase_user,
  #   })
  #   return None
  # res = { 'hits': [hit for hit in all_users if 'firebase' in hit and hit['firebase'] == firebaseUid] }
  res = db.Users().search(params=params)
  print('First result!')
  pp.pprint(res)
  if 'hits' in res and len(res['hits']):
    # User already exists in db
    if len(res['hits']) > 1:
      print('More than one result for firebaseUid ' + str(firebaseUid) + ' - aborting for security reasons!')
      sentry.captureMessage('More than one result for this firebaseUid - aborting for security reasons!', extra={
        'user': firebase_user,
        'firebaseUid': firebaseUid,
        'hits': res['hits'],
      })
      return False # @TODO: return something more useful in errors?
    user = res['hits'][0]
    if '_highlightResult' in user:
      del user['_highlightResult']
    print('Serving back user:')
    print(user)
    return user
  if not 'email' in firebase_user:
    # No email captured by Firebase login
    print('No existing user nor email captured by Firebase login!')
    sentry.captureMessage('No existing user nor email captured by Firebase login!', extra={
      'params': params,
      'firebaseUid': firebaseUid
    })
    return None
  # Match user to existing one (e.g. created from Slack or invited to join) by email
  email_params = {
    'filters': 'emails: "' + firebase_user['email'] + '"'
  }
  res = db.Users().search(params=email_params)
  if res and 'hits' in res and len(res['hits']):
    user = res['hits'][0]
    if '_highlightResult' in user:
      del user['_highlightResult']
    print('Found this match by email:', user)
    # Add firebase details and save in db
    user['firebase'] = firebaseUid
    user['created'] = calendar.timegm(time.gmtime())
    db.Users().save(user) # @TODO: Get and check result from this?
    mp.track('admin', 'Added Firebase Details to User', user)
    print('Serving back user (just added firebase details to it):')
    return user
  else:
    # Remove all special characters, then replace ' ' with '_', then reduce '__' to '_', then add '__<random_number>' to the end
    full_name = firebase_user['name'] if 'name' in firebase_user else firebase_user['email'] if 'email' in firebase_user else firebase_user['uid']
    organisationID = re.sub(r'(_)\1+', r'\1', re.sub(r'\s', '_', re.sub(r'[^\w]', ' ', str(full_name)))) + '_' + str(random.randint(10000000, 99999999))
    # Create new organisation!
    try:
      organisation = setUpOrg(organisationID)
      if not organisation or not len(organisation) or 'objectID' not in organisation:
        raise Exception('Couldn\'t create organisation')
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
    print('organisation')
    pp.pprint(organisation)

    # Create new user!
    user = {
      'firebase': firebaseUid,
      'organisationID': organisationID,
      'emails': [firebase_user['email']],
      'created': calendar.timegm(time.gmtime()),
      'role': 'admin',
    }
    db.Users().add(user) # @TODO: Get and check result from this?
    print('Created new user:', user)
    mp.track('admin', 'Created User in Database after very first Google login', user)
    try:
      track.slack('New User Created! *' + (firebase_user['name'] if 'name' in firebase_user else user_to_name(user)) + '*')
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
    return user


def setUpOrg(organisationID: str=None):
  """ For now this just sets up Cards and Files Indices,
  Creates algoliaApiKey and saves this to organisations index.
  Currently only called from Slack (savvy-api, slack-interface.js).
  """
  if not organisationID:
    return None
  searchParams = {
    'filters': 'organisationID: "' + organisationID + '"'
  }
  results = db.Organisations().search(params=searchParams)
  if results and 'hits' in results and results['hits'] and len(results['hits']):
    print('Organisation with organisationID ' + organisationID + ' already exists!')
    sentry.captureMessage('Organisation with organisationID ' + organisationID + ' already exists!')
    mp.track('admin', 'Organisation with organisationID ' + organisationID + ' already exists!', { 'organisationID': organisationID })
    return None
  print('Setting Up Organisation', organisationID)
  mp.track('admin', 'Setting Up Organisation', { 'organisationID': organisationID })
  try:
    # Create new indices
    db.Cards(organisationID).create_index()
    db.Files(organisationID).create_index()
  except Exception as e:
    print('Failed to create new Cards and Files indices')
    sentry.captureException()
    mp.track('admin', 'Failed to create new Cards and Files indices', { 'organisationID': organisationID })
    return None
  mp.track('admin', 'Org Setup: Indexes Created', { 'organisationID': organisationID })
  objectID = organisationID
  organisation = {
    'objectID': objectID,
    'organisationID': organisationID,
    'name': organisationID, # Still saving this for now in case of legacy issues
  }
  try:
    db.Organisations().save(organisation)
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    mp.track('admin', 'Organisation Setup Failed', { 'organisationID': organisationID })
    print('Organisation Setup Failed')
    sentry.captureException()
    return None
  mp.track('admin', 'Org Setup: New Org Object Created', { 'objectID': organisationID, 'organisationID': organisationID })
  mp.track('admin', 'Org Setup: API Key Saved to Org', { 'objectID': organisationID, 'organisationID': organisationID })

  totalOrgs = db.Organisations().get_size()
  mp.track('admin', 'Organisation Setup Complete', { 'objectID': objectID, 'organisationID': organisationID, 'totalOrgs': totalOrgs })
  track.slack('New Organisation Created: *' + organisationID + '*')
  print('Organisation Setup Complete', organisationID)
  return organisation

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

def addSource(source: dict=None):
  """This is for when a user adds a new source,
  such as connecting up their Google Drive.
  It automatically indexes all files after connecting.
  """
  if not source:
    e = 'No source provided!'
    print(e)
    sentry.captureMessage(e)
    return { 'success': False, 'error': e }
  for key in [ 'organisationID', 'service' ]:
    if key not in source:
      e = 'source must contain \'' + key + '\''
      print(e)
      sentry.captureMessage(e)
      return { 'success': False, 'error': e }
  if 'superService' in source and source['superService'] == 'google':
    if 'code' in source and 'scopes' in source:
      # Exchange auth code for access token, refresh token, and ID token
      credentials = googleClient.credentials_from_clientsecrets_and_code(GOOGLE_CLIENT_SECRET_FILE, source['scopes'], source['code'])
      pp.pprint(dir(credentials))
      source['access_token'] = credentials.access_token
      source['refresh_token'] = credentials.refresh_token
      source['id_token'] = credentials.id_token
      source['token_expiry'] = credentials.token_expiry
      source['user_agent'] = credentials.user_agent
      source['revoke_uri'] = credentials.revoke_uri
      pp.pprint(source)
    elif 'access_token' not in source and 'refresh_token' not in source and 'id_token' not in source:
      e = 'source must contain either: both "code" and "scopes"; or "access_token" and "refresh_token" and "id_token"'
      print(e)
      sentry.captureMessage(e)
      return { 'success': False, 'error': e }
  print('source:', source)
  # TODO: Check whether a source with this accountID (and organisationID/service combo) already exists
  try:
    res = db.Sources().add(source)
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    sentry.captureException()
    return { 'success': False, 'error': e }
  source['objectID'] = str(res['objectID'])
  source['totalSources'] = db.Sources().get_size()
  mp.track('admin', 'Source Added', source)

  # @TODO Check this is still necessary and stable
  # If either DB Index doesn't exist then create them, create api keys and add this to organisations index
  indices = db.Client().list_indices()
  if not any(i['name'] == db.Files(source['organisationID']).get_index_name() for i in indices['items']) or not any(i['name'] == db.Cards(source['organisationID']).get_index_name() for i in indices['items']):
    setUpOrg(source['organisationID'])

  # @NOTE: Now not indexing here because:
  # (a) it never works first time (with Kloudless at least - it always says 0 files)
  # (b) we want to return success to the browser that at least it's connected, and not wait 5 * 20 seconds
  # (c) we are separating out indexing into a separate app
  # @TODO: Send a request to the indexing app to start trying to index this source
  # # Index all files from source
  # numIndexed = 0
  # numAttempts = 0
  # while numIndexed == 0 and numAttempts < 20:
  #   time.sleep(5)
  #   numAttempts += 1
  #   numIndexed = indexFiles(source)
  try:
    track.slack('New Source Connected! *' + source['organisationID'] + '* connected up to *' + source['service'] + '*')
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    sentry.captureException()
  return {
    'success': True,
    'source': source,
  }

def listSources():
  return db.Sources().browse()

def indexAll(includingLastXSeconds=0):
  """Indexes all files from all sources that have been updated since their own lastUpdated value"""
  sources = listSources()
  print('sources:')
  print(sources)
  mp.track('admin', 'Beginning Global Index', {
    # 'accounts': sources,
    'numberOfAccounts': len(sources)
  })
  indexed = []
  for source in sources:
    print(source)
    accountID = source.get('accountID', source.get('objectID', None))
    if accountID:
      organisationID = source['organisationID']
      source['accountID'] = accountID
      try:
        num = indexFiles(source, includingLastXSeconds=includingLastXSeconds)
      except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sentry.captureException()
        num = 0
      if num:
        indexed.append({
          'organisationID': organisationID,
          'accountID': accountID,
          'numberOfFiles': num
        })
    else:
      print('No accountID or objectID!!')
      sentry.captureMessage('No accountID or objectID!!', extra={
        'source': source,
      })
    # db.Sources().save(source)

    # NOTE: This is to save memory
    # TODO: Check this doesn't mess anything up
    del(source)
  mp.track('admin', 'Completed Global Index', {
    'accounts': indexed,
    'numberOfAccounts': len(indexed)
  })

def indexFiles(accountInfo: dict=None, allFiles=False, includingLastXSeconds=0):
  """Indexes all files from a single source that have been updated since their own lastUpdated value"""
  print('indexFiles')
  if not accountInfo or 'organisationID' not in accountInfo:
    print('Couldn\'t index files - missing source info', accountInfo)
    sentry.captureMessage('Couldn\'t index files - missing source info', extra={
      'accountInfo': accountInfo,
      'allFiles': allFiles,
      'includingLastXSeconds': includingLastXSeconds,
    })
    return None
  integrationData = services.getIntegrationData(accountInfo=accountInfo)
  allServiceData = services.getAllServiceData(accountInfo=accountInfo)
  print('integrationData1')
  pp.pprint(integrationData)
  if not integrationData or 'module' not in integrationData:
    print('No module defined')
    sentry.captureMessage('No module defined', extra={
      'integrationData': integrationData,
      'allServiceData': allServiceData,
    })
    return False
  integration = integrationData['module']
  try:
    print(integration)
    files = integration.listFiles(accountInfo)
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    sentry.captureException()
    files = None
  if not files or not len(files):
    print('No files retrieved')
    sentry.captureMessage('No files retrieved', extra={
      'integrationData': integrationData,
      'allServiceData': allServiceData,
    })
    return None
  filesTracker = {
    'indexing': [],
    'notIndexing': []
  }
  print('files')
  pp.pprint(files)
  indexedFiles = db.Files(accountInfo['organisationID']).get(objectIDs=[f['objectID'] for f in files])
  # print('actualFiles')
  # pp.pprint(files)
  # print('indexedFiles')
  # pp.pprint(indexedFiles)
  for f in files:
    indexedFileArray = [iFile for iFile in indexedFiles['results'] if iFile and iFile['objectID'] == f['objectID']]
    indexedFile = indexedFileArray[0] if len(indexedFileArray) else None

    if allFiles or not indexedFile or 'modified' not in indexedFile or not indexedFile['modified'] or indexedFile['modified'] < f['modified'] or calendar.timegm(time.gmtime()) - includingLastXSeconds < f['modified']:
      filesTracker['indexing'].append({
        'title': f['title'],
        'modified': f['modified'],
        'lastIndexed': indexedFile['modified'] if indexedFile and 'modified' in indexedFile else 'Never!',
        'service': allServiceData['service']['serviceName'] if allServiceData and 'service' in allServiceData and 'serviceName' in allServiceData['service'] else None,
      })
      try:
        indexFile(accountInfo, f['objectID'], actualFile=f)
      except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sentry.captureException()
    else:
      filesTracker['notIndexing'].append({ 'title': f['title'] })
  print('indexing:')
  pp.pprint(filesTracker['indexing'])
  if not Testing and len(filesTracker['indexing']):
    other = {
      # 'onlyFilesModifiedAfter': after,
      'allFiles': allFiles,
      'numberOfFiles': len(files),
      'filesUpdated': len(filesTracker['indexing']),
    }
    mp.track('admin', 'Files Indexed', {**accountInfo, **other})
  return len(files)

def indexFile(accountInfo: dict=None, fileID: str=None, actualFile: dict=None):
  if not accountInfo or 'organisationID' not in accountInfo or not fileID:
    print('Couldn\'t index file - missing info', accountInfo, fileID)
    sentry.captureMessage('Couldn\'t index file - missing info', extra={
      'accountInfo': accountInfo,
      'fileID': fileID,
      'actualFile': actualFile,
    })
    return None
  integrationData = services.getIntegrationData(accountInfo=accountInfo, specificCard=actualFile)
  print('integrationData')
  pp.pprint(integrationData)
  if not integrationData or 'module' not in integrationData:
    print('No module defined')
    sentry.captureMessage('No module defined', extra={
      'accountInfo': accountInfo,
      'fileID': fileID,
      'actualFile': actualFile,
      'integrationData': integrationData,
    })
    return False
  integration = integrationData['module']
  f = None
  if actualFile:
    keys = ['objectID', 'service', 'source', 'title', 'modified']
    keysInActualFile = [(key in actualFile and actualFile[key]) for key in keys]
    if keysInActualFile.count(False) == 0:
      f = actualFile
  if not f:
    try:
      f = integration.getFile(accountInfo, fileID=fileID)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      return False
  if not f:
    sentry.captureMessage('Couldn\'t get file', extra={
      'accountInfo': accountInfo,
      'fileID': fileID,
      'actualFile': actualFile,
      'integrationData': integrationData,
    })
    return False
  if hasattr(integration, 'get_thumbnail'):
    try:
      thumbnail_file = integration.get_thumbnail(accountInfo, fileID=fileID)
      blob = google_bucket.blob('assets/' + accountInfo['organisationID'] + '/thumb_' + fileID)
      temp_filename = 'temp_thumb.png'
      out_file = open(temp_filename, 'wb')
      out_file.write(thumbnail_file)
      out_file = open(temp_filename, 'rb')
      blob.upload_from_file(out_file, content_type='image/png')
      res = blob.make_public()
      thumbnail_url = blob.public_url
      f['thumbnail'] = thumbnail_url
    except Exception as e:
      print('Couldn\'t get thumbnail', e)
      sentry.captureException()
    try:
      os.remove(temp_filename)
    except Exception as e:
      sentry.captureMessage('No file to remove')
  try:
    print('f1')
    print(f)
    oldFile = db.Files(accountInfo['organisationID']).get(f['objectID'], allowFail=True)
  except Exception as e:
    print('Old file doesn\'t exist.', e)
    oldFile = None
  if not Testing:
    db.Files(accountInfo['organisationID']).add(f)
  print('oldFile')
  print(oldFile)
  print('f')
  print(f)
  createFileCard(accountInfo, f)
  cardsSaved = indexFileContent(accountInfo, f)
  f['cardsSaved'] = cardsSaved
  f['organisationID'] = accountInfo['organisationID']
  # notifyChanges(oldFile, f)
  if not Testing and cardsSaved:
    mp.track('admin', 'File Indexed', f)
  print('File Indexed with ' + str(cardsSaved) + ' updated cards: ' + (f['title'] if 'title' in f else ''))

def indexFileContent(accountInfo: dict=None, f: dict=None):
  if not accountInfo or 'organisationID' not in accountInfo or not f or 'objectID' not in f:
    print('Couldn\'t index file content - missing info', accountInfo, f)
    sentry.captureMessage('Couldn\'t index file - missing info', extra={
      'accountInfo': accountInfo,
      'f': f,
    })
    return False
  # Create new cards
  integrationData = services.getIntegrationData(accountInfo=accountInfo, specificCard=f)
  print('integrationData')
  pp.pprint(integrationData)
  if not integrationData or 'module' not in integrationData:
    print('No module defined')
    sentry.captureMessage('No module defined', extra={
      'accountInfo': accountInfo,
      'f': f,
      'integrationData': integrationData,
    })
    return False
  integration = integrationData['module']
  cards = None
  if hasattr(integration, 'getFileCards'):
    # This is for services that are already split into card-like chunks (e.g. Trello)
    print('getFileCards')
    cards = integration.getFileCards(accountInfo, f['objectID'])
    contentArray = None
  if not cards:
    # This is for services that need to be parsed into card-like chunks (e.g. docs, sheets (though maybe ultimately not sheets!))
    try:
      contentArray = integration.getContentForCards(accountInfo, f['objectID']) # Should only take first one!!!
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      contentArray = None
    if not contentArray:
      return 0
    cards = createCardsFromContentArray(accountInfo, contentArray, f)['allCards']
  if not cards or not len(cards):
    return 0
  for i, card in enumerate(cards):
    card['index'] = i
  # Freeze this one
  newFreeze = fileCardsToFreeze(cards)
  # Retrive last freeze (if available)
  blob = google_bucket.blob('diff/' + accountInfo['organisationID'] + '/' + f['objectID'])
  if contentArray: # Need to think more about whether this is the right condition!
    try:
      oldFreeze = blob.download_as_string()
      oldFreeze = oldFreeze.decode("utf-8").split('\n')
      print('oldFreeze')
      pp.pprint([line[:100] for line in oldFreeze])
      print('newFreeze')
      pp.pprint([line[:100] for line in newFreeze])
      print(type(oldFreeze))
      print(type(newFreeze))
    except Exception as e:
      oldFreeze = None
  else:
    oldFreeze = None

  smartReplace = False
  if oldFreeze and len(oldFreeze) == len(newFreeze) and not ForceOverwrite:
    # Retrieve all existing cards
    params = {
      'query': '',
      'filters': 'fileID: "' + f['objectID'] + '"'
    }
    oldCards = db.Cards(accountInfo['organisationID']).browse(params=params)
    oldCards = [hit for hit in oldCards]
    print('oldCards')
    pp.pprint(oldCards)

    # Store objectIDs to replace
    objectIDsToReplace = {}
    smartReplace = True
    for i, line in enumerate(newFreeze):
      oldCard = [card for card in oldCards if 'index' in card and card['index'] == i]
      realObjectID = str(oldCard[0]['objectID']) if len(oldCard) and 'objectID' in oldCard[0] else None
      newCard = [card for card in cards if 'index' in card and card['index'] == i]
      tempObjectID = str(newCard[0]['objectID']) if len(newCard) and 'objectID' in newCard[0] else None
      if tempObjectID and realObjectID:
        objectIDsToReplace[tempObjectID] = realObjectID
      else:
        print('Abandoning Smart Replace')
        sentry.captureMessage('Abandoning Smart Replace', extra={
          'accountInfo': accountInfo,
          'f': f,
          'integrationData': integrationData,
          'cards': cards,
          'oldCards': oldCards,
          'oldCard': oldCard,
          'realObjectID': realObjectID,
          'newCard': newCard,
          'tempObjectID': tempObjectID,
        })
        smartReplace = False
  if smartReplace:
    print('Smart Replace!')
    pp.pprint(objectIDsToReplace)
    # objectIDsToReplace = [[cards[i]['objectID'], oldCards[i]['objectID']] for line, i in enumerate(newFreeze)]
    # Filter to only new cards
    cards = [card for i, card in enumerate(cards) if oldFreeze[i] != newFreeze[i]]
    # Replace new objectIDs with existing ones - INCLUDING references to other cards
    for card in cards:
      card['objectID'] = objectIDsToReplace[card['objectID']]
      if 'listItems' in card:
        for i, item in enumerate(card['listItems']):
          card['listItems'][i] = objectIDsToReplace[item]
    print('Now replaced objectIDs:')
    pp.pprint(cards)
  else:
    if not Testing and 'objectID' in f and len(f['objectID']): # Avoids a blank objectID deleting all cards in index
      # print(f)
      # Delete all chunks from file
      params = {
        'filters': 'type: "p" AND fileID: "' + f['objectID'] + '"'
      }
      db.Cards(accountInfo['organisationID']).delete_by_query(params=params) # Is this dangerous???

      print('Deleted')

  if not Testing:
    # Replace freeze
    try:
      blob.upload_from_string('\n'.join(newFreeze))
    except Exception as e:
      sentry.captureException()
      traceback.print_exc(file=sys.stdout)
    try:
      db.Cards(accountInfo['organisationID']).add(cards)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('Something went wrong saving cards to the database!')
  print('Number of Cards Updated:', len(cards))
  if toPrint['cardsCreated']:
    pp.pprint(cards)
  return len(cards)

def createFileCard(accountInfo, f):
  card = {
    'type': 'file',
    'isFile': True,
    'objectID': str(f['objectID']),
    'format': f['fileFormat'] if 'fileFormat' in f else None,
    'title': f['title'],
    'fileID': f['objectID'],
    'fileUrl': f['url'],
    'fileFormat': f['fileFormat'] if 'fileFormat' in f else None,
    'mimeType': f['mimeType'] if 'mimeType' in f else f['fileType'] if 'fileType' in f else None,
    'fileTitle': f['title'],
    'fileThumbnail': f.get('thumbnail', None),
    'created': f['created'],
    'modified': f['modified'],
    'service': f['service'],
    'superService': f['superService'] if 'superService' in f else None,
    'subService': f['subService'] if 'subService' in f else None,
    'source': f['source'],
  }
  if 'description' in f and f['description']:
    card['description'] = f['description']
  if 'createdBy' in f and f['createdBy']:
    card['createdBy'] = f['createdBy']
  if 'integrationFields' in f and f['integrationFields']:
    card['integrationFields'] = f['integrationFields']
  if not Testing:
    db.Cards(accountInfo['organisationID']).add(card)
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
      'format': fileToCardFormat(f),
      'description': chunk['content'],
      'fileID': f['objectID'],
      'fileUrl': f['url'],
      'fileType': f['fileType'] if 'fileType' in f else f['mimeType'] if 'mimeType' in f else None,
      'fileTitle': f['title'],
      'fileFormat': f['fileFormat'] if 'fileFormat' in f else None,
      'context': parentContext,
      'entityTypes': entityTypes,
      'created': f['created'],
      'modified': f['modified'],
      # 'index': chunk['index'] if 'index' in chunk else None,
      'source': accountInfo.get('accountID', accountInfo.get('objectID', None)),
      'service': f['service'],
      'superService': f['superService'] if 'superService' in f else None,
      'subService': f['subService'] if 'subService' in f else None,
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
  cardIDs = { 'objectIDs': [str(random.randint(1, 1000000000000)) for c in cards] }
  for i, objectID in enumerate(cardIDs['objectIDs']):
    cards[i]['objectID'] = objectID
  return {
    'cards': cards, # Cards on this level
    'allCards': allCards # Cards passed up that should continue being passed
  }

def fileToCardFormat(file):
  subServiceFormats = {
    'gdocs': 'paragraph',
    'gsheets': 'row',
  }
  if 'subService' in file and file['subService'] in subServiceFormats:
    return subServiceFormats[file['subService']]
  else:
    return 'card'


def fileCardsToFreeze(cards):
  newCards = []
  for card in cards:
    newCard = dict(card)
    keysToRemove = ['objectID', 'listItems', 'modified', 'created', 'fileID', 'fileType', 'fileUrl']
    for key in keysToRemove:
      if key in newCard:
        del(newCard[key])
    newCards.append(newCard)
  freeze = [str(card) for card in newCards]
  return freeze

def searchCards(user: dict=None, query: str='', params: dict=None):
  if not user or not len(user) or 'organisationID' not in user:
    return None
  # The next 2 lines are pretty much (if not exactly) dealt with in db.Cards.search so should decide where best to put them
  if (not query or not len(query)) and params and len(params) and 'query' in params:
    query = params['query']
  if params and len(params) and 'search_service' in params:
    search_service = params['search_service']
    del(params['search_service'])
  else:
    search_service = 'algolia'
  results = db.Cards(user['organisationID']).search(query=query, params=params, search_service=search_service)
  track.slack('*' + user_to_name(user) + '* searched and got *' + str(len(results['hits'])) + ' results*.')
  return results

def getCard(user: dict=None, objectID: str=None, params: dict=None):
  if not user or not len(user) or 'organisationID' not in user or not objectID:
    return None
  search_service = params['search_service'] if params and len(params) and 'search_service' in params else 'algolia'
  return db.Cards(user['organisationID']).get(objectID=objectID, search_service=search_service)

def saveCard(card: dict, author:dict):
  # @TODO: Figure out whether sometimes an update will delete a field but it'll be automatically put back in
  if not author or 'organisationID' not in author or 'objectID' not in author:
    return None
  organisationID = author['organisationID']
  keysToRemove = ['_highlightResult']
  for key in keysToRemove:
    if key in card:
      del(card[key])
  existingCard = None
  if 'objectID' in card:
    # Retrieve existing card
    try:
      existingCard = db.Cards(organisationID).get(card['objectID'])
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
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
    integrationData = services.getIntegrationData(specificCard=card)
    integration = integrationData['module'] if integrationData and 'module' in integrationData else None
  else:
    integration = None
  if integration:
    print('has module')
    if 'source' in card and card['source']:
      try:
        source = db.Sources().get(card['source'])
      except Exception as e:
        print('Couldn\'t get source from db.', e)
        sentry.captureException()
        source = None
    else:
      sources = db.Sources().browse(params = {
        'filters': 'organisationID:' + author['organisationID'] + ' AND service:' + card['service']
      })
      source = sources[0]
    # @TODO: Account for the fact that the Sifter API currently doesn't let us update issues, so it always creates a new one
    try:
      if ('type' in card and card['type'] == 'file'):
        print('Saving file to integration!')
        serviceCard = integration.saveFile(source, card)
      else:
        print('Saving card to integration!')
        serviceCard = integration.saveCard(source, card)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      serviceCard = None
      sentry.captureException()
    # Assemble final card
    if serviceCard and type(serviceCard) is dict:
      for key in serviceCard:
        card[key] = serviceCard[key]
  # Save to Savvy
  print('card')
  pp.pprint(card)
  if not Testing:
    savedResult = db.Cards(organisationID).add(card)
    card['objectID'] = savedResult['objectID']
    mp.track(author['objectID'] if author and 'objectID' in author else 'admin', 'Card Saved', card)
  notifyChanges(existingCard, card)
  return { 'success': True, 'card': card }

def deleteCard(card, author):
  if 'objectID' not in card:
    return { 'success': False, 'error': 'Card has no objectID' }
  if not author or 'organisationID' not in author or 'objectID' not in author:
    return { 'success': False, 'error': 'No author with correct details' }
  organisationID = author['organisationID']
  try:
    existingCard = db.Cards(organisationID).get(card['objectID'])
    if not existingCard:
      print('Not found in Algolia - trying ElasticSearch. objectID:', card['objectID'])
      existingCard = db.Cards(organisationID).get(card['objectID'], search_service='elasticsearch')
  except Exception as e:
    sentry.captureException()
    traceback.print_exc(file=sys.stdout)
    existingCard = None
  if not existingCard:
    error_message = 'No existing card to delete.'
    print(error_message)
    sentry.captureMessage(error_message)
    return { 'success': False, 'error': error_message }
  verified = authorIsSavvy(existingCard, author)
  if verified:
    if 'service' in card and card['service']:
      integrationData = services.getIntegrationData(specificCard=card)
      if integrationData and 'module' in integrationData:
        integration = integrationData['module']
        print('has module')
      if 'source' in card and card['source']:
        source = db.Sources().get(card['source'])
      else:
        sources = db.Sources().browse(params={
          'filters': 'organisationID:' + author['organisationID'] + ' AND service:' + card['service']
        })
        source = sources[0]
      if ('type' in card and card['type'] == 'file'):
        # @TODO: Account for the fact that the Sifter API currently doesn't let us delete issues
        try:
          serviceCard = integration.deleteFile(source, card)
        except Exception as e:
          traceback.print_exc(file=sys.stdout)
          serviceCard = {}
    try:
      db.Cards(organisationID).delete(card['objectID'])
      notifyChanges(card, None)
      return { 'success': True, 'card': None }
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      return { 'success': False, 'error': 'Couldn\'t delete card' }
  else:
    try:
      existingCard = db.Cards(organisationID).get(card['objectID'])
      card = dict(existingCard)
      card['pendingDelete'] = True
      db.Cards(organisationID).save(card)
      notifyChanges(existingCard, card)
      return { 'success': True, 'card': card }
    except Exception as e:
      sentry.captureException()
      return { 'success': False, 'error': 'Couldn\'t set card to be pending deletion' }

def verify(objectID: dict, author: dict, prop: str = None, approve: bool = True):
  organisationID = author['organisationID']
  try:
    existingCard = db.Cards(organisationID).get(objectID)
  except Exception as e:
    sentry.captureException()
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
  if not author or not len(author):
    return None
  pp.pprint(card)
  pp.pprint(author)
  userIsAnAdmin = ('role' in author and author['role'] == 'admin')
  print('userIsAnAdmin', userIsAnAdmin)
  cardExists = card and type(card) is dict
  print('cardExists', cardExists)
  print(type(card))
  cardHasNoTopics = card and ('topics' not in card or not card['topics'] or not len(card['topics']))
  print('cardHasNoTopics', cardHasNoTopics)
  authorHasACardTopic = 'topics' in author and type(author['topics']) is list and card and 'topics' in card and len([topic for topic in author['topics'] if topic in card['topics']])
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
  if newFile and type(newFile) is dict and 'service' in newFile and newFile['service'] == 'sifter':
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

def user_to_name(user):
  pp.pprint('user_to_name')
  pp.pprint(user)
  org_name = user['organisationID'] if 'organisationID' in user and user['organisationID'] else None
  user_name = str(user.get('first', '')) + ' ' + str(user.get('last' , ''))
  if len(user_name) < 2:
    user_name = user['emails'][0] if 'emails' in user and user['emails'] and len(user['emails']) else user.get('email', None)
  if org_name:
    if user_name:
      user_name = user_name + ' (' + org_name + ')'
    else:
      user_name = org_name + ' member (ID: ' + user.get('objectID', user.get('uid', 'unknown user')) + ')'
  if not user_name:
    user_name = 'Unknown User'
  return user_name


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
  print('hi')
  indexAll()
  s.enter(60 * minsInterval, 1, reIndex)
  s.run()



"""Below here is stuff for testing"""

# indexAll()


# indexFiles({
#   "organisationID": "Savvy_User4_50014706",
#   "superService": "kloudless",
#   "service": "gdrive",
#   "accountID": 301251343,
#   "access_token": "RDa7SWgGhU7lcGOXXBiPIvX0yL3e5M",
#   "raw_source": {
#     "id": 301251343,
#     "account": "savvyuser4@gmail.com",
#     "active": True,
#     "service": "gdrive",
#     "created": "2018-04-25T10:53:15.235887Z",
#     "modified": "2018-04-25T14:45:30.082237Z",
#     "service_name": "Google Drive",
#     "admin": False,
#     "apis": [
#       "storage"
#     ],
#     "effective_scope": "gdrive:normal.storage.default gdrive:normal.storage.default",
#     "api": "meta",
#     "type": "account"
#   },
#   "scope": "gdrive:normal.storage",
#   "addedBy": "savvyuser4@gmail.com",
#   "title": "Google Drive"
# })
