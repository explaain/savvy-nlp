#!/usr/bin/env python
import os
from algoliasearch import algoliasearch
from flask import Flask, jsonify, request

client = algoliasearch.Client("I2VKMNNAXI", 'be6155d34789643ea81563fb671ebb85')
index = client.init_index('Savvy')
app = Flask(__name__)

results = {
  'hits': [
    {
      'content': {
        'description': 'This is a card'
      },
      'objectID': '123',
      'teams': [
        'gqLdFXQ4Z9SAHfjd6IXX'
      ],
      'highlight': True
    }
  ],
  'pings': [

  ],
  'memories': [

  ],
  'reminders': [

  ]
}

res = index.search("query string")

def processPageData(organisationID, user, pageData):


def compoundSearch(user, pageText):
    try:

    except ValueError:
        print("Oops!  This didn't work...")

def commonWords():
    listOfCommonWords = ['i',
      'a',
      'of',
      'me',
      'my',
      'is',
      'im',
      'so',
      'all',
      'get',
      'how',
      'new',
      'out',
      'the',
      'use',
      'best',
      'name',
      'next',
      'take',
      'what',
      'image',
      'something',
    ]
    return listOfCommonWords

def emailPhrases():
    listOfEmailPhrases = ['Skip to content',
      'Using',
      'with screen readers',
      'Search',
      'Mail',
      'COMPOSE',
      'Labels',
      'Inbox',
      'Starred',
      'Sent Mail',
      'Drafts',
      'More',
      '---------- Forwarded message ----------',
      'From: ',
      'Date: ',
      'Subject: ',
      'To: ',
      'Click here to Reply or Forward',
      'GB',
      'GB used',
      'Manage',
      'Program Policies',
      'Powered by Google',
      'Last account activity:',
      'hour ago',
      'hours ago',
      'Details',
    ]
    return listOfEmailPhrases


@app.route('/parse', methods=['POST'])
def get_results():
  results['memories'].append({
    'content': {
      'description': request.json['content'][:100]
    },
    'objectID': '246',
    'teams': [
      'gqLdFXQ4Z9SAHfjd6IXX'
    ]
  })
  return jsonify({'results': results})

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
