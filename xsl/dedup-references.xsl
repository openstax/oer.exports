<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns:x="http://www.w3.org/1999/xhtml"
  xmlns="http://www.w3.org/1999/xhtml"
  version="1.0">

<!-- This file removes any references inside citation links. -->

<xsl:include href="ident.xsl"/>

<xsl:template match="//x:a[contains(@class, 'cite')]/x:div[contains(@class, 'reference')]">
    <xsl:message>Cleaning up reference inside citation.</xsl:message>
</xsl:template>

</xsl:stylesheet>
