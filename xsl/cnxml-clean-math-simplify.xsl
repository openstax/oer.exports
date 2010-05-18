<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:c="http://cnx.rice.edu/cnxml"
  exclude-result-prefixes="c mml">

<xsl:import href="debug.xsl"/>

<xsl:param name="cnx.log.onlyaggregate">yes</xsl:param>

<xsl:output indent="yes" method="xml" omit-xml-declaration="yes"/>

<!-- Identity Transform -->
<xsl:template match="@*|node()">
   <!-- xsl:copy -->
      <xsl:apply-templates select="@*|node()"/>
   <!-- /xsl:copy -->
</xsl:template>


<xsl:template match="mml:math">
	<!-- Check if we can simplify it (convert the math to cnxml) -->
	<xsl:variable name="isComplex">
		<xsl:apply-templates mode="cnx.iscomplex" select="."/>
	</xsl:variable>
	<xsl:choose>
		<xsl:when test="normalize-space($isComplex)!=''">
			<xsl:call-template name="cnx.log"><xsl:with-param name="msg">INFO: MathML too complex because of <xsl:value-of select="$isComplex"/></xsl:with-param></xsl:call-template>
			<!-- xsl:copy -->
				<xsl:apply-templates select="@*|node()"/>
			<!-- /xsl:copy -->
		</xsl:when>
		<xsl:otherwise>
			<xsl:call-template name="cnx.log"><xsl:with-param name="msg">INFO: MathML is simple!</xsl:with-param></xsl:call-template>
			<xsl:apply-templates mode="cnx.simplify" select="."/>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<!-- Terminal nodes that we don't need to recurse down and are NOT complex -->
<xsl:template mode="cnx.iscomplex" match="text()|mml:annotation-xml"/>

<!-- Terminal nodes that are NOT complex but we should recurse just to be safe -->
<xsl:template mode="cnx.iscomplex" match="mml:mn|mml:mi|mml:mo">
	<xsl:apply-templates mode="cnx.iscomplex"/>
</xsl:template>

<!-- Non-terminal nodes that MAY be complex, but that we support -->
<xsl:template mode="cnx.iscomplex" match="mml:mrow|mml:semantics|mml:msub|mml:msup|mml:msubsup|mml:math[not(@display='block')]"> 
	<xsl:apply-templates mode="cnx.iscomplex"/>
</xsl:template>

<!-- Non-terminal nodes that MUST be complex (everything else) -->
<xsl:template mode="cnx.iscomplex" match="*">
	<xsl:value-of select="local-name()"/>
	<xsl:text>|</xsl:text>
</xsl:template>




<!-- Below are the conversions -->


<xsl:template mode="cnx.simplify" match="mml:math">
	<c:span class="simplemath">
		<xsl:apply-templates mode="cnx.simplify" select="node()"/>
	</c:span>
</xsl:template>


<xsl:template mode="cnx.simplify" match="mml:mi">
	<c:emphasis class="mi">
		<xsl:apply-templates mode="cnx.simplify" select="node()"/>
	</c:emphasis>
</xsl:template>

<xsl:template mode="cnx.simplify" match="mml:mo|mml:mn|mml:mtext">
	<xsl:apply-templates mode="cnx.simplify" select="node()"/>
</xsl:template>

<xsl:template mode="cnx.simplify" match="mml:msup">
	<xsl:apply-templates mode="cnx.simplify" select="*[1]"/>
	<c:sup>
		<xsl:apply-templates mode="cnx.simplify" select="*[2]"/>
	</c:sup>
</xsl:template>

<xsl:template mode="cnx.simplify" match="mml:msub">
	<xsl:apply-templates mode="cnx.simplify" select="*[1]"/>
	<c:sub>
		<xsl:apply-templates mode="cnx.simplify" select="*[2]"/>
	</c:sub>
</xsl:template>

<xsl:template mode="cnx.simplify" match="mml:msubsup">
	<xsl:apply-templates mode="cnx.simplify" select="*[1]"/>
	<c:sub>
		<xsl:apply-templates mode="cnx.simplify" select="*[2]"/>
	</c:sub>
	<c:sup>
		<xsl:apply-templates mode="cnx.simplify" select="*[3]"/>
	</c:sup>
</xsl:template>


<!-- Just pass through -->
<xsl:template mode="cnx.simplify" select="mml:mrow|mml:semantics">
	<xsl:apply-templates mode="cnx.simplify"/>
</xsl:template>

</xsl:stylesheet>
