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
  'xml': xml,
}

testFiles = [
  'askporter_contract.xml',
  'public_faqs.xml',
  'jan_build.xml',
  'privacy_policy.xml',
  'internal_faqs.xml',
  'competitor_analysis.xml',
  'feature_list_pricing_tier.xml',
  'test_account_logins.xml',
  'election_2017_handbook.xml',
  'abc_company_handbook.xml',
  'resume.xml',
]

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

def parseTestFile(service, filename: str, sourceDirectory: str, generatedDirectory: str):
  testFile = open(sourceDirectory + filename, 'r')
  xmlContent = testFile.read()
  chunkHierarchy = service.getContentArray(xmlContent)
  generatedContent = service.chunksToPrint(chunkHierarchy)
  generated = open(generatedDirectory + filename.split('.')[:-1][0] + '.txt', 'w')
  for chunk in generatedContent:
    generated.write('\n' + chunk)
  correct = open('tests/files/html/correct/sample_product.txt', 'r')
  correctContent = correct.read()
  return {
    'passed': generatedContent == correctContent,
    'generatedContent': generatedContent,
    'correctContent': correctContent,
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
  correctDirectory = directoryStub + '/correct/'
  generatedDirectory = directoryStub + '/generated/'

  return [parseTestFile(sourceFormat, filename, sourceDirectory, generatedDirectory) for filename in getAllFilesInDirectory(sourceDirectory) if filename.split('.')[-1] == sourceFileEnding]

# def test_gdocs():
#   parse('gdocs', 'xml')

def test_html():
  assert parse('html', 'html')
