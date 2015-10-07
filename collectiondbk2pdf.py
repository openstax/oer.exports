"""
Copyright (c) 2013 Rice University

This software is subject to the provisions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).
See LICENSE.txt for details.
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

from lxml import etree
import urllib2

import module2dbk
import collection2dbk
import util

DEFAULT_PDFGEN_PATHS = ['/usr/bin/prince','/usr/local/bin/prince']

path = os.path.abspath(__file__)
BASE_PATH = os.path.dirname(path)

# XSL files
DOCBOOK2XHTML_XSL=util.makeXsl('dbk2xhtml.xsl')
DOCBOOK_CLEANUP_XSL = util.makeXsl('dbk-clean-whole.xsl')

MODULES_XPATH = etree.XPath('//col:module/@document', namespaces=util.NAMESPACES)
IMAGES_XPATH = etree.XPath('//c:*/@src[not(starts-with(.,"http:"))]', namespaces=util.NAMESPACES)

def collection2pdf(collection_dir, print_style, output_pdf, pdfgen, temp_dir, verbose=False,reduce_quality=False):

  p = util.Progress()

  collxml = etree.parse(os.path.join(collection_dir, 'collection.xml'))

  moduleIds = MODULES_XPATH(collxml)

  modules = {} # {'m1000': (etree.Element, {'file.jpg':'23947239874'})}
  allFiles = {}
  for moduleId in moduleIds:
    moduleDir = os.path.join(collection_dir, moduleId)
    if os.path.isdir(moduleDir):
      cnxml, files = loadModule(moduleDir)
      for f in files:
        allFiles[os.path.join(moduleId, f)] = files[f]

      modules[moduleId] = (cnxml, files)

  p.start(1, 'Converting collection to Docbook')
  dbk, newFiles = collection2dbk.convert(p, collxml, modules, temp_dir, svg2png=False, math2svg=True, reduce_quality=reduce_quality)
  allFiles.update(newFiles)

  p.tick('Converting Docbook to PDF')
  stdErr = convert(p, dbk, allFiles, print_style, temp_dir, output_pdf, pdfgen, verbose)

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
  cnxml, files = loadModule(module_dir)
  _, newFiles = module2dbk.convert(moduleId, cnxml, files, {}, temp_dir, svg2png=False, math2svg=True, reduce_quality=False) # Last arg is coll params
  dbkFile = open(os.path.join(temp_dir, 'index.standalone.dbk'))
  dbk = etree.parse(dbkFile)
  allFiles = {}
  allFiles.update(files)
  allFiles.update(newFiles)

  p = util.Progress()
  stdErr = convert(p, dbk, allFiles, printStyle, temp_dir, '/dev/stdout', pdfgen)
  return stdErr

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

  def transform(xslDoc, xmlDoc):
    """ Performs an XSLT transform and parses the <xsl:message /> text """
    ret = xslDoc(xmlDoc) # xslDoc(xmlDoc, **({'cnx.tempdir.path':"'%s'" % temp_dir}))
    for entry in xslDoc.error_log:
      # TODO: Log the errors (and convert JSON to python) instead of just printing
      print >> sys.stderr, entry.message.encode('utf-8')
    return ret

  # Step 0 (Sprinkle in some index hints whenever terms are used)
  # termsprinkler.py $DOCBOOK > $DOCBOOK2
  if verbose:
    open(os.path.join(temp_dir, 'temp-collection1.dbk'),'w').write(etree.tostring(dbk1,pretty_print=False))

  p.start(2, 'Cleaning up Docbook')
  # Step 1 (Cleaning up Docbook)
  dbk2 = transform(DOCBOOK_CLEANUP_XSL, dbk1)
  if verbose:
    open(os.path.join(temp_dir, 'temp-collection2.dbk'),'w').write(etree.tostring(dbk2,pretty_print=False))

  p.tick('Converting Docbook to HTML')
  # Step 2 (Docbook to XHTML)
  xhtml_file = os.path.join(temp_dir, 'collection.xhtml')
  xhtml = transform(DOCBOOK2XHTML_XSL, dbk2)
  open(xhtml_file,'w').write(etree.tostring(xhtml))

  p.tick('Converting HTML to PDF')
  #import pdb; pdb.set_trace()
  # Step 4 Converting XSL:FO to PDF (using Apache FOP)
  # Change to the collection dir so the relative paths to images work
  stdErr = xhtml2pdf(xhtml_file, files, temp_dir, print_style, pdfgen, output_pdf, verbose)

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
