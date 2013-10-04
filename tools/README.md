pdfdiff python commandline-tool
================================

Requirements:  
- It only runs in Linux because diff-pdf needs to be compiled (only tested in Ubuntu 12.04)
- Python 2.7+

Usage
-----

    python pdfdiff.py fdiff <file1> <file2>
    python pdfdiff.py ddiff <dir1> <dir2>
    python pdfdiff.py (-h | --help)

PDFdiff either two files or two directories containing *.pdf files.
When comparing two directories the PDF filenames need to be the same.

Installation on Ubuntu 12.04
----------------------------

Install this libraries:

    sudo apt-get install libwxgtk2.8-dev libcairo2-dev libpoppler-dev python-virtualenv
    
Compile diff-pdf binaries

    cd diff-pdf
    ./bootstrap
    ./configure
    make

Install Python-Virtualenv and libraries or install docopt globally

    cd ..
    virtualenv .
    source bin/activate
    pip install docopt

Hint: Everytime you want to use pdfdiff.py you need to activate virtualenv.
Activation and deactivation of virtualenv:

    source bin/activate
    (... run pdfdiff.py here... )
    deactivate
