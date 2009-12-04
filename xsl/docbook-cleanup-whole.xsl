<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:c="http://cnx.rice.edu/cnxml"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  version="1.0">

<xsl:import href="debug.xsl"/>
<xsl:output indent="yes" method="xml"/>
<xsl:param name="moduleId"/>

<!-- Boilerplate -->
<xsl:template match="/">
	<xsl:apply-templates select="*"/>
</xsl:template>
<!-- Identity Transform -->
<xsl:template match="@*|node()">
   <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
   </xsl:copy>
</xsl:template>


<!-- If the Module title starts with the chapter title then discard it. -->
<xsl:template match="db:chapter/db:section">
	<xsl:choose>
		<xsl:when test="starts-with(db:title/text(), ../db:title/text())">
			<xsl:call-template name="cnx.log"><xsl:with-param name="msg">WARNING: Stripping chapter name from title</xsl:with-param></xsl:call-template>
			<xsl:copy>
				<xsl:copy-of select="@*"/>
				<xsl:apply-templates mode="strip-title" select="db:title"/>
				<xsl:apply-templates select="*[local-name()!='title']|processing-instruction()|comment()"/>
			</xsl:copy>
		</xsl:when>
		<xsl:otherwise>
			<xsl:copy>
				<xsl:copy-of select="@*"/>
				<xsl:apply-templates/>
			</xsl:copy>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>
<xsl:template mode="strip-title" match="db:title">
	<xsl:variable name="chapTitle">
		<xsl:value-of select="../../db:title/text()"/>
		<xsl:text>: </xsl:text>
	</xsl:variable>
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:for-each select="node()">
			<xsl:choose>
				<xsl:when test="position()=1">
					<xsl:value-of select="substring-after(., $chapTitle)"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates select="."/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:for-each>
	</xsl:copy>
</xsl:template>

<!-- Combine all module glossaries into a single book glossary -->
<xsl:template match="db:book">
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates/>
		<xsl:if test="//db:chapter/db:section/db:glossary">
			<db:glossary>
				<xsl:apply-templates select="//db:chapter/db:section/db:glossary/*"/>
			</db:glossary>
		</xsl:if>
	</xsl:copy>
</xsl:template>
<!-- Discard matches for db:chapter/db:section/db:glossary -->
<xsl:template match="db:chapter/db:section/db:glossary">
	<!-- Discard this. it's handled in match="db:book" -->
</xsl:template>


</xsl:stylesheet>