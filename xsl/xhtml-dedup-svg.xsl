<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns:x="http://www.w3.org/1999/xhtml"
  xmlns="http://www.w3.org/1999/xhtml"
  version="1.0">

<!-- This file finds any duplicated svgs, that occur somehow from the mathml -> svg conversion -->

<xsl:include href="ident.xsl"/>

<xsl:template match="//x:span[contains(@class,'cnx-svg')]/svg:svg[preceding-sibling::svg:svg]"/>

</xsl:stylesheet>
