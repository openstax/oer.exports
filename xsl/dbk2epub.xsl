<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/1999/xhtml"
  version="1.0">

<xsl:import href="debug.xsl"/>
<xsl:import href="../docbook-xsl/epub/docbook.xsl"/>
<!-- Use .xhtml so browsers are in XML-mode (and render inline SVG) -->
<xsl:param name="html.ext">.xhtml</xsl:param>
<!-- <xsl:param name="chunk.quietly">0</xsl:param>  -->
<xsl:param name="svg.doctype-public">-//W3C//DTD SVG 1.1//EN</xsl:param>
<xsl:param name="svg.doctype-system">http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd</xsl:param>
<xsl:param name="svg.media-type">image/svg+xml</xsl:param>

<xsl:output indent="yes" method="xml"/>

<!-- Output the PNG with the baseline info -->
<xsl:template match="*['imagedata'=local-name() and @pmml2svg:baseline-shift]" xmlns:svg="http://www.w3.org/2000/svg" xmlns:pmml2svg="https://sourceforge.net/projects/pmml2svg/">
	<img src="{@fileref}">
		<xsl:attribute name="style">
		    <!-- Ignore width and height information for now
			<xsl:text>width:</xsl:text>
			<xsl:value-of select="@width"/>
			<xsl:text>; height:</xsl:text>
			<xsl:value-of select="@depth"/>
			<xsl:text>;</xsl:text>
			-->
		  	<xsl:text>position:relative; top:</xsl:text>
		  	<xsl:value-of select="@pmml2svg:baseline-shift" />
		  	<xsl:text>pt;</xsl:text>
	  	</xsl:attribute>
  	</img>
<!--
  <object id="{$id}" type="image/svg+xml" data="{$chunkfn}" width="{@width}" height="{@height}">
 	<xsl:if test="svg:metadata/pmml2svg:baseline-shift">
  	  <xsl:attribute name="style">position:relative; top:<xsl:value-of
		select="svg:metadata/pmml2svg:baseline-shift" />px;</xsl:attribute>
  	</xsl:if>
	<img src="{$png}" width="{@width}" height="{@height}"/>
  </object>
--></xsl:template>


<!-- Put the equation number on the RHS -->
<xsl:template match="equation">
  <div class="equation">
    <xsl:attribute name="id">
      <xsl:call-template name="object.id"/>
    </xsl:attribute>
	<xsl:apply-templates/>
	<span class="label">
	  <xsl:text>(</xsl:text>
	  <xsl:apply-templates select="." mode="label.markup"/>
      <xsl:text>)</xsl:text>
    </span>
  </div>
</xsl:template>

</xsl:stylesheet>
