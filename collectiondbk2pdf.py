"""
Copyright (c) 2013 Rice University


"""

# python collectiondbk2pdf.py -v -s ccap-physics -d ./test-ccap result.pdf

import sys
import os
try:
  import Image
except:
  from PIL import Image
import shutil
from StringIO import StringIO
from tempfile import mkdtemp
import subprocess
import shutil
import time

from lxml import etree
import urllib2

import module2dbk
import collection2dbk
import util

DEFAULT_PDFGEN_PATHS = ['/usr/bin/prince', '/usr/local/bin/prince']

path = os.path.abspath(__file__)
BASE_PATH = os.path.dirname(path)

# XSL files
DOCBOOK2XHTML_XSL = util.makeXsl('dbk2xhtml.xsl')
DOCBOOK_CLEANUP_XSL = util.makeXsl('dbk-clean-whole.xsl')
DEDUPSVG_XSL = util.makeXsl('xhtml-dedup-svg.xsl')
DEDUPREFS_XSL = util.makeXsl('dedup-references.xsl')


MODULES_XPATH = etree.XPath('//col:module/@document', namespaces=util.NAMESPACES)
IMAGES_XPATH = etree.XPath('//c:*/@src[not(starts-with(.,"http:"))]', namespaces=util.NAMESPACES)

def collection2pdf(collection_dir, print_style, output_pdf, pdfgen, temp_dir, verbose=False,reduce_quality=False):

  p = util.Progress()

  collxml, modules, allFiles = util.loadCollection(collection_dir)
  
  p.start(1, 'Converting collection to Docbook')
  # clear benchmark
  if not os.path.exists(temp_dir):
      os.makedirs(temp_dir)
  util.log(temp_dir, 'benchmark.txt', '', mode='w')
  now = time.time()
  benchmark = []
  dbk, newFiles = collection2dbk.convert(p, collxml, modules, temp_dir, svg2png=False, math2svg=True, reduce_quality=reduce_quality)
  allFiles.update(newFiles)
  util.log(temp_dir, 'benchmark.txt',
           'Converting collection to Docbook: %.1fs\n\n' % (time.time() - now,))

  p.tick('Converting Docbook to PDF')
  now = time.time()
  stdErr = convert(p, dbk, allFiles, print_style, temp_dir, output_pdf, pdfgen, verbose)
  util.log(temp_dir, 'benchmark.txt',
           'Converting Docbook to PDF: %.1fs\n' % (time.time() - now,))

  p.finish()
  return stdErr

def __doStuff(collection_dir, print_style):

  output_pdf = '/dev/stdout'

  pdfgen = _find_pdfgen()
  if not pdfgen:
    print >> sys.stderr, "No valid pdfgen script found. Specify one via the command line"
    return 1

  temp_dir = mkdtemp(suffix='-xhtml2pdf')
  verbose = False

  return collection2pdf(collection_dir, print_style, output_pdf, pdfgen, temp_dir, verbose)

def __doStuffModule(moduleId, module_dir, printStyle):

  pdfgen = _find_pdfgen()
  if not pdfgen:
    print >> sys.stderr, "No valid pdfgen script found. Specify one via the command line"
    return 1

  temp_dir = mkdtemp(suffix='-module-xhtml2pdf')
  cnxml, files = util.loadModule(module_dir)
  _, newFiles = module2dbk.convert(moduleId, cnxml, files, {}, temp_dir, svg2png=False, math2svg=True, reduce_quality=False) # Last arg is coll params
  dbkFile = open(os.path.join(temp_dir, 'index.standalone.dbk'))
  dbk = etree.parse(dbkFile)
  allFiles = {}
  allFiles.update(files)
  allFiles.update(newFiles)

  p = util.Progress()
  stdErr = convert(p, dbk, allFiles, printStyle, temp_dir, '/dev/stdout', pdfgen)
  return stdErr

def xhtml2pdf(xhtml_file, files, temp_dir, print_style, pdfgen, output_pdf, verbose=False):
  """ Convert XHTML and assorted files to PDF using a XHTML+CSS to PDF script """

  CSS_FILE = os.path.join(BASE_PATH, 'css', '%s.css' % print_style)

  # Run Prince (or an Opensource) to generate an abstract tree 1st
  strCmd = [pdfgen, '-v', '--style=%s' % CSS_FILE, '--output=%s' % output_pdf, xhtml_file]
  if verbose:
    print >> sys.stderr, "Executing PDF generation: " + ' '.join(strCmd)

  env = { }

  # run the program with subprocess and pipe the input and output to variables
  p = subprocess.Popen(strCmd, close_fds=True, env=env)
  # set STDIN and STDOUT and wait untill the program finishes
  _, stdErr = p.communicate()

  return stdErr

def convert(p, dbk1, files, print_style, temp_dir, output_pdf, pdfgen, verbose=False):
  """ Converts a Docbook Element and a dictionary of files into a PDF. """

  # Step 0 (Sprinkle in some index hints whenever terms are used)
  # termsprinkler.py $DOCBOOK > $DOCBOOK2
  if verbose:
    open(os.path.join(temp_dir, 'temp-collection1.dbk'),'w').write(etree.tostring(dbk1,pretty_print=False))

  p.start(3, 'Cleaning up Docbook')
  # Step 1 (Cleaning up Docbook)
  now = time.time()
  dbk2 = util.transform(DOCBOOK_CLEANUP_XSL, dbk1)
  if verbose:
    open(os.path.join(temp_dir, 'temp-collection2.dbk'),'w').write(etree.tostring(dbk2,pretty_print=False))
  util.log(temp_dir, 'benchmark.txt',
           '  Cleaning up Docbook: %.1fs\n' % (time.time() - now,))

  now = time.time()
  p.tick('Converting Docbook to HTML')
  # Step 2 (Docbook to XHTML)
  xhtml_file = os.path.join(temp_dir, 'collection.xhtml')
  xhtml = util.transform(DOCBOOK2XHTML_XSL, dbk2)
  util.log(temp_dir, 'benchmark.txt',
           '  Converting Docbook to html: %.1fs\n' % (time.time() - now,))

  now = time.time()
  p.tick('Dedup SVGs')
  xhtml_deduped = util.transform(DEDUPSVG_XSL, xhtml)
  util.log(temp_dir, 'benchmark.txt',
           '  Dedup SVGs: %.1fs\n' % (time.time() - now,))

  now = time.time()
  p.tick('Cleaning up references')
  xhtml_dedupeder = util.transform(DEDUPREFS_XSL, xhtml_deduped)
  util.log(temp_dir, 'benchmark.txt',
           '  Cleaning up references: %.1fs\n' % (time.time() - now,))

  open(xhtml_file,'w').write(etree.tostring(xhtml_dedupeder))

  now = time.time()
  p.tick('Converting HTML to PDF')
  # Step 4 Converting XSL:FO to PDF (using Apache FOP)
  # Change to the collection dir so the relative paths to images work
  stdErr = xhtml2pdf(xhtml_file, files, temp_dir, print_style, pdfgen, output_pdf, verbose)
  util.log(temp_dir, 'benchmark.txt',
           '  Converting HTML to PDF: %.1fs\n' % (time.time() - now,))

  p.finish()
  return stdErr

def _find_pdfgen(pdfgen_file=None):
    pdfgen = None
    if pdfgen_file:
      pdfgen = pdfgen_file.name
    else:
      for path in DEFAULT_PDFGEN_PATHS:
        if os.path.isfile(path):
          pdfgen = path
          break
    return pdfgen


def main(argv=None):
    try:
      import argparse
    except ImportError:
      print "argparse is needed for commandline"
      return 2

    parser = argparse.ArgumentParser(description='Convert an unzipped Collection to a PDF')
    parser.add_argument('-v', dest='verbose', help='Print detailed messages and output debug files', action='store_true')
    parser.add_argument('-d', dest='collection_dir', help='Path to an unzipped collection', required=True)
    parser.add_argument('-s', dest='print_style', help='Print style to use (name of CSS file in css dir)', required=True)
    parser.add_argument('-p', dest='pdfgen', help='Path to a PDF generation script', nargs='?', type=argparse.FileType('r'))
    parser.add_argument('-t', dest='temp_dir', help='Path to store temporary files to (default is a temp dir that will be removed)', nargs='?')
    parser.add_argument('-r', dest='reduce_quality', help='Reduce image quality', action='store_true')
    parser.add_argument('output_pdf', help='Path to write the PDF file', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args(argv)

    if not os.path.isdir(args.collection_dir) or not os.path.isfile(os.path.join(args.collection_dir, 'collection.xml')):
      print >> sys.stderr, "collection_dir Must point to a directory containing a collection.xml file"
      return 1

    # Determine the PDF generation script to run
    pdfgen = _find_pdfgen(args.pdfgen)
    if not pdfgen:
      print >> sys.stderr, "No valid pdfgen script found. Specify one via the command line"
      return 1

    # Verify the user pointed to a valid collection dir
    if not os.path.isdir(args.collection_dir) or not os.path.isfile(os.path.join(args.collection_dir, 'collection.xml')):
      print >> sys.stderr, "Must point to a valid collection directory (with a collection.xml file)"
      return 1

    # Choose a temp dir
    delete_temp_dir = False
    temp_dir = args.temp_dir
    if not temp_dir:
      temp_dir = mkdtemp(suffix='-xhtml2pdf')
      delete_temp_dir = True

    # Set the output file
    if args.output_pdf == sys.stdout:
      output_pdf = '/dev/stdout'
    else:
      output_pdf = os.path.abspath(args.output_pdf.name)

    stdErr = collection2pdf(args.collection_dir, args.print_style, output_pdf, pdfgen, temp_dir, args.verbose, args.reduce_quality)

    if delete_temp_dir:
      shutil.rmtree(temp_dir)

if __name__ == '__main__':
    sys.exit(main())
