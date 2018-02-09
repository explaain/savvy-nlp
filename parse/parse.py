#!/usr/bin/env python
import re
import pprint
import operator
from collections import Counter
from wordfreq import word_frequency
from . import search, phrases
# from parse.integrations import kloudless_integration as kloudlessDrives
pp = pprint.PrettyPrinter(indent=4)

commonWords = phrases.commonWords()
emailPhrases = phrases.emailPhrases()

def getPhrasePoints(phrase, content):
  if phrase.lower() not in commonWords and len(phrase) > 2:
    points = content.lower().count(phrase.lower()) * len(phrase) / (word_frequency(phrase, 'en') if word_frequency(phrase, 'en') != 0 else 1)
    return points
  else:
    return 0

def getMatchScore(string1, string2):
  score = 0
  words = string1.split(' ')
  for i, word in enumerate(words):
    if (len(word) > 2):
      points = getPhrasePoints(word, string2)
      score += points
      if (i < len(words) - 1):
        bonusPoints = getPhrasePoints(word + ' ' + words[i+1], string2)
        score += bonusPoints
  print('MatchScore: ', score, string1[0:120])
  return score

def getResults(data):
  organisationID = '123' # data['organisationID']
  if 'user' in data:
    user = data['user']
  else:
    user = {
      'uid': data['userID']
    }
  content = data['content']

  # @TODO: Also factor headings etc into points
  # Split into array of words
  wordList = re.sub("[^\w]", " ",  content).split()
  # @TODO: Stem words
  # Get word counts
  wordCounts = Counter(wordList)
  # Get points for words
  pointList = {k: int(v / word_frequency(k, 'en') if word_frequency(k, 'en') != 0 else 0) for k, v in wordCounts.items()}
  # pointList = {k: v for k, v in pointList.items() if v > 200000}
  # pp.pprint(sorted(pointList.items(), key=operator.itemgetter(1)))
  # @TODO: Get points for phrases of 2, 3, ... words in sequence
  # @TODO: Order by value
  # Filter to only words with score > 200,000 @TODO: Include 'or v == 0'
  # Combine into arrays of search terms (on array for each search platform)
  algoliaQuery = ' '.join({k: v for k, v in pointList.items() if v > 200000})
  driveQuery = ' '.join({k: v for k, v in pointList.items() if v > 800000})
  print('\n\nalgoliaQuery\n', algoliaQuery)
  print('\n\ndriveQuery\n', driveQuery)
  # @TODO: Conduct searches

  results = {
    'hits': [],
    'pings': [],
    'memories': [],
    'reminders': []
  }

  for phrase in emailPhrases:
    re.sub(phrase, '', content)

  algoliaCards = search.compound(organisationID, user, algoliaQuery)
  # fileCards = kloudlessDrives.search({}, driveQuery)
  cards = algoliaCards # + fileCards
  for card in cards:
    score = 0
    if 'content' in card['card']:
      text = card['card']['content'].get('title', '') + ' ' + card['card']['content'].get('description', '')
      score = getMatchScore(text, content)
    if len(text) < 2 and 'file' in card['card']:
      text = ''
      # text = kloudlessDrives.getContentForCards('', '', card['card']['file'].get('id'))
      score = 10000000
    else:
      text = ''
    # print(score, text[0:100])
    if score > 1000 * len(text):
      print('Score:', score, len(text), 1000 * len(text), text[0:100])
      card['card']['highlight'] = True
      results['hits'].append(card)
      results['pings'].append(card)
    elif score > 0:
      results['memories'].append(card)

  pp.pprint([{key: list(map(lambda r: getCardText(r), results[key]))} for key in results])
  return results


def getCardText(card):
  c = card['card']
  text = '\n'
  if 'content' in c:
    if 'title' in c['content']:
      text += c['content']['title'] + ' '
    if 'description' in c['content']:
      text += c['content']['description'] + ' '
  if 'file' in c and 'title' in c['file']:
    text += '[FILE]: ' + c['file']['title'] + ' '
  return text
