import pprint, json, requests, dateutil.parser as dp, traceback, sys

pp = pprint.PrettyPrinter(indent=4, width=160)

trelloKey = '40bf04080255c5fe6b5e9643a9b9011b'

def listFiles(source):
  pp.pprint('source')
  pp.pprint(source)
  try:
    b = requests.get('https://api.trello.com/1/members/me/boards?key=' + trelloKey + '&token=' + source['token'])
    print(b)
    boards = json.loads(b.content)
    pp.pprint(boards)
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    return None
  # pp.pprint(boards)
  files = [boardToFile(source, board) for board in boards]
  pp.pprint('files')
  pp.pprint(files)
  return files

def getFile(source, fileID):
  try:
    b = requests.get('https://api.trello.com/1/boards/' + fileID + '?fields=all&key=' + trelloKey + '&token=' + source['token'])
    board = json.loads(b.content)
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    return None
  pp.pprint(board)
  file = boardToFile(source, board)
  return file

def getCard(source, cardID, board=None):
  try:
    c = requests.get('https://api.trello.com/1/cards/' + cardID + '?key=' + trelloKey + '&token=' + source['token'])
    trelloCard = json.loads(c.content)
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    return None
  if not board:
    boardFile = getFile(source, trelloCard['idBoard'])
  card = trelloToCard(source, trelloCard, boardFile)
  return card

def getFileCards(source, fileID):
  """Returns cards ready to be saved!"""
  boardFile = getFile(source, fileID)
  cards = []
  try:
    l = requests.get('https://api.trello.com/1/boards/' + boardFile['objectID'] + '/lists?cards=open&key=' + trelloKey + '&token=' + source['token'])
    lists = json.loads(l.content)
    for list in lists:
      cards += [trelloToCard(source, trelloCard, boardFile) for trelloCard in list['cards']]
  except Exception as e:
    traceback.print_exc(file=sys.stdout)
    print(e)
    return None
  print('cards')
  print(len(cards))
  return cards




def saveFile(source, fileData):
  return None

def deleteFile(f):
  return None

def boardToFile(source, board):
  f = {
    'service': 'trello',
    'source': source['objectID'],
    'organisationID': source['organisationID'],
    'objectID': board.get('id', None),
    'url': board.get('url', None),
    'title': board.get('name', None),
    'description': board.get('desc', None),
    'fileType': 'web',
    'fileID': board.get('id', None), # Duplicate of 'objectID' (safer to have both for now)
    'fileTitle': board.get('name', None), # Duplicate of 'title' (safer to have both for now)
    'fileUrl': board.get('url', None),
    'fileFormat': 'kanban',
    'created': None, # int(dp.parse(board.get('dateLastActivity', None)).strftime('%s')) / 1000,
    'modified': int(dp.parse(board['dateLastActivity']).strftime('%s')) if 'dateLastActivity' in board and board['dateLastActivity'] else None,
    # 'creator': board.get('reported_person', None), # @TODO: This needs to be matched with Savvy users!!!
    # 'creatorID': board.get('reporter_id', None), # @TODO: This needs to be matched with Savvy users!!!
    'integrationFields': {
      'isClosed': board.get('closed', None),
      'isPinned': board.get('pinned', None),
      'integrationOrganisation': board.get('idOrganization', None),
      'permissionLevel': board['prefs'].get('permissionLevel', None),
    }
  }
  return f

def trelloToCard(source, trelloCard, boardFile):
  card = {
    'service': 'trello',
    'format': 'card',
    'source': source['objectID'],
    'organisationID': source['organisationID'],
    'objectID': trelloCard.get('id', None),
    'url': trelloCard.get('url', None),
    'title': trelloCard.get('name', None),
    'description': trelloCard.get('desc', None),
    'fileType': 'web',
    'fileID': trelloCard.get('idBoard', None), # Duplicate of 'objectID' (safer to have both for now)
    'fileTitle': boardFile.get('title', None), # Duplicate of 'title' (safer to have both for now)
    'fileUrl': boardFile.get('fileUrl', None),
    'fileFormat': 'kanban',
    'created': None, # int(dp.parse(trelloCard.get('dateLastActivity', None)).strftime('%s')) / 1000,
    'modified': int(dp.parse(trelloCard['dateLastActivity']).strftime('%s')) if 'dateLastActivity' in trelloCard and trelloCard['dateLastActivity'] else None,
    # 'creator': trelloCard.get('reported_person', None), # @TODO: This needs to be matched with Savvy users!!!
    # 'creatorID': trelloCard.get('reporter_id', None), # @TODO: This needs to be matched with Savvy users!!!
    'due': trelloCard.get('due', None),
    'integrationFields': {
      'isClosed': trelloCard.get('closed', None),
      'listID': trelloCard.get('idList', None),
      'subscribed': trelloCard.get('subscribed', None),
    }
  }
  return card


# pp.pprint(listFiles({
# pp.pprint(getFileCards({
#   "service": "trello",
#   "organisationID": "explaain",
#   "token": "c283a237943533739162cb46b07f9b2ec0d1a383b7307aac4b64d62393103583",
#   "accountID": "trello-jeremynevans",
# # }))
# }, '5720c1d16d40a8788d0eb6d1'))


# getFile({
#   "service": "zoho",
#   "organisationID": "explaain",
#   "superService": False,
#   "accountID": "savvy",
#   "token": "1461d2e158c6e83ffa4a45e4e32c9c01",
#   "email": "jeremy@heysavvy.com",
#   "objectID": "bugtracker.zoho.eu/portal/savvy"
# }, '29670000000014017')
