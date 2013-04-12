#!/bin/sh

# Copyright (c) 2013 Rice University
#
# This software is subject to the provisions of the GNU AFFERO GENERAL PUBLIC LICENSE Version 3.0 (AGPL).
# See LICENSE.txt for details.

# See the docs/link-checker.txt for info on how to use this alpha-level script

DBK_FILE=$1

ROOT=`dirname "$0"`
ROOT=`cd "$ROOT/.."; pwd` # .. since we live in scripts/

XSLTPROC="xsltproc"

LINK_CHECKER_XSL=$ROOT/xsl/debug/link-checker.xsl

$XSLTPROC $LINK_CHECKER_XSL $DBK_FILE 
