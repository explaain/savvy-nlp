import pprint, os, json, traceback, sys, db
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


# pp.pprint(client.IndicesClient(es).stats(index='explaain__cards'))
# pp.pprint(client.IndicesClient(es).stats(index='explaain__files'))

query = 'brand colour'

# pp.pprint(db.Cards('explaain').search(query=query, search_service='elasticsearch'))

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


# pp.pprint(client.IndicesClient(es).get(index='explaain__cards'))

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

pp.pprint(client.IndicesClient(es).get(index='explaain__cards'))
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


# pp.pprint(client.IndicesClient(es).delete(index='explaain__cards'))

# savvyCards = [card for card in db.Cards('explaain').browse() if (not 'service' in card or not card['service']) and 'fileID' not in card]
# res = db.Cards('explaain').add(savvyCards)
# pp.pprint(res)
