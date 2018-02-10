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
  # Get latest file info
  page = connect.get_content_by_id('294914', expand='childTypes.all,operations,history,history.lastUpdated,metadata.currentuser')
  pp.pprint(page)
  # # Get latest visible content from confluence instance
  # page = connect.get_content_by_id('294914', expand='body.view,childTypes.all,operations,history,metadata.currentuser')
  # pp.pprint(page)
  # body = page.get('body')
  # compatible_print("{} - {} ({})".format(page.get("space", {}).get("key", "???"),
  #                                               page.get("title", "(No title)"),
  #                                               page.get("id", "(No ID!?)")))
  # content = page.get("body", {}).get("view", {}).get("value", "No content.")
  # print('content1')
  # pp.pprint(content)
  # pp.pprint(page)
  return page

def getFile(accountInfo, fileID):
  """Returns complete exported file data"""
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest visible content from confluence instance
  page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,history.lastUpdated,metadata.currentuser')
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
    'created': page['history']['createdDate'], # @TODO: Check this is in the right format
    'modified': page['history']['lastUpdated']['when'], # @TODO: Check this is in the right format
    'source': accountInfo['accountID']
  }
  return f

def getFileContent(accountInfo, fileID):
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest visible content from confluence instance
  page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,metadata.currentuser')
  # Get content
  content = page['body']['view']['value']
  return content

def getContentForCards(accountInfo, fileID):
  """Returns content parsed as data (array) ready to be turned into cards"""
  content = getFileContent(accountInfo, fileID)
  contentArray = html.getContentArray(content)
  return contentArray

# listFiles({
#   'username': 'admin',
#   'password': 'h3110w0r1d',
#   'siteDomain': 'explaain',
#   'accountID': 'https://explaain.atlassian.net/wiki/'
# })
#
# getContentForCards({
#   'username': 'admin',
#   'password': 'h3110w0r1d',
#   'siteDomain': 'explaain',
#   'accountID': 'https://explaain.atlassian.net/wiki/'
# }, '294914')
