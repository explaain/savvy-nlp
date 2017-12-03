#!/usr/bin/env python
import pprint, datetime, sched, time
from algoliasearch import algoliasearch
from parse import drives
pp = pprint.PrettyPrinter(indent=4)

client = algoliasearch.Client("I2VKMNNAXI", 'a202abb1140bd81265eb38b186d822d3') # This API key was generated specifically for modifying SavvyFiles and SavvyChunks indices
algoliaFilesIndex = client.init_index('SavvyFiles')
algoliaChunksIndex = client.init_index('SavvyChunks')

def indexFiles():
  memory = open('memory.txt','r')
  lastRefresh = datetime.datetime.strptime(memory.read().splitlines()[0], '%Y-%m-%d %H:%M:%S.%f')
  print(lastRefresh)
  memory = open('memory.txt','w')
  memory.write(str(datetime.datetime.now()))
  files = drives.listfiles('', '', after=lastRefresh)
  pp.pprint(files)
  # algoliaFilesIndex.add_objects(files)

  for f in files:
    indexFile(f['objectID']) # We index them again because they seem to first come in with their original names e.g. "Untitled document"

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
  print(contentArray)
  cards = [{
    'content': c,
    'fileID': f['objectID'],
    'fileTitle': f['title'],
    'created': f['created'],
    'modified': f['modified'],
    'type': 'p',
    'index': i
  } for i,c in enumerate(contentArray)]
  pp.pprint(cards)
  algoliaChunksIndex.add_objects(cards)


minsInterval = 10
s = sched.scheduler(time.time, time.sleep)
def reIndex():
  indexFiles()
  s.enter(60 * minsInterval, 1, reIndex)

s.enter(60 * minsInterval, 1, reIndex)
s.run()


# indexFiles()
# indexFile('FBNJFgtvI4HkQoiqKPmByPL0BYCrnkAy_iP56qn2QMe8=')
# indexFileContent({'objectID': 'FVNDMMXfVj99RqJMyz1xiFpk63kKA44NqCKEKimaUF1F63QxFJmvnRuuGKN2JyLXY', 'title': 'Policy Tracker for GE2017.com', 'modified': '1499418614', 'created': 'null'})
