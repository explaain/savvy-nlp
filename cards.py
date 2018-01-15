#!/usr/bin/env python
import xmltodict
import urllib

def generateCardData(req):
  print(req)
  url = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryString=' + urllib.parse.quote_plus(req['query'])
  print(url)
  read = urllib.request.urlopen(url).read()
  data = xmltodict.parse(read)
  return data
