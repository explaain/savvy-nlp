# ELASTICSEARCH TODOS:
# @TODO: browse()

import pprint, os, json, traceback, sys, datetime, calendar, time
from dotenv import load_dotenv
import templates
from raven import Client as SentryClient
from algoliasearch import algoliasearch
from elasticsearch import Elasticsearch
from elasticsearch import client as es_client
from mixpanel import Mixpanel

# Loads .env into environment variables
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

mp = Mixpanel('e3b4939c1ae819d65712679199dfce7e')

pp = pprint.PrettyPrinter(indent=4) #, width=160)

sentry = SentryClient(
  'https://9a0228c8fde2404c9ccd6063e6b02b4c:d77e32d1f5b64f07ba77bda52adbd70e@sentry.io/1004428',
  environment = 'local' if 'HOME' in os.environ and os.environ['HOME'] == '/Users/jeremy' else 'production')

es = Elasticsearch(
# https://elastic:z5X0jw5hyJRzpEIOvFQmWwxN@ad56f010315f958f3a4d179dc36e6554.us-east-1.aws.found.io:9243/
    ['https://ad56f010315f958f3a4d179dc36e6554.us-east-1.aws.found.io:9243/'],
    http_auth=('elastic', os.getenv('ELASTIC_PWD')),
    scheme='https',
    port=9243,)

UsingAlgolia = False

class Client:
  """docstring for Client"""
  def __init__(self, app_id='D3AE3TSULH', api_key='1b36934cc0d93e04ef8f0d5f36ad7607'): # This API key allows everything
  # def __init__(self, app_id='__', api_key='__'): # This API key allows everything
    self.client = algoliasearch.Client(app_id, api_key)

  def index(self, index_name: str=None):
    # @TODO: What happens with this when it's ElasticSearch???
    if index_name:
      return self.client.init_index(index_name)
    else:
      return None

  def list_indices(self, search_service: str='elasticsearch'):
    if search_service == 'algolia':
      return self.client.list_indexes()
    else:
      indices = es_client.IndicesClient(es).get(index='_all')
      # @NOTE: Currently only produces property 'name' for each index
      if not indices:
        return None
      return {
        'items': [{ 'name': key } for key in indices if key[0] != '.']
      }

  # def delete_index(self, index_name: str=None):
  #   if index_name and len(index_name):
  #     return self.client.delete(index=index_name)
  #   else:
  #     return None


class Index:
  """docstring for Index."""
  def __init__(self, index_name: str=None, doc_type: str='doc'):
    self.init_index(index_name=index_name, doc_type=doc_type)

  def init_index(self, index_name: str=None, doc_type: str='doc'):
    if not index_name:
      return None
    self.index_name = index_name
    self.lowercase_index_name = index_name.lower()
    self.doc_type = doc_type
    _client = Client()
    try:
      self.index = _client.index(index_name=self.index_name)
      return self.index
    except Exception as e:
      print('Algolia: Couldn\'t connect to index "' + self.index_name + '". ', e)
      sentry.captureException()
      return None

  def get_index_name(self, search_service: str='elasticsearch'):
    if search_service == 'algolia':
      return self.index_name
    else:
      return self.lowercase_index_name

  def get_size(self, search_service: str='elasticsearch'):
    stats = es_client.IndicesClient(es).stats(index=self.get_index_name('elasticsearch'))
    size = stats.get('_all', {}).get('primaries', {}).get('docs', {}).get('count', None)
    return size

  def create_index(self):
    # ElasticSearch Only
    # @TODO: Handle case where index already exists
    es_client.IndicesClient(es).create(index=self.get_index_name('elasticsearch'))
    return self.get_index_name('elasticsearch')

  def search(self, query: str='', params: dict=None, search_service: str='elasticsearch', size: int=10):
    if not query:
      query = ''
    if not len(query) and params and 'query' in params and params['query']:
      query = params['query']
    try:
      if search_service == 'algolia' and UsingAlgolia:
        print('Searching Algolia!')
        return self.index.search(query, params)
      else:
        print('Searching ElasticSearch!')
        # @TODO: configure search and insert query (NOW DONE???)
        # body = _params_to_query_dsl(params)
        body = _params_to_query_dsl()
        pp.pprint('body')
        pp.pprint(body)
        start_time = time.time()
        print('Time of Sending ES Request: ', datetime.datetime.now())
        if query and len(query):
          print('mode 1')
          res = es.search(index=self.get_index_name('elasticsearch'), q=query, body=body, size=size)
        elif params and 'filters' in params:
          print('mode 2')
          res = es.search(index=self.get_index_name('elasticsearch'), q=params['filters'], body=body, size=size)
        else:
          print('mode 3')
          res = es.search(index=self.get_index_name('elasticsearch'), body=body, size=size)
        print('Time of Receiving ES Result:', datetime.datetime.now())
        end_time = time.time()
        try:
          duration = float(int((end_time - start_time) * 1000)) / 1000
          print('-- DURATION --', duration)
          mp.track('admin', 'ElasticSearch Response', {
            'duration': duration,
            'query': query,
            'params': params,
            'size': size,
            'environment': 'local' if 'HOME' in os.environ and os.environ['HOME'] == '/Users/jeremy' else 'production',
          })
        except Exception as e:
          traceback.print_exc(file=sys.stdout)
          sentry.captureException()
        print('-- START OF RES --')
        pp.pprint(json.dumps(res)[:500])
        print('-- END OF RES --')
        return {
          'hits': [_transform_from_elasticsearch(self.doc_type, hit['_source'], id=hit['_id']) for hit in res['hits']['hits']]
        }
    except Exception as e:
      print(search_service + ': Couldn\'t search for records in index "' + self.get_index_name('elasticsearch') + '". ', e)
      sentry.captureException()
      return None

  def get(self, objectID: str=None, objectIDs: list=None, allowFail: bool=False, search_service: str='elasticsearch'):
    # allowFail should only be True if it's fine for the object not to be found
    if not objectID and (not objectIDs or not len(objectIDs)):
      return None
    if objectIDs and len(objectIDs):
      # Fetching multiple objects
      # @TODO: ElasticSearch for multiple objects
      try:
        return self.index.get_objects(objectIDs)
      except Exception as e:
        print('Algolia: Couldn\'t get records from index "' + self.get_index_name('algolia') + '". ', e)
        sentry.captureException()
        return None
    else:
      if search_service == 'algolia' and UsingAlgolia:
        try:
          return self.index.get_object(objectID)
        except Exception as e:
          if allowFail:
            print('Algolia: Didn\'t find record in index, but this is OK so not throwing error')
          else:
            print('Algolia: Couldn\'t get record from index "' + self.get_index_name('algolia') + '". ', e)
            sentry.captureException()
          return None
      else:
        try:
          exists = es.exists(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, id=objectID)
          if exists:
            res = es.get(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, id=objectID)
            print('From ElasticSearch:')
            res = _transform_from_elasticsearch(self.doc_type, res['_source'], id=res['_id'])
            pp.pprint(res)
            return res
          else:
            print('From ElasticSearch: record from index "' + self.get_index_name('elasticsearch') + '" doesn\'t exist. ')
            return None
        except Exception as e:
          traceback.print_exc(file=sys.stdout)
          sentry.captureException()
          print('ElasticSearch: Couldn\'t get record from index "' + self.get_index_name('elasticsearch') + '". ', e)

  def browse(self, params=None, search_service: str='elasticsearch'):
    # @TODO: Add ElasticSearch here
    if search_service == 'algolia':
      try:
        if params:
          browsed = self.index.browse_all(params)
        else:
          browsed = self.index.browse_all()
        return [hit for hit in browsed]
      except Exception as e:
        print('Algolia: Couldn\'t browse index "' + index_name + '". ', e)
        sentry.captureException()
        return None
    else:
      # @NOTE: 10,000 is the maximum number of results in an ElasticSearch search
      #        We could use scroll() to get more results
      search_results = self.search(params=params, search_service=search_service, size=10000)
      if not search_results or 'hits' not in search_results:
        return None
      browsed = search_results['hits']
      print('browsed')
      pp.pprint(browsed[:5])
      return browsed

  def add(self, toAdd):
    record = None
    records = None
    if type(toAdd) == dict:
      record = toAdd
    elif type(toAdd) == list:
      records = toAdd
    if not record and not records:
      return None
    result = None
    if UsingAlgolia:
      try:
        if records:
          result = self.index.add_objects(records)
        else:
          result = self.index.add_object(record)
      except Exception as e:
        print('Algolia: Couldn\'t add record(s) to index "' + self.get_index_name('algolia') + '". ', e)
        sentry.captureException()
    try:
      if records:
        records = [_transform_to_elasticsearch(self.doc_type, dict(record)) for record in records]
        if result and 'objectIDs' in result:
          body = ['{ "index" : { "_id" : "' + result['objectIDs'][i] + '" } }\n' + json.dumps(record) for i, record in enumerate(records)]
        else:
          body = ['{ "index" : {' + (records[i]['objectID'] if 'objectID' in records[i] and records[i]['objectID'] else '') + '} }\n' + json.dumps(record) for i, record in enumerate(records)]
        body = '\n'.join(body)
        res = es.bulk(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, body=body)
      else:
        body = _transform_to_elasticsearch(self.doc_type, dict(record))
        if (result and 'objectID' in result) or ('objectID' in record and record['objectID']):
          print('Using objectID:', result['objectID'] if result and 'objectID' in result else record['objectID'])
          print(result)
          res = es.index(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, id=(result['objectID'] if result and 'objectID' in result else record['objectID']), body=body)
        else:
          res = es.index(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, body=body)
      print('ElasticSearch Success:')
      pp.pprint(res)
      if not UsingAlgolia:
        result = _transform_elasticsearch_result(res)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t add record(s) to index "' + self.get_index_name('elasticsearch') + '". ', e)
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
        if UsingAlgolia:
          result = self.index.save_objects(records)
      else:
        if 'objectID' not in record:
          print('Record must contain objectID')
          return None
        if UsingAlgolia:
          result = self.index.save_object(record)
    except Exception as e:
      print('Algolia: Couldn\'t save record(s) to index "' + self.get_index_name('algolia') + '". ', e)
      sentry.captureException()
      return None
    if not UsingAlgolia:
      result = None
    try:
      if records:
        body = [_transform_to_elasticsearch(self.doc_type, dict(record)) for record in records]
        body = ['{ "index" : { "_id" : "' + records[i]['objectID'] + '" } }\n' + json.dumps(record) for i, record in enumerate(body)]
        body = '\n'.join(body)
        res = es.bulk(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, body=body)
      else:
        body = _transform_to_elasticsearch(self.doc_type, dict(record))
        res = es.index(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, id=record['objectID'], body=body)
      print('ElasticSearch Success:')
      if not UsingAlgolia:
        result = _transform_elasticsearch_result(res)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t save record(s) to index "' + self.get_index_name('elasticsearch') + '". ', e)
    return result

  def partial_update(self, record: dict):
    result = None
    if UsingAlgolia:
      try:
        # @TODO: Do we need to account for multiple objects here too?
        result = self.index.partial_update_object(record)
      except Exception as e:
        sentry.captureException()
        print('Algolia: Couldn\'t save record to index "' + self.get_index_name('algolia') + '". ', e)
    try:
      body = _transform_to_elasticsearch(self.doc_type, dict(record))
      res = es.index(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, id=result['objectID'], body=body)
      if not UsingAlgolia:
        result = _transform_elasticsearch_result(res)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t update record in index "' + self.get_index_name('elasticsearch') + '". ', e)
    return result

  def delete(self, objectID: str=None):
    if not objectID:
      return None
    result = None
    try:
      result = self.index.delete_object(objectID)
    except Exception as e:
      sentry.captureException()
      print('Algolia: Couldn\'t delete record from index "' + self.get_index_name('algolia') + '". ', e)
    try:
      res = es.delete(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type, id=objectID)
      if not UsingAlgolia:
        result = _transform_elasticsearch_result(res)
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t delete record from index "' + self.get_index_name('elasticsearch') + '". ', e)
    return result

  def delete_by_query(self, params: dict=None):
    # @NOTE: Doesn't return anything standardised yet (different things for Algolia and ElasticSearch)
    if not params or not len(params) or (('query' not in params or not len (params['query'])) and ('filters' not in params or not len (params['filters']))):
      # This makes sure that we don't delete everything! (I.e. that either params['query'] or params['filter'] exists and is non-empty)
      return None
    result = None
    if UsingAlgolia:
      try:
        result = self.index.delete_by(params=params)
      except Exception as e:
        print('Algolia: Couldn\'t delete records from index "' + self.get_index_name('algolia') + '". ', e)
        sentry.captureException()
    try:
      body = _params_to_query_dsl(params)
      res = es.delete_by_query(index=self.get_index_name('elasticsearch'), body=body)
      if not UsingAlgolia:
        result = res # @TODO: transform this result
    except Exception as e:
      traceback.print_exc(file=sys.stdout)
      sentry.captureException()
      print('ElasticSearch: Couldn\'t delete records from index "' + self.get_index_name('elasticsearch') + '". ', e)
    return result

  def get_index_properties(self):
    """This is now interpreted as get_settings() for Algolia and get_mapping() for ElasticSearch.
    It returns both, as {
      'algolia': {},
      'elasticsearch': {}
    }
    """
    algolia_settings = None
    elasticsearch_mapping = None
    if UsingAlgolia:
      try:
        algolia_settings = self.index.get_settings()
      except Exception as e:
        print('Algolia: Couldn\'t get settings from index "' + self.get_index_name('algolia') + '". ', e)
        sentry.captureException()
    try:
      elasticsearch_mapping = es_client.IndicesClient(es).get_mapping(index=self.get_index_name('elasticsearch'), doc_type=self.doc_type)
    except Exception as e:
      print('ElasticSearch: Couldn\'t get settings from index "' + self.get_index_name('elasticsearch') + '". ', e)
      sentry.captureException()
    properties = {
      'algolia': algolia_settings,
      'elasticsearch': elasticsearch_mapping
    }
    return properties

  def set_index_properties(self, properties: dict):
    """This is now interpreted as set_settings() for Algolia and set_mapping() for ElasticSearch
    It sets both, and expects {
      algolia: {},
      elasticsearch: {}
    }
    """
    # @TODO: Return something
    if not properties:
      return None
    if UsingAlgolia and 'algolia' in properties:
      algolia_settings = properties.algolia
      try:
        self.index.set_settings(algolia_settings)
      except Exception as e:
        print('Algolia: Couldn\'t set settings for index "' + self.get_index_name('algolia') + '". ', e)
        sentry.captureException()
    # @NOTE: templates do this for us automatically so currently not bothering to set mappings manually
    # if 'elasticsearch' in properties:
    #   elasticsearch_mapping = properties['elasticsearch']
    #   try:
    #     es_client.IndicesClient(es).set_mapping(index='explaain__cards', doc_type='card', body=elasticsearch_mapping)
    #   except Exception as e:
    #     print('ElasticSearch: Couldn\'t set settings for index "' + self.get_index_name('elasticsearch') + '". ', e)
    #     sentry.captureException()



class Organisations(Index):
  def __init__(self):
    self.init_index(index_name='organisations', doc_type='organisation')

class Sources(Index):
  def __init__(self):
    self.init_index(index_name='sources', doc_type='source')

class Users(Index):
  def __init__(self):
    self.init_index(index_name='users', doc_type='user')

class Cards(Index):
  def __init__(self, organisationID):
    self.init_index(index_name=organisationID + '__Cards', doc_type='card')

class Files(Index):
  def __init__(self, organisationID):
    self.init_index(index_name=organisationID + '__Files', doc_type='file')


def _transform_to_elasticsearch(doc_type: str=None, obj: dict=None):
  # NOTE: 'objectID' gets deleted here so should have already been extracted to use as '_id'
  if 'objectID' in obj:
    del(obj['objectID'])
    # Stuff below is just various hacks to fix issues
  if doc_type and doc_type == 'card':
    # for key in ['created', 'modified']:
    #   if key in obj and obj[key] and isinstance(obj[key], int):
    #     if obj[key] < 10000000000:
    #       obj[key] = obj[key] * 1000
    if 'files' in obj:
      del(obj['files'])
  return obj

def _transform_from_elasticsearch(doc_type: str=None, obj: dict=None, id: str=None):
  if id and ('objectID' not in obj or not obj['objectID']):
    obj['objectID'] = id
    # Currently just various hacks to fix issues - we'll want to remove this sooner than _transform_to_elasticsearch()
  if doc_type and doc_type == 'card':
    # for key in ['created', 'modified']:
    #   if key in obj and obj[key] and isinstance(obj[key], int):
    #     if obj[key] > 10000000000:
    #       obj[key] = int(obj[key] / 1000)
    if 'files' in obj:
      del(obj['files'])
  return obj

def _transform_elasticsearch_result(res: dict=None):
  if not res:
    return None
  if 'items' in res:
    return {
      'objectIDs': [item['index']['_id'] for item in res['items']],
    }
  else:
    return {
      'objectID': res['_id']
    }

def _params_to_query_dsl(params: dict=None):
  # Currently only handles term-based filters (i.e. not ranges, text searches...)
  # Only handles filters separated by 'AND'
  # Assumes each value is in "quotes"
  # if not params:
  #   return None
  if params and 'filters' in params:
    filters = params['filters'].split(' AND ')
    filter = [{
      'term': { f.split(':')[0].strip(): ''.join(f.split(':')[1].strip().split('"')) }
    } for f in filters]
    query = {
      'query': {
        'bool': {
          'filter': filter
        }
      }
    }
  else:
    query = {
      'query': {
        'match_all': {}
      }
    }
  return query


# # Sources()
# print(Cards('explaain').get(objectID='450006879348', search_service='elasticsearch'))
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


# print(card)

# pp.pprint(_transform_to_elasticsearch(card))

#
# res = es.search(index='explaain__cards', q='darren', body={'query': {'match_all': {}}})
# res = es_client.IndicesClient(es).get(index='explaain__cards')
# res = es_client.IndicesClient(es).get(index='testingtesting__cards')
# pp.pprint(res)

# template_type = 'cards'
# template = templates.get_template(template_type)
# pp.pprint(template)
# #
# pp.pprint(es_client.IndicesClient(es).put_template(name=template_type, body=template))
# pp.pprint(es_client.IndicesClient(es).get_template(name=template_type))
# pp.pprint(es_client.IndicesClient(es).get_mapping(index='financialtimes__cards', doc_type='card'))
# res = es_client.IndicesClient(es).put_mapping(index='explaain__cards', doc_type='card', body=template['mappings']['card'])

# res = es.get(index='explaain__cards', doc_type='card', id='450006879348')

# pp.pprint(res)
# pp.pprint(Client().list_indices())
# pp.pprint(es_client.IndicesClient(es).delete('explaain__cards'))
# pp.pprint(es_client.IndicesClient(es).delete('explaain__files'))
# pp.pprint(es_client.IndicesClient(es).delete(index='Guzel_Akhatova_29560673__Cards'))
# pp.pprint([index['name'] + ': ' + str(index['entries']) for index in Client().list_indices()['items']])



# card = {
#    'created': 1516125053,
#    'title': 'Testing Card 8',
#    'description': 'To Test or Not To Test',
#    'modified': 1522746873,
#    'modifier': 'Jeremy Tester',
#    'organisationID': 'explaain',
#    # 'objectID': '11678',
# }
# card2 = {
#    'created': 1516125053,
#    'title': 'Testing Card 9',
#    'description': 'To Test or Not To Test',
#    'modified': 1522746873,
#    'modifier': 'Jeremy Tester',
#    'organisationID': 'explaain',
#    # 'objectID': '14576',
# }
#
# pp.pprint(Cards('testingtesting').add([card, card2]))
