#!/usr/bin/env python
import io, pprint, zipfile
from .formats import xml_doc

pp = pprint.PrettyPrinter(indent=1, width=160)

def getExportParams(fileData, type: str = 'getContent'):
  return {
    'type': 'retrieve'
  }

def fileToCardData(exportedFile):
  print('fileToCardData exportedFile')
  print(exportedFile)
  xmlContent = fileToContent(exportedFile)
  chunkHierarchy = xml_doc.getContentArray(xmlContent)
  return chunkHierarchy

def fileToContent(exportedFile):
  print('fileToContent exportedFile')
  print(exportedFile)
  content = exportedFile.contents().content
  print('\n\n\ncontent\n\n\n')
  z = zipfile.ZipFile(io.BytesIO(content))
  print('\n\n\nz\n\n\n')
  fileList = z.infolist()
  print('\n\n\nfileList\n\n\n')
  docs = [f for f in fileList if f.filename == 'word/document.xml'] # or f.filename == 'word/numbering.xml'] # or f.filename == 'word/styles.xml' or f.filename == 'word/setting.xml' or f.filename == 'word/theme1.xml' or f.filename == 'word/document.xml.rels'] # or 'xl' in f.filename]
  print(len(docs))
  xmlContent = []
  for doc in docs:
    xmlContent.append(z.read(doc).decode('utf-8'))
  print('\n\n\nxmlContent\n\n\n')
  if len(xmlContent):
    return xmlContent[0]
  else:
    return ''
