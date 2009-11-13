<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:col="http://cnx.rice.edu/collxml"
  xmlns:md="http://cnx.rice.edu/mdml"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:xi='http://www.w3.org/2001/XInclude'
  exclude-result-prefixes="col md"
  >
  
<xsl:output indent="yes"/>

<!-- Boilerplate -->
<xsl:template match="/">
    <xsl:apply-templates select="col:collection"/>
</xsl:template>

<xsl:template match="col:collection">
	<db:book>
      <xsl:apply-templates/>
    </db:book>
</xsl:template>

<xsl:template match="col:subcollection[col:content/col:subcollection]">
	<db:part>
		<xsl:apply-templates/>
	</db:part>
</xsl:template>

<xsl:template match="col:subcollection/col:content/col:subcollection[not(col:content/col:subcollection)]|col:subcollection">
	<db:chapter>
		<xsl:apply-templates/>
	</db:chapter>
</xsl:template>

<xsl:template match="col:content">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="col:module">
	<xi:include href="{@document}/index.dbk"/>
</xsl:template>


<xsl:template match="md:title">
	<db:title><xsl:apply-templates/></db:title>
</xsl:template>


<!-- Catch-all -->
<xsl:template match="*">
	<xsl:message>
		<xsl:text>WARNING: </xsl:text>
		<xsl:text>Could not match Element: </xsl:text>
	  	<xsl:value-of select="namespace-uri(.)"/>
	  	<xsl:text> </xsl:text>
	  	<xsl:value-of select="local-name(.)"/>
	  	<xsl:for-each select="@*">
		  	<xsl:text> @</xsl:text>
	  		<xsl:value-of select="local-name(.)"/>
		  	<xsl:text>="</xsl:text>
	  		<xsl:value-of select="."/>
		  	<xsl:text>"</xsl:text>
	  	</xsl:for-each>
  </xsl:message>
</xsl:template>

<xsl:template match="comment()">
    <xsl:copy-of select="."/>comment
</xsl:template>

</xsl:stylesheet>
