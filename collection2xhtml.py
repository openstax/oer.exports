# python collection2xhtml.py -d ./test-ccap result.xhtml

import sys
import os
from tempfile import mkdtemp
import time

from lxml import etree

import collection2dbk
import util


# XSL files
DOCBOOK2XHTML_XSL=util.makeXsl('dbk2xhtml.xsl')
DOCBOOK_CLEANUP_XSL = util.makeXsl('dbk-clean-whole.xsl')
DEDUPSVG_XSL = util.makeXsl('xhtml-dedup-svg.xsl')
DEDUPREFS_XSL = util.makeXsl('dedup-references.xsl')


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
  except ImportError:
    print "argparse is needed for commandline"
    return 1

  parser = argparse.ArgumentParser(description='Converts a a collection directory to an xhtml file and additional images')
  parser.add_argument('-v', dest='verbose', help='Print detailed messages and output debug files', action='store_true')
  parser.add_argument('-d', dest='collection_dir', help='Path to an unzipped collection', required=True)
  parser.add_argument('-t', dest='temp_dir', help='Path to store temporary files to (default is a temp dir that will be removed)', nargs='?')
  parser.add_argument('-r', dest='reduce_quality', help='Reduce image quality', action='store_true')
  parser.add_argument('--math2svg', type=util.str2bool, default=True, help="Transform MathML to SVG using pmml2svg")
  parser.add_argument('output_xhtml', help='Path to write the XHTML file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
  args = parser.parse_args()

  if not os.path.isdir(args.collection_dir) or not os.path.isfile(os.path.join(args.collection_dir, 'collection.xml')):
    print >> sys.stderr, "collection_dir Must point to a directory containing a collection.xml file"
    return 1

  # Choose a temp dir
  delete_temp_dir = False
  temp_dir = args.temp_dir
  if not temp_dir:
    temp_dir = mkdtemp(suffix='-xhtml2pdf')
    delete_temp_dir = True

  p = util.Progress()

  p.start(1, 'Converting collection to Docbook')
  dbk, files, newFiles = collection2dbk.load(p, args.collection_dir, temp_dir, verbose=args.verbose, math2svg=args.math2svg, reduce_quality=args.reduce_quality)

  p.tick('Converting Docbook to XHTML')
  xhtml, files = convert(p, dbk, files, temp_dir, verbose=args.verbose)

  args.output_xhtml.write(etree.tostring(xhtml))

  p.finish()

  if delete_temp_dir:
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sys.exit(main())
