<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.w3.org/1999/xhtml"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns:pmml2svg="https://sourceforge.net/projects/pmml2svg/"
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

<!-- From docbook-xsl/html/graphics.xsl -->

<!-- Ignore -->
<xsl:template match="pmml2svg:baseline-shift" xmlns:pmml2svg="https://sourceforge.net/projects/pmml2svg/">
</xsl:template>


<!-- Chunk the SVG -->
<xsl:template match="svg:svg">
  <xsl:variable name="id" select="generate-id(.)"/>
  <xsl:variable name="chunkfn">
  	<xsl:value-of select="$id"/>
  	<xsl:text>.svg</xsl:text>
  </xsl:variable>
  <xsl:variable name="filename">
    <xsl:call-template name="make-relative-filename">
      <xsl:with-param name="base.dir" select="$base.dir"/>
      <xsl:with-param name="base.name" select="$chunkfn"/>
    </xsl:call-template>
  </xsl:variable>
  <xsl:call-template name="write.chunk">
    <xsl:with-param name="filename" select="$filename"/>
    <xsl:with-param name="content" select="."/>
    <xsl:with-param name="doctype-public" select="$svg.doctype-public"/>
    <xsl:with-param name="doctype-system" select="$svg.doctype-system"/>
    <xsl:with-param name="media-type" select="$svg.media-type"/>
    <xsl:with-param name="quiet" select="$chunk.quietly"/>
  </xsl:call-template>

  <object id="{$id}" type="image/svg+xml" data="{$chunkfn}" width="{@width}" height="{@height}">
 	<xsl:if test="svg:metadata/pmml2svg:baseline-shift">
  	  <xsl:attribute name="style">position:relative; top:<xsl:value-of
		select="svg:metadata/pmml2svg:baseline-shift" />px;</xsl:attribute>
  	</xsl:if>
	<img src="{$chunkfn}" width="{@width}" height="{@height}"/>
  </object>
</xsl:template>


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
