#!/usr/bin/env python
import io, pprint, zipfile
from .formats import xml_doc as xmlDoc

pp = pprint.PrettyPrinter(indent=1, width=160)

def getExportParams(fileData):
  return {
    'type': 'retrieve'
  }

def fileToCardData(exportedFile):
  xmlContent = fileToContent(exportedFile)
  chunkHierarchy = xmlDoc.getContentArray(xmlContent)
  return chunkHierarchy

def fileToContent(exportedFile):
  content = exportedFile.contents().content
  z = zipfile.ZipFile(io.BytesIO(content))
  fileList = z.infolist()
  docs = [f for f in fileList if f.filename == 'word/document.xml'] # or f.filename == 'word/numbering.xml'] # or f.filename == 'word/styles.xml' or f.filename == 'word/setting.xml' or f.filename == 'word/theme1.xml' or f.filename == 'word/document.xml.rels'] # or 'xl' in f.filename]
  print(len(docs))
  xmlContent = []
  for doc in docs:
    xmlContent.append(z.read(doc).decode('utf-8'))
  if len(xmlContent):
    return xmlContent[0]
  else:
    return ''
