# @TODO: Investigate! Could instead do this with: https://github.com/bryanmikaelian/sifter-python

import pprint, json, requests, dateutil.parser as dp

pp = pprint.PrettyPrinter(indent=4)

def listFiles(accountInfo):
  p = requests.get('https://projectsapi.zoho.eu/restapi/portal/' + accountInfo['accountID'] + '/projects/',
    params = {'authtoken': accountInfo['token']})
  projects = json.loads(p.content)['projects']
  pp.pprint(projects)
  issues = []
  for project in projects:
    bugsLink = project['link']['bug']['url']
    project['id'] = project['id_string']
    r = requests.get(bugsLink,
      params = {'authtoken': accountInfo['token']})
    zohoBugs = json.loads(r.content)['bugs'] # Only 100 per page! @TODO: sort out
    # pp.pprint(zohoBugs)
    issues += [zohoToFile(zohoBug, accountInfo, project) for zohoBug in zohoBugs]
  pp.pprint(issues)
  return issues

def getFile(accountInfo, fileID):
  p = requests.get('https://projectsapi.zoho.eu/restapi/portal/' + accountInfo['accountID'] + '/projects/',
    params = {'authtoken': accountInfo['token']})
  projects = json.loads(p.content)['projects']
  issue = None
  for project in projects:
    pp.pprint(project)
    bugsLink = project['link']['bug']['url']
    project['id'] = project['id_string']
    r = requests.get(bugsLink + fileID + '/',
      params = {'authtoken': accountInfo['token']})
    if r.status_code == 200:
      zohoBug = json.loads(r.content)['bugs'][0]
      pp.pprint(zohoBug)
      issue = zohoToFile(zohoBug, accountInfo, project)
  pp.pprint(issue)
  return issue

def saveFile(accountInfo, fileData):
  return None
  # if 'integrationFields' not in fileData or 'projectID' not in fileData['integrationFields']:
  #   print('Sifter cards must specify a projectID')
  #   return None
  # sifterIssue = fileToSifter(fileData, accountInfo)
  # project = {
  #   'id': fileData['integrationFields']['projectID'],
  # }
  # if 'projectName' in fileData['integrationFields']:
  #   project['name'] = fileData['integrationFields']['projectName']
  # else:
  #   p = requests.get('https://' + accountInfo['accountID'] + '/api/projects/' + project['id'],
  #     headers = {'X-Sifter-Token': accountInfo['token']})
  #   project['name'] = json.loads(p.content)['project']['name']
  # url = 'https://' + accountInfo['accountID'] + '/api/projects/' + project['id'] + '/issues/'
  # print(url)
  # r = requests.post(url,
  #   headers = {'X-Sifter-Token': accountInfo['token']},
  #   data = sifterIssue)
  # savedIssue = json.loads(r.text)['issue']
  # pp.pprint(savedIssue)
  # savedFile = zohoToFile(savedIssue, accountInfo, project)
  # return savedFile

def deleteFile(f):
  return None

def zohoToFile(bug, accountInfo, project):
  f = {
    'objectID': bug.get('id_string', None),
    'url': 'https://bugtracker.zoho.eu/portal/' + accountInfo['accountID'] + '/#buginfo/' + project['id'] + '/' + bug['id_string'],
    'title': bug.get('title', None),
    'description': bug.get('description', None),
    'created': bug.get('created_time_long', None) / 1000,
    'modified': bug.get('updated_time_long', None) / 1000,
    'fileID': bug.get('id_string', None), # Duplicate of 'objectID' (safer to have both for now)
    'fileTitle': bug.get('title', None), # Duplicate of 'title' (safer to have both for now)
    'fileType': 'web',
    'fileUrl': 'https://bugtracker.zoho.eu/portal/' + accountInfo['accountID'] + '/#buginfo/' + project['id'] + '/' + bug['id_string'], # Duplicate of 'url' (safer to have both for now)
    'source': accountInfo['accountID'],
    'service': 'zoho',
    'creator': bug.get('reported_person', None), # @TODO: This needs to be matched with Savvy users!!!
    'creatorID': bug.get('reporter_id', None), # @TODO: This needs to be matched with Savvy users!!!
    'integrationFields': {
      'projectID': project['id_string'],
      'projectName': project['name'],
      'priority': bug['severity']['type'] if 'severity' in bug else None,
      'priorityData': bug.get('severity', None),
      'status': bug['status']['type'] if 'status' in bug else None,
      'statusData': bug.get('status', None),
      'key': bug.get('key', None),
      'number': bug.get('bug_number', None),
      'assignedTo': bug.get('assignee_name', None),
      'milestone': bug['milestone']['name'] if 'milestone' in bug else None,
      'affectedMilestone': bug['affected_milestone']['name'] if 'affected_milestone' in bug else None,
      'category': bug.get('category_name', None),
      'reproducible': bug.get('reproducible', None),
      'module': bug.get('module', None),
      'escalation_level': bug.get('escalation_level', None),
    }
  }
  # @TODO: Attachments

  # if bug['attachment_count'] > 0:
  #   f['attachments'] = [attachment for comment in issue['comments'] for attachment in comment['attachments']]
  return f

def fileToSifter(f, accountInfo):
  return None
  # # Required values
  # if 'title' not in f:
  #   print('File must contain "title"')
  #   return None
  # issue = {
  #   'subject': f['title'],
  # }
  # # Optional values
  # if 'description' in f:
  #   issue['body'] = f['description']
  # if 'integrationFields' in f:
  #   if 'priority' in f['integrationFields']:
  #     issue['priority_name'] = f['integrationFields']['priority']
  #   if 'assignedTo' in f['integrationFields']:
  #     issue['assignee_name'] = f['integrationFields']['assignedTo']
  #   if 'milestone' in f['integrationFields']:
  #     issue['milestone_name'] = f['integrationFields']['milestone']
  #   if 'category' in f['integrationFields']:
  #     issue['category_name'] = f['integrationFields']['category']
  # return issue




#
# listFiles({
#   "service": "zoho",
#   "organisationID": "explaain",
#   "superService": False,
#   "accountID": "savvy",
#   "token": "1461d2e158c6e83ffa4a45e4e32c9c01",
#   "email": "jeremy@heysavvy.com",
#   "objectID": "bugtracker.zoho.eu/portal/savvy"
# })


# getFile({
#   "service": "zoho",
#   "organisationID": "explaain",
#   "superService": False,
#   "accountID": "savvy",
#   "token": "1461d2e158c6e83ffa4a45e4e32c9c01",
#   "email": "jeremy@heysavvy.com",
#   "objectID": "bugtracker.zoho.eu/portal/savvy"
# }, '29670000000014017')
