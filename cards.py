#!/usr/bin/env python
import json
import pprint
import xmltodict
import urllib
import re

print(urllib.parse.quote_plus('asdasd'))

pp = pprint.PrettyPrinter(indent=2)

def generateCardData(req):
  print(req)
  lang = req['lang'] if 'lang' in req else 'en'
  if 'objectID' in req:
    data = generateFromID(req['objectID'], lang)
  elif 'sameAs' in req:
    data = generateFromSameAs(req['sameAs'], lang)
  elif 'query' in req:
    data = generateFromQuery(req['query'], lang)
  return data

def generateFromID(objectID, lang):
  # Other
  # url = 'https://en.wikipedia.org/w/api.php?action=parse&page=' + objectID + '&format=json'
  # read = urllib.request.urlopen(url).read()
  # print(read)
  # data = json.loads(read)['parse']
  # pp.pprint(data)
  # langlinks = data['langlinks']
  # print(langlinks)
  # url = [x['url'] for x in langlinks if 'lang' in x and x['lang'] == lang]
  # print(url)
  # sources = [
  #   {
  #     'type': 'source',
  #     'name': 'Wikipedia',
  #     'url': url
  #   }
  # ]
  # Content
  contentUrl = 'https://' + lang + '.wikipedia.org/w/api.php?action=query&titles=' + objectID + '&prop=revisions&rvprop=content&format=json&formatversion=2'
  print(contentUrl)
  read = urllib.request.urlopen(contentUrl).read()
  data = json.loads(read)
  title = data['query']['pages'][0]['title']
  content = data['query']['pages'][0]['revisions'][0]['content']
  content = wikiToContent(content, lang)
  description = contentToDescription(content)

  card = {
    'title': title,
    'description': description
  }
  pp.pprint(card)
  return data

def generateFromSameAs(sameAs, lang):
  objectID = sameAs.split('/')[-1]
  return generateFromID(objectID)

def generateFromQuery(query, lang):
  url = 'http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryString=' + urllib.parse.quote_plus(query)
  print(url)
  read = urllib.request.urlopen(url).read()
  data = xmltodict.parse(read)
  return data

def contentToDescription(description):
  maxChars = 300
  description = re.sub(r'(\n)+', ' ', description)
  description = re.sub(r' +', ' ', description)
  description = re.sub(r' *\([^)]*\) *', ' ', description) #.replace(r' \.', '.')
  sentences = re.split(r'\. (?=[A-Z])', description)
  sentences = [(s.strip() + '.').strip() for s in sentences]
  # var sentences = description.split(/\. (?=[A-Z])/).map(s => s + '.')
  while len(' '.join(sentences)) > maxChars and len(sentences) > 1:
    sentences.pop()
  description = ' '.join(sentences)
  description = description.strip()
  # print(description)
  return description

def wikiToContent(wiki, lang):
  content = unhtml(1, wiki)
  content = parseText(content, lang)
  content = re.sub(r'{{(.|\n)*?}}', '', content)
  content = re.sub(r'\(.*?\)', '', content)
  content = re.sub(r'\n\n(\n)+', ' ', content)
  print(content[:2500])
  return content

# Using help from: https://pastebin.com/idw8vQQK

def parseText(wiki, lang):
  textLang = {}
  textLang['en'] = {
    'IPA': 'IPA',
    'Lang': 'Lang',
    'Category': 'Category',
    'Image': 'Image',
    'File': 'File',
  }
  textLang['no'] = {
    'IPA': 'IPA', # ???
    'Lang': 'Lang', # ???
    'Category': 'Category', # ???
    'Image': 'Image', # ???
    'File': 'Fil',
  }
  print(wiki[:1500])
  wiki = wiki[:1500]
  wiki = re.sub(r'(?i)\{\{' + textLang[lang]['IPA'] + '(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
  wiki = re.sub(r'(?i)\{\{' + textLang[lang]['Lang'] + '(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
  wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
  wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
  wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
  wiki = re.sub(r'(?i)\[\[' + textLang[lang]['Category'] + ':[^\[\]]*?\]\]', '', wiki)
  wiki = re.sub(r'(?i)\[\[' + textLang[lang]['Image'] + ':[^\[\]]*?\]\]', '', wiki)
  wiki = re.sub(r'(?i)\[\[' + textLang[lang]['File'] + ':[^\[\]]*?\]\]', '', wiki)
  print('\n\n\n1\n' + wiki)
  wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
  print('\n\n\n2\n' + wiki)
  wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
  print('\n\n\n3\n' + wiki)
  wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
  print('\n\n\n4\n' + wiki)
  wiki = re.sub(r'(?i)' + textLang[lang]['File'] + ':[^\[\]]*?', '', wiki)
  wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
  wiki = re.sub(r"''+", '', wiki)
  wiki = re.sub(r'(?m)^\*$', '', wiki)
  return wiki

def unhtml(self, html):
  """
  Remove HTML from the text.
  """
  html = re.sub(r'(?i)&nbsp;', ' ', html)
  html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
  html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
  html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
  html = re.sub(r'(?m)<.*?>', '', html)
  html = re.sub(r'(?i)&amp;', '&', html)

  return html

generateFromID('Barack_Obama', 'no')

# myText = '"{{redirect|Einstein|the musicologist|Alfred Einstein|other people|Einstein (surname)|other uses|Albert Einstein (disambiguation)|and|Einstein (disambiguation)}} {{pp-semi-indef}} {{pp-move-indef}} {{Good article}} {{Infobox scientist | name = Albert Einstein | pronounce = {{IPAc-en|ˈ|aɪ|n|s|t|aɪ|n}}<ref>{{cite book|last=Wells|first=John|authorlink=John C. Wells|title=Longman Pronunciation Dictionary|publisher=Pearson Longman|edition=3rd|date=3 April 2008|isbn=1-4058-8118-6}}</ref> {{IPA-de|ˈalbɛɐ̯t ˈaɪnʃtaɪn|lang|Albert Einstein german.ogg}} | image = Einstein 1921 by F Schmutzer - restoration.jpg | caption = Albert Einstein in 1921 | birth_date = {{Birth date|df=yes|1879|3|14}} | birth_place = [[Ulm]], [[Kingdom of Württemberg]], [[German Empire]] | death_date = {{Death date and age|df=yes|1955|4|18|1879|3|14}} | death_place = {{nowrap|[[Princeton, New Jersey]], U.S.}} | children = [[Lieserl Einstein|"Lieserl" Einstein]] <br />[[Hans Albert Einstein]] <br />[[Einstein family#Eduard "Tete" Einstein (Albert\s son)|Eduard "Tete" Einstein]] | spouse = {{marriage|[[Mileva Marić]]<br>|1903|1919|end=div}}<br />{{nowrap|{{marriage|[[Elsa Löwenthal]]<br>|1919|1936|end=died}}<ref>{{cite book |editor-last=Heilbron |editor-first=John L. |title=The Oxford Companion to the History of Modern Science |url=https://books.google.com/books?id=abqjP-_KfzkC&pg=PA233 |date=2003 |publisher=Oxford University Press |isbn=978-0-19-974376-6 |page=233}}</ref>{{sfnp|Pais|1982|p=301}}}} | residence = Germany, Italy, Switzerland, Austria (present-day Czech Republic), Belgium, United States | citizenship = {{Plainlist| * Subject of the [[Kingdom of Württemberg]] during the German Empire <small>(1879–1896)</small><ref name=GEcitizen group=note>During the German Empire, citizenship were exclusively subject of one of the 27 \\Bundesstaaten\\</ref> * [[Statelessness|Stateless]] <small>(1896–1901)</small> * Citizen of [[Switzerland]] <small>(1901–1955)</small> * Austrian subject of the [[Austro-Hungarian Empire]] <small>(1911–1912)</small> * Subject of the [[Kingdom of Prussia]] during the German Empire <small>(1914–1918)</small><ref name=GEcitizen group=note/> * German citizen of the [[Free State of Prussia]] <small>([[Weimar Republic]], 1918–1933)</small> * Citizen of the United States <small>(1940–1955)</small> }} | fields = [[Physics]], [[philosophy]] | workplaces = {{Plainlist| * [[Swiss Patent Office]] ([[Bern]]) <small>(1902–1909)</small> * [[University of Bern]] <small>(1908–1909)</small> * [[University of Zurich]] <small>(1909–1911)</small> * [[Karl-Ferdinands-Universität|Charles University in Prague]] <small>(1911–1912)</small> * [[ETH Zurich]] <small>(1912–1914)</small> * [[Prussian Academy of Sciences]] <small>(1914–1933)</small> * [[Humboldt University of Berlin]] <small>(1914–1933)</small> * [[Kaiser Wilhelm Institute]] <small>(director, 1917–1933)</small> * [[German Physical Society]] <small>(president, 1916–1918)</small> * [[Leiden University]] <small>(visits, 1920)</small> * [[Institute for Advanced Study]] <small>(1933–1955)</small> * [[Caltech]] <small>(visits, 1931–1933)</small> * [[University of Oxford]] <small>(visits, 1931-1933)</small> }} | education = {{Plainlist| * [[ETH Zurich|Swiss Federal Polytechnic]] <small>(1896–1900; B.A., 1900)</small> * [[University of Zurich]] <small>(Ph.D., 1905)</small> }} | doctoral_advisor = [[Alfred Kleiner]] | thesis_title = {{lang|de|Eine neue Bestimmung der Moleküldimensionen}} (A New Determination of Molecular Dimensions) | thesis_url = http://e-collection.library.ethz.ch/eserv/eth:30378/eth-30378-01.pdf | thesis_year = 1905 | academic_advisors = [[Heinrich Friedrich Weber]] | influenced = {{Plainlist| * [[Ernst G. Straus]] * [[Nathan Rosen]] * [[Leó Szilárd]] }} | known_for = {{Plainlist| * [[General relativity]] * [[Special relativity]] * [[Photoelectric effect]] * [[Mass–energy equivalence|\\E=mc<sup>2</sup>\\ (Mass–energy equivalence)]] * [[Planck–Einstein relation|\\E=hf\\ (Planck–Einstein relation)]] * Theory of [[Brownian motion]] * [[Einstein field equations]] * [[Bose–Einstein statistics]] * [[Bose–Einstein condensate]] * [[Gravitational wave]] * [[Cosmological constant]] * [[Classical unified field theories|Unified field theory]] * [[EPR paradox]] * [[Ensemble interpretation]] * [[List of things named after Albert Einstein|List of other concepts]] }} | awards = {{Plainlist| * [[Barnard Medal for Meritorious Service to Science|Barnard Medal]] (1920) * [[Nobel Prize in Physics]] (1921) * [[Matteucci Medal]] (1921) * [[ForMemRS]] (1921)<ref name="frs" /> * [[Copley Medal]] (1925)<ref name="frs" /> * [[Gold Medal of the Royal Astronomical Society]] (1926) * [[Max Planck Medal]] (1929) * [[Time 100: The Most Important People of the Century|\\Time\\ Person of the Century]] (1999) }} | signature = Albert Einstein signature 1934.svg }} \\\Albert Einstein\\\ (14 March 1879&nbsp;– 18&nbsp;April 1955) was a German-born<!-- Please do not change this—see talk page and its many archives.--> [[theoretical physicist]]<ref name="Bio">{{cite web |url=http://nobelprize.org/nobel_prizes/physics/laureates/1921/einstein-bio.html |title=Albert Einstein&nbsp;– Biography |accessdate=7 March 2007 |publisher=[[Nobel Foundation]]| archiveurl= https://web.archive.org/web/20070306133522/http://nobelprize.org/nobel_prizes/physics/laureates/1921/einstein-bio.html| archivedate= 6 March 2007 <!--DASHBot-->| deadurl= no}}</ref> who developed the [[theory of relativity]], one of the two pillars of [[modern physics]] (alongside [[quantum mechanics]]).<ref name="frs">{{cite journal | last1 = Whittaker | first1 = E. | authorlink = E. T. Whittaker| doi = 10.1098/rsbm.1955.0005 | title = Albert Einstein. 1879–1955 | journal = [[Biographical Memoirs of Fellows of the Royal Society]] | volume = 1 | pages = 37–67 | date = 1 November 1955| jstor = 769242| doi-access = free}}</ref><ref name="YangHamilton2010">{{cite book|author1=Fujia Yang|author2=Joseph H. Hamilton|title=Modern Atomic and Nuclear Physics|date=2010|publisher=World Scientific|isbn=978-981-4277-16-7}}</ref>{{rp|274}} Einstein\s work is also known for its influence on the [[philosophy of science]].<ref>{{Citation |title=Einstein\s Philosophy of Science |url=http://plato.stanford.edu/entries/einstein-philscience/#IntWasEinEpiOpp |website=Stanford Encyclopedia of Philosophy |publisher=The Metaphysics Research Lab, Center for the Study of Language and Information (CSLI), Stanford University |editor-first=Don A. | editor-last=Howard |date=2014 |orig-year=First published 11 February 2004 |type=website |accessdate=2015-02-04}}</ref><ref>{{Citation |first=Don A. | last=Howard |title=Albert Einstein as a Philosopher of Science |url=http://www3.nd.edu/~dhoward1/vol58no12p34_40.pdf |format=PDF |date=December 2005 |journal=Physics Today |volume=58 |issue=12 |publisher=American Institute of Physics |pages=34–40 |via=University of Notre Dame, Notre Dame, IN, author\s personal webpage |accessdate=2015-03-08|bibcode=2005PhT....58l..34H |doi=10.1063/1.2169442 }}</ref> Einstein is best known by the general public for his [[mass–energy equivalence]] formula'
#
#
# a = unhtml(1, myText)
# print('aaaaa')
# print(a)
# b = parseText(a)
# print('bbbbb')
# print(b)
# c = re.sub(r'{{.*?}}', '', b)
# print('ccccc')
# print(c)
