#!/bin/sh

# 1st arg is the path to the collection
# 2nd arg (optional) is the module name

echo "NOTE: You will need to set 'cnx.output xhtml' in params.txt"
echo "Sleeping for 5 seconds..."
sleep 5

COL_PATH=$1

ROOT=`dirname "$0"`
ROOT=`cd "$ROOT/.."; pwd` # .. since we live in scripts/



if [ ".$2" != "." ]; then 
  MODULE=$2;
  bash $ROOT/scripts/module2dbk.sh $COL_PATH $MODULE
  DBK_FILE=$COL_PATH/$MODULE/index.dbk
  EPUB_FILE=$COL_PATH/$MODULE.epub.zip
else
  MODULES=`ls $COL_PATH`
  bash $ROOT/scripts/collection2dbk.sh $COL_PATH
  DBK_FILE=$COL_PATH/collection.dbk
  EPUB_FILE=$COL_PATH.epub.zip
fi


echo $ROOT/docbook-xsl/epub/bin/dbtoepub --stylesheet $ROOT/xsl/dbk2epub.xsl -d $DBK_FILE -o $EPUB_FILE

$ROOT/docbook-xsl/epub/bin/dbtoepub --stylesheet $ROOT/xsl/dbk2epub.xsl -d $DBK_FILE -o $EPUB_FILE
