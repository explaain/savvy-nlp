import re, pprint, untangle
from html.parser import HTMLParser

pp = pprint.PrettyPrinter(indent=1, width=160)

def getContentArray(html):
  print(html)
  content = []
  currentTags = []
  # create a subclass and override the handler methods
  class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
      currentTags.append(tag)

    def handle_endtag(self, tag):
      currentTags.pop()

    def handle_data(self, data):
      tags = list(currentTags)
      text = data.strip()
      if len(text):
        content.append({
          'content': text,
          'tags': tags,
          'ranking': getRankingFromTags(tags)
        })

  # instantiate the parser and fed it some HTML
  parser = MyHTMLParser()
  parser.feed(html)
  chunkHierarchy = getChunkHierarchy(content)
  for c in chunksToPrint(chunkHierarchy):
    print(c)
  return chunkHierarchy

def getRankingFromTags(tags):
  ranks = {
    'h1': 400,
    'h2': 300,
    'h3': 200,
    'h4': 100,
    'h5': 60,
    'h6': 40,
    'ul': -10,
    'b': 10
  }
  ranking = 0
  for tag in tags:
    if tag in ranks:
      ranking += ranks[tag]

  return ranking


# getContentArray('<html><head><title>Test</title></head><body><h1>Parse me!</h1></body></html>')




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
