"""
Copyright (c) 2013 Rice University



"""

import os
import sys
from PIL import Image

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
