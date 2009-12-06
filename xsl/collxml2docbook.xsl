<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:col="http://cnx.rice.edu/collxml"
  xmlns:md="http://cnx.rice.edu/mdml"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:xi='http://www.w3.org/2001/XInclude'
  exclude-result-prefixes="col md"
  >
<xsl:include href="cnxml2docbook.xsl"/>

<xsl:output indent="yes"/>

<xsl:template match="col:*/@*">
	<xsl:copy/>
</xsl:template>

<xsl:template match="col:collection">
	<db:book><xsl:apply-templates select="@*|node()"/></db:book>
</xsl:template>

<xsl:template match="col:metadata">
	<db:info><xsl:apply-templates select="@*|node()"/></db:info>
</xsl:template>

<xsl:template match="col:subcollection[col:content/col:subcollection]">
	<db:part><xsl:apply-templates select="@*|node()"/></db:part>
</xsl:template>

<xsl:template match="col:subcollection/col:content/col:subcollection[not(col:content/col:subcollection)]|col:subcollection">
	<db:chapter><xsl:apply-templates select="@*|node()"/></db:chapter>
</xsl:template>

<xsl:template match="col:content">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="col:module[@document]">
	<xi:include href="{@document}/index.dbk"/>
</xsl:template>


<xsl:template match="md:title">
	<db:title><xsl:apply-templates/></db:title>
</xsl:template>



<xsl:template match="comment()|processing-instruction()">
    <xsl:copy/>
</xsl:template>

</xsl:stylesheet>
