# python -c "import collectiondbk2pdf; print collectiondbk2pdf.__doStuff('./tests', 'modern-textbook');" > result.pdf

import sys
import os
try:
  import Image
except:
  from PIL import Image
from StringIO import StringIO
from tempfile import mkdtemp
import subprocess

from lxml import etree
import urllib2

import module2dbk
import collection2dbk
import util

DEBUG= 'DEBUG' in os.environ

BASE_PATH = os.getcwd()

# XSL files
DOCBOOK2XHTML_XSL=util.makeXsl('dbk2xhtml.xsl')
DOCBOOK_CLEANUP_XSL = util.makeXsl('dbk-clean-whole.xsl')

MODULES_XPATH = etree.XPath('//col:module/@document', namespaces=util.NAMESPACES)
IMAGES_XPATH = etree.XPath('//c:*/@src[not(starts-with(.,"http:"))]', namespaces=util.NAMESPACES)


def __doStuff(dir):
  collxml = etree.parse(os.path.join(dir, 'collection.xml'))

  moduleIds = MODULES_XPATH(collxml)

  modules = {} # {'m1000': (etree.Element, {'file.jpg':'23947239874'})}
  allFiles = {}
  for moduleId in moduleIds:
    print >> sys.stderr, "LOG: Starting on %s" % (moduleId)
    moduleDir = os.path.join(dir, moduleId)
    if os.path.isdir(moduleDir):
      cnxml, files = util.loadModule(moduleDir)
      for f in files:
        allFiles[os.path.join(moduleId, f)] = files[f]

      modules[moduleId] = (cnxml, files)

  dbk, newFiles = collection2dbk.convert(collxml, modules, svg2png=False, math2svg=True)
  allFiles.update(newFiles)
  return convert(dbk, allFiles)

def convert(dbk1, files):
  """ Converts a Docbook Element and a dictionary of files into a PDF. """
  tempdir = mkdtemp(suffix='-fo2pdf')

  # Step 0 (Sprinkle in some index hints whenever terms are used)
  # termsprinkler.py $DOCBOOK > $DOCBOOK2
  if DEBUG:
    open('temp-collection1.dbk','w').write(etree.tostring(dbk1,pretty_print=True))

  # Step 1 (Cleaning up Docbook)
  dbk2 = util.transform(DOCBOOK_CLEANUP_XSL, dbk1, tempdir=tempdir)
  if DEBUG:
    open('temp-collection2.dbk','w').write(etree.tostring(dbk2,pretty_print=True))

  # Step 2 (Docbook to XHTML)
  xhtml = util.transform(DOCBOOK2XHTML_XSL, dbk2, tempdir=tempdir)
  if DEBUG:
    open('temp-collection3.xhtml','w').write(etree.tostring(xhtml))

  return xhtml, files


def main():
  try:
    import argparse
    parser = argparse.ArgumentParser(description='Converts a a collection directory to an xhtml file and additional images')
    parser.add_argument('directory')
    parser.add_argument('-o', dest='output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    xhtml, files = __doStuff(args.directory)

    args.output.write(etree.tostring(xhtml))

  except ImportError:
    print "argparse is needed for commandline"

if __name__ == '__main__':
    sys.exit(main())
