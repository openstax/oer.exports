"""Usage:
    pdfdiff.py fdiff [-g|--graphical] <file1> <file2>
    pdfdiff.py ddiff [-g|--graphical] <dir1> <dir2>
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
from itertools import izip
from PIL import Image
from difflib import SequenceMatcher

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
def diff_pdf_files(file1, file2, diffgraphic=False):
    print_single_seperator()
    _check_pdf_exist(file1)
    _check_pdf_exist(file2)
    info('Comparing PDF files {0} and {1}'.format(path.basename(file1), path.basename(file2)))
    diff_pdf_bin = 'comparepdf'
    _check_poppler_helper(diff_pdf_bin)
    diff_pdf_cmd = [diff_pdf_bin, '--verbose=1',file1, file2]
    p = Popen(diff_pdf_cmd , shell=False, stdout=PIPE, stderr=PIPE)
    out, errorout = p.communicate()
    print out.rstrip(), errorout.rstrip()
    if (p.returncode==0):
        pass # "OK!" will be printed later
    elif (p.returncode==10):
        err('Files differ only visually (no text affected)!')
        if diffgraphic:
            diff_pdf_graphics(file1, file2)
    elif (p.returncode==13):
        err('Files differ textually and maybe visually! Diff:')
        diff_pdf_text(file1, file2)
        if diffgraphic:
            diff_pdf_graphics(file1, file2)
    elif (p.returncode==15):
        err('Files have different page counts!')
    else: # 1 or 2
        err('FATAL ERROR DURING COMPARING!')
    return (p.returncode)

# =================================

# diff only pdf text differences.
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
        pdftextfile1 = path.join(tmp_dir, path.basename(file1) + "1.txt")
        pdftotext_cmd = [pdftotext_bin, file1, pdftextfile1]
        p = Popen(pdftotext_cmd , shell=False, stdout=PIPE, stderr=PIPE)
        out, errorout = p.communicate()
        print out.rstrip(), errorout.rstrip()
        # convert second file to text
        pdftextfile2 = path.join(tmp_dir, path.basename(file2) + "2.txt")
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
        # calculate percentage difference of text:
        text1 = open(pdftextfile1).read()
        text2 = open(pdftextfile2).read()
        m = SequenceMatcher(None, text1, text2)
        info("Text percentage % difference: {0:.2f}%".format((1 - m.ratio()) * 100))
    finally:
        try:
            shutil.rmtree(tmp_dir)  # delete directory
        except OSError as exc:
            if exc.errno != 2:  # code 2 - no such file or directory
                raise  # re-raise exception

# =================================

# returns difference between two files in percentage. 0 = no difference, 1 = 100% difference
def _diff_images(file1, file2):
    if (not(path.isfile(file1))):
        err('Wow this should never happen. A temporary extracted pdf image file was not found! ' + file1)
        sys.exit(1)
    if (not(path.isfile(file2))):
        err('Wow this should never happen. A temporary extracted pdf image file was not found! ' + file2)
        sys.exit(1)

    i1 = Image.open(file1)
    i2 = Image.open(file2)
    assert i1.mode == i2.mode, "Different kinds of images."
    assert i1.size == i2.size, "Different image sizes."
     
    pairs = izip(i1.getdata(), i2.getdata())
    if len(i1.getbands()) == 1:
        # for gray-scale jpegs
        dif = sum(abs(p1-p2) for p1,p2 in pairs)
    else:
        dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
     
    ncomponents = i1.size[0] * i1.size[1] * 3
    return (dif / 255.0) / ncomponents

# diff only pdf image differences.
# Info: Only do this if pdfs have same amount of pages!
def diff_pdf_graphics(file1, file2):
    _check_pdf_exist(file1)
    _check_pdf_exist(file2)
    pdftoimg_bin = 'pdftoppm'
    _check_poppler_helper(pdftoimg_bin)
    # extract earch pdf to png images in a temporary directory and compare them visually (by percentage)
    try:
        tmp_dir1 = tempfile.mkdtemp()
        tmp_dir2 = tempfile.mkdtemp()
        # convert first pdf to png images in temp dir
        pdf_img_filebase1 = path.join(tmp_dir1, 'pdfimage')
        pdftoimg_cmd1 = [pdftoimg_bin, '-png', file1, pdf_img_filebase1]
        p = Popen(pdftoimg_cmd1 , shell=False, stdout=PIPE, stderr=PIPE)
        out, errorout = p.communicate()
        print out.rstrip(), errorout.rstrip()
        # convert second pdf to png images in temp dir
        pdf_img_filebase2 = path.join(tmp_dir2, 'pdfimage')
        pdftoimg_cmd2 = [pdftoimg_bin, '-png', file2, pdf_img_filebase2]
        p = Popen(pdftoimg_cmd2 , shell=False, stdout=PIPE, stderr=PIPE)
        out, errorout = p.communicate()
        print out.rstrip(), errorout.rstrip()

        # list all files in tmp_dir1 and assume that we have the same amount in tmp_dir2. Otherwise error!
        imgfiles1 = []
        for imgfile1 in os.listdir(tmp_dir1):
            if fnmatch.fnmatch(imgfile1, '*.png'):
                imgfiles1.append(imgfile1)
        imgfiles2 = []
        for imgfile2 in os.listdir(tmp_dir2):
            if fnmatch.fnmatch(imgfile2, '*.png'):
                imgfiles2.append(imgfile2)
        if (len(imgfiles1) != len(imgfiles2)):
            err('The number of extracted images do not match. Disk out of space? This error should not happen!')
            sys.exit(2)
        simgfiles1 = set(imgfiles1)
        simgfiles2 = set(imgfiles2)
        only_in_onedir = list(simgfiles1.union(simgfiles2) - simgfiles1.intersection(simgfiles2))
        if (len(only_in_onedir) > 0):
            err('Different filenames in temp directory 1 and 2. Fatal error. This should never happen!')
            sys.exit(2)
        info('Diffing PDF graphically {0} and {1}'.format(path.basename(file1), path.basename(file2)))
        diff_overall = 0
        for page, f in enumerate(imgfiles1): # use files1 list. It is has the same values as files2 now (we checked that above).
            f1 = path.join(tmp_dir1, f)
            f2 = path.join(tmp_dir2, f)
            difference = _diff_images(f1, f2)
            diff_overall += difference
            print "Page {0} difference: {1:.5f}%".format(page+1, difference * 100)
        diff_overall /= len(imgfiles1) # divide the sum of diffs by page number
        info("Graphic percentage % difference: {0:.2f}%".format(diff_overall * 100))
    finally:
        try:
            shutil.rmtree(tmp_dir1)  # delete directory
            shutil.rmtree(tmp_dir2)
        except OSError as exc:
            if exc.errno != 2:  # code 2 - no such file or directory
                raise  # re-raise exception

# =================================

# diffs two directories with pdf files and returns 0 when no difference
def diff_pdf_dirs(dir1, dir2, diffgraphic=False):
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
        exit_code = exit_code or diff_pdf_files(f1, f2, diffgraphic)

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
    make_graphicdiff = arg['-g'] or arg['--graphical']
    if (arg['fdiff']):
        exit_code = diff_pdf_files(arg['<file1>'], arg['<file2>'], diffgraphic=make_graphicdiff)
        exit_message(exit_code)
    elif (arg['ddiff']):
        infog('Comparing two directories')
        exit_code = diff_pdf_dirs(arg['<dir1>'], arg['<dir2>'], diffgraphic=make_graphicdiff)
        exit_message(exit_code)

# =================================

if  __name__ == '__main__':
    main()
