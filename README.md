# oer.exports

To install and get it running:

# System Dependencies

Tested with python 2.4 and python 2.7 but it will probably work with all versions in between.

## For Ubuntu/Debian

    sudo apt-get install python-virtualenv        # for the following commands
    sudo apt-get install libxslt1-dev libxml2-dev # For lxml to compile
    sudo apt-get install librsvg2-bin             # To convert SVG and math to PNG
    sudo apt-get install otf-stix

## For Osx

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
    easy_install lxml argparse pil

Once you run these steps, every time you open a terminal you will need to run `source bin/activate`.

## Install PrinceXML

Finally, you will need to install http://princexml.com (remember the path to where it gets installed).

## Optional: Local docbook-xsl files

The `docbook-xsl` has files that point to http://docbook.sourceforge.net . Loading these is slow and sometimes times out.

You can download the zip file from http://sourceforge.net/projects/docbook/files/docbook-xsl-ns/ (1.72 works) and replace the `docbook-xsl` directory with its contents.


# Generate Books

Ok, let's make sure you can create a PDF and EPUB!

To generate a PDF:

    python collectiondbk2pdf.py -p ${path-to-wkhtml2pdf-or-princexml} -d ./test-ccap -s ccap-physics ./result.pdf

To generate an EPUB:

    ./scripts/module2epub.sh "Connexions" ./test-ccap ./test-ccap.epub "col12345" ./xsl/dbk2epub.xsl ./static/content.css

Alternative script for EPUB:

    # For a collection:
    python content2epub.py -c ./static/content.css -e ./xsl/dbk2epub.xsl -t "collection" -o ./test-ccap.epub ./test-ccap/

    # For just a module:
    python content2epub.py -c ./static/content.css -e ./xsl/dbk2epub.xsl -t "module" -o ./m123.epub -i "m123" ./test-ccap/m-section/
