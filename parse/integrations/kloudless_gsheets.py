#!/usr/bin/env python
import urllib, kloudless
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

def getExportParams(fileData):
  return {
    'type': 'raw',
    'raw_uri': '/drive/v2/files/' + fileData['rawID'] + '/export?mimeType=' + urllib.parse.quote_plus('text/csv'),
    'raw_method': 'GET'
  }

def fileToCardData(exportedFile):
  content = exportedFile.content.decode("utf-8")
  contentArray = getCsvContentArray(csvContent)
  return contentArray

def getCsvContentArray(csvContent):
  split = csvContent.split('\r\n')
  print(split)
  firstRow = split[0].split(',')
  contents = [ '\n'.join([(addColon(firstRow[i]) + ' ' + cell) for i, cell in enumerate(row.split(',')) if len(cell)]) for row in split[1:] ]
  print(contents)
  contentArray = [{'content': content, 'allRankings': {}, 'otherContext': {}, 'ranking': 0} for content in contents]
  return contentArray


def addColon(text):
  return text + ':' if not text.endswith(':') else text
