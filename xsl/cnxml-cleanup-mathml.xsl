<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:c="http://cnx.rice.edu/cnxml"
xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/"
    exclude-result-prefixes="c">

<xsl:import href="debug.xsl"/>
<xsl:output omit-xml-declaration="yes" indent="yes" method="xml"/>
<xsl:param name="moduleId"/>

<!-- Boilerplate -->
<xsl:template match="/">
    <xsl:apply-templates/>
</xsl:template>
<xsl:template match="*|@*|comment()|text()">
	<xsl:copy>
	    <xsl:copy-of select="@*"/>
    	<xsl:apply-templates select="*|comment()|text()"/>
    </xsl:copy>
</xsl:template>

<!-- Remove empty mml:mo -->
<xsl:template match="mml:mo[normalize-space(text())='']">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Removing whitespace mml:mo from c2p transform</xsl:with-param></xsl:call-template>
</xsl:template>


<!-- pmml2svg chokes on this -->
<xsl:template match="mml:mo[string-length(normalize-space(text())) > 1]">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: mml:mo contains more than 1 character and pmml2svg doesn't like that. '<xsl:value-of select="normalize-space(text())"/>'</xsl:with-param></xsl:call-template>
	<mml:mtext>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates/>
	</mml:mtext>
</xsl:template>

<!-- pmml2svg chokes on this.
	See: m21852
	Can't just remove mml:mi because it could be in a mml:msub
 -->
<xsl:template match="mml:mi[count(*)=0 and normalize-space(text())='']">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Converting empty mml:mi to a mml:mspace</xsl:with-param></xsl:call-template>
	<mml:mspace />
</xsl:template>


<!-- pmml2svg Does not support certain nodes yet. Display an error and use the non-embellished child.
	See: m21852
 -->
<xsl:template match="mml:mmultiscripts|mml:mlabeledtr|mml:mpadded|mml:mglyph">
	<xsl:call-template name="debug"><xsl:with-param name="str">ERROR: Cannot convert this node to SVG (for PDF generation). Please try to use something else</xsl:with-param></xsl:call-template>
	<xsl:apply-templates select="mml:*[1]"/>
</xsl:template>


<!-- Make sure only Presentation MathML is left. All presentation MathML starts with 'm' or is the element 'none'
	Unfortunately, pmml2svg can't handle the element mml:none. so, we'll convert mml:none to mml:mspace
    match="*[namespace-uri(.)='http://www.w3.org/1998/Math/MathML' and (not(starts-with(local-name(.), 'm')) or 'none'=local-name(.))]"
    See: m21852
-->
<xsl:template match="mml:none" priority="100">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Converting mml:none to a mml:mspace</xsl:with-param></xsl:call-template>
	<mml:mi>.</mml:mi>
</xsl:template>
<!-- Make sure only Presentation MathML is left. All presentation MathML starts with 'm' or is the element 'none' -->
<xsl:template match="*[namespace-uri(.)='http://www.w3.org/1998/Math/MathML' and not(starts-with(local-name(.), 'm'))]">
	<xsl:call-template name="debug"><xsl:with-param name="str">BUG: Found some Content MathML that seeped through. <xsl:value-of select="namespace-uri(.)"/>^<xsl:value-of select="local-name(.)"/></xsl:with-param></xsl:call-template>
	<mml:mi>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates/>
	</mml:mi>
</xsl:template>

<xsl:template match="mml:apply" priority="100">
	<xsl:call-template name="debug"><xsl:with-param name="str">BUG: Found some Content MathML that seeped through. mml:apply</xsl:with-param></xsl:call-template>
	<mml:mspace/>
</xsl:template>

<xsl:template match="mml:cn" priority="100">
	<xsl:call-template name="debug"><xsl:with-param name="str">BUG: Found some Content MathML that seeped through. mml:cn</xsl:with-param></xsl:call-template>
	<mml:mn>
		<xsl:apply-templates select="text()"/>
	</mml:mn>
</xsl:template>

<!-- For some reason the mml:* pass the RNG but still only have 1 child. -->
<xsl:template match="mml:munder[count(*)=1]" priority="100">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: mml:munder only has 1 child. Unwrapping the element</xsl:with-param></xsl:call-template>
	<xsl:apply-templates/>
</xsl:template>

<!-- 
	pmml2svg cannot handle mml:mtable with different numbers of mml:mtd.
	So, pad them.
	See: m21927
 -->
<xsl:template match="mml:mtable">
	<!-- Will be != '' if there is a row that doesn't match -->
	<xsl:variable name="mtdCount" select="count(mml:mtr[1]/mml:mtd)"/>
	<xsl:variable name="mismatchedMtdCount">
		<xsl:for-each select="mml:mtr">
			<xsl:if test="count(mml:mtd) != $mtdCount">
				<xsl:text>.</xsl:text>
			</xsl:if>
		</xsl:for-each>
	</xsl:variable>
	<xsl:choose>
		<xsl:when test="$mismatchedMtdCount">
			<xsl:call-template name="debug"><xsl:with-param name="str">ERROR: Mismatched number of mml:mtd in the mml:mtable. Discarding mml:mtable</xsl:with-param></xsl:call-template>
			<mml:mtext>[ERROR: Mismatched number of mml:mtd in the mml:mtable]</mml:mtext>
		</xsl:when>
		<xsl:otherwise>
			<xsl:copy>
				<xsl:copy-of select="@*"/>
				<xsl:apply-templates/>
			</xsl:copy>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

</xsl:stylesheet>
