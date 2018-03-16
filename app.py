#!/usr/bin/env python
import os, pprint
# import bugsnag, os, pprint
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import index
import cards
from parse import parse

# bugsnag.configure(
# api_key="d0731cc66b977d432f6e328d4952c168",
# project_root="savvy/savvy-1",
# )

pp = pprint.PrettyPrinter(indent=4)

from algoliasearch import algoliasearch
client = algoliasearch.Client('D3AE3TSULH', '88bd0a77faff65d4ace510fbf172a4e1') # This API key allows everything
algoliaExplaainIndex = client.init_index('explaain__Cards')

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
  print('API Returning:')
  pp.pprint(results)
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

@app.route('/save-card', methods=['POST'])
def save_card():
  print('Starting to save card!')
  pp.pprint(request.json)
  result = index.saveCard(request.json['card'], request.json['author'])
  pp.pprint(result)
  return jsonify(result)

@app.route('/delete-card', methods=['POST'])
def delete_card():
  print('Starting to delete card!')
  pp.pprint(request.json)
  result = index.deleteCard(request.json['card'], request.json['author'])
  pp.pprint(result)
  return jsonify(result)

@app.route('/verify-card', methods=['POST'])
def verify_card():
  print('Starting to verify card!')
  pp.pprint(request.json)
  result = index.verify(request.json['objectID'], request.json['author'], prop = request.json['prop'] if 'prop' in request.json else None, approve = request.json['approve'] if 'approve' in request.json else None)
  pp.pprint(result)
  return jsonify(result)

@app.route('/generate-card-data', methods=['POST'])
def generate_card_data():
  print('Starting generate_card_data()')
  results = cards.generateCardData(request.json)

  return jsonify({'results': results})

@app.route('/save-to-savvy', methods=['POST'])
def save_to_savvy():
  print('Saving to Savvy')
  results = algoliaExplaainIndex.add_object(request.json)
  print(results)
  return jsonify({'results': results})

if __name__ == '__main__':
  # Bind to PORT if defined, otherwise default to 5000.
  port = int(os.environ.get('PORT', 5050))
  app.run(host='0.0.0.0', port=port)
