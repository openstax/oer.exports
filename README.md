# oer.exports

**For Windows Users:** If your username contains whitespace, the setup and installation will not work. Create a new user without whitespace in the username in order to succesfully complete installation.

To install and get it running:

# System Dependencies

Tested with python 2.4 and python 2.7 but it will probably work with all versions in between.

## For Ubuntu/Debian

    sudo apt-get update
    sudo apt-get install python-virtualenv                   # for the following commands
    sudo apt-get install libxslt1-dev libxml2-dev zlib1g-dev # For lxml to compile
    sudo apt-get install librsvg2-bin                        # To convert SVG and math to PNG
    sudo apt-get install otf-stix
    sudo apt-get install openjdk-7-jdk                       # for saxon

if attempting to install openjdk-7-jdk gives an error, try the following:

    sudo add-apt-repository ppa:openjdk-r/ppa  
    sudo apt-get update   
    sudo apt-get install openjdk-7-jdk

also:

    sudo apt-get install imagemagick                    # PNG resizing
    sudo apt-get install inkscape                       # svg processing
    sudo apt-get install ruby                           # Hmmm...
    sudo apt-get install libxml2-utils                  # for xmllint
    sudo apt-get install zip                            # building the zip
    sudo apt-get install unzip
    sudo apt-get install docbook-xsl-ns
    sudo apt-get install xsltproc                       # for generating epub
    sudo apt-get install libopencv-dev                  # for unittests
    sudo apt-get install python-opencv                  # for unittests
    sudo apt-get install python-dev                     # for unittest dependency builds
    sudo apt-get install memcached                      # for exercise, equation, and svg caching

    ./script/setup
    ./script/test

### Install PrinceXML

Additionally, linux users will need to install http://princexml.com (for OSX this is already installed via `brew`).


## For Osx

Install [Homebrew](https://brew.sh).

Then run:

    ./script/setup
    ./script/test   # To verify things are setup properly

    # If you run into problems, try:
    DEBUG=true ./script/setup
    DEBUG=true ./script/test

## Using Docker

### Installing Docker and Docker Compose

Follow the instructions to install [Docker](https://docs.docker.com/install/).

Follow the instructions to install [Docker Compose](https://docs.docker.com/compose/install/).

### Build a pdf using Docker Compose

1. Download an offline zip
2. Create a “data” folder in oer.exports repo (to be ignored by git)
3. Create an “entrepreneurship” folder in the “data” folder
4. Extract the downloaded complete zip into the “entrepreneurship” folder

Build the oer.exports image using docker-compose

    docker-compose build

Run the [./script/build-pdf](./script/build-pdf) script using docker-compose

    docker-compose run --rm build-pdf ./script/build-pdf entrepreneurship

### Running scripts from within the container or debugging

You'll want to keep the container from closing out immediately.

To do this look inside the [docker-compose.yml](./docker-compose.yml).

Uncomment the line mentioned in the file.

Run docker-compose so that the container starts up and stays alive:

    docker-compose up -d

Ensure that the container is running:

    docker-compose ps

Enter the container so that you can run any ad-hoc commands:
    
    docker-compose exec build-pdf /bin/bash

Stop the container from running:

    docker-compose stop

## Install Fonts

These are the fonts used in generating the PDF and EPUB files.
Prince uses TTF and OTF fonts (not Type-1 fonts which are used in newer systems).
Many are openly licensed fonts found in Ubuntu.
Some fonts can be found at http://mountainbunker.org/~ew2/fonts/truetype-open-fonts.zip

* `URW Palladio L`: http://svn.ghostscript.com/ghostscript/trunk/ghostpdl/urwfonts/ (download all 4 variants)

To test that the TTF/OTF (note Type-1) fonts were installed, run the following and verify there are no differences:

    prince -v -o /dev/null ./test-fonts.html 2>&1 | diff test-fonts.out -

## Optional: run unittests

Run the command ``python setup.py install`` to install the scripts collectiondbk2pdf and content2epub.  To run unittests use the command ``python setup.py test`` or ``python -m unittest tests.test_collectiondbk2pdf``.  There is a bug in the OpenCV library which causes the ``libdc1394 error: Failed to initialize libdc1394`` to be thrown.  Type ``sudo ln /dev/null /dev/raw1394`` to remove the driver causing the issue.

# Generate Books

Ok, let's make sure you can create a PDF and EPUB!

To generate a PDF... Let us assume that the ${book_name} is 'biology'. It needs to match one of the `./css/ccap-*.css` files.

1. Find a complete zip
1. unzip it into `./data/${book_name}/`
1. run `./script/build-pdf ${book_name} -p ${path-to-princexml-binary}`


# Building, Diffing, and Coverage

Testing and build tools use `grunt`. It can do several things:

- compile all the LESS files to CSS files
- generate HTML+CSS diffs to see how books have changed

First, you will need to create a `./config.yml` file. You can start by copying `./config.example.yml`. This file allows provides paths to all the downloaded books (unzipped comeplete ZIP files) as well as configuring some optimizations when running the tasks.

Now, we can go over the various tasks.

## Compile all the LESS files

You should run this step before pushing changes to github; fortunately it's easy. Just run `./script/build-css` and the CSS files should be generated.

**NOTE:** if you are adding a new book, you will need to add it to `./Gruntfile.coffee`.

```sh
# Generate all the CSS files
./script/build-css
```

To automatically rebuild the CSS files when you edit a `.less` file, run:

```sh
./script/build-css-watch
```

## Generate a PDF

To generate a PDF of a book run `./script/grunt shell:pdf:{BOOK_NAME}` where `{BOOK_NAME}` is configured in `./config.yml`. This will also create a directory in `./testing/` which contains the generated HTML file for development.

## Diff the Books

You can compare your CSS/XSLT changes against a book generated using the `master` branch by doing a couple of steps.
First, you will need to switch to the master branch and **prepare** a "cooked" XHTML file of the book.

**NOTE:** you will only need to prepare a book whenever the `master` branch updates!

Then, you can switch back to the development branch and compare it to what was prepared earlier.

Below is an example (assuming the book is named `calculus` and the development branch is named `dev-branch`):

```sh
# Switch to master
git checkout master

# Download the content for the calculus book (see ./books.txt)
./script/fetch-book calculus

./script/fetch-book calculus 1.1 # Download a specific version of calculus

# "prepare" the PDF and XHTML files for diffing later
./script/diff-book-prepare calculus

git checkout dev-branch

# Generate the PDF and XHTML files and see if there are any differences
./script/diff-book calculus

# To start the diff on a specific page include a page number
./script/diff-book calculus 44

# To specify a page range to start and end on
./script/diff-book calculus 44 95
```

That's it! If you want to generate diffs of all the books, you can drop the `:calculus` from `./script/grunt prepare` and `./script/grunt diff`.

**NOTE:** It will probably take several hours to diff all the books. You can speed up the process by manually generating 1 book per core.

## Generate CSS Coverage Reports

To generate a CSS coverage file (`.lcov`) and an interactive HTML report, run `./script/build-coverage ${BOOK_NAME}` after generating a PDF using `./script/build-pdf ${BOOK_NAME}`.

This will create or update (if a report already exists) a report in `./coverage/`.


# Overview

## Content Workflow

1. vendors (WiseWire, 6RedMarbles) hire Subject Matter Experts (SMEs) to write a textbook as a series of Word documents with markup like `[H1] Kinematics in 9 Dimensions`
1. these vendors subcontract to people to convert the Word Docs into CNXML files which are stored on a **Legacy** Staging Server
1. PDFs are generated on the Staging Server for Quality Assurance
1. When content production is complete and the book is ready to be published, Content Managers (CMs) migrate the CNXML files from the Staging Server and onto Production
    - Among the many things that happen in this step, one is to rewrite the links because module id's on Staging and Production are different
1. Developers download a Complete Zip from the Legacy Staging Server or Legacy production so they can generate PDFs locally. Example: http://legacy-textbook-dev.cnx.org/content/col10128/1.12/content_info#cnx_downloads_header . The legacy links are common because CM's work with those URLs and they tend to provide these links.


## Tools

The PDF generation system uses the following additional tools:
- [Docbook](http://www.sagehill.net/docbookxsl/index.html) for generating the Table of Contents, Index, footnotes, and other bookish pieces
- [PrinceXML](http://www.princexml.com/doc/) to convert HTML+CSS into a PDF
- [XSLT](https://en.wikipedia.org/wiki/XSLT) and [specification](https://www.w3.org/TR/xslt) to convert [CNXML](https://legacy.cnx.org/eip-help/tags) to Docbook and eventually to XHTML
- [LESSCSS](http://lesscss.org/) to write the PrinceXML-specific CSS
- [nodejs](https://nodejs.org) to run scripts to generate CSS files and other utilities


## Terminology

- **complete zip**: A Zip file containing all the Textbook Content needed to create a PDF (or other file formats). For details on how this file is used see [complete zip data](#completezipdata)
- **collection**: A legacy name for a Book
- **module**: A legacy name for a Page in a book (something smaller than a Chapter, but larger than a Paragraph)
- **cnxml**: The XML format used for marking up a Page in a Book
- **collxml**: The XML format used for marking up the Table of Contents for a Book
- **MathML**: An XML format used for marking up Math content
- **SVG**:
- **PNG**:
- **XHTML**: Similar to HTML but it is easily machine-parseable
- **pipeline**: A series of transformations that convert a set of CNXML files into an XHTML file
- **ccap**: Legacy name used for the initial set of books generated using this method
- **legacy**: An old user interface for editing textbook content. It is slow but used by Content Managers and subcontractors
- **webview**: What a user sees when they visit https://cnx.org
- **archive**: The read-only server for https://cnx.org
- **environment**: A set of servers that talk to each other. Used for QA, development, or content-entry


## Styling

**TODO:** (describe how the CSS files are organized)


## Transformations

The PDF-generation process begins with a [Complete Zip](https://github.com/openstax/book-tools/blob/master/terms.md) and results in a PDF document. Here are the steps:

Follow the instructions in https://github.com/Connexions/ost-the-dark-side/blob/master/29.-Generating-PDFs-Locally.md

1. Download a complete zip and extract it to a directory (ie `col123_complete`)
1. Run https://github.com/Connexions/oer.exports/blob/master/collectiondbk2pdf.py (see file for command line arguments)
  - optionally, there is a debug flag that will output some of the intermediary Docbook (`.dbk`) files
1. The previous step will do the following:
  1. convert the `.cnxml` files to `.dbk` files
  1. convert the MathML in  the `.cnxml` files into `.svg` and `.png` files using http://pmml2svg.sf.net stored at [./xslt2/](./xslt2/)
  1. convert the `.collxml` file to a big `.dbk` file using [XInclude](https://www.w3.org/TR/xinclude/)
  1. convert the big `.dbk` file to an `.xhtml` file
  1. convert the `.xhtml` file plus the CSS file in [./css/](./css/) into a PDF using PrinceXML



Here are the steps in more detail:

Call [./collectiondbk2pdf.py](./collectiondbk2pdf.py) which runs:

1. [./collection2dbk.py](./collection2dbk.py) which runs:
    1. [./xsl/collxml2dbk.xsl](./xsl/collxml2dbk.xsl) converts the "Table of Contents" file into a Docbook file with a bunch of XInclude links
    1. For every [Module in the Book](https://github.com/openstax/book-tools/blob/master/terms.md#page), call [./module2dbk.py](./module2dbk.py) which runs:
        1. [./xsl/cnxml-clean.xsl](./xsl/cnxml-clean.xsl) normalizes some attributes and elements
        1. [./xsl/cnxml-clean-math.xsl](./xsl/cnxml-clean-math.xsl) normalizes the MathML so the pmml2svg conversion does not crash
        1. [./xsl/cnxml-clean-math.xsl](./xsl/cnxml-clean-math.xsl) runs again to remove now-empty elements
        1. [./xsl/cnxml-clean-math-simplify.xsl](./xsl/cnxml-clean-math-simplify.xsl) SVG inside PDF files significantly increases the size of the PDF. If the Math is "simple" (numbers, letters, sub/superscript) then just convert it to HTML
        1. [./xsl/cnxml2dbk.xsl](./xsl/cnxml2dbk.xsl) converts CNXML elements to Docbook+ elements
            - the `+` is because Exercises have no direct representation in Docbook
        1. Convert [MathML to SVG](./module2dbk.py) by calling a service
        1. [./xsl/dbk-clean.xsl](./xsl/dbk-clean.xsl) adjust Math SVG baseline so formulas line up vertically with the surrounding text
        1. Downsample [Images](./module2dbk.py) to reduce the file size of the resulting PDF
        1. Convert [SVG to PNG](./module2dbk.py)
        1. [./xsl/dbk-svg2png.xsl](./xsl/dbk-svg2png.xsl) cleans up the image attributes now that the MathML has the additional SVG and PNG formats available in the content

    1. [./xsl/dbk2epub-normalize-paths.xsl](./xsl/dbk2epub-normalize-paths.xsl) Adjusts the `<img src=` attribute to point to the image file since the `.dbk` will be XIncluded into a giant `.dbk` file.
        - It also creates a list of book authors, publishers, copyright holders, and sets the version on modules that do not have a version in the CNXML file
    1. [./xsl/dbk-clean-whole.xsl](./xsl/dbk-clean-whole.xsl) unwraps the now XIncluded modules, generates a Chapter-level Glossary, converts external links to really be external
    1. [./xsl/dbk-clean-whole-remove-duplicate-glossentry.xsl](./xsl/dbk-clean-whole-remove-duplicate-glossentry.xsl) removes duplicate glossary entries (added in the previous step) and adds an Attribution section at the end of the book

1. [./xsl/dbk-clean-whole.xsl](./xsl/dbk-clean-whole.xsl) runs again, not sure why
1. [./xsl/dbk2xhtml.xsl](./xsl/dbk2xhtml.xsl) configures Docbook by setting parameters, overrides some Docbook-to-HTML conversions, and performs the Docbook conversion
1. [./xsl/xhtml-dedup-svg.xsl](./xsl/xhtml-dedup-svg.xsl) Removes duplicate SVG elements (BUG?)
1. [./xsl/dedup-references.xsl](./xsl/dedup-references.xsl) Removes references inside a Citation
1. Convert HTML+CSS to PDF using PrinceXML


# Complete Zip Data

The Zip file contains the following interesting files which are frequently tweaked for testing:

- `collection.xml` This is the Table of Contents of the book. It links to individual pages in a book and specifies the chapters/appendixes in the book. It can be edited to make a much smaller book for development/testing

- `index_auto_generated.cnxml` These files contain the book content. To test styling changes locally content can be edited by changing these files. The XML format still needs to follow the format described in https://legacy.cnx.org/eip-help/tags
