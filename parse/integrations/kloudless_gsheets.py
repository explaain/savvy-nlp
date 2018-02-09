#!/usr/bin/env python
import urllib, kloudless
from .formats import csv
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

def getExportParams(fileData):
  return {
    'type': 'raw',
    'raw_uri': '/drive/v2/files/' + fileData['rawID'] + '/export?mimeType=' + urllib.parse.quote_plus('text/csv'),
    'raw_method': 'GET'
  }

def fileToCardData(exportedFile):
  content = exportedFile.content.decode("utf-8")
  contentArray = csv.getContentArray(csvContent)
  return contentArray
