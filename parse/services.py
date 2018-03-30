import pprint, sys
from parse.integrations import kloudless_integration as kloudlessDrives, confluence, sifter, zoho_bugtracker, gsites, trello

pp = pprint.PrettyPrinter(indent=4)

Integrations = {
  'confluence': {
    'name': 'Confluence',
    'superService': False,
    'format': 'html',
    'module': confluence
  },
  'kloudless': {
    'superService': True,
    'module': kloudlessDrives,
    'services': {
      'gdocs': {
        'name': 'Google Docs',
        'format': 'xml_doc',
        'module': kloudlessDrives
      },
      'gsheets': {
        'name': 'Google Sheets',
        'format': 'csv',
        'module': kloudlessDrives
      }
    }
  },
  'sifter': {
    'name': 'Sifter',
    'superService': False,
    'format': None,
    'module': sifter
  },
  'zoho': {
    'name': 'Zoho',
    'superService': False,
    'format': None,
    'module': zoho_bugtracker
  },
  'gsites': {
    'name': 'Google Sites',
    'superService': False,
    'format': 'html',
    'module': gsites
  },
  'trello': {
    'name': 'Trello',
    'superService': False,
    'format': None,
    'module': trello
  },
}

def getIntegrations():
  return Integrations

def getServices():
  services = {}
  for i in Integrations:
    if Integrations[i]['superService']:
      for j in Integrations[i]['services']:
        services[j] = Integrations[i]['services'][j]
        services[j]['superService'] = i
    else:
      services[i] = Integrations[i]
  return services

def getService(accountInfo=None, serviceName=None, superServiceName=None, specificCard=None):
  pp.pprint(accountInfo)
  services = getServices()
  if accountInfo:
    if 'service' in accountInfo:
      serviceName = accountInfo['service']
    if 'superService' in accountInfo:
      superServiceName = accountInfo['superService']
  if serviceName and serviceName == 'gdrive':
    serviceName = None
    superServiceName = 'kloudless'
  service = services[serviceName] if serviceName in services else Integrations[superServiceName] if superServiceName and superServiceName in Integrations else None
  # Convert mimeType to fileType (for legacy cards)
  if specificCard and 'mimeType' in specificCard and 'fileType' not in specificCard:
    specificCard['fileType'] = specificCard['mimeType']
  if specificCard and 'fileType' in specificCard:
    try:
      tempService = service['module'].getServiceByFileType(specificCard['fileType'])
    except Exception as e:
      tempService = None
    if tempService and 'service' in tempService:
      service = services[tempService['service']]
  return service

def getServiceFormat(serviceName: str):
  service = getService(serviceName=serviceName)
  return service['format'] if service and 'format' in service else None
