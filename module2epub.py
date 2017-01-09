#!/usr/bin/env python
"""
Copyright (c) 2013 Rice University

This software is subject to the provisions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).
See LICENSE.txt for details.
"""

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
DOCBOOK2XHTML_XSL=util.makeXsl('dbk2epub.xsl')
DOCBOOK_CLEANUP_XSL = util.makeXsl('dbk-clean-whole.xsl')

EMBED_FONTS = [
  'fonts/stix/STIXGeneral.ttf',
  'fonts/stix/STIXGeneralBol.ttf',
  'fonts/stix/STIXGeneralBolIta.ttf',
  'fonts/stix/STIXGeneralItalic.ttf',
  'fonts/stix/STIXSiz1Sym.ttf',
  'fonts/stix/STIXSiz1SymBol.ttf'
]


def convert(dbk1, temp_dir, cssFile, epubFile):
  """ Converts a Docbook Element into EPUB HTML. """

  # Hackish flatten function for command line arguments
  def flatten(l):
    out = []
    for item in l:
      if isinstance(item, (list, tuple)):
        out.extend(flatten(item))
      else:
        out.append(item)
    return out

  def transform(xslDoc, xmlDoc):
    """ Performs an XSLT transform and parses the <xsl:message /> text """
    ret = xslDoc(xmlDoc) # , **({'cnx.tempdir.path':"'%s'" % tempdir}))    Don't set the tempdir. We don't need it
    for entry in xslDoc.error_log:
      # TODO: Log the errors (and convert JSON to python) instead of just printing
      print >> sys.stderr, entry.message.encode('utf-8')
    return ret

  # Step 1 (Convert Docbook to EPUB HTML)
  # The epub script will generate HTML files in temp_dir
  # It will not return anything
  orig_dir = os.getcwd()
  # $RUBY $ROOT/docbook-xsl/epub/bin/dbtoepub --stylesheet $DBK_TO_HTML_XSL -c $CSS_FILE $EMBEDDED_FONTS_ARGS -o $EPUB_FILE -d $DBK_FILE

  RUBY_BIN = 'ruby'
  DBK_TO_EPUB_BIN = './docbook-xsl/epub/bin/dbtoepub'
  DBK_FILE_NAME = 'collection.dbk'
  DBK_TO_HTML_XSL_PATH = os.path.join(orig_dir, 'xsl/dbk2epub.xsl')

  EMBED_FONT_ARGS = [['--font', os.path.join(os.getcwd(), path)] for path in EMBED_FONTS]

  DBK_FILE = os.path.join(temp_dir, DBK_FILE_NAME)

  f = open(DBK_FILE, 'w')
  f.write(etree.tostring(dbk1))
  f.close()

  strCmd = ['--stylesheet', DBK_TO_HTML_XSL_PATH, '-c', cssFile, EMBED_FONT_ARGS, '-o', epubFile, '-d', DBK_FILE]
  strCmd = flatten(strCmd)
  strCmd.insert(0, DBK_TO_EPUB_BIN)
  strCmd.insert(0, RUBY_BIN)

  p = subprocess.Popen(strCmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
  (stdOut, stdErr) = p.communicate()


def main():
  try:
    import argparse
  except ImportError:
    print "argparse is needed for commandline"
    return 1

  parser = argparse.ArgumentParser(description='Converts a module directory to an xhtml file and additional images')
  parser.add_argument('directory')
  parser.add_argument('-i', dest='module_id', help='Published Module id')
  parser.add_argument('-c', dest='css_file', help='CSS File to include')# , type=argparse.FileType('r'))
  parser.add_argument('-e', dest='epub_script', help='Path to script that generates an epub from a dbk file and temporary directory', action='store_true')
  parser.add_argument('-r', dest='reduce_quality', help='Reduce image quality', action='store_true')
  # parser.add_argument('-t', dest='temp_dir', help='Path to store temporary files to (default is a temp dir that will be removed)', nargs='?')
  parser.add_argument('-o', dest='output', nargs='?') # , type=argparse.FileType('w'), default=sys.stdout)
  args = parser.parse_args()

  temp_dir = args.directory

  p = util.Progress()

  cnxml, allFiles = util.loadModule(args.directory)

  dbk, newFiles = module2dbk.convert(args.module_id, cnxml, allFiles, {}, temp_dir, svg2png=True, math2svg=True, reduce_quality=args.reduce_quality)
  allFiles.update(newFiles)

  nothing = convert(etree.parse(StringIO(dbk)), temp_dir, args.css_file, args.output)

  # Write out all the added files
  for name in newFiles:
    f = open(os.path.join(temp_dir, name), 'w')
    f.write(newFiles[name])
    f.close()


  # Now, run the epub script

if __name__ == '__main__':
    sys.exit(main())
