#!/usr/bin/env python
import os
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import index
import cards
from parse import parse

app = Flask(__name__)
CORS(app)

# print(parse.getResults({ 'user': '123', 'organisationID': '12345', 'content': 'Some content the queen' }))

@app.route('/add-source', methods=['POST'])
def add_source():
  print('Starting to add source!')
  results = index.addSource(request.json)
  return jsonify({'results': results})

@app.route('/get-user', methods=['POST'])
def get_user():
  print('Starting to get user data!')
  results = index.serveUserData(request.json['idToken'])
  return jsonify({'results': results})

@app.route('/set-up-org', methods=['POST'])
def set_up_org():
  print('request.json', request.json)
  if 'organisationID' in request.json:
    index.setUpOrg(request.json['organisationID'])
    return jsonify({'completed': True})
  else:
    return jsonify({'completed': False})

@app.route('/parse', methods=['POST'])
def get_results():
  print('Starting get_results()')
  # try:
  results = parse.getResults(request.json)
  # except Exception as e:
  #   print('Main error')
  #   print(e)
  #   results = {}

@app.route('/generate-card-data', methods=['POST'])
def generate_card_data():
  print('Starting generate_card_data()')
  results = cards.generateCardData(request.json)

  return jsonify({'results': results})

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5050))
  app.run(host='0.0.0.0', port=port)
