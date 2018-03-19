#!/usr/bin/env python
from __future__ import print_function
import pprint, urllib, kloudless, oauth2client
from .formats import csv
kloudless.configure(api_key='q4djKR_UXs8MxmUv8M56WdTVihDK6Z7ci8JnL1qJvC2Xx40T')

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

pp = pprint.PrettyPrinter(indent=2, width=200)

def getExportParams(fileData, type: str = 'getContent'):
  print('fileData')
  print(fileData)
  if type == 'getContent':
    return {
      'type': 'raw',
      'raw_uri': '/drive/v2/files/' + fileData['rawID'] + '/export?mimeType=' + urllib.parse.quote_plus('text/csv'),
      'raw_method': 'GET'
    }
  elif type == 'get':
    return {
      'type': 'raw',
      'raw_uri': 'https://www.googleapis.com/v4/spreadsheets/' + fileData['rawID'] + '/values/A1:A9',
      'raw_method': 'GET'
    }

def fileToContent(exportedFile):
  content = exportedFile.content.decode("utf-8")
  return content

def fileToCardData(exportedFile):
  content = fileToContent(exportedFile)
  contentArray = csv.getContentArray(content)
  return contentArray

def saveCard(source: dict, card: dict):
  """Shows basic usage of the Sheets API.

  Creates a Sheets API service object and prints the names and majors of
  students in a sample spreadsheet:
  https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
  """
  print('beginning saving to gsheets')
  if not source:
    return None
  if not card or 'index' not in card or 'cells' not in card:
    return None
  savedCredentials = source['googleRawCredentials'] if 'googleRawCredentials' in source else None
  if not savedCredentials:
    return None
  credentials = oauth2client.client.OAuth2Credentials(
    client_id = savedCredentials['client_id'],
    client_secret = savedCredentials['client_secret'],
    refresh_token = savedCredentials['refresh_token'],
    scopes = savedCredentials['scopes'],
    access_token = savedCredentials['access_token'],
    token_uri = savedCredentials['token_uri'],
    user_agent = savedCredentials['user_agent'],
    token_expiry = savedCredentials['token_expiry']
  )

  # credentials = get_credentials()
  http = credentials.authorize(httplib2.Http())
  discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
    'version=v4')
  service = discovery.build('sheets', 'v4', http=http,
    discoveryServiceUrl=discoveryUrl)

  spreadsheet_id = card['fileUrl'].split('/')[-1]
  rowNumber = str(card['index'] + 2)
  range_name = 'A' + rowNumber + ':' + chr(64 + (len(card['cells']) if 'cells' in card and len(card['cells']) else 1)) + rowNumber # @TODO: Handle multiple sheets here
  values = [[cell['value'] if 'value' in cell else '' for cell in card['cells']]]
  print('values')
  print(values)
  body = {
    'values': values
  }
  result = service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id, range=range_name,
    valueInputOption='USER_ENTERED', body=body).execute()
  print('{0} cells updated.'.format(result.get('updatedCells')))
  if 'cells' in card and len(card['cells']) and type(card['cells'][0]) is dict and 'value' in card['cells'][0]:
    card['description'] = card['cells'][0]['value']
  return card



# saveCard({
#   'id': 297914432,
#   'account': 'ycxsavvy@gmail.com',
#   'active': True,
#   'service': 'gdrive',
#   'created': '2018-03-19T12:44:35.215342Z',
#   'modified': '2018-03-19T12:44:36.638379Z',
#   'service_name': 'Google Drive',
#   'admin': False,
#   'apis': [
#     'storage'
#   ],
#   'effective_scope': 'gdrive:normal.storage.default gdrive:normal.storage.default',
#   'api': 'meta',
#   'type': 'account',
#   'organisationID': 'acme-savvy',
#   'addedBy': 'ycxsavvy@gmail.com',
#   'superService': 'kloudless',
#   'googleRawCredentials': {
#     'client_id': '704974264220-lmbsg98tj0f3q09lv4tk6ha46flit4f0.apps.googleusercontent.com',
#     'client_secret': '7fU16P8yZL-MHzMItnOw-SR0',
#     'refresh_token': '1/zs_yDlL6E5xvLOrdsMjU9QweY-BO5CHI2MVW6hMfDME',
#     'scopes': [
#       'https://www.googleapis.com/auth/drive.metadata.readonly',
#       'https://www.googleapis.com/auth/spreadsheets'
#     ],
#     'access_token': 'ya29.GluDBVfVhHj7y0EWv2q0IFwHfXZ737PddPa1FvamfVsRdNZOn_NeAjC10Wh92SWXbOGdbr54ULsf7mSEoZcUY3H7aesWzpCex5NaklOxr6vYC-nX4DjEvEn3gnrS',
#     'token_uri': 'https://accounts.google.com/o/oauth2/token',
#     'user_agent': None,
#     'token_expiry': False
#   },
#   'accountID': '297914432',
#   'objectID': '297914432'
# },
#
# {
#   "type": "p",
#   "description": "Arrow",
#   "fileID": "F34YseTJTav4m3t9qsfM47EHznoozYSjAZtPKjIc_cAsx2QSUD7OD9gHGjX5sUcL_",
#   "fileUrl": "https://drive.google.com/file/d/1v7uDscxKm8aXmbCv13wLB9q1na_zXqA1VxRMTHW1wVg",
#   "fileType": "application/vnd.google-apps.spreadsheet",
#   "fileTitle": "Copy of YC Companies List",
#   "context": [],
#   "entityTypes": [
#     "PERSON",
#     "PERSON"
#   ],
#   "created": 1521470507,
#   "modified": 1521470507,
#   "index": 1,
#   "service": "gdrive",
#   "source": "297914432",
#   "superService": "kloudless",
#   "cells": [
#     {
#       "content": "Name: Arrow111231",
#       "label": "Name",
#       "value": "Arrow111231"
#     },
#     {
#       "content": "URL: Arrow",
#       "label": "URL",
#       "value": "Arrow"
#     },
#     {
#       "content": "Class: W18",
#       "label": "Class",
#       "value": "W18"
#     },
#     {
#       "content": "Description: Instagram for Augmented reality. Videos of the real world can be really boring - Arrow makes them fun.",
#       "label": "Description",
#       "value": "Instagram for Augmented reality. Videos of the real world can be really boring - Arrow makes them fun."
#     }
#   ],
#   "objectID": "59070927280"
# })
