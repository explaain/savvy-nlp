import pprint, os, json, traceback, sys
from raven import Client as SentryClient
from algoliasearch import algoliasearch
from elasticsearch import Elasticsearch

pp = pprint.PrettyPrinter(indent=4) #, width=160)

sentry = SentryClient(
  'https://9a0228c8fde2404c9ccd6063e6b02b4c:d77e32d1f5b64f07ba77bda52adbd70e@sentry.io/1004428',
  environment = 'local' if 'HOME' in os.environ and os.environ['HOME'] == '/Users/jeremy' else 'production')

es = Elasticsearch(
    ['https://ad56f010315f958f3a4d179dc36e6554.us-east-1.aws.found.io:9243/'],
    http_auth=('elastic', 'z5X0jw5hyJRzpEIOvFQmWwxN'),
    scheme='https',
    port=9243,)

class Client:
  """docstring for Client"""
  def __init__(self, app_id='D3AE3TSULH', api_key='1b36934cc0d93e04ef8f0d5f36ad7607'): # This API key allows everything
    self.client = algoliasearch.Client(app_id, api_key)

  def index(self, index_name: str=None):
    if index_name:
      return self.client.init_index(index_name)
    else:
      return None

  def list_indices(self):
    return self.client.list_indexes()


class Index:
  """docstring for Index."""
  def __init__(self, index_name: str=None, doc_type: str='doc'):
    self.index(index_name=index_name, doc_type=doc_type)

  def index(self, index_name: str=None, doc_type: str='doc'):
    if not index_name:
      return None
    self.index_name = index_name
    self.lowercase_index_name = index_name.lower()
    self.doc_type = doc_type
    client = Client()
    try:
      self.index = client.index(index_name=self.index_name)
      return self.index
    except Exception as e:
      print('Algolia: Couldn\'t connect to index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None

  def get_index_name(self):
    return self.index_name

  def search(self, query: str='', params: dict=None, search_service: str='algolia'):
    if not query:
      query = ''
    if not len(query) and params and 'query' in params and params['query']:
      query = params['query']
    try:
      if search_service == 'algolia':
        return self.index.search(query, params)
      else:
        # @TODO: configure search and insert query
        res = es.search(index=self.lowercase_index_name, body = {'query': {'match_all': {}}})
        return {
          'hits': [hit['_source'] for hit in res['hits']['hits']]
        }
    except Exception as e:
      print(search_service + ': Couldn\'t search for records in index "' + self.lowercase_index_name + '". ', e)
      sentry.captureException()
      return None

  def get(self, objectID: str=None, objectIDs: list=[], allowFail: bool=False):
    # allowFail should only be True if it's fine for the object not to be found
    if not objectID and (not objectIDs or not len(objectIDs)):
      return None
    if objectIDs and len(objectIDs):
      try:
        return self.index.get_objects(objectIDs)
      except Exception as e:
        print('Algolia: Couldn\'t get records from index "' + self.index_name + '". ', e)
        sentry.captureException()
        return None
    else:
      try:
        print(1)
        exists = es.exists(index=self.lowercase_index_name, doc_type=self.doc_type, id=objectID)
        print(exists)
        print(not exists)
        if exists:
          print(22)
          res = es.get(index=self.lowercase_index_name, doc_type=self.doc_type, id=objectID)
          print('From ElasticSearch:')
          pp.pprint(res)
        else:
          print('From ElasticSearch: record from index "' + self.lowercase_index_name + '" doesn\'t exist. ')

        # pp.pprint(res)
      except Exception as e:
        traceback.print_exc(file=sys.stdout)
        sentry.captureException()
        print('ElasticSearch: Couldn\'t get record from index "' + self.lowercase_index_name + '". ', e)
      try:
        return self.index.get_object(objectID)
      except Exception as e:
        if allowFail:
          print('Algolia: Didn\'t find record in index, but this is OK so not throwing error')
        else:
          print('Algolia: Couldn\'t get record from index "' + self.index_name + '". ', e)
          sentry.captureException()
        return None

  def browse(self, params=False):
    try:
      if params:
        browsed = self.index.browse_all(params)
      else:
        browsed = self.index.browse_all()
    except Exception as e:
      print('Algolia: Couldn\'t browse index "' + index_name + '". ', e)
      sentry.captureException()
    return [hit for hit in browsed]

  def add(self, toAdd):
    if type(toAdd) == dict:
      record = toAdd
      records = None
    elif type(toAdd) == list:
      records = toAdd
      record = None
    if not record and not records:
      return None
    try:
      if records:
        result = self.index.add_objects(records)
      else:
        result = self.index.add_object(record)
    except Exception as e:
      print('Algolia: Couldn\'t add record(s) to index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None
    print('result')
    pp.pprint(result)
    try:
      if records:
        body = list(records)
        for record in body:
          if 'objectID' in body:
            del(record['objectID'])
        body = ['{ "index" : { "_id" : "' + result['objectIDs'][i] + '" } }\n' + json.dumps(record) for i, record in enumerate(records)]
        body = '\n'.join(body)
        print('body')
        print(body)
        res = es.bulk(index=self.lowercase_index_name, doc_type=self.doc_type, body=body)
      else:
        body = dict(record)
        if 'objectID' in body:
          del(body['objectID'])
        print('body')
        print(body)
        res = es.index(index=self.lowercase_index_name, doc_type=self.doc_type, id=result['objectID'], body=body)
      print('res')
      pp.pprint(res)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t add record(s) to index "' + self.lowercase_index_name + '". ', e)
    return result

  def save(self, toAdd: dict):
    if type(toAdd) == dict:
      record = toAdd
      records = None
    elif type(toAdd) == list:
      records = toAdd
      record = None
    if not record and not records:
      return None
    try:
      if records:
        for record in records:
          if 'objectID' not in record:
            print('All records must contain objectID')
            return None
        result = self.index.save_objects(records)
      else:
        if 'objectID' not in record:
          print('Record must contain objectID')
          return None
        result = self.index.save_object(record)
    except Exception as e:
      print('Algolia: Couldn\'t save record(s) to index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None
    print('result')
    pp.pprint(result)
    try:
      if records:
        body = list(records)
        for record in body:
          del(record['objectID'])
        body = ['{ "index" : { "_id" : "' + result['objectIDs'][i] + '" } }\n' + json.dumps(record) for i, record in enumerate(records)]
        body = '\n'.join(body)
        print('body')
        print(body)
        res = es.bulk(index=self.lowercase_index_name, doc_type=self.doc_type, body=body)
      else:
        body = dict(record)
        del(body['objectID'])
        print('body')
        print(body)
        res = es.index(index=self.lowercase_index_name, doc_type=self.doc_type, id=result['objectID'], body=body)
      print('res')
      pp.pprint(res)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t save record(s) to index "' + self.lowercase_index_name + '". ', e)
    return result

  def partial_update(self, record: dict):
    try:
      # Do we need to account for multiple objects here too?
      result = self.index.partial_update_object(record)
    except Exception as e:
      print('Algolia: Couldn\'t save record to index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None
    try:
      body = dict(record)
      del(body['objectID'])
      res = es.index(index=self.lowercase_index_name, doc_type=self.doc_type, id=result['objectID'], body=body)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t update record in index "' + self.lowercase_index_name + '". ', e)
    return result

  def delete(self, objectID: str=None):
    if not objectID:
      return None
    try:
      result = self.index.delete_object(objectID)
    except Exception as e:
      print('Algolia: Couldn\'t delete record from index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None
    try:
      res = es.delete(index=self.lowercase_index_name, doc_type=self.doc_type, id=objectID)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t delete record from index "' + self.lowercase_index_name + '". ', e)
    return result

  def delete_by_query(self, params: dict=None):
    if not params or not len(params) or (('query' not in params or not len (params['query'])) and ('filter' not in params or not len (params['filter']))):
      # This makes sure that we don't delete everything! (I.e. that either params['query'] or params['filter'] exists and is non-empty)
      return None
    query = params['query'] if 'query' in params and params['query'] else ''
    try:
      # @TODO: Check this is actually the Algolia command
      result = self.index.delete_by_query(query=query, params=params)
    except Exception as e:
      print('Algolia: Couldn\'t delete records from index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None
    # @TODO: Look this up and finish it
    # try:
    #   res = es.delete_by_query(index=self.lowercase_index_name, doc_type=self.doc_type, id=objectID)
    # except Exception as e:
    #   traceback.print_exc(file=sys.stdout)
    #   sentry.captureException()
    #   print('ElasticSearch: Couldn\'t delete records from index "' + self.lowercase_index_name + '". ', e)
    return result

  def get_settings(self):
    try:
      return self.index.get_settings()
    except Exception as e:
      print('Algolia: Couldn\'t get settings from index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None

  def set_settings(self, settings: dict):
    try:
      return self.index.set_settings(settings)
    except Exception as e:
      print('Algolia: Couldn\'t set settings for index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None


class Organisations(Index):
  def __init__(self):
    self.index(index_name='organisations', doc_type='organisation')

class Sources(Index):
  def __init__(self):
    self.index(index_name='sources', doc_type='source')

class Users(Index):
  def __init__(self):
    self.index(index_name='users', doc_type='user')

class Cards(Index):
  def __init__(self, organisationID):
    self.index(index_name=organisationID + '__Cards', doc_type='card')

class Files(Index):
  def __init__(self, organisationID):
    self.index(index_name=organisationID + '__Files', doc_type='file')


# Sources()
# print(Cards('explaain').get(objectID='CBk1gWIBrXgu31eums2X'))
# pp.pprint(Cards('explaain').search(search_service='elasticsearch', query=''))
# print(Cards('explaain').add([
# {
#   "hello": "hello3",
#   # "objectID": "999111b",
# },
# {
#   "hello": "hello4",
#   # "objectID": "999111c",
# },
# ]))
# Files('explaain').save(file)

#
# res = es.bulk(index='explaain__cards', doc_type='card', body=
# '{ "index" : { "_id" : "2" } }\n'
# +'{"hello": "yo"}\n'
# '{ "index" : { "_id" : "3" } }\n'
# +'{"hello": "yo"}\n'
# )
# pp.pprint(res)
