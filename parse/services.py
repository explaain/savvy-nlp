import pprint, sys
from parse.integrations import kloudless_integration as kloudlessDrives, confluence, sifter, zoho_bugtracker

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

def getService(accountInfo=None, serviceName=None, superServiceName=None, specificFile=None):
  services = getServices()
  if accountInfo:
    if 'service' in accountInfo:
      serviceName = accountInfo['service']
    if 'superService' in accountInfo:
      superServiceName = accountInfo['superService']
  service = services[serviceName] if serviceName in services else Integrations[superServiceName] if superServiceName and superServiceName in Integrations else None
  # Convert mimeType to fileType (for legacy cards)
  if specificFile and 'mimeType' in specificFile and 'fileType' not in specificFile:
    specificFile['fileType'] = specificFile['mimeType']
  if specificFile and 'fileType' in specificFile:
    try:
      tempService = service['module'].getServiceByFileType(specificFile['fileType'])
    except Exception as e:
      tempService = None
    if tempService and 'service' in tempService:
      service = services[tempService['service']]
  return service

def getServiceFormat(serviceName: str):
  service = getService(serviceName=serviceName)
  return service['format'] if service and 'format' in service else None
