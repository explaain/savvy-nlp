# Help from this: https://developers.google.com/gmail/api/quickstart/python
# And this: https://developers.google.com/identity/sign-in/web/server-side-flow

from __future__ import print_function
import pprint
import json, datetime
import httplib2, http
import os
import base64
import email
import itertools
from apiclient import discovery

from .formats import html

pp = pprint.PrettyPrinter(indent=1)

def get_google_service(http_auth):
  service = discovery.build('gmail', 'v1', http=http_auth)
  return service

# @TODO Figure out whether this still needs 'after' or 'number'
def list_files(google_service=None, source: dict=None):
  result = google_service.users().threads().list(userId='me', q='is:important').execute()
  threads = result['threads']
  files = [thread_to_file(google_service, source, thread) for thread in threads]
  return files

def get_file(google_service=None, source: dict=None, file_id: str=None):
  print('get_file', google_service, source, file_id)
  if not google_service or not source or not file_id:
    return None
  thread = google_service.users().threads().get(userId='me', id=file_id).execute()
  file = thread_to_file(google_service, source, thread)
  return file

def get_message(google_service=None, message_id: str=None):
  print('get_message', google_service, message_id)
  if not google_service or not message_id:
    return None
  message = google_service.users().messages().get(userId='me', id=message_id, format='raw').execute()
  msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
  msg_str = msg_str.decode('utf-8')
  if 'Content-Transfer-Encoding: quoted-printable' in msg_str:
    print('aaa')
    html_message = msg_str.split('Content-Transfer-Encoding: quoted-printable')[1]
  elif 'Content-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: base64':
    print('bbb')
    raw = msg_str.split('Content-Type: text/html; charset="utf-8"\r\nContent-Transfer-Encoding: base64')[1]
    html_message = base64.urlsafe_b64decode(raw.encode('ASCII')).decode('utf-8')
  else:
    print('Unrecognised email format!!!')
    sentry.captureMessage('Unrecognised email format!!!', message=message, msg_str=msg_str)
    html_message = None
  print('html_message')
  print(html_message)
  return html_message

  # pp.pprint('html_message')
  # pp.pprint(html_message)
  # pp.pprint(dir(html_message))
  # pp.pprint(html_message.values)
  # pp.pprint(html_message.items)
  # pp.pprint(html_message.keys)
  # pp.pprint(html_message.as_string)
  # pp.pprint(html_message.as_string())




def get_content_for_cards(google_service=None, source: dict=None, file_id: str=None):
  if not google_service or not source or not file_id:
    return None
  thread = google_service.users().threads().get(userId='me', id=file_id).execute()
  messages = []
  if 'messages' in thread and thread['messages'] and len(thread['messages']):
    for message in thread['messages']:
      if message and len(message) and 'id' in message:
        message = get_message(google_service, message['id'])
        message = ''.join(''.join(''.join(message.split('=\r\n')).split('\r\n')).split('=C2=A0'))
        messages.append(message)
  content = '\n'.join(messages)
  contentArrays = [html.getContentArray(message) for message in messages]
  contentArray = list(itertools.chain.from_iterable(contentArrays))
  print('contentArray')
  print([c['content'] for c in contentArray])
  return contentArray

def file_to_card_data():
  xmlContent = fileToContent(exportedFile)
  chunkHierarchy = xml_doc.getContentArray(xmlContent)
  return chunkHierarchy

def thread_to_file(google_service=None, source: dict=None, thread: dict=None):
  if not source or 'objectID' not in source or not thread or 'id' not in thread:
    print(111)
    return None
  pp.pprint('thread')
  pp.pprint(thread)
  subject = None
  # Currently only getting headers from first message in thread
  file = {
    'service': 'gmail',
    'superService': 'google',
    'fileFormat': 'email',
    'objectID': thread.get('id', None),
    'source': source.get('objectID', None),
    'modified': thread.get('modified', None),
    'created': thread.get('created', None),
    'url': 'https://mail.google.com/mail/u/0/#inbox/' + thread.get('id', '')
  }
  headers = thread.get('messages', [{}])[0].get('payload', {}).get('headers', [{}])
  print('headers')
  print(headers)
  if headers:
    try:
      file['title'] = next(header for header in headers if 'name' in header and header['name'] == 'Subject')['value']
    except Exception as e:
      print('No subject of email', e)
  print(file)
  return file




def saveCard(source: dict, card: dict):
  return None
