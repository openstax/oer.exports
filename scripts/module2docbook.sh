#!/bin/sh

COL_PATH=$1
MOD_NAME=$2
MOD_PATH=$COL_PATH/$MOD_NAME

echo "Working on $MOD_NAME"

# If XSLTPROC_ARGS is set (by say a hadoop job) then pass those through

ROOT=`dirname "$0"`
ROOT=`cd "$ROOT/.."; pwd` # .. since we live in scripts/

SCHEMA=$ROOT/docbook-rng/docbook.rng
SAXON="java -jar $ROOT/lib/saxon9he.jar"
JING="java -jar $ROOT/lib/jing-20081028.jar"
XSLTPROC="xsltproc --nonet --stringparam moduleId $MOD_NAME $XSLTPROC_ARGS"

#Temporary files
CNXML=$MOD_PATH/index.cnxml
CNXML1=$MOD_PATH/cnxml1.xml
CNXML2=$MOD_PATH/cnxml2.xml
CNXML3=$MOD_PATH/cnxml3.xml
DOCBOOK=$MOD_PATH/index.dbk # Important. Used in collxml2docbook xinclude
DOCBOOK1=$MOD_PATH/index1.dbk
DOCBOOK2=$MOD_PATH/index2.dbk
VALID=$MOD_PATH/valid.dbk

#XSLT files
CLEANUP_XSL=$ROOT/xsl/cnxml-cleanup.xsl
CLEANUP2_XSL=$ROOT/xsl/cnxml-cleanup-mathml.xsl
CNXML2DOCBOOK_XSL=$ROOT/xsl/cnxml2docbook.xsl
DOCBOOK_CLEANUP_XSL=$ROOT/xsl/docbook-cleanup.xsl
DOCBOOK_VALIDATION_XSL=$ROOT/xsl/docbook-cleanup-for-validation.xsl
MATH2SVG_XSL=$ROOT/xslt2/math2svg-in-docbook.xsl

# Load up the custom params to xsltproc:
if [ -s params.txt ]; then
    echo "Using the following additional params to xsltproc:"
    cat params.txt
    OLD_IFS=$IFS
    IFS="
"
    XSLTPROC_ARGS=""
    for ARG in `cat params.txt`; do
      XSLTPROC_ARGS="$XSLTPROC_ARGS --param $ARG"
    done
    IFS=$OLD_IFS
    XSLTPROC="$XSLTPROC $XSLTPROC_ARGS"
fi


# Just some code to filter what gets re-converted so all modules don't have to.
#GREP_FOUND=`grep "newline" $CNXML`
#if [ ".$GREP_FOUND" == "." ]; then exit 0; fi

# First check that the XML file is well-formed
#XMLVALIDATE="xmllint --nonet --noout --valid --relaxng /Users/schatz/Documents/workspace/cnx-schema/cnxml.rng"
XMLVALIDATE="xmllint --nonet --noout"
#$XMLVALIDATE $CNXML 2> /dev/null
#if [ $? -ne 0 ]; then exit 0; fi
($XMLVALIDATE $CNXML 2>&1) > $MOD_PATH/__err.txt
if [ -s $MOD_PATH/__err.txt ]; 
then 
  echo "Invalid cnxml doc" 1>&2
  rm $MOD_PATH/__err.txt
  exit 0
fi
rm $MOD_PATH/__err.txt



$XSLTPROC -o $CNXML1 $CLEANUP_XSL $CNXML
$XSLTPROC -o $CNXML2 $CLEANUP2_XSL $CNXML1
# Have to run the cleanup twice because we remove empty mml:mo,
# then remove mml:munder with only 1 child.
# See m21903
$XSLTPROC -o $CNXML3 $CLEANUP2_XSL $CNXML2

# Convert to docbook
$XSLTPROC -o $DOCBOOK1 $CNXML2DOCBOOK_XSL $CNXML3

# Convert MathML to SVG
$SAXON -s:$DOCBOOK1 -xsl:$MATH2SVG_XSL -o:$DOCBOOK2
# If there is an error, just use the original file
MATH2SVG_ERROR=$?
if [ $MATH2SVG_ERROR -ne 0 ]; then mv $DOCBOOK1 $DOCBOOK2; fi
if [ $MATH2SVG_ERROR -eq 0 ]; then 
  rm $CNXML1
  rm $CNXML2
  rm $CNXML3
  rm $DOCBOOK1
fi

$XSLTPROC -o $DOCBOOK $DOCBOOK_CLEANUP_XSL $DOCBOOK2
rm $DOCBOOK2

# Create a file to validate against
$XSLTPROC -o $VALID $DOCBOOK_VALIDATION_XSL $DOCBOOK

# Validate
$JING $SCHEMA $VALID # 1>&2 # send validation errors to stderr
RET=$?
if [ $RET -eq 0 ]; then rm $VALID; fi
if [ $RET -eq 0 ]; then echo "BUG: Validation Errors" 1>&2 ; fi

exit $MATH2SVG_ERROR || $RET
