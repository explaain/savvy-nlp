# Uses https://github.com/pushrodtechnology/PythonConfluenceAPI

import pprint, sys
from parse.integrations import kloudless_integration as kloudlessDrives, confluence

pp = pprint.PrettyPrinter(indent=4)

Integrations = {
  'confluence': {
    'superService': False,
    'module': confluence
  },
  'kloudless': {
    'superService': True,
    'module': kloudlessDrives,
    'services': {
      'gdocs': {
        'module': kloudlessDrives
      },
      'gsheets': {
        'module': kloudlessDrives
      }
    }
  }
}

def getIntegrations():
  return Integrations

def getServices():
  services = {}
  # services = [Integrations[i] for i in Integrations if 'superService' not in Integrations[i]]
  for i in Integrations:
    print(i)
    if Integrations[i]['superService']:
      for j in Integrations[i]['services']:
        services[j] = Integrations[i]['services'][j]
        services[j]['superService'] = i
    else:
      services[i] = Integrations[i]
  print('services')
  pp.pprint(services)
  return services

print('getServices()')
pp.pprint(getServices())
print('end')

def getService(serviceName: str):
  services = getServices()
  print('serviceName')
  print(serviceName)
  print('services')
  print(services)
  return services[serviceName]

def getServiceFormat(serviceName: str):
  serviceFormats = {
    'kloudless': True,
    'gdocs': 'xml_doc',
    'gsheets': 'csv',
    'confluence': 'html'
  }
  return serviceFormats[serviceName]

# def listAccounts():
#   return None
#
# def getAccount(accountID):
#   return None
#
# def compatible_print(msg):
#     sys.stdout.write("{}\n".format(msg))
#     sys.stdout.flush()
#
#
# def listFiles(accountInfo, after=False, number=500):
#   # Create API object
#   connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
#   # Get latest file info
#   page = connect.get_content_by_id('294914', expand='childTypes.all,operations,history,metadata.currentuser')
#   pp.pprint(page)
#   # # Get latest visible content from confluence instance
#   # page = connect.get_content_by_id('294914', expand='body.view,childTypes.all,operations,history,metadata.currentuser')
#   # pp.pprint(page)
#   # body = page.get('body')
#   # compatible_print("{} - {} ({})".format(page.get("space", {}).get("key", "???"),
#   #                                               page.get("title", "(No title)"),
#   #                                               page.get("id", "(No ID!?)")))
#   # content = page.get("body", {}).get("view", {}).get("value", "No content.")
#   # print('content1')
#   # pp.pprint(content)
#   # pp.pprint(page)
#   return page
#
# def getFile(accountInfo, fileID):
#   """Returns complete exported file data"""
#   # Create API object
#   connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
#   # Get latest visible content from confluence instance
#   page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,metadata.currentuser')
#   # Convert to file info
#   f = fileToAlgolia(page, accountInfo)
#   return f
#
# def fileToAlgolia(page, accountInfo):
#   f = {
#     'objectID': page['id'],
#     'url': page['_links']['self'],
#     'rawID': page['id'],
#     'mimeType': 'html',
#     'title': page['title'],
#     'created': page['history']['createdDate'],
#     'modified': page['history']['createdDate'], # @TODO: find actual modified!
#     'source': accountInfo['accountID']
#   }
#   return f
#
# def getContent(accountInfo, fileID):
#   """Returns content parsed as data (array) ready to be turned into cards"""
#   # Create API object
#   connect = ConfluenceAPI(accountInfo['username'], accountInfo['password'], 'https://' + accountInfo['siteDomain'] + '.atlassian.net/wiki/')
#   # Get latest visible content from confluence instance
#   page = connect.get_content_by_id(fileID, expand='body.view,childTypes.all,operations,history,metadata.currentuser')
#   # Get content
#   content = page['body']['view']['value']
#   contentArray = html.getContentArray(content)
#   return contentArray
#
# # listFiles({
# #   'username': 'admin',
# #   'password': 'h3110w0r1d',
# #   'siteDomain': 'explaain',
# #   'accountID': 'https://explaain.atlassian.net/wiki/'
# # })
# #
# # getContent({
# #   'username': 'admin',
# #   'password': 'h3110w0r1d',
# #   'siteDomain': 'explaain',
# #   'accountID': 'https://explaain.atlassian.net/wiki/'
# # }, '294914')
