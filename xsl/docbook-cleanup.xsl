<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/"
  version="1.0">

<xsl:import href="debug.xsl"/>
<xsl:output omit-xml-declaration="yes" indent="yes" method="xml"/>
<xsl:param name="moduleId"/>

<xsl:template match="node()|comment()">
    <xsl:copy>
    	<xsl:copy-of select="@*"/>
        <xsl:apply-templates select="node()|comment()"/>
    </xsl:copy>
</xsl:template>

<xsl:template mode="copy" match="node()|comment()">
    <xsl:copy>
    	<xsl:copy-of select="@*"/>
        <xsl:apply-templates select="node()|comment()"/>
    </xsl:copy>
</xsl:template>


<xsl:template match="db:inlinemediaobject[.//mml:math]">
	<xsl:call-template name="debug"><xsl:with-param name="str">BUG: Inline MathML Not converted</xsl:with-param></xsl:call-template>
	<xsl:text>[ERROR: MathML not converted]</xsl:text>
</xsl:template>

<xsl:template match="db:mediaobject[.//mml:math]">
	<xsl:call-template name="debug"><xsl:with-param name="str">BUG: MathML Not converted</xsl:with-param></xsl:call-template>
	<db:para>[ERROR: MathML not converted]</db:para>
</xsl:template>


<!-- move neighboring db:qandaset elements together.
	Currently done very hackishly because we don't want to
	group text or other elements into
 -->
<xsl:template match="*[count(db:qandaset[not(db:title) and count(db:qandaentry)=1])>1]">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Moving exercises to bottom of module</xsl:with-param></xsl:call-template>
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates select="comment()|text()|db:qandaset[db:title or not(count(db:qandaentry)=1)]|*[local-name()!='qandaset']"/>
		<db:qandaset>
			<xsl:apply-templates select="db:qandaset[not(db:title) and count(db:qandaentry)=1]/db:qandaentry"/>
		</db:qandaset>
	</xsl:copy>
</xsl:template>

<!-- Boilerplate -->
<xsl:template match="/">
	<xsl:apply-templates select="*"/>
</xsl:template>


</xsl:stylesheet>
