# @TODO: Crawl entire site using https://docs.scrapy.org/en/latest/topics/spiders.html#sitemapspider
import pprint
from .formats import html
from algoliasearch import algoliasearch

pp = pprint.PrettyPrinter(indent=4)

client = algoliasearch.Client('D3AE3TSULH', '1b36934cc0d93e04ef8f0d5f36ad7607') # This API key allows everything

def listFiles(accountInfo):
  if not accountInfo or not 'organisationID' in accountInfo or not 'accountID' in accountInfo:
    return None
  algoliaScrapedIndex = client.init_index(accountInfo['organisationID'] + '__Scraped')
  print(accountInfo['organisationID'] + '__Scraped')
  print('source:"' + accountInfo['accountID'] + '"')
  files = [hit for hit in algoliaScrapedIndex.browse_all({'filters': 'source:"' + accountInfo['accountID'] + '"'})]
  pp.pprint(files)
  return files

def getFile(accountInfo, fileID):
  if not accountInfo or not 'organisationID' in accountInfo or not fileID or not len(fileID):
    return None
  algoliaScrapedIndex = client.init_index(accountInfo['organisationID'] + '__Scraped')
  f = algoliaScrapedIndex.get_object(fileID)
  pp.pprint(f)
  return f

def getFileContent(accountInfo, fileID):
  f = getFile(accountInfo, fileID)
  if f and 'content' in f:
    print(f['content'])
    return f['content']
  else:
    return None

def getContentForCards(accountInfo, fileID):
  content = getFileContent(accountInfo, fileID)
  contentArray = html.getContentArray(content)
  return contentArray

def getServiceByFileType(fileType):
  return None


# TESTING

# listFiles({'organisationID': 'explaain', 'accountID': 'https://sites.google.com/explaain.com'})

# getFile({'organisationID': 'explaain', 'accountID': 'https://sites.google.com/explaain.com'},
#   'https://sites.google.com/explaain.com/ourfirstwiki/blog')

# getFileContent({'organisationID': 'explaain', 'accountID': 'https://sites.google.com/explaain.com'},
#   'https://sites.google.com/explaain.com/ourfirstwiki/blog')





# @TODO: Figure out whether to use this code for getting stuff from Scrapy Cloud:
#
# from scrapinghub import ScrapinghubClient
#
# apikey = '6a11dba2d8494b1aac43f045fc65906d'
# client = ScrapinghubClient(apikey)
#
# project = client.get_project('292495')
# spider = project.spiders.get('gsites')
# job = spider.jobs.get(spider.key + '/' + str(spider.jobs.count()))
# for item in job.items.iter():
#   print(html.getContentArray(item['main']))




# getFile({
#   'organisationID': 'explaain',
#   'accountID': '282782204'
# }, 'F1UVWb2gWfAQZO4FbkhySjqnnu6W2YVHAh2qAVb-bbleYPrNzGv-Re5xozb8UNKXi')
