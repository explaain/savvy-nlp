import pprint, sys
from parse.integrations import kloudless_integration as kloudlessDrives, confluence, sifter, zoho_bugtracker, gsites, trello

pp = pprint.PrettyPrinter(indent=4)

Services = {
  'confluence': {
    'title': 'Confluence',
    'superService': False,
    'module': confluence
  },
  'gdrive': {
    'title': 'Google Drive',
    'superService': 'kloudless',
  },
  'dropbox': {
    'title': 'Dropbox',
    'superService': 'kloudless',
  },
  'sifter': {
    'title': 'Sifter',
    'superService': False,
    'module': sifter
  },
  'zoho': {
    'title': 'Zoho',
    'superService': False,
    'module': zoho_bugtracker
  },
  'gsites': {
    'title': 'Google Sites',
    'superService': False,
    'module': gsites
  },
  'trello': {
    'title': 'Trello',
    'superService': False,
    'module': trello
  },
}

SuperServices = {
  'kloudless': {
    'module': kloudlessDrives,
  },
}

def getAllServiceData(accountInfo=None, serviceName=None, superServiceName=None, specificCard=None):
  pp.pprint(accountInfo)
  allServiceData = {}
  if specificCard:
    if 'service' in specificCard:
      serviceName = specificCard['service']
    if 'superService' in specificCard:
      superServiceName = specificCard['superService']
    if 'mimeType' in specificCard:
      try:
        allServiceData['subService'] = service['module'].getSubServiceByFileType(specificCard['mimeType'])
      except Exception as e:
        print('No subService')
  if accountInfo:
    if 'service' in accountInfo:
      serviceName = accountInfo['service']
    if 'superService' in accountInfo:
      superServiceName = accountInfo['superService']
  if serviceName and serviceName in Services:
    allServiceData['service'] = Services[serviceName]
    allServiceData['service']['serviceName'] = serviceName
  else:
    return None
  if superServiceName and superServiceName in SuperServices:
    allServiceData['superService'] = SuperServices[superServiceName]
    allServiceData['superService']['superServiceName'] = serviceName
  return allServiceData

def getIntegrationData(accountInfo=None, serviceName=None, superServiceName=None, specificCard=None):
  allServiceData = getAllServiceData(accountInfo, serviceName, superServiceName, specificCard)
  print('allServiceData')
  pp.pprint(allServiceData)
  return None if not allServiceData else allServiceData['superService'] if 'superService' in allServiceData else allServiceData['service'] if 'service' in allServiceData else None
