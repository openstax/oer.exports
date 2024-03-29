"""
Copyright (c) 2013 Rice University



"""

import os
import sys
from StringIO import StringIO
from lxml import etree
from tempfile import mkstemp
import subprocess

try:
  import pkg_resources
  resource_filename = pkg_resources.resource_filename
except ImportError:
  def resource_filename(dir, file):
    return os.path.join(os.getcwd(), dir, file)

### We use BOTH inkscape AND imagemagick (convert) because:
# Only inkscape can load the STIX fonts from the OS (imagemagick's SVG libs don't)
# Only imagemagick allows changing the color depth of an image (math/SVG use 8 bits)
#

# Instead of inkscape, use rsvg
INKSCAPE_BIN = '/Applications/Inkscape.app/Contents/Resources/bin/inkscape'
if not os.path.isfile(INKSCAPE_BIN):
  INKSCAPE_BIN = 'inkscape'

CONVERT_BIN = 'convert'

# Change the max recursion depth because the Astronomy book has m59999 which
# contains a large table of planets and moons and this chokes in that case
etree.XSLT.set_global_max_depth(4000) # Default is 3000


# http://lxml.de/xpathxslt.html
def makeXsl(filename):
  """ Helper that creates a XSLT stylesheet """
  path = resource_filename("xsl", filename)
  #print "Loading resource: %s" % path
  xml = etree.parse(path)
  return etree.XSLT(xml)

COLLXML_PARAMS = makeXsl('collxml-params.xsl')
COLLXML2DOCBOOK_XSL = makeXsl('collxml2dbk.xsl')

DOCBOOK_CLEANUP_XSL = makeXsl('dbk-clean-whole.xsl')
DOCBOOK_NORMALIZE_PATHS_XSL = makeXsl('dbk2epub-normalize-paths.xsl')
DOCBOOK_NORMALIZE_GLOSSARY_XSL = makeXsl('dbk-clean-whole-remove-duplicate-glossentry.xsl')



NAMESPACES = {
  'xhtml':'http://www.w3.org/1999/xhtml',
  'c'  :'http://cnx.rice.edu/cnxml',
  'svg':'http://www.w3.org/2000/svg',
  'mml':'http://www.w3.org/1998/Math/MathML',
  'db' :'http://docbook.org/ns/docbook',
  'xi' :'http://www.w3.org/2001/XInclude',
  'col':'http://cnx.rice.edu/collxml',
  'cmlnle': 'http://katalysteducation.org/cmlnle/1.0',
}


# For SVG Cover image
DBK2SVG_COVER_XSL = makeXsl('dbk2svg-cover.xsl')
COLLECTION_COVER_PREFIX='_collection_cover'


# Used for loading collection/module from the filesystem
MODULES_XPATH = etree.XPath('//col:module/@document', namespaces=NAMESPACES)
IMAGES_XPATH = etree.XPath('//c:*/@src[not(starts-with(.,"http:"))]', namespaces=NAMESPACES)

def _reduce_png(pngData):
  strCmd = '-compose Copy_Opacity -depth 8 +dither -quality 100 png:/dev/stdin png:-'.split()
  strCmd.insert(0, CONVERT_BIN)
  p = subprocess.Popen(strCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
  pngReduced, strError = p.communicate(pngData)
  return pngReduced, strError

def svg2png(svgStr):
  # Can't just use stdout because Inkscape outputs text to stdout _and_ stderr
  strCmd = ['rsvg-convert', '-d', '96', '-p', '96' ]
  p = subprocess.Popen(strCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
  pngData, strError = p.communicate(svgStr)

  pngReduced, strError = _reduce_png(pngData)
  return pngReduced

# From http://stackoverflow.com/questions/2932408/
def svg2png_inkscape(svgStr):
  # Can't just use stdout because Inkscape outputs text to stdout _and_ stderr
  fd, pngPath = mkstemp(suffix='.png')
  # Can't just use stdout because Inkscape outputs text to stdout _and_ stderr
  strCmd = [INKSCAPE_BIN, '--without-gui', '-f', '/dev/stdin', '--export-png=%s' % pngPath]
  p = subprocess.Popen(strCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
  _, strError = p.communicate(svgStr)
  pngFile = open(pngPath)
  pngData = pngFile.read()
  pngFile.close()
  os.close(fd)
  os.remove(pngPath)

  pngReduced, strError = _reduce_png(pngData)
  return pngReduced

def dbk2cover(dbk, filesDict, svg2pngFlag=True):
  newFiles = {}
  if ('%s.png' % COLLECTION_COVER_PREFIX) in filesDict:
    return filesDict['%s.png' % COLLECTION_COVER_PREFIX], newFiles

  if ('%s.svg' % COLLECTION_COVER_PREFIX) in filesDict:
    svgStr = filesDict['%s.svg' % COLLECTION_COVER_PREFIX]
  else:
    svg = transform(DBK2SVG_COVER_XSL, dbk)
    svgStr = etree.tostring(svg)

  newFiles['cover.svg'] = svgStr

  if svg2pngFlag:
    png = svg2png_inkscape(svgStr)
    return png, newFiles
  else:
    return svg, newFiles

def transform(xslDoc, xmlDoc):
  """ Performs an XSLT transform and parses the <xsl:message /> text """
  ret = xslDoc(xmlDoc)
  for entry in xslDoc.error_log:
    # TODO: Log the errors (and convert JSON to python) instead of just printing
    print entry
  return ret


### The following are methods that load up files on the filesysteme into memory

def loadModule(moduleDir):
  """ Given a directory of files (containing an index.cnxml)
      load it into memory """
  # Try autogenerated CNXML 1st
  cnxmlPath = os.path.join(moduleDir, 'index_auto_generated.cnxml')
  if not os.path.exists(cnxmlPath):
    cnxmlPath = os.path.join(moduleDir, 'index.cnxml')
  cnxmlStr = open(cnxmlPath).read()
  cnxml = etree.parse(StringIO(cnxmlStr))
  files = {}
  for f in IMAGES_XPATH(cnxml):
    try:
      data = open(os.path.join(moduleDir, f)).read()
      files[f] = data
      #print >> sys.stderr, "LOG: Image ADDED! %s %s" % (module, f)
    except IOError:
      print >> sys.stderr, "LOG: Image not found %s %s" % (os.path.basename(moduleDir), f)
  # If the dbk file has already been generated, include it
  dbkPath = os.path.join(moduleDir, 'index.included.dbk')
  if os.path.exists(dbkPath):
    dbkStr = open(dbkPath).read()
    files['index.included.dbk'] = dbkStr
  return (cnxml, files)


def loadCollection(dir):
  collxml = etree.parse(os.path.join(dir, 'collection.xml'))

  moduleIds = MODULES_XPATH(collxml)

  modules = {} # {'m1000': (etree.Element, {'file.jpg':'23947239874'})}
  allFiles = {}
  for moduleId in moduleIds:
    moduleDir = os.path.join(dir, moduleId)
    if os.path.isdir(moduleDir):
      cnxml, files = loadModule(moduleDir)
      for f in files:
        allFiles[os.path.join(moduleId, f)] = files[f]

      modules[moduleId] = (cnxml, files)

  return collxml, modules, allFiles


def log(temp_dir, filename, message, mode='a'):
  open(os.path.join(temp_dir, filename), mode).write(message)



class Progress(object):
  def __init__(self):
    self.stack = []
    pass

  def start(self, ticks, msg):
    self.stack.append({ 'done': 0, 'total': ticks + 1, 'msg': msg })
    self._log()

  def tick(self, msg):
    self.stack[-1]['done'] += 1
    self.stack[-1]['msg'] = msg
    if self.stack[-1]['done'] > self.stack[-1]['total']:
      import pdb; pdb.set_trace()
    self._log()

  def finish(self):
    self.stack[-1]['done'] = self.stack[-1]['total']
    self.stack[-1]['msg'] = 'Done'
    self._log()
    if self.stack[-1]['done'] != self.stack[-1]['total']:
      import pdb; pdb.set_trace()
    self.stack = self.stack[:-1]

  def _log(self):
    # Build up the percentage
    percent = 0.0
    weight = 1.0
    msg = []
    for p in self.stack:
      percent += weight * p['done'] / p['total']
      weight = weight * 1.0 / p['total']
      msg.append(p['msg'])

    # Discard the top-most message since it will never change
    if len(msg) > 1:
      msg = msg[1:]
    print >> sys.stderr, "STATUS: %3.2f%% %s" % (percent * 100, ': '.join(msg))
