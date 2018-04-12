# Help from this: https://developers.google.com/gmail/api/quickstart/python
# And this: https://developers.google.com/identity/sign-in/web/server-side-flow

from __future__ import print_function
import pprint, re, json
from raven import Client as SentryClient
import json, datetime
import httplib2, http
import os
import base64
import email
import itertools
from apiclient import discovery
from bs4 import BeautifulSoup as bs
import html2text

from .formats import html

pp = pprint.PrettyPrinter(indent=1)
sentry = SentryClient(
  'https://9a0228c8fde2404c9ccd6063e6b02b4c:d77e32d1f5b64f07ba77bda52adbd70e@sentry.io/1004428',
  environment = 'local' if 'HOME' in os.environ and os.environ['HOME'] == '/Users/jeremy' else 'production')

def get_google_service(http_auth):
  service = discovery.build('gmail', 'v1', http=http_auth)
  return service

# @TODO Figure out whether this still needs 'after' or 'number'
def list_files(google_service=None, source: dict=None):
  result = google_service.users().threads().list(userId='me', q='is:important').execute()
  threads = result['threads']
  files = [_thread_to_file(google_service, source, thread) for thread in threads[:5]]
  return files

def get_file(google_service=None, source: dict=None, file_id: str=None):
  print('get_file', google_service, source, file_id)
  if not google_service or not source or not file_id:
    return None
  thread = _get_thread(google_service, file_id)
  file = _thread_to_file(google_service, source, thread)
  return file

def _get_thread(google_service=None, file_id: str=None):
  if not file_id:
    return None
  thread_id = file_id[7:] if file_id[:7] == 'thread-' else file_id
  thread = google_service.users().threads().get(userId='me', id=thread_id).execute()
  # open('thread-' + thread_id + '.txt', 'w').write(str(json.dumps(thread, indent=2, sort_keys=True)))
  return thread

def _get_message_text(google_service=None, message_id: str=None):
  # print('_get_message_text', google_service, message_id)
  if not google_service or not message_id:
    return None
  message = google_service.users().messages().get(userId='me', id=message_id, format='raw').execute()
  msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
  msg_str = msg_str.decode('utf-8')
  html_message = None
  if 'Content-Transfer-Encoding: quoted-printable' in msg_str:
    html_message = msg_str.split('Content-Transfer-Encoding: quoted-printable')[1]
  elif 'Content-Type: text/html; charset="utf-8"\nContent-Transfer-Encoding: base64':
    raw = msg_str.split('Content-Type: text/html; charset="utf-8"\r\nContent-Transfer-Encoding: base64')
    if len(raw) > 1:
      html_message = base64.urlsafe_b64decode(raw[1].encode('ASCII')).decode('utf-8')
  if not html_message:
    print('Unrecognised email format!!!')
    sentry.captureMessage('Unrecognised email format!!!', message=message, msg_str=msg_str)
  return html_message


def get_cards(google_service=None, source: dict=None, file_id: str=None):
  if not google_service or not source or not file_id:
    return None
  thread = _get_thread(google_service, file_id)

  messages = []
  if 'messages' in thread and thread['messages'] and len(thread['messages']):
    for message in thread['messages']:
      if message and len(message) and 'id' in message:
        id = message['id']
        message_text = _get_message_text(google_service, message['id'])
        message_text = ''.join(''.join(''.join(message_text.split('=\r\n')).split('\r\n')).split('=C2=A0'))
        soup=bs(message_text)                #make BeautifulSoup
        for div in soup.find_all("div", {'class':'3D"gmail_signature"'}):
          div.decompose()
        for div in soup.find_all("blockquote"):
          div.decompose()
        for div in soup.find_all("div", {'class':'gmail_signature'}):
          div.decompose()
        for div in soup.find_all("div", {'class':'3D"gmail_extra"'}):
          div.decompose()
        prettyHTML=soup.prettify()          #prettify the html
        markdown = html2text.html2text(prettyHTML)
        # markdown = '\n\n'.join([m for m in re.compile('\n\s+\n').split(markdown) if not m == '' and not m == '  '])
        # markdown = '\n\n'.join([m for m in markdown.split('\n') if len(m) and not m[0] == '>'])
        markdown = '\n\n'.join([m for m in markdown.split('\n') if len(m) and not m[:3] == '\--'])
        for i, m in enumerate(markdown.split('\n')):
          if bool(re.match('On \d+ \w+ \d+, at \d\d:\d\d, .+ < \[.+', m)):
            markdown = '\n'.join(markdown.split('\n')[:i])
        # markdown = '\n\n'.join([m for m in markdown.split('\n') if len(m) and not re.compile('On \d+ \w+ \d+, at \d\d:\d\d, .+ < \[.+').match(m)])
        message['markdown_text'] = markdown
        messages.append(message)

        # open('message-' + id + '.html', 'w').write(prettyHTML)
        # open('message-' + id + '.md', 'w').write(markdown)
  file = _thread_to_file(google_service, source, thread)
  cards = [_message_to_card(google_service, source, file, message_text) for message_text in messages]
  return cards

# This is for splitting up the content of emails - Not currently used
def get_content_for_cards__for_spltting_up_content(google_service=None, source: dict=None, file_id: str=None):
  if not google_service or not source or not file_id:
    return None
  thread = _get_thread(google_service, file_id)
  messages = []
  if 'messages' in thread and thread['messages'] and len(thread['messages']):
    for message in thread['messages']:
      if message and len(message) and 'id' in message:
        message = _get_message_text(google_service, message['id'])
        message = ''.join(''.join(''.join(message.split('=\r\n')).split('\r\n')).split('=C2=A0'))
        messages.append(message)
  content = '\n'.join(messages)
  contentArrays = [html.getContentArray(message) for message in messages]
  contentArray = list(itertools.chain.from_iterable(contentArrays))
  return contentArray

def file_to_card_data():
  xmlContent = fileToContent(exportedFile)
  chunkHierarchy = xml_doc.getContentArray(xmlContent)
  return chunkHierarchy

def _thread_to_file(google_service=None, source: dict=None, thread: dict=None):
  if not google_service or not source or 'objectID' not in source or not thread or 'id' not in thread:
    return None
  thread = _get_thread(google_service, thread['id'])
  # Currently only getting headers from first message in thread
  file = {
    'service': 'gmail',
    'superService': 'google',
    'fileFormat': 'email',
    'objectID': 'thread-' + thread.get('id', None),
    'source': source.get('objectID', None),
    'modified': int(thread.get('messages', [{}])[-1]['internalDate']) / 1000 if 'internalDate' in thread.get('messages', [{}])[-1] else None,
    'created': int(thread.get('messages', [{}])[0]['internalDate']) / 1000 if 'internalDate' in thread.get('messages', [{}])[0] else None,
    'url': 'https://mail.google.com/mail/u/0/#inbox/' + thread.get('id', ''),
    'fileUrl': 'https://mail.google.com/mail/u/0/#inbox/' + thread.get('id', ''),
  }
  file['title'] = _get_header(thread.get('messages', [None])[0], 'Subject')
  file['fileTitle'] = file['title']
  if not file['title']:
    print('No subject of email')
  return file

def _message_to_card(google_service=None, source: dict=None, file: dict=None, message: str=None):
  if not google_service or not source or 'objectID' not in source or not file or 'objectID' not in file or not message or 'id' not in message:
    return None
  creator = _get_header(message, 'From')
  recipient = _get_header(message, 'To')
  card = {
    'service': 'gmail',
    'superService': 'google',
    'fileFormat': 'email',
    'objectID': message.get('id', None),
    'source': source.get('objectID', None),
    'modified': int(message['internalDate']) / 1000 if 'internalDate' in message else None,
    'created': int(message['internalDate']) / 1000 if 'internalDate' in message else None,
    'url': file.get('url', file.get('fileUrl', None)),
    'fileUrl': file.get('url', file.get('fileUrl', None)),
    'title': file.get('title', file.get('fileTitle', None)),
    'fileTitle': file.get('title', file.get('fileTitle', None)),
    'description': message.get('markdown_text'),
    'creator': creator,
    'recipient': recipient,
  }
  return card


def _get_header(message: dict=None, name: str=None):
  print('_get_header', message, name)
  if not message or not name or not len(name):
    return None
  header = [header['value'] for header in message.get('payload', {}).get('headers', []) if 'name' in header and header['name'] == name]
  if len(header) and header[0] and len(header[0]):
    return header[0]
  else:
    return None


def saveCard(source: dict, card: dict):
  return None
