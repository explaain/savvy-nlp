# Uses https://github.com/pushrodtechnology/PythonConfluenceAPI

import pprint, sys, dateutil.parser as dp
from PythonConfluenceAPI import ConfluenceAPI
from .formats import html

pp = pprint.PrettyPrinter(indent=4)

def listAccounts(): # Probably don't need this?
  return None

def getAccount(accountID): # Probably don't need this?
  return None

def compatible_print(msg): # Probably don't need this?
    sys.stdout.write("{}\n".format(msg))
    sys.stdout.flush()


def listFiles(accountInfo, after=False, number=500): # 'after' and 'number' don't do anything!
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest file info
  response = connect.get_content(expand='childTypes.all,operations,history,history.lastUpdated,metadata.currentuser')
  pp.pprint(response)
  files = [confluenceToFile(page, accountInfo) for page in response['results']]
  return files

def getFile(accountInfo, fileID):
  """Returns complete exported file data"""
  # Create API object
  connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
  # Get latest visible content from confluence instance
  page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,history.lastUpdated,metadata.currentuser')
  # Convert to file info
  f = confluenceToFile(page, accountInfo)
  return f

def confluenceToFile(page, accountInfo):
  f = {
    'objectID': page['id'],
    'url': page['_links']['self'],
    'rawID': page['id'],
    'mimeType': 'html',
    'title': page['title'],
    'created': int(dp.parse(page['history']['createdDate']).strftime('%s')),
    'modified': int(dp.parse(page['history']['lastUpdated']['when']).strftime('%s')),
    'source': accountInfo['accountID'],
    'service': 'confluence'
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
