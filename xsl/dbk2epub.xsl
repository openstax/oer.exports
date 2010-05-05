<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:fo="http://www.w3.org/1999/XSL/Format"
  version="1.0">

<xsl:import href="debug.xsl"/>
<xsl:include href="../docbook-xsl/epub/docbook.xsl"/>

<xsl:output indent="yes" method="xml"/>

<!-- From docbook-xsl/html/graphics.xsl -->
<xsl:template match="svg:*[svg:metadata/pmml2svg:baseline-shift]" xmlns:svg="http://www.w3.org/2000/svg" xmlns:pmml2svg="https://sourceforge.net/projects/pmml2svg/">
	<!-- Add a positioning style to the div/span -->
	<!-- 
	<xsl:call-template name="cnx.log"><xsl:with-param name="msg">Aligning svg</xsl:with-param></xsl:call-template>
	 -->
	<xsl:copy>
		<xsl:attribute name="style">position:relative; top:<xsl:value-of
			select="svg:metadata/pmml2svg:baseline-shift" />px;</xsl:attribute>
		<xsl:copy-of select="@*" />
		<xsl:apply-templates />
	</xsl:copy>
</xsl:template>

<!-- Ignore -->
<xsl:template match="pmml2svg:baseline-shift" xmlns:pmml2svg="https://sourceforge.net/projects/pmml2svg/">
</xsl:template>


</xsl:stylesheet>