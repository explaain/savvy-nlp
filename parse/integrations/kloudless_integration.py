#!/usr/bin/env python
import re, io, pprint, itertools, zipfile, untangle
from collections import OrderedDict
import xmljson
from . import kloudless_gdocs as gdocs, kloudless_gsheets as gsheets
from xmljson import parker, Parker
# bf = BadgerFish(dict_type=OrderedDict)
from xml.etree.ElementTree import fromstring
pp = pprint.PrettyPrinter(indent=1, width=160)

import kloudless
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

# Decide what to print out:
toPrint = {
  'fileList': True,
  'xmlString': False,
  'elements': False,
  'arrayOfPars': False,
  'justScores': False,
  'hierarchies': False,
  'hierarchyText': True
}


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
  print('Number of Files:', len(recent))
  print('files: ', '\n'.join(list(map(lambda x: x['name'], recent))))
  files = [fileToAlgolia(f, accountInfo) for f in recent]
  return files

def getFile(accountInfo, fileID):
  account = getAccount(accountInfo['accountID'])
  f = {}
  try:
    f = account.files.retrieve(id=fileID)
    # Starting to add author info but need to fix permissions issue - team admin access?
    # print("f['owner']['id']", f['owner']['id'])
    # author = account.users.retrieve(id=f['owner']['id'])
    f = fileToAlgolia(f, accountInfo)
    print('file:')
    pp.pprint(f)
  except Exception as e:
    f = None
    print('Error getting file: "' + fileID + '"', e)
  return f


def getFileUrl(id, fileType):
  roots = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'https://docs.google.com/document/d/',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'https://docs.google.com/spreadsheets/d/',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'https://docs.google.com/presentation/d/',
    # 'application/pdf': 'https://drive.google.com/file/d/'
  }
  return (roots[fileType] if fileType in roots else 'https://drive.google.com/file/d/') + id

def fileToAlgolia(f, accountInfo):
  print('fileToAlgolia')
  print(f)
  pp.pprint(accountInfo)
  return {
    'objectID': f['id'],
    'url': getFileUrl(f['raw_id'], f['mime_type']),
    'rawID': f['raw_id'],
    'mimeType': f['mime_type'],
    'title': f['name'],
    'created': f['created'],
    'modified': f['modified'],
    'source': accountInfo['accountID']
  }

# Delete this soon if its being commented out doesn't break anything!
# def fileToCard(f):
#   name = f['name']
#   card = {
#     'card': {
#       'content': {},
#       'file': {
#         'id': f['id'],
#         'url': getFileUrl(f['raw_id'], f['mime_type']),
#         'title': f['name'],
#         'folder': 'Google Drive'
#       },
#       'objectID': f['id'][:12],
#       'highlight': True
#     }
#   }
#   return card

def getContent(accountInfo, fileID):
  fileData = getFile(accountInfo, fileID)
  if not fileData:
    return None
  servicesByFileType = {
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': gdocs,
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': gsheets
  }
  fileType = fileData['mimeType']
  if fileType not in servicesByFileType:
    return None
  account = getAccount(account['accountID'])
  driveService = servicesByFileType[fileType]
  exportParams = driveService.getExportType(fileData)
  exportMethod = {
    'retrieve': account.files.retrieve(fileID),
    'raw': account.raw(raw_uri='/drive/v2/files/' + rawID + '/export?mimeType=' + urllib.parse.quote_plus(format), raw_method='GET')
  }
  exportedFile = exportMethod[exportParams['type']]
  return driveService.fileToCardData(exportedFile)




# getFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'F1UVWb2gWfAQZO4FbkhySjqnnu6W2YVHAh2qAVb-bbleYPrNzGv-Re5xozb8UNKXi')
