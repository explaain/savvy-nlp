#!/usr/bin/env python
import pprint, datetime, sched, time
from algoliasearch import algoliasearch
from parse import drives
import xmljson
pp = pprint.PrettyPrinter(indent=4)

client = algoliasearch.Client("I2VKMNNAXI", 'a202abb1140bd81265eb38b186d822d3') # This API key was generated specifically for modifying SavvyFiles and SavvyChunks indices
algoliaFilesIndex = client.init_index('SavvyFiles')
algoliaChunksIndex = client.init_index('SavvyChunks')

def indexFiles():
  memory = open('memory.txt','r')
  lastRefreshTime = datetime.datetime.strptime(memory.read().splitlines()[0], '%Y-%m-%d %H:%M:%S.%f')
  print(lastRefreshTime)
  thisRefreshTime = str(datetime.datetime.now())
  files = drives.listfiles('', '', after=lastRefreshTime)
  pp.pprint([f['title'] for f in files])
  pp.pprint(files)

  for f in files:
    indexFile(f['objectID']) # We index them again because they seem to first come in with their original names e.g. "Untitled document"

  memory = open('memory.txt','w') # Happens now so that incomplete indexing doesn't overwrite lastRefreshTime
  memory.write(thisRefreshTime)

def indexFile(fileID):
  f = drives.getfile('', '', fileID=fileID)
  pp.pprint(f)
  algoliaFilesIndex.add_object(f)
  indexFileContent(f)

def indexFileContent(f):
  print(f)
  # Delete all chunks from file
  params = {
    'filters': 'fileID: "' + f['objectID'] + '"'
  }
  algoliaChunksIndex.delete_by_query('', params)

  # Create new chunks
  contentArray = drives.getContent('', '', f['objectID'], True)
  print('contentArray', contentArray)
  cards = createCardsFromContentArray(contentArray, f)['allCards']
  # print(cards)
  pp.pprint(cards)


def createCardsFromContentArray(contentArray, f):
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
      subdata = createCardsFromContentArray(chunk['chunks'], f)
      subcards = subdata['cards']
      allCards += subdata['allCards']
      # cards += subcards
      card['listItems'] = [c['objectID'] for c in subcards]
      card['listCards'] = [c['content'] for c in subcards]
    cards.append(card)
    allCards.append(card)
  cardIDs = algoliaChunksIndex.add_objects(cards)
  print(cardIDs['objectIDs'])
  for i, objectID in enumerate(cardIDs['objectIDs']):
    cards[i]['objectID'] = objectID
  return {
    'cards': cards, # Cards on this level
    'allCards': allCards # Cards passed up that should continue being passed
  }



minsInterval = 10
s = sched.scheduler(time.time, time.sleep)
def reIndex():
  indexFiles()
  s.enter(60 * minsInterval, 1, reIndex)

s.enter(60 * minsInterval, 1, reIndex)
s.run()


# indexFiles()
# indexFile('FqTmNLmwOqrf3tLudMvuJYhRhFgdMPgFk4nWbFGLEnN5jjQSba26Olb_j6G_YZQEm')
# indexFileContent({'objectID': 'FVNDMMXfVj99RqJMyz1xiFpk63kKA44NqCKEKimaUF1F63QxFJmvnRuuGKN2JyLXY', 'title': 'Policy Tracker for GE2017.com', 'modified': '1499418614', 'created': 'null'})


# xmlstring = open('parse/sample.xml').read()
# print(xmlstring)
# drives.xmlFindText(xmlstring)
