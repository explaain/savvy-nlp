# @TODO: Investigate! Could instead do this with: https://github.com/bryanmikaelian/sifter-python

import pprint, json, requests, dateutil.parser as dp

pp = pprint.PrettyPrinter(indent=4)

def listFiles(accountInfo, after=False, number=500): # 'after' and 'number' don't do anything!
  p = requests.get('https://' + accountInfo['accountID'] + '/api/projects',
    headers = {'X-Sifter-Token': accountInfo['token']})
  print(p.content)
  projects = json.loads(p.content)['projects']
  pp.pprint(projects)
  issues = []
  for project in projects:
    print(1)
    project['id'] = project['url'].split('/')[-1]
    print(2)
    r = requests.get('https://' + accountInfo['accountID'] + '/api/projects' + project['id'] + '/issues',
      headers = {'X-Sifter-Token': accountInfo['token']})
    print(r.content)
    sifterIssues = json.loads(r.content)['issues'] # Only 100 per page! @TODO: sort out
    pp.pprint(sifterIssues)
    issues += [sifterToFile(sifterIssue, accountInfo, project) for sifterIssue in sifterIssues]
  pp.pprint(issues)
  return issues

def getFile(accountInfo, fileID):
  p = requests.get('https://' + accountInfo['accountID'] + '/api/projects',
    headers = {'X-Sifter-Token': accountInfo['token']})
  projects = json.loads(p.content)['projects']
  pp.pprint(projects)
  issue = None
  for project in projects:
    project['id'] = project['url'].split('/')[-1]
    r = requests.get('https://' + accountInfo['accountID'] + '/api/projects' + project['id'] + '/issues/' + fileID,
      headers = {'X-Sifter-Token': accountInfo['token']})
    if r.status_code == 200:
      sifterIssue = json.loads(r.content)['issue']
      issue = sifterToFile(sifterIssue, accountInfo, project)
  pp.pprint(issue)
  return issue

def saveFile(accountInfo, fileData):
  if 'integrationFields' not in fileData or 'projectID' not in fileData['integrationFields']:
    print('Sifter cards must specify a projectID')
    return None
  sifterIssue = fileToSifter(fileData, accountInfo)
  project = {
    'id': fileData['integrationFields']['projectID'],
  }
  if 'projectName' in fileData['integrationFields']:
    project['name'] = fileData['integrationFields']['projectName']
  else:
    p = requests.get('https://' + accountInfo['accountID'] + '/api/projects/' + project['id'],
      headers = {'X-Sifter-Token': accountInfo['token']})
    project['name'] = json.loads(p.content)['project']['name']
  url = 'https://' + accountInfo['accountID'] + '/api/projects/' + project['id'] + '/issues/'
  print(url)
  r = requests.post(url,
    headers = {'X-Sifter-Token': accountInfo['token']},
    data = sifterIssue)
  savedIssue = json.loads(r.text)['issue']
  pp.pprint(savedIssue)
  savedFile = sifterToFile(savedIssue, accountInfo, project)
  return savedFile

def deleteFile(f):
  return None

def sifterToFile(issue, accountInfo, project):
  f = {
    'objectID': issue['url'].split('/')[-1], # Is this the right thing to choose? In theory two sifter accounts could have the same id?
    'url': issue['url'],
    'title': issue['subject'],
    'description': issue['description'],
    'created': int(dp.parse(issue['created_at']).strftime('%s')),
    'modified': int(dp.parse(issue['updated_at']).strftime('%s')),
    'fileID': issue['url'].split('/')[-1], # Duplicate of 'objectID' (safer to have both for now)
    'fileTitle': issue['subject'], # Duplicate of 'title' (safer to have both for now)
    'fileType': 'web',
    'fileUrl': issue['url'], # Duplicate of 'url' (safer to have both for now)
    'source': accountInfo['accountID'],
    'service': 'sifter',
    'createdBy': issue['opener_email'], # @TODO: This needs to be matched with Savvy users!!!
    'integrationFields': {
      'projectID': project['id'],
      'projectName': project['name'],
      'priority': issue['priority'],
      'status': issue['status'],
      'number': issue['number'],
      'assignedTo': issue['assignee_name'],
      'milestone': issue['milestone_name'],
      'category': issue['category_name'],
    }
  }
  if 'comments' in issue and len(issue['comments']):
    f['attachments'] = [attachment for comment in issue['comments'] for attachment in comment['attachments']]
  return f

def fileToSifter(f, accountInfo):
  # Required values
  if 'title' not in f:
    print('File must contain "title"')
    return None
  issue = {
    'subject': f['title'],
  }
  # Optional values
  if 'description' in f:
    issue['body'] = f['description']
  if 'integrationFields' in f:
    if 'priority' in f['integrationFields']:
      issue['priority_name'] = f['integrationFields']['priority']
    if 'assignedTo' in f['integrationFields']:
      issue['assignee_name'] = f['integrationFields']['assignedTo']
    if 'milestone' in f['integrationFields']:
      issue['milestone_name'] = f['integrationFields']['milestone']
    if 'category' in f['integrationFields']:
      issue['category_name'] = f['integrationFields']['category']
  return issue












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
