#!/usr/bin/env python
import io, pprint, zipfile
from .formats import xml_doc

pp = pprint.PrettyPrinter(indent=1, width=160)

def getExportParams(fileData, type: str = 'getContent'):
  print("fileData['mimeType']")
  print(fileData['mimeType'])
  mimeTypes_we_can_export = [
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.google-apps.document',
    'application/vnd.google-apps.spreadsheet',
    'application/vnd.google-apps.presentation',
  ]
  if fileData and 'mimeType' in fileData and fileData['mimeType'] and fileData['mimeType'] in mimeTypes_we_can_export:
    return {
      'type': 'retrieve'
    }
  else:
    return None

def fileToCardData(exportedFile):
  xmlContent = fileToContent(exportedFile)
  chunkHierarchy = xml_doc.getContentArray(xmlContent)
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
