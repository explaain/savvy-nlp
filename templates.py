cards_template = {
  'index_patterns': ['*__cards'],
  'mappings': {
    'card': {
      'properties': {
        'cells': {
          'properties': {
            'content': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text',
              'analyzer': 'english',
            },
            'label': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text',
              'analyzer': 'english',
            },
            'objectID': {
              'type':'long'
            },
            'value': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text',
              'analyzer': 'english',
            }
          }
        },
        'context': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'created': {
          'type':'date',
          'format': 'epoch_second'
        },
        'creator': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'creatorID': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'description': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'entityTypes': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'fileFormat': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'fileID': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'fileTitle': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'fileType': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'fileUrl': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'format': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'hello': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'index': {
          'type':'long'
        },
        'integrationFields': {
          'properties': {
            'assignedTo': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text',
              'analyzer': 'english',
            },
            'escalation_level': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text'
            },
            'key': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text'
            },
            'module': {
              'properties': {
                'id': { 'type': 'long' },
                'name': {
                  'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
                  'type':'text'
                }
              }
            },
            'number': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text'
            },
            'priority': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text'
            },
            'priorityData': {
              'properties': {
                'id': { 'type': 'long' },
                'type': {
                  'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
                  'type':'text'
                }
              }
            },
            'projectID': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text'
            },
            'projectName': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text',
              'analyzer': 'english',
            },
            'reproducible': {
              'properties': {
                'id': { 'type': 'long' },
                'type': {
                  'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
                  'type':'text'
                }
              }
            },
            'status': {
              'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
              'type':'text'
            },
            'statusData': {
              'properties': {
                'colorcode': {
                  'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
                  'type':'text'
                },
                'id': {
                  'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
                  'type':'text'
                },
                'type': {
                  'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
                  'type':'text'
                }
              }
            }
          }
        },
        'isFile': {
          'type':'boolean'
        },
        'listCards': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'listItems': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'mimeType': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'modified': {
          'type':'date',
          'format': 'epoch_second'
        },
        'modifier': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'modifierID': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'objectID': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'organisationID': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'service': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'source': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'subService': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'superService': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        },
        'title': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text',
          'analyzer': 'english',
        },
        'type': {
          'fields': { 'keyword': { 'type': 'keyword', 'ignore_above': 256 } },
          'type':'text'
        }
      }
    }
  },
  'settings': {
    'analysis': {
      'filter': {
        'english_stop': {
          'type':       'stop',
          'stopwords':  '_english_'
        },
        'english_keywords': {
          'type':       'keyword_marker',
          'keywords':   []
        },
        'english_stemmer': {
          'type':       'stemmer',
          'language':   'english'
        },
        'english_possessive_stemmer': {
          'type':       'stemmer',
          'language':   'possessive_english'
        }
      },
      'analyzer': {
        'english': {
          'tokenizer': 'standard',
          'filter': [
            'english_possessive_stemmer',
            'lowercase',
            'english_stop',
            'english_keywords',
            'english_stemmer'
          ]
        }
      }
    }
  }
}

files_template = {
  'index_patterns': ['*__files'],
  'mappings': {  'file': {   'properties': {   'created': {   'type': 'float'},
                 'fileFormat': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                                'type': 'keyword'}},
                                   'type': 'text'},
                 'mimeType': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                              'type': 'keyword'}},
                                 'type': 'text'},
                 'modified': {
                   'type':'date',
                   'format': 'epoch_second'
                 },
                 'rawID': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                           'type': 'keyword'}},
                              'type': 'text'},
                 'service': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                             'type': 'keyword'}},
                                'type': 'text'},
                 'source': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                            'type': 'keyword'}},
                               'type': 'text'},
                 'subService': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                                'type': 'keyword'}},
                                   'type': 'text'},
                 'superService': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                                  'type': 'keyword'}},
                                     'type': 'text'},
                 'title': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                           'type': 'keyword'}},
                              'type': 'text'},
                 'url': {   'fields': {   'keyword': {   'ignore_above': 256,
                                                         'type': 'keyword'}},
                            'type': 'text'}}}}}

def get_template(type: str=None):
  if not type:
    return None
  if type == 'cards':
    return cards_template
  if type == 'files':
    return files_template
