# Uses https://github.com/pushrodtechnology/PythonConfluenceAPI

import pprint, sys
from PythonConfluenceAPI import ConfluenceAPI
from .formats import html

pp = pprint.PrettyPrinter(indent=4)

def listAccounts():
  return None

def getAccount(accountID):
  return None

def compatible_print(msg):
    sys.stdout.write("{}\n".format(msg))
    sys.stdout.flush()


def listFiles(accountInfo, after=False, number=500):
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest visible content from confluence instance
  page = connect.get_content_by_id('294914', expand='body.view,childTypes.all,operations,history,metadata.currentuser')
  pp.pprint(page)
  body = page.get('body')
  compatible_print("{} - {} ({})".format(page.get("space", {}).get("key", "???"),
                                                page.get("title", "(No title)"),
                                                page.get("id", "(No ID!?)")))
  content = page.get("body", {}).get("view", {}).get("value", "No content.")
  pp.pprint(content)
  pp.pprint(page)
  return None

def getFile(accountInfo, fileID):
  """Returns complete exported file data"""
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest visible content from confluence instance
  page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,metadata.currentuser')
  # Convert to file info
  f = fileToAlgolia(page, accountInfo)
  return f

def fileToAlgolia(page, accountInfo):
  f = {
    'objectID': page['id'],
    'url': page['_links']['self'],
    'rawID': page['id'],
    'mimeType': 'html',
    'title': page['title'],
    'created': page['history']['createdDate'],
    'modified': page['history']['createdDate'], # @TODO: find actual modified!
    'source': accountInfo['accountID']
  }
  return f

def getContent(accountInfo, fileID):
  """Returns content parsed as data (array) ready to be turned into cards"""
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest visible content from confluence instance
  page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,metadata.currentuser')
  # Get content
  content = page['body']['view']['value']
  contentArray = html.getContentArray(content)
  return contentArray

# listFiles({
#   'username': 'admin',
#   'password': 'h3110w0r1d',
#   'siteDomain': 'explaain',
#   'accountID': 'https://explaain.atlassian.net/wiki/'
# })
#
# getContent({
#   'username': 'admin',
#   'password': 'h3110w0r1d',
#   'siteDomain': 'explaain',
#   'accountID': 'https://explaain.atlassian.net/wiki/'
# }, '294914')
