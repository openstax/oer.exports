"""
Copyright (c) 2013 Rice University

This software is subject to the provisions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).
See LICENSE.txt for details.
"""

import os
import sys
import Image

def main(dir):
  print "<images>"
  for f in os.listdir(dir):
    try:
      im = Image.open(os.path.join(dir, f))
      print '<image name="%s" width="%d" height="%d"/>' % (f, im.size[0], im.size[1])
    except IOError:
      pass
  print "</images>"

if __name__ == '__main__':
    main(sys.argv[1])
