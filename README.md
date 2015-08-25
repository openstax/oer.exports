# oer.exports

To install and get it running:

# System Dependencies

Tested with python 2.4 and python 2.7 but it will probably work with all versions in between.

## For Ubuntu/Debian

    sudo apt-get install python-virtualenv                   # for the following commands
    sudo apt-get install libxslt1-dev libxml2-dev zlib1g-dev # For lxml to compile
    sudo apt-get install librsvg2-bin                        # To convert SVG and math to PNG
    sudo apt-get install otf-stix

also:

    apt-get install imagemagick                    # PNG resizing
    apt-get install inkscape                       # svg processing
    apt-get install ruby                           # Hmmm...
    apt-get install libxml2-utils                  # for xmllint
    apt-get install zip                            # building the zip
    apt-get install unzip
    apt-get install openjdk-7-jdk                  # for saxon
    apt-get install docbook-xsl-ns
    apt-get install xsltproc                       # for generating epub
    apt-get install libopencv-dev                  # for unittests 
    apt-get install python-opencv                  # for unittests
    apt-get install python-dev                     # for unittest dependency builds
    apt-get install memcached                      # for svg caching
# For Osx

Install http://mxcl.github.com/homebrew/

    brew install librsvg
    brew install imagemagick
    brew install node           # Only if you want to compile the `.less` files
    sudo npm install -g less    # Only if you want to compile the `.less` files


Install python virtualenv

    sudo easy_install virtualenv

## For all Operating Systems

This will set up the virtual environment in your terminal (all packages are not installed globally).

    cd oer.exports
    virtualenv .
    source bin/activate
    easy_install lxml argparse pillow
    easy_install install numpy wand     # for unittests
    pip install python-memcached        # for svg caching

Once you run these steps, every time you open a terminal you will need to run `source bin/activate`.

## Install PrinceXML

Finally, you will need to install http://princexml.com (remember the path to where it gets installed, or use "which prince").

## Optional: Local docbook-xsl files

The `docbook-xsl` has files that point to http://docbook.sourceforge.net . Loading these is slow and sometimes times out.

You can download the zip file from http://sourceforge.net/projects/docbook/files/docbook-xsl-ns/ (1.72 works) and replace the `docbook-xsl` directory with its contents.

## Install Fonts

These are the fonts used in generating the PDF and EPUB files.
Prince uses TTF and OTF fonts (not Type-1 fonts which are used in newer systems).
Many are openly licensed fonts found in Ubuntu.
Some fonts can be found at http://mountainbunker.org/~ew2/fonts/truetype-open-fonts.zip

* `URW Palladio L`: http://svn.ghostscript.com/ghostscript/trunk/ghostpdl/urwfonts/ (download all 4 variants)

To test that the TTF/OTF (note Type-1) fonts were installed, run the following and verify there are no differences:

    prince -v -o /dev/null ./test-fonts.html 2>&1 | diff test-fonts.out -

## Compile Saxon

In the eor.exports/lib directory type the following command.

```
javac -cp saxon9he.jar SaxonTransformWrapper.java
```

This should create a file named SaxonTransformWrapper.class in the eor.exports/lib directory.

## Install python scripts and run unittests

Run the command ``python setup.py install`` to install the scripts collectiondbk2pdf and content2epub.  To run unittests use the command ``python setup.py test`` or ``python -m unittest tests.test_collectiondbk2pdf``.  There is a bug in the OpenCV library which causes the ``libdc1394 error: Failed to initialize libdc1394`` to be thrown.  Type ``sudo ln /dev/null /dev/raw1394`` to remove the driver causing the issue. 

# Generate Books

Ok, let's make sure you can create a PDF and EPUB!

To generate a PDF:

    collectiondbk2pdf -p ${path-to-wkhtml2pdf-or-princexml} -d ./test-ccap -s ccap-physics ./result.pdf

To generate an EPUB:

    ./scripts/module2epub.sh "Connexions" ./test-ccap ./test-ccap.epub "col12345" ./xsl/dbk2epub.xsl ./static/content.css

Alternative script for EPUB:

    # For a collection:
    content2epub -c ./static/content.css -e ./xsl/dbk2epub.xsl -t "collection" -o ./test-ccap.epub ./test-ccap/

    # For just a module:
    content2epub -c ./static/content.css -e ./xsl/dbk2epub.xsl -t "module" -o ./m123.epub -i "m123" ./test-ccap/m-section/

# Building, Diffing, and Coverage

Testing and build tools use `grunt`. It can do several things:

- compile all the LESS files to CSS files
- generate CSS coverage reports
- generate HTML+CSS diffs to see how books have changed

First, you will need to install `node` and `grunt`. http://gruntjs.com/getting-started has instructions for setting up `grunt`.

Then, you will need to create a `./config.yml` file. You can start by copying `./config.example.yml`. This file allows provides paths to all the downloaded books (unzipped comeplete ZIP files) as well as configuring some optimizations when running the tasks.

Now, we can go over the various tasks.

## Compile all the LESS files

You should run this step before pushing changes to github; fortunately it's easy. Just run `grunt compile` (or just `grunt`) and the CSS files should be generated.

**NOTE:** if you are adding a new book, you will need to add it to `./Gruntfile.coffee`.

    # Generate all the CSS files
    grunt compile

## Generate a PDF

To generate a PDF of a book run `grunt shell:pdf:{BOOK_NAME}` where `{BOOK_NAME}` is configured in `./config.yml`. This will also create a directory in `./testing/` which contains the generated HTML file for development.

## Generate HTML+CSS Diff

You can compare your CSS/XSLT changes against a book generated using the `master` branch by doing a couple of steps.
First, you will need to switch to the master branch and `prepare` a baked HTML file of the book.

**NOTE:** you will only need to `prepare` a book whenever the `master` branch updates!

Then, you can switch back to the development branch and generate a `diff`.

Below is an example (assuming the book is named `calculus` and the development branch is named `dev-branch`):

    # Switch to master
    git checkout master

    # Make sure an entry for calculus is in config.yml
    cat ./config.yml | grep calculus

    # "prepare" the baked file for diffing later
    grunt prepare:calculus

    git checkout dev-branch

    # Generate the diff'd HTML file
    grunt diff:calculus

    # View the changes by going to ./testing/calculus-diff.xhtml

That's it! If you want to generate diffs of all the books, you can drop the `:calculus` from `grunt prepare` and `grunt diff`.

**NOTE:** It will probably take several hours to diff all the books. You can speed up the process by manually generating 1 book per core.

## Generate CSS Coverage Reports

To generate a CSS coverage LCOV file, you can either set `coverage: true` inside `./config.yml` or run `grunt shell:coverage:{BOOK_NAME}:{OPTIONAL_BRANCH_NAME}`.

To generate an HTML report, you can run `genhtml` directly (`brew install lcov` on OSX) on the LCOV file or run `grunt shell:coverage-report:{BOOK_NAME}:{OPTIONAL_BRANCH_NAME}`

# License:

This software is subject to the provisions of the GNU Affero General Public License Version 3.0 (AGPL). See license.txt for details. Copyright (c) 2012 Rice University
