import pprint
from csv import reader

pp = pprint.PrettyPrinter(indent=4)

def getContentArray(csvContent):
  split = csvContent.split('\r\n')
  if (len(split) == 1):
    split = csvContent.split('\n') # Ideally we fix this - it seems to be just for test_parse() (not even test_fetchAndParse())
  firstRow = split[0].split(',')
  rows = [[cell for cell in reader([row])][0] for row in split]
  # contentArray =
  # [{'content': 'Table', 'allRankings': {}, 'otherContext': {}, 'ranking': 20, 'chunks':
  contentArray = [{'content': row[0], 'allRankings': {}, 'otherContext': {}, 'ranking': 10,
     'cells': [
      {'content': labelPlusValue(firstRow[i], cell), 'label': firstRow[i], 'value': cell} for i, cell in enumerate(row)
    ]
     # 'chunks': [
      # {'content': addColon(firstRow[i]) + ' ' + cell, 'label': firstRow[i], 'value': cell, 'allRankings': {}, 'otherContext': {}, 'ranking': 0} for i, cell in enumerate(row) if cell and len(cell)
    # ]
    } for row in rows[1:]]
  # }]
  # print('contentArray')
  # print(contentArray)
  print(len(contentArray))
  pp.pprint(contentArray)

  return contentArray

def addColon(text):
  return text + ':' if not text.endswith(':') else text

def labelPlusValue(text1, text2):
  if not text2 or not len(text2):
    return ''
  elif text1 and len(text1):
    return addColon(text1) + ' ' + text2
  else:
    return text2

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
