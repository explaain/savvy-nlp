#!/usr/bin/env python
import urllib, kloudless
from .formats import csv
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

def getExportParams(fileData):
  print('fileData')
  print(fileData)
  return {
    'type': 'raw',
    'raw_uri': '/drive/v2/files/' + fileData['rawID'] + '/export?mimeType=' + urllib.parse.quote_plus('text/csv'),
    'raw_method': 'GET'
  }

def fileToContent(exportedFile):
  content = exportedFile.content.decode("utf-8")
  return content

def fileToCardData(exportedFile):
  content = fileToContent(exportedFile)
  contentArray = csv.getContentArray(csvContent)
  return contentArray
