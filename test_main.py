import os, json
from parse.integrations import kloudless_integration as kloudlessDrives, confluence
from parse.integrations.formats import html, xml_doc as xml

testAccountInfo = {
  'organisationID': 'explaain',
  'accountID': '282782204'
}

services = {
  'kloudless': kloudlessDrives,
  'gdocs': kloudlessDrives,
  'gsheets': kloudlessDrives,
  'confluence': confluence
}

formats = {
  'html': html,
  'xml_doc': xml,
}

def parseTestFileByID(service, fileID: str):
  f = service.getFile(testAccountInfo, fileID)
  name = f['title']
  xmlContent = service.extractRawXMLContent(testAccountInfo, fileID)
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
  return {
    'passed': generatedContent == correctContent,
    'generatedContent': generatedContent,
    'correctContent': correctContent.split('\n')[1:],
  }

  # # Extra
  # generatedScore = open('tests/generatedScores/' + filename[:-4] + '.js', 'w')
  # generatedScore.write(json.dumps(chunkHierarchy, indent=2))

def fetchAndParse(serviceName: str, sourceFileEnding: str):
  print(1)
  # @TODO

def parse(formatName: str, sourceFileEnding: str):
  sourceFormat = formats[formatName]
  directoryStub = 'tests/files/' + formatName
  sourceDirectory = directoryStub + '/source/'
  generatedDirectory = directoryStub + '/generated/'
  correctDirectory = directoryStub + '/correct/'

  return [parseTestFile(sourceFormat, filename, sourceDirectory, generatedDirectory, correctDirectory) for filename in getAllFilesInDirectory(sourceDirectory) if filename.split('.')[-1] == sourceFileEnding]

# def test_gdocs():
#   parse('gdocs', 'xml')

def test_html():
  for test in parse('html', 'html'):
    for i, line in enumerate(test['generatedContent']):
      assert line == test['correctContent'][i]
  for test in parse('xml_doc', 'xml'):
    for i, line in enumerate(test['generatedContent']):
      assert line == test['correctContent'][i]
