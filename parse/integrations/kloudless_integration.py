#!/usr/bin/env python
import re, io, pprint, itertools, zipfile, untangle, time
from collections import OrderedDict
import xmljson
from . import kloudless_gdocs as gdocs, kloudless_gsheets as gsheets
from xmljson import parker, Parker
# bf = BadgerFish(dict_type=OrderedDict)
from xml.etree.ElementTree import fromstring
pp = pprint.PrettyPrinter(indent=1, width=160)

import kloudless
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

def listAccounts():
  accounts = kloudless.Account.all()
  return accounts

def getAccount(accountID):
  account = kloudless.Account(id=accountID)
  return account

def listFiles(accountInfo, after=False, number=500):
  account = getAccount(accountInfo['accountID'])
  recent = []
  if after:
    recent = account.recent.all(page_size=number, after=after)
  else:
    recent = account.recent.all(page_size=number)
  # print('Number of Files:', len(recent))
  # print('files: ', '\n'.join(list(map(lambda x: x['name'], recent))))
  files = [kloudlessToFile(f, accountInfo) for f in recent]
  return files

def getFile(accountInfo, fileID):
  print('getFile')
  account = getAccount(accountInfo['accountID'])
  f = {}
  try:
    f = account.files.retrieve(id=fileID)
    # Starting to add author info but need to fix permissions issue - team admin access?
    # print("f['owner']['id']", f['owner']['id'])
    # author = account.users.retrieve(id=f['owner']['id'])
    f = kloudlessToFile(f, accountInfo)
  except Exception as e:
    f = None
    print('Error getting file: "' + fileID + '"', e)
  return f


def getFileUrl(id, fileType):
  print('getFileUrl', id, fileType)
  roots = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'https://docs.google.com/document/d/',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'https://docs.google.com/spreadsheets/d/',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'https://docs.google.com/presentation/d/',
    'application/vnd.google-apps.document': 'https://docs.google.com/document/d/',
    'application/vnd.google-apps.spreadsheet': 'https://docs.google.com/spreadsheets/d/',
    'application/vnd.google-apps.presentation': 'https://docs.google.com/presentation/d/',
    # 'application/pdf': 'https://drive.google.com/file/d/'
  }
  return (roots[fileType] if fileType and fileType in roots else 'https://drive.google.com/file/d/') + id

def kloudlessToFile(f, accountInfo):
  serviceData = getServiceByFileType(f['mime_type'])
  algoliaFile = {
    'objectID': f['id'],
    'url': getFileUrl(f['raw_id'], f['mime_type']),
    'rawID': f['raw_id'],
    'fileType': f['mime_type'],
    'title': f['name'],
    'created': time.mktime(f['created'].timetuple()) if f['created'] else None,
    'modified': time.mktime(f['modified'].timetuple()) if f['modified'] else None,
    'source': accountInfo['accountID'],
    'superService': 'kloudless',
    'service': serviceData['service'] if serviceData and 'service' in serviceData else None
  }
  return algoliaFile

def getExportedFileData(accountInfo, fileID):
  print('getExportedFileData')
  fileData = getFile(accountInfo, fileID)
  if not fileData:
    return None
  fileType = fileData['fileType']
  serviceData = getServiceByFileType(fileType)
  if not serviceData or 'module' not in serviceData:
    return None
  driveService = serviceData['module']
  account = getAccount(accountInfo['accountID'])
  exportParams = driveService.getExportParams(fileData, type='getContent')
  # print('exportParams')
  # print(exportParams)
  if exportParams['type'] == 'retrieve':
    exportedFile = account.files.retrieve(fileID)
  elif exportParams['type'] == 'raw':
    exportedFile = account.raw(raw_uri = exportParams['raw_uri'] if 'raw_uri' in exportParams else '', raw_method=exportParams['raw_method'] if 'raw_method' in exportParams else '')
  return {
    'exportedFile': exportedFile,
    'driveService': driveService
  }

def getFileContent(accountInfo, fileID):
  exportedFileData = getExportedFileData(accountInfo, fileID)
  return exportedFileData['driveService'].fileToContent(exportedFileData['exportedFile']) if exportedFileData else None

def getContentForCards(accountInfo, fileID):
  exportedFileData = getExportedFileData(accountInfo, fileID)
  return exportedFileData['driveService'].fileToCardData(exportedFileData['exportedFile']) if exportedFileData else None

def getServiceByFileType(fileType):
  servicesByFileType = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': {
      'service': 'gdocs',
      'format': 'xml_doc',
      'module': gdocs,
    },
    'application/vnd.google-apps.document': {
      'service': 'gdocs',
      'format': 'xml_doc',
      'module': gdocs,
    },
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
      'service': 'gsheets',
      'format': 'csv',
      'module': gsheets,
    },
    'application/vnd.google-apps.spreadsheet': {
      'service': 'gsheets',
      'format': 'csv',
      'module': gsheets,
    },
  }
  driveService = servicesByFileType[fileType] if fileType in servicesByFileType else None
  return driveService


def saveCard(source: dict, card: dict):
  print('saving!')
  if 'cells' in card:
    return gsheets.saveCard(source, card)
  else:
    return None


# getFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'F1UVWb2gWfAQZO4FbkhySjqnnu6W2YVHAh2qAVb-bbleYPrNzGv-Re5xozb8UNKXi')
#
# getExportedFileData({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'FptwaKolhPnYFPLUWBubCo3ASpk14lLPhK_ndV0jmlaQg6hmdRX0zb5Autwinmcce')

# pp.pprint(listAccounts())
