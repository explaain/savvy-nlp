import os, json, pprint
from parse import services
from parse.integrations import kloudless_integration as kloudlessDrives, confluence
from parse.integrations.formats import html, xml_doc as xml, csv

pp = pprint.PrettyPrinter(indent=4)

TestAccountInfo = {
  'gdocs': {
    'organisationID': 'explaain',
    'accountID': '282782204',
  },
  'gsheets': {
    'organisationID': 'explaain',
    'accountID': '282782204',
  },
  'confluence': {
    'accountID': 'https://explaain.atlassian.net/wiki/',
    'username': 'admin',
    'password': 'h3110w0r1d',
    'siteDomain': 'explaain',
  }
}

TestFilesToFetch = {
  'gdocs': [
    'FS1864iLNT6VttUFpOrGziWMoAqIyx3CZM6wV5jfUKPoE3qCHI0_eh3RELL7I5HIU',
    'F1UVWb2gWfAQZO4FbkhySjqnnu6W2YVHAh2qAVb-bbleYPrNzGv-Re5xozb8UNKXi',
  ],
  'gsheets': [],
  'confluence': [],
}

Formats = {
  'html': html,
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

def parseAndTestFileFromContent(formatModule, filename, content, directories: dict):
  contentArray = formatModule.getContentArray(content)
  print('formatModule')
  print(formatModule)
  print('contentArray')
  print(contentArray)
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

def parseAndTestFileFromFolder(formatModule, filename: str, directories: dict):
  testFile = open(directories['source'] + filename, 'r')
  content = testFile.read()
  return parseAndTestFileFromContent(formatModule, filename, content, directories)

def fetchContentFromFiles(serviceName: str):
  serviceData = services.getService(serviceName)
  service = serviceData['module']
  print('service')
  print(service)
  print('TestAccountInfo[serviceName]')
  print(TestAccountInfo[serviceName])
  files = service.listFiles(TestAccountInfo[serviceName])
  print('files')
  print(files)
  contentFromFiles = [{
    'title': f['title'],
    'content': service.getFileContent(TestAccountInfo[serviceName], f['objectID']),
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
  return [parseAndTestFileFromFolder(formatModule, filename, directories) for filename in getAllFilesInDirectory(directories['source']) if filename.split('.')[-1] == sourceFileEnding]

def test_parse():
  for fileFormat in Formats:
    for test in parse(fileFormat):
      print('test')
      pp.pprint(test)
      assert test['passed']

def test_fetchandparse():
  for serviceName in services.getServices():
    service = services.getService(serviceName)
    formatName = services.getServiceFormat(serviceName)
    directories = formatToDirectories(formatName)
    for content in fetchContentFromFiles(serviceName):
      print('content111')
      print(content)
      formatModule = Formats[formatName]
      test = parseAndTestFileFromContent(formatModule, titleToFilename(content['title']), content['content'], directories)
      print('test')
      pp.pprint(test)
      assert test['passed']

# def test_a():
#   fetchContentFromFiles('gdocs')
#   assert 1 == 2
