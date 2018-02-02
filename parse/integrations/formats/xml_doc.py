import re, pprint, untangle

pp = pprint.PrettyPrinter(indent=1, width=160)

def getContentArray(xmlContent):
  xml = untangle.parse(xmlContent)
  textArray = []
  ongoingCounter = []
  xmlSearchTextInChildren(xml, 0, textArray, ongoingCounter, { 'parFormatting': False, 'hyperlink': False })
  for t in textArray:
    t['ranking'] = sum(t['allRankings'].values())
  textArray = [chunk for chunk in textArray if len(chunk['content'])]
  if toPrint['arrayOfPars']:
    pp.pprint(textArray)
  if toPrint['justScores']:
    for t in textArray:
      print(t['ranking'], t['content'])
  chunkHierarchy = getChunkHierarchy(textArray)
  chunkHierarchy = completeContent(chunkHierarchy)
  if toPrint['hierarchies']:
    pp.pprint(chunkHierarchy)
  if toPrint['hierarchyText']:
    print(chunksToPrint(chunkHierarchy, 0))
  return chunkHierarchy

def chunksToPrint(chunks, layer = 0):
  printArray = []
  for chunk in chunks:
    content = ''.join(chunk['content'])
    content = content[:80] + '...' if len(content) > 80 else content
    if 'title' in chunk:
      content = chunk['title'] + ': ' + content
    printArray += [('    ' * layer) + content]
    if 'chunks' in chunk:
      printArray += chunksToPrint(chunk['chunks'], layer + 1)
  return printArray

def xmlSearchTextInChildren(xml, level, dataPassedDown, ongoingCounter, context):
  children = xml.__dict__['children'] or xml['children']
  spacing = ''.join([' ' for l in range(level)])
  if children is not None:
    for child in children:
      child.context = dict(context) # Is NOT a deep copy
    for i, child in enumerate(children):
      if toPrint['elements']:
        print(spacing, child)
      if child._name == 'w_p':
        chunkData = {
          'content': [],
          'allRankings': {},
          'otherContext': {}
        }
      else:
        chunkData = dataPassedDown
      if child._name == 'w_tbl':
        child.context['table'] = True
      if 'cdata' in child.__dict__ and child.__dict__['cdata'] and not child.__dict__['cdata'].isspace() and child._name != 'w_instrText':
        dataPassedDown['content'].append(child.__dict__['cdata'].strip())
        if child.context['hyperlink']:
          dataPassedDown['content'][-1] = '[' + dataPassedDown['content'][-1] + '](' + child.context['hyperlink'] + ')'
      if child._name == 'w_numPr':
        chunkData['otherContext']['numbered'] = True
      if child._name == 'w_pPr':
        child.context['parFormatting'] = True
      if child.context['parFormatting']:
        ranking = getRanking(child)
        if sum(ranking.values()) != 0:
          dataPassedDown['allRankings'] = {**dataPassedDown['allRankings'], **ranking}
      if hasattr(child, 'w_instrText') and 'cdata' in child.w_instrText.__dict__ and 'HYPERLINK' in child.w_instrText.__dict__['cdata'] and i < len(children) - 1:
        p = re.compile('HYPERLINK \"(.*)\"')
        children[i+1].context['hyperlink'] = p.search(child.w_instrText.__dict__['cdata']).group(1)
      try:
        xmlSearchTextInChildren(child, level + 1, chunkData, ongoingCounter, child.context)
      except Exception as e:
        print(e)
      if child._name == 'w_p':
        for prop in ['w_sz']:
          if prop not in chunkData['allRankings'] and len(dataPassedDown) and prop in dataPassedDown[-1]['allRankings']:
            chunkData['allRankings'][prop] = dataPassedDown[-1]['allRankings'][prop]
        dataPassedDown.append(chunkData)


def getRanking(el):
  ranking = 0
  if 'table' in el.context:
    ranking = -40 # Hack for the Contract doc
  if el._name == 'w_numPr':
    ranking = -10
  if el._name == 'w_numId' and el._attributes['w:val'] == "8": # Purely a hack for Contract doc
    ranking = 11
  if el._name == 'w_ilvl':
    ranking = -10 * int(el._attributes['w:val'])
  if el._name == 'w_ind':
    ranking = -1 * int(el._attributes['w:left']) / 20
  if el._name == 'w_sz':
    ranking = int(el._attributes['w:val'])
  if el._name == 'w_pStyle':
    style = el._attributes['w:val']
    styles = {
      'Title': 800,
      'Subtitle': 600,
      'Heading1': 400,
      'Heading2': 300,
      'Heading3': 200,
      'Heading4': 100,
      'Heading5': 60,
      'Heading6': 40
    }
    if style in styles:
      ranking = styles[style]
  if el._name == 'w_b' and el._attributes['w:val'] == '1':
    ranking = 10
  return {
    el._name: ranking
  }

def getChunkHierarchy(textArray):
  chunks = []
  base = 0
  for i, chunk in enumerate(textArray):
    if chunk['ranking'] >= textArray[base]['ranking'] and i > 0:
      if textArray[i-1]['ranking'] == chunk['ranking']:
        chunks.append(textArray[i-1])
      else:
        myChunk = textArray[base]
        myChunk['chunks'] = getChunkHierarchy(textArray[base+1:i])
        chunks.append(myChunk)
      base = i
    if i == len(textArray)-1:
      if textArray[i]['ranking'] == textArray[base]['ranking']:
        chunks.append(textArray[i])
      else:
        myChunk = textArray[base]
        myChunk['chunks'] = getChunkHierarchy(textArray[base+1:])
        chunks.append(myChunk)
    # if chunk['ranking'] < baseRanking and base == 0:
    #   base = i
  # if len(chunks) == 0:
  #   chunks = textArray
  return chunks

# Joins content arrays and adds numbering
def completeContent(chunks, parentNumber=False):
  for i, chunk in enumerate(chunks):
    chunk['content'] = ' '.join(chunk['content'])
    number = parentNumber
    if 'numbered' in chunk['otherContext']:
      number = (str(number) + '.' if number else '') + str(i + 1)
      chunk['title'] = number # + ' ' + chunk['content']
    if 'chunks' in chunk:
      chunk['chunks'] = completeContent(chunk['chunks'], number)
  return chunks
