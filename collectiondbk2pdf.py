"""
Copyright (c) 2013 Rice University


"""

# python collectiondbk2pdf.py -v -s ccap-physics -d ./test-ccap result.pdf

import sys
import os
import shutil
from tempfile import mkdtemp
import subprocess
import time

from lxml import etree

import collection2dbk
import collection2xhtml
import util

DEFAULT_PDFGEN_PATHS = ['/usr/bin/prince', '/usr/local/bin/prince']

path = os.path.abspath(__file__)
BASE_PATH = os.path.dirname(path)


def collection2pdf(collection_dir, print_style, output_pdf, pdfgen, temp_dir, verbose=False,reduce_quality=False):

  p = util.Progress()

  collxml, modules, allFiles = util.loadCollection(collection_dir)
  
  p.start(1, 'Converting collection to Docbook')
  dbk, allFiles, newFiles = collection2dbk.load(p, collection_dir, temp_dir, verbose, svg2png=False, math2svg=True, reduce_quality=reduce_quality)

  p.tick('Converting Docbook to PDF')
  now = time.time()
  stdErr = convert(p, dbk, allFiles, print_style, temp_dir, output_pdf, pdfgen, verbose)
  util.log(temp_dir, 'benchmark.txt',
           'Converting Docbook to PDF: %.1fs\n' % (time.time() - now,))

  p.finish()
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

  xhtml, files = collection2xhtml.convert(p, dbk1, files, temp_dir, verbose)

  xhtml_file = os.path.join(temp_dir, 'collection.xhtml')
  open(xhtml_file,'w').write(etree.tostring(xhtml, encoding='utf-8', xml_declaration=True))

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
