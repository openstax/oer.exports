#!/bin/sh

COL_PATH=$1

ROOT=`dirname "$0"`
ROOT=`cd "$ROOT/.."; pwd` # .. since we live in scripts/

COLLXML=$COL_PATH/collection.xml
DOCBOOK=$COL_PATH/collection.dbk

XSLTPROC="xsltproc --nonet"
COLLXML2DOCBOOK_XSL=$ROOT/xsl/collxml2docbook.xsl
MODULE2DOCBOOK=$ROOT/scripts/module2docbook.sh

# If the docbook for the collection doesn't exist yet, create it
if [ ! -e $DOCBOOK ]; 
then 
  $XSLTPROC -o $DOCBOOK $COLLXML2DOCBOOK_XSL $COLLXML
fi

# For each module, generate a docbook file
for MODULE in `ls $COL_PATH`
do
  if [ -d $COL_PATH/$MODULE ];
  then
    echo "Processing $MODULE"
    bash $MODULE2DOCBOOK $COL_PATH $MODULE
  fi
done
