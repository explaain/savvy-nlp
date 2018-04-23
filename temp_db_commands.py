import pprint, os, json, traceback, sys, db, requests
import templates
from raven import Client as SentryClient
from algoliasearch import algoliasearch
from elasticsearch import Elasticsearch
from elasticsearch import client

pp = pprint.PrettyPrinter(indent=1) #, width=160)

es = Elasticsearch(
# https://elastic:z5X0jw5hyJRzpEIOvFQmWwxN@ad56f010315f958f3a4d179dc36e6554.us-east-1.aws.found.io:9243/
    ['https://ad56f010315f958f3a4d179dc36e6554.us-east-1.aws.found.io:9243/'],
    http_auth=('elastic', 'z5X0jw5hyJRzpEIOvFQmWwxN'),
    scheme='https',
    port=9243,)

# @NOTE: Getting info about a particular index/cluster etc
# pp.pprint(client.IndicesClient(es).stats(index='users'))
# pp.pprint(client.IndicesClient(es).stats(index='alborz_bozorgi_al_30068826__cards'))
# pp.pprint(client.IndicesClient(es).stats(index='mohamad_el_boudi_19370086__cards'))
# pp.pprint(client.IndicesClient(es).stats(index='financialtimes__cards'))
# pp.pprint(client.IndicesClient(es).stats(index='matthew_rusk_62352643__cards'))

# all_orgs = [
#   'explaain',
#   'Matthew_Rusk_62352643',
#   'yc',
#   'Andrew_Davies_29862274',
#   'financialtimes',
# ]
# all_index_names = [org.lower() + '__cards' for org in all_orgs] + [org.lower() + '__files' for org in all_orgs] + ['organisations', 'sources', 'users']
# for index_name in all_index_names:
#   print(index_name)
#   print(client.IndicesClient(es).stats(index=index_name)['_all']['primaries']['docs']['count'])

query = 'savvy'

# pp.pprint(db.Cards('jillian_kowalchuk_44819851').search(query=query, search_service='elasticsearch'))


# pp.pprint(es.search(index='users', body = {'query': {'match_all': {}}}, size=100))
# res = es.search(index='sources', q=query, body = {'query': {'match_all': {}}}, size=100)
# pp.pprint(res)
# pp.pprint([hit['_id'] for hit in res['hits']['hits']])
# pp.pprint([hit['_id'] + ': ' + hit['_source']['addedBy'] if 'addedBy' in hit['_source'] else None for hit in res['hits']['hits']])
# pp.pprint(res['hits']['hits'])
# pp.pprint(es.search(index='organisations', body = {'query': {'match_all': {}}}, size=100))
# pp.pprint(es.get(index='sources', doc_type='source', id='9IYW8mIBVmRs6EKTRK1Q'))
# pp.pprint(es.delete(index='organisations', doc_type='organisation', id='Savvy_Test_38471264'))
# pp.pprint(es.delete(index='users', doc_type='user', id='6KRm82IBFJlaWnBE59JA'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='701157581'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717781852'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717781852'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717659592'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717659592'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='707213261'))
# pp.pprint(es.get(index='sources', doc_type='source', id='707213261'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='698350271'))
# pp.pprint(es.get(index='sources', doc_type='source', id='698350271'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717449552'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717449552'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717449302'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717449302'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='707271521'))
# pp.pprint(es.get(index='sources', doc_type='source', id='707271521'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='707009831'))
# pp.pprint(es.get(index='sources', doc_type='source', id='707009831'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='706790801'))
# pp.pprint(es.get(index='sources', doc_type='source', id='706790801'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717692572'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717692572'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717692552'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717692552'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717449572'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717449572'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='717449452'))
# pp.pprint(es.get(index='sources', doc_type='source', id='717449452'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='698815861'))
# pp.pprint(es.get(index='sources', doc_type='source', id='698815861'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='698350251'))
# pp.pprint(es.get(index='sources', doc_type='source', id='698350251'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='QPWz82IBwpczb9a6pvPJ'))
# pp.pprint(es.get(index='sources', doc_type='source', id='QPWz82IBwpczb9a6pvPJ'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='712726292'))
# pp.pprint(es.get(index='sources', doc_type='source', id='712726292'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='711558252'))
# pp.pprint(es.get(index='sources', doc_type='source', id='711558252'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='707213221'))
# pp.pprint(es.get(index='sources', doc_type='source', id='707213221'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='707198911'))
# pp.pprint(es.get(index='sources', doc_type='source', id='707198911'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='707198831'))
# pp.pprint(es.get(index='sources', doc_type='source', id='707198831'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='698859021'))
# pp.pprint(es.get(index='sources', doc_type='source', id='698859021'))
# pp.pprint(es.delete(index='sources', doc_type='source', id='713438322'))
# pp.pprint(es.get(index='sources', doc_type='source', id='713438322'))


# pp.pprint(es.search(index='users', body = {'query': {'match_all': {}}}, size=100))
# pp.pprint(es.get(index='users', doc_type='user', id='vZweCaZEWlZPx0gpQn2b1B7DFAZ2'))
# pp.pprint(es.get(index='explaain__cards', doc_type='card', id='Comu1GIBYGsTCJWEXGgN'))
# pp.pprint(es.search(index='matthew_rusk_62352643__cards', q=query, body = {'query': {'match_all': {}}}, size=4))
# pp.pprint(es.search(index='financialtimes__cards', q=query, body = {'query': {'match_all': {}}}, size=4))
# res = es.search(index='matthew_rusk_62352643__cards',q=query, body = {'query': {'match_all': {}}})
# res = db.Cards('Matthew_Rusk_62352643').search(query=query)
# res = db.Cards('Matthew_Rusk_62352643').search(query=query, search_service='elasticsearch')
# pp.pprint(res)
# print(len(res['hits']))

# pp.pprint(es.search(index='explaain__cards', q=query, body = {'query': {'match_all': {}}}, size=4))
# pp.pprint(es.search(index='explaain__cards', q=query, body = {'query': {'match_all': {}}}, size=5, explain=True))
# print(json.dumps(es.search(index='explaain__cards', q=query, body = {'query': {'match_all': {}}}, size=5, explain=True), indent=2, sort_keys=True))
# print(json.dumps(es.search(index='explaain__cards', q=query, body = {'query': {'match_all': {}}}, analyzer='in_situ', size=5, explain=True), indent=2, sort_keys=True))
# print(json.dumps(es.search(index='explaain__cards', body=
# {
#   'query': {
#     'match': {
#       'description': {
#         'query': query,
#         'auto_generate_synonyms_phrase_query': False,
#       }
#     }
#   }
# }
# # {
# #   'query': {
# #     'multi_match': {
# #       'query': query,
# #       'auto_generate_synonyms_phrase_query': True,
# #     }
# #   }
# # }
# , explain=True, size=12), indent=2, sort_keys=True))


# pp.pprint(client.IndicesClient(es).get(index='_all'))

# pp.pprint(db.Client().list_indices(search_service='elasticsearch'))
# pp.pprint([i['name'] for i in db.Client().list_indices(search_service='algolia')['items']])

# pp.pprint(client.IndicesClient(es).get(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).get(index='matthew_rusk_62352643__cards'))

# pp.pprint(client.IndicesClient(es).analyze(index='explaain__cards', body=
# {
#   "tokenizer":  "standard",
#   "filter": [
#     "english_possessive_stemmer",
#     "lowercase",
#     "english_stop",
#     "english_keywords",
#     "english_stemmer"
#   ],
#   'text' : query
# }
# ))


# pp.pprint(client.IndicesClient(es).close(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).put_settings(index='explaain__cards', body=
# {
#   "analysis": {
#     "filter": {
#       "english_stop": {
#         "type":       "stop",
#         "stopwords":  "_english_"
#       },
#       "english_keywords": {
#         "type":       "keyword_marker",
#         "keywords":   []
#       },
#       "english_stemmer": {
#         "type":       "stemmer",
#         "language":   "english"
#       },
#       "english_possessive_stemmer": {
#         "type":       "stemmer",
#         "language":   "possessive_english"
#       }
#     },
#     "analyzer": {
#       "english": {
#         "tokenizer":  "standard",
#         "filter": [
#           "english_possessive_stemmer",
#           "lowercase",
#           "english_stop",
#           "english_keywords",
#           "english_stemmer"
#         ]
#       }
#     }
#   }
# }
# ))
# pp.pprint(client.IndicesClient(es).open(index='explaain__cards'))

# pp.pprint(client.IndicesClient(es).close(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).put_settings(index='explaain__cards', body=
# {
#   "analysis": {
#     "filter": {
#       "unique_stem": {
#         "type": "unique",
#         "only_on_same_position": True
#       }
#     },
#     "analyzer": {
#       "in_situ": {
#         "tokenizer": "standard",
#         "filter": [
#           "lowercase",
#           "keyword_repeat",
#           "porter_stem",
#           "unique_stem"
#         ]
#       }
#     }
#   }
# }
# ))
# pp.pprint(client.IndicesClient(es).open(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).get(index='explaain__cards'))


# pp.pprint(client.IndicesClient(es).close(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).put_settings(index='explaain__cards', body=
# {
#   "analysis": {
#     "analyzer" : {
#       "search_synonyms" : {
#         "tokenizer" : "whitespace",
#         "filter" : ["graph_synonyms"]
#       },
#     },
#     "filter" : {
#       "graph_synonyms" : {
#         "type" : "synonym_graph",
#         "synonyms_path" : "analysis/synonym.txt"
#       }
#     }
#   }
# }
# ))
# pp.pprint(client.IndicesClient(es).open(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).get(index='explaain__cards'))

# pp.pprint(client.NodesClient(es).info())
# pp.pprint(client.CatClient(es).indices())
# pp.pprint(client.ClusterClient(es).get_settings())
# pp.pprint(client.ClusterClient(es).put_settings(body=
# {
#   'persistent': {
#     'cluster': {
#       'indices': {
#         'close': {
#           'enable': True
#         }
#       }
#     }
#   }
# }
# ))


# pp.pprint(client.IndicesClient(es).get_mapping(index='users', doc_type='user'))


# pp.pprint(client.IndicesClient(es).get_mapping(index='explaain__cards', doc_type='card'))
# # pp.pprint(client.IndicesClient(es).get_field_mapping(index='explaain__cards', doc_type='card', fields='description' ))
#
#
#
# pp.pprint(client.IndicesClient(es).analyze(index='explaain__cards', body=
# {
#   "field": "description",
#   "text": "purple colours"
# }
# ))

# pp.pprint(es.reindex(body=
# {
#   'source': {
#     'index': '2_explaain__cards'
#   },
#   'dest': {
#     'index': 'explaain__cards'
#   }
# }
# ))

#
# pp.pprint(client.IndicesClient(es).delete(index='savvy_test_27566448__cards'))
# pp.pprint(client.IndicesClient(es).delete(index='savvy_test_27566448__files'))
# pp.pprint(client.IndicesClient(es).delete(index='savvy_test_99753051__cards'))
# pp.pprint(client.IndicesClient(es).delete(index='savvy_test_99753051__files'))

# savvyCards = [card for card in db.Cards('explaain').browse() if (not 'service' in card or not card['service']) and 'fileID' not in card]
# res = db.Cards('explaain').add(savvyCards)
# pp.pprint(res)

def chunks(l, n):
  """Yield successive n-sized chunks from l."""
  for i in range(0, len(l), n):
    yield l[i:i + n]

# res = db.Files('Matthew_Rusk_62352643').browse()
# print(len(res))

# @NOTE: This copies everything from Algolia to ES
# @NOTE: MAKE SURE UsingAlgolia = False in db.py!!!

def copy_docs_from_algolia(index):
  print(index.get_index_name())
  all_cards = index.browse(search_service='algolia')
  for card in all_cards:
    if '__highlightResult' in card:
      del(card['_highlightResult'])
  all_card_chunks = list(chunks(all_cards, 500))
  for chunk in all_card_chunks:
    res = index.save(chunk)
    print('len: ' + str(len(res['objectIDs'])))
  print('\n\n\n\n\n\n')

# copy_docs_from_algolia(index = db.Cards('financialtimes'))

def reset_and_fill_all_indices():
  all_orgs = [
    'explaain',
    'Matthew_Rusk_62352643',
    'yc',
    'Andrew_Davies_29862274',
    'financialtimes',
  ]
  all_index_names = [org.lower() + '__cards' for org in all_orgs] + [org.lower() + '__files' for org in all_orgs] + ['organisations', 'sources', 'users']

  all_card_indices = [db.Cards(org) for org in all_orgs]
  all_file_indices = [db.Files(org) for org in all_orgs]
  # all_indices = all_card_indices + all_file_indices + [db.Organisations(), db.Sources(), db.Users()]
  all_indices = all_file_indices + [db.Organisations(), db.Sources(), db.Users()]

  template_type = 'cards'
  template = templates.get_template(template_type)
  pp.pprint(client.IndicesClient(es).put_template(name=template_type, body=template))
  # for org in all_orgs:
  #   index_name = org.lower() + '__cards'
  #   print(index_name)
    # print(json.dumps(client.IndicesClient(es).get_mapping(index=index_name, doc_type='card'), indent=2))
    # client.IndicesClient(es).close(index=index_name)
    # try:
    #   client.IndicesClient(es).put_mapping(index=index_name, doc_type='card', body=cards_template['mappings']['card'])
    #   client.IndicesClient(es).put_settings(index=index_name, body=cards_template['settings'])
    # except Exception as e:
    #   print(e)
    # client.IndicesClient(es).open(index=index_name)

  template_type = 'files'
  template = templates.get_template(template_type)
  pp.pprint(client.IndicesClient(es).put_template(name=template_type, body=template))
  # for org in all_orgs:
  #   index_name = org.lower() + '__files'
  #   print(index_name)
    # client.IndicesClient(es).put_mapping(index=index_name, doc_type='file', body=files_template['mappings']['file'])

  # for index_name in all_index_names:
  #   print(index_name)
  #   if client.IndicesClient(es).exists(index=index_name):
  #     client.IndicesClient(es).delete(index=index_name)
  #   client.IndicesClient(es).create(index=index_name)
  for index in all_indices:
    copy_docs_from_algolia(index=index)


# reset_and_fill_all_indices()


# Matt Rusk
# ES: 3564
# Al: len(15749)
# New ES: 15749
# FILES:
# 19
# 384
# 384

# Explaain
# ES: 18478
# Al: 9801
# New ES: 23907

# FT
# ES: 111466
# Al: 237461
# New ES:






# exports.slack = (eventName, details, data) => {
#   console.log('Sending to Slack:', eventName, details, data)
#   axios.post('https://hooks.zapier.com/hooks/catch/3134011/kv4k3j/', {
#     event_name: eventName,
#     event_details: details,
#     data: data
#   })
# }

# requests.post('https://hooks.zapier.com/hooks/catch/3134011/kv4k3j/', {
#   'event_name': 'testing eventName',
#   'event_details': 'details',
#   'data': 'data'
# })
