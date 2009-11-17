#!/bin/sh

COL_PATH=$1
MOD_NAME=$2
MOD_PATH=$COL_PATH/$MOD_NAME

ROOT=.
SCHEMA=docbook-rng/docbook.rng
SAXON="java -jar $ROOT/lib/saxon9he.jar"
JING="java -jar $ROOT/lib/jing-20081028.jar"
XSLTPROC="xsltproc --stringparam moduleId $MOD_NAME"

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
$JING $SCHEMA $VALID
RET=$?
if [ $RET -eq 0 ]; then rm $VALID; fi

exit $MATH2SVG_ERROR || $RET
