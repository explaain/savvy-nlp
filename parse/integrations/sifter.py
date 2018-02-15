# @TODO: Investigate! Could instead do this with: https://github.com/bryanmikaelian/sifter-python

import pprint, json, requests, dateutil.parser as dp

pp = pprint.PrettyPrinter(indent=4)

def listFiles(accountInfo, after=False, number=500): # 'after' and 'number' don't do anything!
  print(accountInfo['accountID'])
  print(accountInfo['accountID'])
  p = requests.get('https://' + accountInfo['accountID'] + '/api/projects', headers={'X-Sifter-Token': accountInfo['token']})
  print(p.content)
  projects = json.loads(p.content)['projects']
  pp.pprint(projects)
  issues = []
  for project in projects:
    projectID = project['url'].split('/')[-1]
    r = requests.get('https://savvy.sifterapp.com/api/projects/' + projectID + '/issues', headers={'X-Sifter-Token': accountInfo['token']})
    sifterIssues = json.loads(r.content)['issues'] # Only 100 per page! @TODO: sort out
    issues += [sifterToFile(sifterIssue, accountInfo, projectID) for sifterIssue in sifterIssues]
  pp.pprint(issues)
  return issues

def getFile(accountInfo, fileID):
  p = requests.get('https://' + accountInfo['accountID'] + '/api/projects', headers={'X-Sifter-Token': accountInfo['token']})
  projects = json.loads(p.content)['projects']
  pp.pprint(projects)
  issue = None
  for project in projects:
    projectID = project['url'].split('/')[-1]
    r = requests.get('https://savvy.sifterapp.com/api/projects/' + projectID + '/issues/' + fileID, headers={'X-Sifter-Token': accountInfo['token']})
    if r.status_code == 200:
      sifterIssue = json.loads(r.content)['issue']
      issue = sifterToFile(sifterIssue, accountInfo, projectID)
  pp.pprint(issue)
  return issue

def sifterToFile(issue, accountInfo, projectID):
  f = {
    'objectID': issue['url'].split('/')[-1], # Is this the right thing to choose? In theory two sifter accounts could have the same id?
    'url': issue['url'],
    'rawID': issue['url'], # Necessary?
    'title': issue['subject'],
    'description': issue['description'],
    'created': int(dp.parse(issue['created_at']).strftime('%s')),
    'modified': int(dp.parse(issue['updated_at']).strftime('%s')),
    'fileType': 'web',
    'source': accountInfo['accountID'],
    'service': 'sifter',
    'projectID': projectID,
    'createdBy': issue['opener_email'],
    'integrationFields': {
      'priority': issue['priority'],
      'status': issue['status'],
      'number': issue['number'],
      'milestone': issue['milestone_name'],
      'category': issue['category_name'],
    }
  }
  if 'comments' in issue and len(issue['comments']):
    f['attachments'] = [attachment for comment in issue['comments'] for attachment in comment['attachments']]
  return f

def getFileContent(accountInfo, fileID):
  return None

def getContentForCards(accountInfo, fileID):
  return None

# listFiles({
#   'service': 'sifter',
#   'organisationID': 'explaain',
#   'superService': False,
#   'accountID': 'savvy',
#   'objectID': 'sifter-savvy',
#   'token': '16b6caf289218da7fd6a1bcae4696870'
# }
# # , '4313159'
# )
