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
    'FxfyEPKrpbHvnhYunG8nvXLW4Trg6C85-KrjCrBX9gpo2QJozK1Nba2n5sfx923iL'
  ]
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

def parseTestFileByID(serviceName, fileID: str):
  serviceData = services.getService(serviceName)
  service = serviceData['module']
  f = service.getFile(TestAccountInfo[serviceName], fileID)
  name = f['title']
  xmlContent = service.extractRawXMLContent(TestAccountInfo[serviceName], fileID)
  # Use this when you want to add more files to the test bank
  xmlFile = open(sourceDirectory + name.replace(' ', '_') + '.xml', 'w')
  xmlFile.write(xmlContent)
  #

def getAllFilesInDirectory(directory):
  return os.listdir(directory)

def parseTestFile(service, filename: str, sourceDirectory: str, generatedDirectory: str, correctDirectory: str):
  testFile = open(sourceDirectory + filename, 'r')
  xmlContent = testFile.read()
  chunkHierarchy = service.getContentArray(xmlContent)
  generatedContent = service.chunksToPrint(chunkHierarchy)
  generated = open(generatedDirectory + filename.split('.')[:-1][0] + '.txt', 'w')
  for chunk in generatedContent:
    generated.write('\n' + chunk)
  correct = open(correctDirectory + filename.split('.')[:-1][0] + '.txt', 'r')
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

  # # Extra
  # generatedScore = open('tests/generatedScores/' + filename[:-4] + '.js', 'w')
  # generatedScore.write(json.dumps(chunkHierarchy, indent=2))

def fetchAndParse(serviceName: str):
  serviceData = services.getService(serviceName)
  service = serviceData['module']
  files = service.listFiles(TestAccountInfo[serviceName])
  for f in files:
    print(f)
    parseTestFileByID(serviceName, f['id'])
  print(1)
  # @TODO

def fetchFiles(serviceName: str):
  serviceData = services.getService(serviceName)
  service = serviceData['module']
  print('service')
  print(service)
  print('TestAccountInfo[serviceName]')
  print(TestAccountInfo[serviceName])
  files = service.listFiles(TestAccountInfo[serviceName])
  print('files')
  print(files)
  for f in files:
    print('f')
    print(f)
    if f['objectID'] in TestFilesToFetch[serviceName]:
      service.getFile(TestAccountInfo, f['objectID'])
  return files

def parse(formatName: str):
  sourceFormat = Formats[formatName]
  sourceFileEnding = FormatFileEndings[formatName]
  directoryStub = 'tests/files/' + formatName
  sourceDirectory = directoryStub + '/source/'
  generatedDirectory = directoryStub + '/generated/'
  correctDirectory = directoryStub + '/correct/'

  return [parseTestFile(sourceFormat, filename, sourceDirectory, generatedDirectory, correctDirectory) for filename in getAllFilesInDirectory(sourceDirectory) if filename.split('.')[-1] == sourceFileEnding]

def test_parse():
  for fileFormat in Formats:
    for test in parse(fileFormat):
      print('test')
      pp.pprint(test)
      assert test['passed']

def test_fetchandparse():
  for serviceName in services.getServices():
    service = services.getService(serviceName)
    fileFormat = services.getServiceFormat(serviceName)
    files = fetchFiles(serviceName)
    for test in parse(fileFormat):
      print('test')
      pp.pprint(test)
      assert test['passed']

# def test_a():
#   fetchFiles('gdocs')
#   assert 1 == 2
