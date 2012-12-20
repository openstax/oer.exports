#!/bin/bash
# NOTE: corresponding test collections should reside within oer.exporst/test-ccap directory
# evince is an open source document viewer for multiple document formats
# ex: oer.exports/test-ccap/colbiology
#     oer.exports/test-ccap/colsociology
# only passing one parameter which should be subject title
# acceptable values for first parameter:
# 1 - physics
# 2 - sociology
# 3 - biology
# 4 - biology-non-majors


COMPILE_CSS=$(lessc css/ccap-$1.less > css/ccap-$1.css) #todo: add error handling for less compile errors
GENERATE_PDF=$(python collectiondbk2pdf.py -v -s ccap-$1 -d ./test-ccap/col$1 $1.pdf -t tempdir)
VIEW_PDF=$(evince $1.pdf) 
 
echo $COMPILE_CSS
echo $GENERATE_PDF
echo $VIEW_PDF
exit $?