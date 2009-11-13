#!/bin/sh

for MODULE in `ls`
do
    if [ -d $MODULE ];
    then
        echo "Converting $MODULE"
        xsltproc ../docbook-xsl-1.75.2/fo/docbook.xsl $MODULE/index.dbk > $MODULE/index.dbk.fo 2> $MODULE/_err.log
        xsltproc ../xsl/postprocess-svg.xsl $MODULE/index.dbk.fo > $MODULE/index.dbk.aligned.fo 2> /dev/null
        ../dita/demo/fo/fop/fop -c ../dita/demo/fo/fop/conf/fop.xconf $MODULE/index.dbk.aligned.fo $MODULE/index.dbk.aligned.fo.pdf > $MODULE/_fop.log 2> $MODULE/_fop.err.log
        ERR_CODE=$?

        rm $MODULE/_err.txt 2> /dev/null
        if [ $ERR_CODE -eq 0 ];
        then
            rm $MODULE/_err.log 2> /dev/null
            rm $MODULE/_fop.log 2> /dev/null
            rm $MODULE/_fop.err.log 2> /dev/null
            rm $MODULE/index.dbk.fo 2> /dev/null
            rm $MODULE/index.dbk.aligned.fo 2> /dev/null
        fi
        if [ $ERR_CODE -ne 0 ];
        then
            echo "Error generating pdf"
        fi
    fi
done
