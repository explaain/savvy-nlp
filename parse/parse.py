#!/usr/bin/env python
import re
from parse import search, phrases

commonWords = phrases.commonWords()
emailPhrases = phrases.emailPhrases()

def getPhrasePoints(phrase, content):
  if phrase.lower() not in commonWords and len(phrase) > 2:
    return content.lower().count(phrase.lower()) * len(phrase)
  else:
    return 0

def getResults(data):
  try:
    organisationID = '123' # data['organisationID']
    if 'user' in data:
      user = data['user']
    else:
      user = {
        'uid': data['userID']
      }
    content = data['content']
    cards = search.compound(organisationID, user, content)
    results = {
      'hits': [],
      'pings': [],
      'memories': [],
      'reminders': []
    }

    for phrase in emailPhrases:
      re.sub(phrase, '', content)

    for card in cards:
      score = 0
      words = card['card']['content']['description'].split(' ')
      for i, word in enumerate(words):
        points = getPhrasePoints(word, content)
        score += points
        if (i < len(words) - 1):
          bonusPoints = getPhrasePoints(word + ' ' + words[i+1], content)
          score += bonusPoints
      if score >= len(card['card']['content']['description']):
        card['card']['highlight'] = True
        results['hits'].append(card)
        results['pings'].append(card)
      elif score > 0:
        results['memories'].append(card)
    return results

  except Exception as e:
    print('Oops! This didn\'t work...', e)
    return { 'error': True }
