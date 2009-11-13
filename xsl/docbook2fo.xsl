<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:db="http://docbook.org/ns/docbook"
  version="1.0">

<xsl:import href="debug.xsl"/>

<xsl:import href="../docbook-xsl/fo/docbook.xsl"/>

<xsl:output omit-xml-declaration="yes" indent="yes" method="xml"/>
<xsl:param name="moduleId"/>

<xsl:template match="*[@xml:id or @id]" priority="1000000">
	<xsl:if test="@id and not(contains(@id, '.'))">
	<xsl:message>
		<xsl:text>DEBUG: Converting </xsl:text>
		<xsl:choose>
			<xsl:when test="@xml:id">
				<xsl:value-of select="@xml:id"/>
			</xsl:when>
			<xsl:when test="@id">
				<xsl:value-of select="@id"/>
			</xsl:when>
		</xsl:choose>
	</xsl:message>
	</xsl:if>
	<xsl:apply-imports select="."/>
</xsl:template>

<!-- ORIGINAL: docbook-xsl/fo/lists.xsl
	Changes: In addition to outputting "???" if a link is broken, 
	  also generate debug message so the author can fix it
 -->

</xsl:stylesheet>
