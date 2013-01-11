import sys
import os
import Image
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

EMBED_FONTS = [
  'fonts/stix/STIXGeneral.ttf',
  'fonts/stix/STIXGeneralBol.ttf',
  'fonts/stix/STIXGeneralBolIta.ttf',
  'fonts/stix/STIXGeneralItalic.ttf',
  'fonts/stix/STIXSiz1Sym.ttf',
  'fonts/stix/STIXSiz1SymBol.ttf'
]

DEFAULT_DOCBOOK2XHTML_XSL='xsl/dbk2epub.xsl'

def convert(dbk1, temp_dir, cssFile, xslFile, epubFile):
  """ Converts a Docbook Element into EPUB HTML. """

  temp_dir = os.path.abspath(temp_dir)

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

  RUBY_BIN = 'ruby'
  DBK_TO_EPUB_BIN = os.path.abspath('./docbook-xsl/epub/bin/dbtoepub')
  DBK_FILE_NAME = 'collection.dbk'

  EMBED_FONT_ARGS = [['--font', os.path.join(os.getcwd(), path)] for path in EMBED_FONTS]

  DBK_FILE = os.path.join(temp_dir, DBK_FILE_NAME)

  f = open(DBK_FILE, 'w')
  f.write(etree.tostring(dbk1))
  f.close()

  strCmd = ['--stylesheet', os.path.abspath(xslFile), '-c', os.path.abspath(cssFile), EMBED_FONT_ARGS, '-o', os.path.abspath(epubFile), '-d', DBK_FILE]
  strCmd = flatten(strCmd)
  strCmd.insert(0, DBK_TO_EPUB_BIN)
  strCmd.insert(0, RUBY_BIN)

  p = subprocess.Popen(strCmd, cwd=temp_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
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
  parser.add_argument('-e', dest='epub_script', help='Name of XSL file that generates an epub from a dbk file (should look like "./xsl/dbk2___.xsl")')
  parser.add_argument('-r', dest='reduce_quality', help='Reduce image quality', action='store_true')
  parser.add_argument('-t', dest='content_type', help='The type of content being converted. One of ["module", "collection"]')
  # parser.add_argument('-t', dest='temp_dir', help='Path to store temporary files to (default is a temp dir that will be removed)', nargs='?')
  parser.add_argument('-o', dest='output', nargs='?') # , type=argparse.FileType('w'), default=sys.stdout)
  args = parser.parse_args()

  epubXsl = args.epub_script
  if not epubXsl:
    epubXsl = DEFAULT_DOCBOOK2XHTML_XSL

  temp_dir = args.directory

  p = util.Progress()

  if args.content_type == 'module':
    cnxml, allFiles = util.loadModule(args.directory)
    dbk, newFiles = module2dbk.convert(args.module_id, cnxml, allFiles, {}, temp_dir, svg2png=True, math2svg=True, reduce_quality=args.reduce_quality)
    dbk = newFiles['index.standalone.dbk']
    allFiles.update(newFiles)
    cover, newFiles = util.dbk2cover(etree.parse(StringIO(dbk)), allFiles, svg2pngFlag=True)
    newFiles['cover.png'] = cover


  elif args.content_type == 'collection':
    p = util.Progress()
    collxml, modulesDict, allFiles = util.loadCollection(args.directory)

    dbk, newFiles = collection2dbk.convert(p, collxml, modulesDict, temp_dir, svg2png=True, math2svg=True, reduce_quality=args.reduce_quality)
    allFiles.update(newFiles)

  else:
    print "Invalid content type. Must be one of ['module', 'collection']"
    return 1

  # Write out all the added files
  for name in newFiles:
    f = open(os.path.join(temp_dir, name), 'w')
    f.write(newFiles[name])
    f.close()

  # Now, run the epub script
  nothing = convert(etree.parse(StringIO(dbk)), temp_dir, args.css_file, epubXsl, args.output)

if __name__ == '__main__':
    sys.exit(main())
