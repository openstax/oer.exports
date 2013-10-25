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
import shutil
import tempfile

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

def print_single_seperator():
    print '-' * 79

def infog(msg):
    print OKGREEN + msg + ENDC

def info(msg):
    print OKBLUE + msg + ENDC

def warn(msg):
    print WARNING + 'WARNING: ' + msg + ENDC

def err(msg):
    print FAIL + 'ERROR: ' + msg + ENDC

# =================================

# Check if program is available
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

# =================================

def _check_pdf_exist(filename):
    if (not(path.isfile(filename))):
        err('PDF file not found: ' + filename)
        sys.exit(1)

def _check_poppler_helper(program_bin):
    if (which(program_bin) == None):
        err(program_bin + ' not found! Not installed Poppler yet?')
        sys.exit(2)

# =================================

# diffs two pdf files and returns 0 when no difference
def diff_pdf_files(file1, file2):
    print_single_seperator()
    _check_pdf_exist(file1)
    _check_pdf_exist(file2)
    info('Comparing PDF files {0} and {1}'.format(path.basename(file1), path.basename(file2)))
    diff_pdf_bin = 'comparepdf'
    _check_poppler_helper(diff_pdf_bin):
    diff_pdf_cmd = [diff_pdf_bin, '--verbose=1',file1, file2]
    p = Popen(diff_pdf_cmd , shell=False, stdout=PIPE, stderr=PIPE)
    out, errorout = p.communicate()
    print out.rstrip(), errorout.rstrip()
    if (p.returncode==0):
        pass # "OK!" will be printed later
    elif (p.returncode==10):
        err('Files differ visually!')
    elif (p.returncode==13):
        err('Files differ textually! Diff:')
        diff_pdf_text(file1, file2)
    elif (p.returncode==15):
        err('Files have different page counts!')
    else: # 1 or 2
        err('FATAL ERROR DURING COMPARING!')
    return (p.returncode)

# =================================

# diff only pdf text differences
def diff_pdf_text(file1, file2):
    _check_pdf_exist(file1)
    _check_pdf_exist(file2)
    #info('Comparing PDF text between {0} and {1}'.format(path.basename(file1), path.basename(file2)))
    pdftotext_bin = 'pdftotext'
    _check_poppler_helper(pdftotext_bin)
    # create temporary directory
    try:
        tmp_dir = tempfile.mkdtemp()
        # convert first file to text
        pdftextfile1 = path.join(tmp_dir, path.basename(file1) + ".txt")
        pdftotext_cmd = [pdftotext_bin, file1, pdftextfile1]
        p = Popen(pdftotext_cmd , shell=False, stdout=PIPE, stderr=PIPE)
        out, errorout = p.communicate()
        print out.rstrip(), errorout.rstrip()
        # convert second file to text
        pdftextfile2 = path.join(tmp_dir, path.basename(file2) + ".txt")
        pdftotext_cmd = [pdftotext_bin, file2, pdftextfile2]
        p = Popen(pdftotext_cmd , shell=False, stdout=PIPE, stderr=PIPE)
        out, errorout = p.communicate()
        print out.rstrip(), errorout.rstrip()
        # diff the two pdf texts
        info('Diffing PDF text between {0} and {1}'.format(path.basename(file1), path.basename(file2)))
        diff_cmd = ['diff', pdftextfile1, pdftextfile2]
        p = Popen(diff_cmd , shell=False, stdout=PIPE, stderr=PIPE)
        out, errorout = p.communicate()
        print out.rstrip(), errorout.rstrip()
    finally:
        try:
            shutil.rmtree(tmp_dir)  # delete directory
        except OSError as exc:
            if exc.errno != 2:  # code 2 - no such file or directory
                raise  # re-raise exception

# =================================

# diffs two directories with pdf files and returns 0 when no difference
def diff_pdf_dirs(dir1, dir2):
    exit_code = 0 # Assume no errors
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
        exit_code = exit_code or diff_pdf_files(f1, f2)

    return exit_code

# =================================

def exit_message(exit_code):
    if 0 == exit_code:
        infog('OK!')
    else:
        sys.exit(exit_code)

# =================================

def main():
    arg = docopt(__doc__)
    if (arg['fdiff']):
        exit_code = diff_pdf_files(arg['<file1>'], arg['<file2>'])
        exit_message(exit_code)
    elif (arg['ddiff']):
        infog('Comparing two directories')
        exit_code = diff_pdf_dirs(arg['<dir1>'], arg['<dir2>'])
        exit_message(exit_code)

# =================================

if  __name__ == '__main__':
    main()
