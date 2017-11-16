#!/usr/bin/env python
from flask import Flask, jsonify, request

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

@app.route('/parse', methods=['POST'])
def get_results():
  results['memories'].append({
    'content': {
      'description': request.json['content']
    },
    'objectID': '246',
    'teams': [
      'gqLdFXQ4Z9SAHfjd6IXX'
    ]
  })
  return jsonify({'results': results})

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  # port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0')
