#!/usr/bin/env python
import os
from flask import Flask, jsonify, request
from parse import parse

app = Flask(__name__)

# print(parse.getResults({ 'user': '123', 'organisationID': '12345', 'content': 'Some content the queen' }))

@app.route('/parse', methods=['POST'])
def get_results():
  print('Starting get_results()')
  # try:
  results = parse.getResults(request.json)
  # except Exception as e:
  #   print('Main error')
  #   print(e)
  #   results = {}

  return jsonify({'results': results})

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)
