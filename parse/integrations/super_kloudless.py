#!/usr/bin/env python
import re, io, pprint, itertools, zipfile, untangle, time, traceback, sys, requests
from raven import Client as SentryClient
from collections import OrderedDict
import xmljson
from . import kloudless_gdrive as gdrive, kloudless_gdocs as gdocs, kloudless_gsheets as gsheets, kloudless_dropbox as dropbox
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

def listFiles(accountInfo, after=False, number=50):
  account = getAccount(accountInfo['accountID'])
  recent = []
  if after:
    recent = account.recent.all(page_size=number, after=after)
  else:
    recent = account.recent.all(page_size=number)
  # print('Number of Files:', len(recent))
  # print('files: ', '\n'.join(list(map(lambda x: x['name'], recent))))
  files = [kloudlessToFile(f, accountInfo) for f in recent]
  print('len(files)')
  print(len(files))
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

    # conn = tinys3.Connection('AKIAJGW24TQI7M6LLI3A','Lnkm+eArFD7HPbI4Ppe83l8WJmlXDiaDjKtiLm6y',tls=True)
    # f = open('gslides.png','rb')
    # a = conn.upload('gslides.png', f, 'savvy-storage')
    # print(a)
    # return None
    # try:
    # except Exception as e:
    #   thumb = None
    #   print('Error getting thumbnail: "' + fileID + '"', e)

  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    f = None
    print('Error getting file: "' + fileID + '"', e)
  return f

def get_thumbnail(source, fileID):
  if not source or 'accountID' not in source or not fileID:
    return None
  thumb = requests.get('https://api.kloudless.com/v1/accounts/' + str(source['accountID']) + '/storage/files/' + str(fileID) + '/thumbnail',
    headers={ 'Authorization': 'APIKey q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T' })
  return thumb.content

def kloudlessToFile(f, accountInfo):
  # print('kloudlessToFile')
  # pp.pprint(f)
  subServiceData = getSubServiceByMimeType(f['mime_type'], accountInfo)
  file = {
    'objectID': f['id'],
    'url': getFileUrl(f['raw_id'], f['mime_type']),
    'rawID': f['raw_id'],
    'fileFormat': mimeTypeToFileFormat(f['mime_type']),
    'mimeType': f['mime_type'],
    'title': f['name'],
    'created': time.mktime(f['created'].timetuple()) if f['created'] else None,
    'modified': time.mktime(f['modified'].timetuple()) if f['modified'] else None,
    'source': accountInfo['accountID'],
    'superService': 'kloudless',
    'service': accountInfo['service'],
  }
  if subServiceData and 'serviceName' in subServiceData:
    file['subService'] = subServiceData['serviceName']
  # pp.pprint(file)
  return file

def getExportedFileData(accountInfo, fileID):
  print('getExportedFileData')
  fileData = getFile(accountInfo, fileID)
  if not fileData:
    return None
  mimeType = fileData['mimeType']
  subServiceData = getSubServiceByMimeType(mimeType, accountInfo)
  if subServiceData and 'module' in subServiceData:
    driveService = subServiceData['module']
  else:
    driveService = getServiceModuleByName(accountInfo['service'])
  if not driveService:
    return None
  account = getAccount(accountInfo['accountID'])
  exportParams = driveService.getExportParams(fileData, type='getContent')
  print('exportParams')
  pp.pprint(exportParams)
  if exportParams['type'] == 'retrieve':
    exportedFile = account.files.retrieve(fileID)
    # print('exportedFile')
    # pp.pprint(exportedFile)
  elif exportParams['type'] == 'raw':
    exportedFile = account.raw(raw_uri = exportParams['raw_uri'] if 'raw_uri' in exportParams else '', raw_method=exportParams['raw_method'] if 'raw_method' in exportParams else '')
  else:
    exportedFile = None
  return {
    'exportedFile': exportedFile,
    'driveService': driveService
  }

# @TODO: Seems like this is no longer used!
# def getFileContent(accountInfo, fileID):
#   exportedFileData = getExportedFileData(accountInfo, fileID)
#   return exportedFileData['driveService'].fileToContent(exportedFileData['exportedFile']) if exportedFileData else None

def getContentForCards(accountInfo, fileID):
  print('getContentForCards')
  exportedFileData = getExportedFileData(accountInfo, fileID)
  # print('exportedFileData')
  # pp.pprint(exportedFileData)
  return exportedFileData['driveService'].fileToCardData(exportedFileData['exportedFile']) if exportedFileData and 'exportedFile' in exportedFileData and exportedFileData['exportedFile'] else None


def getFileUrl(id, mimeType):
  # print('getFileUrl', id, mimeType)
  roots = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'https://docs.google.com/document/d/',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'https://docs.google.com/spreadsheets/d/',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'https://docs.google.com/presentation/d/',
    'application/vnd.google-apps.document': 'https://docs.google.com/document/d/',
    'application/vnd.google-apps.spreadsheet': 'https://docs.google.com/spreadsheets/d/',
    'application/vnd.google-apps.presentation': 'https://docs.google.com/presentation/d/',
    # 'application/pdf': 'https://drive.google.com/file/d/'
  }
  return (roots[mimeType] if mimeType and mimeType in roots else 'https://drive.google.com/file/d/') + id

def getServiceModuleByName(serviceName):
  serviceModules = {
    'dropbox': dropbox,
    'gdrive': gdrive,
  }
  return serviceModules[serviceName] if serviceName in serviceModules else None

def getSubServiceByMimeType(mimeType: str, accountInfo: dict=None):
  if not accountInfo or 'service' not in accountInfo or accountInfo['service'] != 'gdrive':
    return None
  if mimeType in [
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.google-apps.document'
  ]:
    return {
      'serviceName': 'gdocs',
      'title': 'Google Docs',
      'format': 'xml_doc',
      'module': gdocs,
    }
  elif mimeType in [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.spreadsheet'
  ]:
    return {
      'serviceName': 'gsheets',
      'title': 'Google Sheets',
      'format': 'csv',
      'module': gsheets,
    }
  else:
    return None

def mimeTypeToFileFormat(mimeType: str):
  if mimeType in [
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.google-apps.document',
    'application/vnd.oasis.opendocument.text', # .odt
    'application/msword', # .doc
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # .docx
    'application/rtf',
  ]:
    return 'document'
  elif mimeType in [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.google-apps.spreadsheet',
    'application/vnd.oasis.opendocument.spreadsheet', # .ods
    'application/vnd.ms-excel', # .xls
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', # .xlsx
    'text/csv',
  ]:
    return 'spreadsheet'
  elif mimeType in [
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.google-apps.presentation',
    'application/vnd.oasis.opendocument.presentation', # .odp
    'application/vnd.ms-powerpoint', # .ppt
    'application/vnd.openxmlformats-officedocument.presentationml.presentation', # .pptx
  ]:
    return 'presentation'
  elif mimeType[:6] == 'image/':
    return 'image'
  elif mimeType[:6] == 'video/':
    return 'video'
  elif mimeType[:6] == 'audio/':
    return 'audio'
  elif mimeType == 'application/pdf':
    return 'pdf'
  elif mimeType == 'text/plain':
    return 'text'
  elif mimeType == 'text/html':
    return 'webpage'
  elif mimeType == 'text/calendar':
    return 'event'
  elif mimeType == 'application/zip':
    return 'archive'
  elif mimeType == 'application/json':
    return 'data' # Should CSV be this too?
  else:
    return None



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



# listFiles({
#   "organisationID": "soham_trivedi_16267537",
#   "superService": "kloudless",
#   "service": "gdrive",
#   "accountID": 301467186,
#   "access_token": "mBmiNbWh06RBzn5EFanV2Irs5rwR4o",
#   "raw_source": {
#     "id": 301467186,
#     "account": "soham@techalchemy.co",
#     "active": True,
#     "service": "gdrive",
#     "created": "2018-04-27T13:44:41.561578Z",
#     "modified": "2018-04-27T13:44:42.870781Z",
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
#   "addedBy": "soham@techalchemy.co",
#   "title": "Google Drive"
# })
