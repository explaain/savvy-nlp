#!/usr/bin/env python
import math
import json
from algoliasearch import algoliasearch

client = algoliasearch.Client("I2VKMNNAXI", 'be6155d34789643ea81563fb671ebb85')
index = client.init_index('Savvy')

def search(organisationID, user, query):
  filters = ''
  if 'data' in user and 'teams' in user['data']:
    filters = 'teams: "' + '" OR teams: "'.join(list(map(lambda x: x['team'], user['data']['teams']))) + '"'
  results = index.search(query, {
    'filters': filters
  })
  cards = algoliaToCards(results)
  if (card for card in cards if card["card"]["content"]["description"] and 'flock' in card["card"]["content"]["description"]):
    print('FOUND IT')
    print(query)
  # print(cards)
  return cards




def compound(organisationID, user, query):
  length = 400
  limit = 20
  textRange = range(0, min(int(math.ceil(len(query) / length) + 1), limit))
  # print(range)
  results = list(map(lambda x:
    # print(query[length * x:length * (x + 1)]),
    search(organisationID, user, query[length * x:length * (x + 1)]),
    textRange
    ))
  results = [x for x in results if x != []]
  cards = []
  for result in results:
    cards += result
  cards = deDup(cards)
  return cards

def algoliaToCards(results):
  cards = results['hits']
  for i, card in enumerate(cards):
    card['content'] = {}
    if 'description' in card:
      card['content']['description'] = card['description']
      del card['description']
    if 'listItems' in card:
      card['content']['listItems'] = card['listItems']
      del card['listItems']
    if '_highlightResult' in card: del card['_highlightResult']
    cards[i] = {
      'card': card
    }
  return cards

def deDup(array):
  for i, card1 in enumerate(array):
    for j, card2 in enumerate(array[0:i]):
      if card2 and card1['card']['objectID'] == card2['card']['objectID']:
        array[j] = {}
  array = [x for x in array if x != {}]
  return array
