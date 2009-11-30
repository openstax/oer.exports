<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:c="http://cnx.rice.edu/cnxml"
xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/"
    exclude-result-prefixes="c">

<xsl:import href="debug.xsl"/>
<xsl:output omit-xml-declaration="yes" indent="yes" method="xml"/>
<xsl:param name="moduleId"/>

<!-- Convert Content MathML to Presentation MathML -->
<xsl:include href="c2p.xsl"/>

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

<xsl:template match="root">
	<xsl:apply-templates/>
</xsl:template>
<xsl:template match="c:metadata"/>

<!--  Fix some CNXML 0.5 stuff -->
<xsl:template match="c:link[@src]">
	<c:link url="{@src}">
		<xsl:apply-templates/>
	</c:link>
</xsl:template>

<xsl:template match="c:media[@src]">
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:if test="c:param[@name='alt']">
			<xsl:attribute name="alt"><xsl:value-of select="c:param[@name='alt']/@value"/></xsl:attribute>
		</xsl:if>
		<c:image>
			<xsl:copy-of select="@*"/>
			<xsl:if test="c:param[@name='print-width']">
				<xsl:attribute name="print-width"><xsl:value-of select="c:param[@name='print-width']/@value"/></xsl:attribute>
			</xsl:if>
		</c:image>
	</xsl:copy>
</xsl:template>

<xsl:template match="c:cnxn">
	<c:link>
		<xsl:apply-templates select="@*"/>
		<xsl:if test="@target"><xsl:attribute name="target-id">
			<xsl:value-of select="@target"/></xsl:attribute></xsl:if>
		<xsl:apply-templates/>
	</c:link>
</xsl:template>

<xsl:template match="c:name">
	<c:title>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates/>
	</c:title>
</xsl:template>


<xsl:template match="c:list[@type='inline']">
	<xsl:copy>
		<xsl:attribute name="display">inline</xsl:attribute>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates/>
	</xsl:copy>
</xsl:template>


<xsl:template match="c:para//c:div">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Removing c:div</xsl:with-param></xsl:call-template>
	<xsl:apply-templates/> 
</xsl:template>

<!-- Word importer does not detect these. -->
<xsl:template match="c:list[c:item[1]/c:label/text()='a']">
	<xsl:call-template name="format-list"><xsl:with-param name="numberStyle">lower-alpha</xsl:with-param></xsl:call-template>
</xsl:template>
<xsl:template match="c:list[c:item[1]/c:label/text()='A']">
	<xsl:call-template name="format-list"><xsl:with-param name="numberStyle">upper-alpha</xsl:with-param></xsl:call-template>
</xsl:template>
<xsl:template match="c:list[c:item[1]/c:label/text()='i']">
	<xsl:call-template name="format-list"><xsl:with-param name="numberStyle">lower-roman</xsl:with-param></xsl:call-template>
</xsl:template>
<xsl:template match="c:list[c:item[1]/c:label/text()='I']">
	<xsl:call-template name="format-list"><xsl:with-param name="numberStyle">upper-roman</xsl:with-param></xsl:call-template>
</xsl:template>
<xsl:template name="format-list">
	<xsl:param name="numberStyle">arabic</xsl:param>
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Inferring the @number-style on a list (probably imported from Word)</xsl:with-param></xsl:call-template>
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:attribute name="list-type">enumerated</xsl:attribute>
		<xsl:attribute name="number-style"><xsl:value-of select="$numberStyle"/></xsl:attribute>
		<xsl:apply-templates/>
	</xsl:copy>
</xsl:template>
<xsl:template match="c:list[c:item[1]/c:label[text()='A' or text()='a' or text()='I' or text()='i']]/c:item/c:label">
	<!-- Intentionally ignore. -->
</xsl:template>


<!-- Handle c:newline elements. -->
<xsl:template match="c:para[c:newline]">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Converting c:para[c:newline] to multiple c:para elements</xsl:with-param></xsl:call-template>
	<!-- Need to use a special prefix for the c:para... grr (so c:newline can close it and reopen it -->
	<xsl:text disable-output-escaping="yes">&lt;cnxmlAdded:para xmlns:cnxmlAdded="http://cnx.rice.edu/cnxml"</xsl:text>
	<xsl:for-each select="@*">
		<xsl:text> </xsl:text>
		<xsl:value-of select="name(.)"/>
		<xsl:text>="</xsl:text>
		<xsl:value-of select="."/>
		<xsl:text>"</xsl:text>
	</xsl:for-each>
	<xsl:text disable-output-escaping="yes">></xsl:text>
	<xsl:apply-templates/>
	<xsl:text disable-output-escaping="yes">&lt;/cnxmlAdded:para></xsl:text>
</xsl:template>
<xsl:template match="c:para/c:newline">
	<xsl:text disable-output-escaping="yes">&lt;/cnxmlAdded:para></xsl:text>
	<xsl:comment>c:newline removed</xsl:comment>
	<xsl:text disable-output-escaping="yes">&lt;cnxmlAdded:para xmlns:cnxmlAdded="http://cnx.rice.edu/cnxml"></xsl:text>
</xsl:template>
<!-- If they're in a c:item, make sure the c:item has a c:para child -->
<xsl:template match="c:*[(not(c:para) or local-name(*[1]) != 'para') and c:newline]">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Converting c:<xsl:value-of select="local-name()"/>[c:newline] to multiple c:para elements</xsl:with-param></xsl:call-template>
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:text disable-output-escaping="yes">&lt;cnxmlAdded:para xmlns:cnxmlAdded="http://cnx.rice.edu/cnxml"></xsl:text>
		<xsl:apply-templates/>
		<xsl:text disable-output-escaping="yes">&lt;/cnxmlAdded:para></xsl:text>
	</xsl:copy>
</xsl:template>
<!-- For c:*/c:para when a newline exists, close the c:para and then reopen it -->
<xsl:template match="c:*[(not(c:para) or local-name(*[1]) != 'para') and c:newline]/c:para">
	<xsl:text disable-output-escaping="yes">&lt;/cnxmlAdded:para></xsl:text>
	<xsl:copy>
		<xsl:copy-of select="@*"/>
		<xsl:apply-templates/>
	</xsl:copy>
	<xsl:text disable-output-escaping="yes">&lt;cnxmlAdded:para xmlns:cnxmlAdded="http://cnx.rice.edu/cnxml"></xsl:text>
</xsl:template>
<!-- For c:*/c:newline, close the c:para and then reopen it (effectively making a newline) -->
<xsl:template match="c:*[(not(c:para) or local-name(*[1]) != 'para') and c:newline]/c:newline">
	<xsl:text disable-output-escaping="yes">&lt;/cnxmlAdded:para></xsl:text>
	<xsl:comment>c:newline removed</xsl:comment>
	<xsl:text disable-output-escaping="yes">&lt;cnxmlAdded:para xmlns:cnxmlAdded="http://cnx.rice.edu/cnxml"></xsl:text>
</xsl:template>

</xsl:stylesheet>
