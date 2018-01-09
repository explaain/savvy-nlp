import json
from parse import drives

testFiles = [
  'askporter_contract',
  'public_faqs',
  'jan_build',
  'privacy_policy',
  'internal_faqs',
  'competitor_analysis',
  'feature_list_pricing_tier',
]

def parseTestFileByFilename(filename):
  sampleFile = open('tests/sampleFiles/' + filename + '.xml', 'r')
  xmlContent = sampleFile.read()
  chunkHierarchy = drives.xmlFindText(xmlContent)
  generatedScore = open('tests/generatedScores/' + filename + '.js', 'w')
  generatedScore.write(json.dumps(chunkHierarchy, indent=2))
  generatedHierarchy = open('tests/generatedHierarchies/' + filename + '.txt', 'w')
  for chunk in drives.chunksToPrint(chunkHierarchy):
    generatedHierarchy.write('\n' + chunk)

def test_answer():
  for filename in testFiles:
    parseTestFileByFilename(filename)
  assert 4 == 4
