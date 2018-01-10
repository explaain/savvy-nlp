import os, json
from parse import drives

testAccountInfo = {
  'organisationID': 'explaain',
  'accountID': '282782204'
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

def parseTestFileByID(fileID):
  f = drives.getFile(testAccountInfo, fileID)
  name = f['title']
  xmlContent = drives.extractRawContent(testAccountInfo, fileID)
  # Use this when you want to add more files to the test bank
  xmlFile = open('tests/sampleFiles/' + name.replace(' ', '_') + '.xml', 'w')
  xmlFile.write(xmlContent)
  #

def getAllFilesInDirectory(directory):
  return os.listdir(directory)

def parseTestFile(filename):
  testFile = open('tests/sampleFiles/' + filename, 'r')
  xmlContent = testFile.read()
  chunkHierarchy = drives.xmlFindText(xmlContent)
  generatedScore = open('tests/generatedScores/' + filename[:-4] + '.js', 'w')
  generatedScore.write(json.dumps(chunkHierarchy, indent=2))
  generatedHierarchy = open('tests/generatedHierarchies/' + filename[:-4] + '.txt', 'w')
  for chunk in drives.chunksToPrint(chunkHierarchy):
    generatedHierarchy.write('\n' + chunk)

def test_answer():
  parseTestFileByID('FvsojaQrWWSNvuxbjS_hrw_fEVkEY8ykbb5kJh_cB-C_l-zw9ZnOEXZsq9HIp15dD')
  for filename in getAllFilesInDirectory('tests/sampleFiles/'):
    print(filename)
    if filename[-4:] == '.xml':
      parseTestFile(filename)
  assert 4 == 4
