def getContentArray(csvContent):
  split = csvContent.split('\r\n')
  print(split)
  firstRow = split[0].split(',')
  contents = [ '\n'.join([(addColon(firstRow[i]) + ' ' + cell) for i, cell in enumerate(row.split(',')) if len(cell)]) for row in split[1:] ]
  print(contents)
  contentArray = [{'content': content, 'allRankings': {}, 'otherContext': {}, 'ranking': 0} for content in contents]
  return contentArray


def addColon(text):
  return text + ':' if not text.endswith(':') else text
