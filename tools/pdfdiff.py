"""Usage:
    pdfdiff.py fdiff <file1> <file2>
    pdfdiff.py ddiff <dir1> <dir2>
    pdfdiff.py (-h | --help)

PDFdiff either two files or two directories containing *.pdf files.
When comparing two directories the PDF filenames need to be the same.

Options:
  -h --help

"""

import fnmatch
import os
from os import path
import sys
import re
from docopt import docopt
from subprocess import Popen, PIPE

# =================================
# just some fancy colors for output

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = "\033[1m"

def disable():
    HEADER = ''
    OKBLUE = ''
    OKGREEN = ''
    WARNING = ''
    FAIL = ''
    ENDC = ''

def infog(msg):
    print OKGREEN + msg + ENDC

def info(msg):
    print OKBLUE + msg + ENDC

def warn(msg):
    print WARNING + msg + ENDC

def err(msg):
    print FAIL + 'ERROR: ' + msg + ENDC

# =================================

def pdf_files_different(file1, file2):
    if (not(path.isfile(file1))):
        err('PDF file not found: ' + file1)
        sys.exit(1)
    if (not(path.isfile(file2))):
        err('PDF file not found: ' + file2)
        sys.exit(1)
    infog('Comparing PDF files {0} and {1}'.format(path.basename(file1), path.basename(file2)))
    diff_pdf_bin = path.join(os.path.dirname(os.path.realpath(__file__)), 'diff-pdf', 'diff-pdf')
    if (not(path.isfile(diff_pdf_bin))):
        err('Compiled diff-pdf not found! Is it not built yet?')
        sys.exit(2)
    diff_pdf_cmd = ['./diff-pdf/diff-pdf','-v', file1, file2]
    p = Popen(diff_pdf_cmd , shell=False, stdout=PIPE, stderr=PIPE)
    out, errorout = p.communicate()
    print out.rstrip(), errorout.rstrip()
    if (p.returncode!=0):
        err('File differs!')
    else:
        info('OK!')
    return (p.returncode!=0)

# =================================

def pdf_dirs_different(dir1, dir2):
    if (not(path.isdir(dir1))):
        err('Directory not found: ' + dir1)
        sys.exit(1)
    if (not(path.isdir(dir2))):
        err('Directory not found: ' + dir2)
        sys.exit(1)
    dir1 = path.abspath(dir1)
    dir2 = path.abspath(dir2)
    if (dir1 == dir2):
        err('dir1 is the same as dir2. They should be different!')
        sys.exit(1)
    files1 = []
    for file1 in os.listdir(dir1):
        if fnmatch.fnmatch(file1, '*.pdf'):
            files1.append(file1)
    files2 = []
    for file2 in os.listdir(dir2):
        if fnmatch.fnmatch(file2, '*.pdf'):
            files2.append(file2)
    if (len(files1) != len(files2)):
        warn('The number of *.pdfs in both directories do not match!')        
    sfiles1 = set(files1)
    sfiles2 = set(files2)
    only_in_onedir = list(sfiles1.union(sfiles2) - sfiles1.intersection(sfiles2))
    if (len(only_in_onedir) > 0):
        warn('There are PDF files only in directory 1 or directory 2!')
        for f in only_in_onedir:
            warn('Filename which is only in one of the directories: ' + f)
    #compare only intersection files (which are in both directories)
    in_both_dirs = list(sfiles1.intersection(sfiles2))
    for f in in_both_dirs:
        f1 = path.join(dir1, f)
        f2 = path.join(dir2, f)
        pdf_files_different(f1, f2)

# =================================

def main():
    arg = docopt(__doc__)
    if (arg['fdiff']):
        pdf_files_different(arg['<file1>'], arg['<file2>'])
    elif (arg['ddiff']):
        infog('Comparing two directories')
        pdf_dirs_different(arg['<dir1>'], arg['<dir2>'])

# =================================

if  __name__ == '__main__':
    main()
