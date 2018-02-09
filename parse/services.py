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
  for i in Integrations:
    print(i)
    if Integrations[i]['superService']:
      for j in Integrations[i]['services']:
        services[j] = Integrations[i]['services'][j]
        services[j]['superService'] = i
    else:
      services[i] = Integrations[i]
  return services

def getService(serviceName: str):
  services = getServices()
  return services[serviceName]

def getServiceFormat(serviceName: str):
  serviceFormats = {
    'kloudless': True,
    'gdocs': 'xml_doc',
    'gsheets': 'csv',
    'confluence': 'html'
  }
  return serviceFormats[serviceName]
