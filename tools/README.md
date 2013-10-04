pdfdiff python commandline-tool
================================

Requirements:  
- comparepdf http://www.qtrac.eu/comparepdf.html
- Python 2.6+ and Virtualenv

Usage
-----

    python pdfdiff.py fdiff <file1> <file2>
    python pdfdiff.py ddiff <dir1> <dir2>
    python pdfdiff.py (-h | --help)

PDFdiff either two files or two directories containing *.pdf files.
When comparing two directories the PDF filenames need to be the same.

Installation of comparepdf on Ubuntu
------------------------------------

Starting with Ubuntu 12.10 (Quantal Quetzal) you can install it with

    sudo apt-get install comparepdf

For older Ubuntu versions please build it from source from
http://www.qtrac.eu/comparepdf.html

Installation of comparepdf on OS X
----------------------------------

You can install comparepdf with [Homebrew](http://brew.sh/)

    brew install comparepdf

General installation
--------------------

Install Python-Virtualenv and libraries or install docopt globally
If you need a good latest python OS X guide [look here](http://hackercodex.com/guide/python-virtualenv-on-mac-osx-mountain-lion-10.8/)

    virtualenv .
    source bin/activate
    pip install docopt

Hint: Everytime you want to use pdfdiff.py you need to activate virtualenv.
Activation and deactivation of virtualenv:

    source bin/activate
    (... run pdfdiff.py here... )
    deactivate
