#!/usr/bin/env python
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

results = {
  'hits': [
    {
    'card': {
      'content': {
        'description': 'This is a card'
      },
      'objectID': '123',
      'teams': [
        'gqLdFXQ4Z9SAHfjd6IXX'
      ],
      'highlight': True
      }
    }
  ],
  'pings': [

  ],
  'memories': [

  ],
  'reminders': [

  ]
}

@app.route('/parse', methods=['POST'])
def get_results():
  print request.json['url']
  if 'mail.google.com' in request.json['url']:
    results['pings'] = [{
      'card': {
        'content': {
          'description': 'Zendesk integration is due for launch in Sprint 7 (23rd January) and will be posted here'
        },
        'objectID': '246',
        'teams': [
          'gqLdFXQ4Z9SAHfjd6IXX'
        ],
        'highlight': True
      }
    }]
  return jsonify({'results': results})

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
