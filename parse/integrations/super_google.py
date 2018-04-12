from __future__ import print_function
import pprint, json, datetime
import httplib2, http
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from oauth2client.client import GoogleCredentials
from oauth2client import GOOGLE_TOKEN_URI

from . import gmail

CLIENT_SECRET_FILE = 'google_connect_client_secret.json'
APPLICATION_NAME = 'Savvy'

pp = pprint.PrettyPrinter(indent=1, width=160)

client = json.load(open(CLIENT_SECRET_FILE))

def get_credentials(source):
  gCreds = GoogleCredentials(
    source['access_token'],
    client['web']['client_id'],
    client['web']['client_secret'],
    source['refresh_token'],
    source['token_expiry'],
    GOOGLE_TOKEN_URI,
    source['user_agent'],
    revoke_uri=source['revoke_uri']
  )
  return gCreds

def get_service(serviceName):
  services = {
    'gmail': {
      'serviceName': 'gmail',
      'title': 'Gmail',
      'module': gmail,
    }
  }
  return services[serviceName]

def get_google_service(source):
  credentials = get_credentials(source)
  http_auth = credentials.authorize(httplib2.Http())
  service_module = get_service(source['service'])['module']
  google_service = service_module.get_google_service(http_auth)
  return google_service

# @TODO Figure out whether this still needs 'after' or 'number'
def listFiles(source, after=False, number=500):
  service_module = get_service(source['service'])['module']
  google_service = get_google_service(source)
  files = service_module.list_files(google_service, source)
  for file in files:
    if file and len(file) > 0:
      file['superService'] = 'google'
  pp.pprint(files)
  return files

def getFile(source: dict=None, fileID: str=None):
  if not source or not fileID:
    return None
  service_module = get_service(source['service'])['module']
  google_service = get_google_service(source)
  file = service_module.get_file(google_service, source, fileID)
  file['superService'] = 'google'
  return file

# def getExportedFileData(source, file_id):
#   return None

def getFileCards(source: dict=None, file_id: str=None):
  if not source or 'service' not in source or not file_id:
    return None
  service = get_service(source['service'])
  if 'module' not in service:
    return None
  service_module = service['module']
  if not hasattr(service_module, 'get_cards'):
    return None
  google_service = get_google_service(source)
  if not google_service:
    return None
  cards = service_module.get_cards(google_service, source, file_id)
  return cards

def getContentForCards(source, file_id):
  service_module = get_service(source['service'])['module']
  google_service = get_google_service(source)
  content_for_cards = service_module.get_content_for_cards(google_service, source, file_id)
  return content_for_cards


def getFileUrl(id, mimeType):
  return None

def getServiceModuleByName(serviceName):
  return None

def getSubServiceByMimeType(mimeType: str, source: dict=None):
  return None

def mimeTypeToFileFormat(mimeType: str):
  return None



def saveCard(source: dict, card: dict):
  return None

#
# source = {   'access_token': 'ya29.GluWBas4lqycjRobeUke5AWjeWNqphLZN4M_gWkcY0YfiC0er4fvw_z1h0akMle0-X79aMpGjTg9NWfRX6-khcqEJj0XuI_jRm6w4YOfwCZsFzy1amF2isfa_mKP',
#     'code': '4/AAAPQUlZqLo985b_9slclk2DYKGJVk8d3t1OXhZJBVivxAq_NM5nUNDR6MFQAqwc5mkdQ-LtFLnz1i2rvffwZjg',
#     'id_token': {   'at_hash': '0Y3Lg94fJ29-AfcsQO4klg',
#                     'aud': '704974264220-lmbsg98tj0f3q09lv4tk6ha46flit4f0.apps.googleusercontent.com',
#                     'azp': '704974264220-lmbsg98tj0f3q09lv4tk6ha46flit4f0.apps.googleusercontent.com',
#                     'email': 'jeremy@explaain.com',
#                     'email_verified': True,
#                     'exp': 1523119243,
#                     'hd': 'explaain.com',
#                     'iat': 1523115643,
#                     'iss': 'accounts.google.com',
#                     'sub': '104380110279658920175'},
#     'objectID': '826182612',
#     'organisationID': 'explaain',
#     'refresh_token': '1/t1CV_co7Ruo4pBgCGfXGhqVPn9oDn-t_a-3VL6Q0MYU',
#     'revoke_uri': 'https://accounts.google.com/o/oauth2/revoke',
#     'scopes': ['https://www.googleapis.com/auth/gmail.readonly'],
#     'service': 'gmail',
#     'superService': 'google',
#     'title': 'Gmail',
#     'token_expiry': datetime.datetime(2018, 4, 7, 16, 40, 43, 784752),
#     'totalSources': 72,
#     'user_agent': None}
#
# getContentForCards(source, '161ce2a9ea8dc4a7')
