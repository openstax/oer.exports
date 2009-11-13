#!/bin/sh

COL_PATH=$1

ROOT=`pwd`

FOP_OPTS=-Xmx14000M # FOP Needs a lot of memory (4+Gb for Elementary Algebra)
DOCBOOK=$COL_PATH/collection.dbk
DOCBOOK2=$COL_PATH/collection.cleaned.dbk
UNALIGNED=$COL_PATH/collection.unaligned.fo
FO=collection.fo
PDF=collection.pdf

XSLTPROC=xsltproc
FOP="sh $ROOT/fop/fop -c $ROOT/lib/fop.xconf"

# XSL files
DOCBOOK_CLEANUP_XSL=$ROOT/xsl/docbook-cleanup-whole.xsl
DOCBOOK2FO_XSL=$ROOT/xsl/docbook2fo.xsl
ALIGN_XSL=$ROOT/xsl/postprocess-svg.xsl


$XSLTPROC --xinclude -o $DOCBOOK2 $DOCBOOK_CLEANUP_XSL $DOCBOOK

time $XSLTPROC -o $UNALIGNED $DOCBOOK2FO_XSL $DOCBOOK2
$XSLTPROC -o $COL_PATH/$FO $ALIGN_XSL $UNALIGNED

# Change to the collection dir so the relative paths to images work
cd $COL_PATH
time $FOP $FO $PDF
cd $ROOT
