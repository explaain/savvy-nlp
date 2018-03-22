import os, json, pprint
import index
from parse import services
from parse.integrations import kloudless_integration as kloudlessDrives, confluence
from parse.integrations.formats import html, xml_doc as xml, csv

pp = pprint.PrettyPrinter(indent=4)

TestAccountInfo = {
  'kloudless': {
    'organisationID': 'yc',
    'accountID': '297914432',
    'superService': 'kloudless',
  },
  'gsheets': {
    'organisationID': 'explaain',
    'accountID': '282782204',
    'superService': 'kloudless',
    'service': 'gdocs',
  },
  # 'confluence': {
  #   'organisationID': 'explaain',
  #   'accountID': 'https://explaain.atlassian.net/wiki/',
  #   'username': 'admin',
  #   'password': 'h3110w0r1d',
  #   'siteDomain': 'explaain',
  #   'service': 'confluence',
  # }
}

TestFilesToFetch = {
  'gdocs': [
    # 'FS1864iLNT6VttUFpOrGziWMoAqIyx3CZM6wV5jfUKPoE3qCHI0_eh3RELL7I5HIU',
    # 'F1UVWb2gWfAQZO4FbkhySjqnnu6W2YVHAh2qAVb-bbleYPrNzGv-Re5xozb8UNKXi',
    # 'FyjC21jL7Hy3j55_Ek-d5U_oSk3pt4e7zjAq30HGyD7MoWBYhUjgktG9t6aCzfkce',
    'FJamVu29CVRXjYCDJXx2I8Ge-ipSQ2irry0emEK-jrZZcQWZEqxhnjoGfpTjL3QMA',
  ],
  'gsheets': [
    # 'FptwaKolhPnYFPLUWBubCo3ASpk14lLPhK_ndV0jmlaQg6hmdRX0zb5Autwinmcce',
  ],
  # 'confluence': [],
}

Formats = {
  # 'html': html,
  'xml_doc': xml,
  'csv': csv,
}
FormatFileEndings = {
  'html': 'html',
  'xml_doc': 'xml',
  'csv': 'csv',
}

def titleToFilename(title: str):
  return title.replace(' ', '_').replace('/', '') + '.xml'

def getAllFilesInDirectory(directory):
  return os.listdir(directory)

def parseAndTestFileFromContent(formatModule, formatName, filename, content, directories: dict):
  print('parseAndTestFileFromContent', formatModule, filename, content, directories)
  source = open(directories['source'] + filename.split('.')[:-1][0] + '.' + FormatFileEndings[formatName], 'w')
  source.write(content)
  contentArray = formatModule.getContentArray(content)
  # print('formatModule')
  # print(formatModule)
  # print('contentArray')
  # print(contentArray)
  generatedContent = formatModule.chunksToPrint(contentArray)
  generated = open(directories['generated'] + filename.split('.')[:-1][0] + '.txt', 'w')
  for chunk in generatedContent:
    generated.write('\n' + chunk)
  correct = open(directories['correct'] + filename.split('.')[:-1][0] + '.txt', 'r')
  correctContent = correct.read()
  correctContent = correctContent.split('\n')[1:]
  lineTests = [{
    'passed': line == correctContent[i],
    'generatedLine': line,
    'correctLine': correctContent[i]
  } for i, line in enumerate(generatedContent)]
  return {
    'lineTests': lineTests,
    'passed': all([test['passed'] for test in lineTests]),
    'generatedContent': generatedContent,
    'correctContent': correctContent,
  }

def parseAndTestFileFromFolder(formatModule, formatName, filename: str, directories: dict):
  testFile = open(directories['source'] + filename, 'r')
  content = testFile.read()
  return parseAndTestFileFromContent(formatModule, formatName, filename, content, directories)

def fetchContentFromFiles(serviceName: str):
  serviceData = services.getService(serviceName=serviceName)
  integrationName = serviceData['superService'] if 'superService' in serviceData and serviceData['superService'] else serviceName
  print('integrationName')
  print(integrationName)
  service = serviceData['module']
  print('service')
  print(service)
  print('TestAccountInfo[integrationName]')
  print(TestAccountInfo[integrationName])
  files = service.listFiles(TestAccountInfo[integrationName])
  print('files')
  print(files)
  contentFromFiles = [{
    'title': f['title'],
    'content': service.getFileContent(TestAccountInfo[integrationName], f['objectID']),
  } for f in files if 'objectID' in f and f['objectID'] in TestFilesToFetch[serviceName]]
  return contentFromFiles

def formatToDirectories(formatName: str):
  stub = 'tests/files/' + formatName
  return {
    'source': stub + '/source/',
    'generated': stub + '/generated/',
    'correct': stub + '/correct/',
  }

def parse(formatName: str):
  formatModule = Formats[formatName]
  sourceFileEnding = FormatFileEndings[formatName]
  directories = formatToDirectories(formatName)
  return [parseAndTestFileFromFolder(formatModule, formatName, filename, directories) for filename in getAllFilesInDirectory(directories['source']) if filename.split('.')[-1] == sourceFileEnding]

def test_parse():
  for fileFormat in Formats:
    for test in parse(fileFormat):
      print('test')
      # pp.pprint(test)
      assert test['passed']

def test_fetchAndParse(record_xml_property):
  for serviceName in TestFilesToFetch:
    print('serviceName')
    print(serviceName)
    service = services.getService(serviceName=serviceName)
    print('service')
    print(service)
    formatName = services.getServiceFormat(serviceName)
    print('formatName')
    print(formatName)
    directories = formatToDirectories(formatName)
    for content in fetchContentFromFiles(serviceName):
      print('content111')
      print(content)
      formatModule = Formats[formatName]
      test = parseAndTestFileFromContent(formatModule, formatName, titleToFilename(content['title']), content['content'], directories)
      print('test')
      pp.pprint(test)
      assert test['passed']

def test_indexAll():
  for integrationName in TestAccountInfo:
    index.indexFiles(TestAccountInfo[integrationName])
