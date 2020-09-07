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
import time

from lxml import etree
import urllib2

import module2dbk
import collection2dbk
import util

BASE_PATH = os.getcwd()

# XSL files
DOCBOOK2XHTML_XSL=util.makeXsl('dbk2xhtml.xsl')
DOCBOOK_CLEANUP_XSL = util.makeXsl('dbk-clean-whole.xsl')
DEDUPSVG_XSL = util.makeXsl('xhtml-dedup-svg.xsl')
DEDUPREFS_XSL = util.makeXsl('dedup-references.xsl')

MODULES_XPATH = etree.XPath('//col:module/@document', namespaces=util.NAMESPACES)
IMAGES_XPATH = etree.XPath('//c:*/@src[not(starts-with(.,"http:"))]', namespaces=util.NAMESPACES)


def __doStuff(dir, verbose=False):
  p = util.Progress()
  tempdir = mkdtemp(suffix='-fo2pdf')
  dbk, allFiles = collection2dbk.load(p, dir, tempdir, verbose, svg2png=False, math2svg=True)
  return convert(p, dbk, allFiles, tempdir, verbose)

def convert(p, dbk1, files, tempdir, verbose=False):
  """ Converts a Docbook Element and a dictionary of files into a PDF. """

  # Step 0 (Sprinkle in some index hints whenever terms are used)
  # termsprinkler.py $DOCBOOK > $DOCBOOK2
  if verbose:
    open(os.path.join(tempdir, 'temp-collection1.dbk'),'w').write(etree.tostring(dbk1,pretty_print=False))

  p.start(3, 'Cleaning up Docbook')
  # Step 1 (Cleaning up Docbook)
  now = time.time()
  dbk2 = util.transform(DOCBOOK_CLEANUP_XSL, dbk1)
  if verbose:
    open(os.path.join(tempdir, 'temp-collection2.dbk'),'w').write(etree.tostring(dbk2,pretty_print=False))
  util.log(tempdir, 'benchmark.txt',
           '  Cleaning up Docbook: %.1fs\n' % (time.time() - now,))

  now = time.time()
  p.tick('Converting Docbook to HTML')
  # Step 2 (Docbook to XHTML)
  xhtml = util.transform(DOCBOOK2XHTML_XSL, dbk2)
  util.log(tempdir, 'benchmark.txt',
           '  Converting Docbook to html: %.1fs\n' % (time.time() - now,))

  now = time.time()
  p.tick('Dedup SVGs')
  xhtml_deduped = util.transform(DEDUPSVG_XSL, xhtml)
  util.log(tempdir, 'benchmark.txt',
           '  Dedup SVGs: %.1fs\n' % (time.time() - now,))

  now = time.time()
  p.tick('Cleaning up references')
  xhtml_dedupeder = util.transform(DEDUPREFS_XSL, xhtml_deduped)
  util.log(tempdir, 'benchmark.txt',
           '  Cleaning up references: %.1fs\n' % (time.time() - now,))

  return xhtml_dedupeder, files


def main():
  try:
    import argparse
    parser = argparse.ArgumentParser(description='Converts a a collection directory to an xhtml file and additional images')
    parser.add_argument('directory')
    parser.add_argument('-v', dest='verbose', help='Print detailed messages and output debug files', action='store_true')
    parser.add_argument('-o', dest='output', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    xhtml, files = __doStuff(args.directory, verbose=args.verbose)

    args.output.write(etree.tostring(xhtml))

  except ImportError:
    print "argparse is needed for commandline"

if __name__ == '__main__':
    sys.exit(main())
