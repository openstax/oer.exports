<?xml version="1.0" ?>
<xsl:stylesheet 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:mml="http://www.w3.org/1998/Math/MathML"
  xmlns:c="http://cnx.rice.edu/cnxml"
  xmlns:db="http://docbook.org/ns/docbook"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  xmlns:md="http://cnx.rice.edu/mdml/0.4" xmlns:bib="http://bibtexml.sf.net/"
  version="1.0">

<xsl:import href="debug.xsl"/>
<xsl:output omit-xml-declaration="yes" indent="yes" method="xml"/>
<xsl:param name="moduleId"/>

<!-- When generating id's we need to prefix them with a module id. 
	This is the text between the module, and the module-specific id. -->
<xsl:param name="moduleSeparator">.</xsl:param>

<xsl:template mode="copy" match="@*|node()|comment()">
    <xsl:copy>
        <xsl:apply-templates mode="copy" select="@*|node()|comment()"/>
    </xsl:copy>
</xsl:template>

<!-- Boilerplate -->
<xsl:template match="/">
	<xsl:apply-templates select="//c:document/c:content"/>
</xsl:template>

<!-- Match the roots and add boilerplate -->
<xsl:template match="c:content">
    <db:section>
    	<xsl:attribute name="xml:id"><xsl:value-of select="$moduleId"/></xsl:attribute>
        <xsl:apply-templates select="../c:title"/>
        <xsl:apply-templates/>
        <!--TODO: Figure out when to move the exercises
        <xsl:if test=".//c:section/c:exercise or c:exercise">
        	<db:qandaset>
        		<xsl:apply-templates mode="end-of-module" select=".//c:section/c:exercise | c:exercise"/>
        	</db:qandaset>
        </xsl:if>-->
    </db:section>
</xsl:template>



<xsl:template name="copy-attributes-to-docbook">
    <xsl:if test="@id">
        <xsl:attribute name="xml:id">
        	<xsl:value-of select="$moduleId"/>
        	<xsl:text>.</xsl:text>
        	<xsl:value-of select="@id"/>
        </xsl:attribute>
    </xsl:if>
</xsl:template>

<xsl:template name="id-and-children">
	<xsl:call-template name="copy-attributes-to-docbook"/>
	<xsl:apply-templates select="*|text()|node()|comment()"/>
</xsl:template>

<xsl:template name="id-title-and-children-in-para">
	<xsl:call-template name="copy-attributes-to-docbook"/>
	<xsl:apply-templates select="c:title"/>
	<db:para>
		<xsl:apply-templates select="*[local-name()!='title']|text()|comment()"/>
	</db:para>
</xsl:template>


<!-- Block elements in docbook cannot have free-floating text. they need to be wrapped in a db:para -->
<xsl:template name="block-id-and-children">
	<xsl:choose>
		<xsl:when test="normalize-space(text()) != ''">
			<db:para>
				<xsl:call-template name="id-and-children"/>
			</db:para>
		</xsl:when>
		<xsl:otherwise>
			<xsl:call-template name="id-and-children"/>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>


<xsl:template match="c:para">
    <db:para><xsl:call-template name="id-and-children"/></db:para>
</xsl:template>

<xsl:template match="c:para[c:title]">
    <db:formalpara><xsl:call-template name="id-title-and-children-in-para"/></db:formalpara>
</xsl:template>


<xsl:template match="c:sub">
    <db:subscript><xsl:call-template name="id-and-children"/></db:subscript>
</xsl:template>

<xsl:template match="c:sup">
    <db:superscript><xsl:call-template name="id-and-children"/></db:superscript>
</xsl:template>


<xsl:template match="c:list">
    <db:itemizedlist><xsl:call-template name="id-and-children"/></db:itemizedlist>
</xsl:template>


<xsl:template match="c:list[@list-type='enumerated']">
	<xsl:variable name="numeration">
		<xsl:choose>
    		<xsl:when test="not(@number-style) or @number-style='arabic'">arabic</xsl:when>
			<xsl:when test="@number-style='upper-alpha'">upperalpha</xsl:when>
			<xsl:when test="@number-style='lower-alpha'">loweralpha</xsl:when>
			<xsl:when test="@number-style='upper-roman'">upperroman</xsl:when>
			<xsl:when test="@number-style='lower-roman'">lowerroman</xsl:when>
    		<xsl:otherwise>
    			<xsl:call-template name="debug"><xsl:with-param name="str">BUG: Unsupported @number-style</xsl:with-param></xsl:call-template>
    			<xsl:text>arabic</xsl:text>
    		</xsl:otherwise>
    	</xsl:choose>
	</xsl:variable>		
    <db:orderedlist numeration="{$numeration}"><xsl:call-template name="id-and-children"/></db:orderedlist>
</xsl:template>

<xsl:template match="c:list[@list-type='labeled-item']">
    <db:orderedlist><xsl:call-template name="id-and-children"/></db:orderedlist>
</xsl:template>

<xsl:template match="c:list[@display='inline']">
	<xsl:for-each select="c:item">
		<xsl:if test="position()!=1">; </xsl:if>
    	<xsl:apply-templates select="*|text()|node()|comment()"/>
    </xsl:for-each>
</xsl:template>


<xsl:template match="c:item">
    <db:listitem>
    	<xsl:choose>
    		<xsl:when test="c:title">
    			<db:formalpara>
    				<xsl:call-template name="copy-attributes-to-docbook"/>
					<xsl:apply-templates select="*[local-name(.)!='para']|text()|node()|comment()"/>
    			</db:formalpara>
    			<xsl:apply-templates select="c:para"/>
    		</xsl:when>
    		<xsl:when test="c:para">
				<xsl:call-template name="id-and-children"/>
    		</xsl:when>
    		<xsl:otherwise>
		    	<db:para>
					<xsl:call-template name="id-and-children"/>
				</db:para>
			</xsl:otherwise>
		</xsl:choose>
    </db:listitem>
</xsl:template>


<xsl:template match="c:emphasis[not(@effect) or @effect='bold']">
    <db:emphasis role="bold"><xsl:call-template name="id-and-children"/></db:emphasis>
</xsl:template>
<xsl:template match="c:emphasis[@effect='italics']">
    <db:emphasis><xsl:call-template name="id-and-children"/></db:emphasis>
</xsl:template>



<xsl:template match="c:link[@url]">
    <db:link xlink:href="{@url}"><xsl:call-template name="id-and-children"/></db:link>
</xsl:template>
<xsl:template match="c:link[@document|@target-id and normalize-space(text())='']">
	<xsl:variable name="linkend">
		<xsl:if test="not(@document)"><xsl:value-of select="$moduleId"/></xsl:if>
		<xsl:value-of select="@document"/>
		<xsl:if test="@target-id"><xsl:value-of select="$moduleSeparator"/></xsl:if>
		<xsl:value-of select="@target-id"/>
	</xsl:variable>
    <db:xref linkend="{$linkend}"><xsl:call-template name="id-and-children"/></db:xref>
</xsl:template>
<xsl:template match="c:link[@document|@target-id and normalize-space(text())!='']">
	<xsl:variable name="linkend">
		<xsl:if test="not(@document)"><xsl:value-of select="$moduleId"/></xsl:if>
		<xsl:value-of select="@document"/>
		<xsl:if test="@target-id"><xsl:value-of select="$moduleSeparator"/></xsl:if>
		<xsl:value-of select="@target-id"/>
	</xsl:variable>
    <db:link linkend="{$linkend}"><xsl:call-template name="id-and-children"/></db:link>
</xsl:template>




<xsl:template match="c:code">
    <db:programlisting><xsl:call-template name="id-and-children"/></db:programlisting>
</xsl:template>


<xsl:template match="c:quote">
    <db:quote><xsl:call-template name="id-and-children"/></db:quote>
</xsl:template>


<xsl:template match="c:cite">
    <db:citetitle><xsl:call-template name="id-and-children"/></db:citetitle>
</xsl:template>


<!-- ****************************************
        A simple c:figure = img
        By simple, I mean:
        * only a c:media (no c:subfigure, c:table, c:code)
        * only a c:image in the c:media (no c:audio, c:flash, c:video, c:text, c:java-applet, c:labview, c:download)
        * no c:caption
        * c:title cannot have xml elements in it, just text
     **************************************** -->
<xsl:template match="c:figure[not(c:subfigure or c:table or c:code) and c:media/c:image]">
	<xsl:choose>
		<xsl:when test="not(c:title)">
			<db:informalfigure><xsl:call-template name="id-and-children"/></db:informalfigure>
		</xsl:when>
		<xsl:otherwise>
			<db:figure><xsl:call-template name="id-and-children"/></db:figure>
		</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<xsl:template match="c:media">
	<db:mediaobject><xsl:call-template name="id-and-children"/></db:mediaobject>
</xsl:template>
<!-- See m21854 //c:equation/@id="eip-id14423064" -->
<xsl:template match="c:para//c:media">
	<db:inlinemediaobject><xsl:call-template name="id-and-children"/></db:inlinemediaobject>
</xsl:template>

<xsl:template match="c:image">
	<db:imageobject>
		<db:imagedata fileref="{@src}">
			<xsl:choose>
				<xsl:when test="@print-width">
					<xsl:attribute name="width"><xsl:value-of select="@print-width"/></xsl:attribute>
				</xsl:when>
				<xsl:when test="@width">
					<xsl:attribute name="width"><xsl:value-of select="@width"/></xsl:attribute>
				</xsl:when>
			</xsl:choose>
			<xsl:if test="@height">
				<xsl:attribute name="depth"><xsl:value-of select="@height"/></xsl:attribute>
			</xsl:if>
		</db:imagedata>
	</db:imageobject>
</xsl:template>




<xsl:template match="c:caption">
	<db:caption><xsl:call-template name="id-and-children"/></db:caption>
</xsl:template>

<xsl:template match="c:title">
	<db:title><xsl:call-template name="id-and-children"/></db:title>
</xsl:template>

<xsl:template match="c:note">
    <db:note>
		<xsl:call-template name="block-id-and-children"/>
    </db:note>
</xsl:template>
<xsl:template match="c:section">
    <db:section>
		<xsl:call-template name="block-id-and-children"/>
    </db:section>
</xsl:template>
<xsl:template match="c:equation">
	<db:equation>
		<xsl:call-template name="block-id-and-children"/>
	</db:equation>
</xsl:template>
<xsl:template match="c:equation[not(c:title)]">
	<db:informalequation>
		<xsl:call-template name="block-id-and-children"/>
	</db:informalequation>
</xsl:template>
<xsl:template match="c:para//c:equation[not(c:title)]">
	<db:inlineequation>
		<xsl:call-template name="block-id-and-children"/>
	</db:inlineequation>
</xsl:template>
<xsl:template match="c:example">
	<db:example>
		<xsl:call-template name="do-example-stuff"/>
	</db:example>
</xsl:template>
<xsl:template match="c:example[not(c:title)]">
	<db:informalexample>
		<xsl:call-template name="do-example-stuff"/>
	</db:informalexample>
</xsl:template>
<xsl:template name="do-example-stuff">
	<xsl:call-template name="block-id-and-children"/>
</xsl:template>

<!--TODO: Figure out when to move the exercises (and definitions)
<xsl:template match="c:exercise">
	<xsl:message>Moving exercise to bottom of module</xsl:message>
</xsl:template>
<xsl:template mode="end-of-module" match="c:exercise">
	<db:qandaentry>
		<xsl:call-template name="id-and-children"/>
	</db:qandaentry>
</xsl:template>
-->
<xsl:template match="c:exercise">
	<db:qandaset role="none">
	<db:qandaentry>
		<xsl:call-template name="id-and-children"/>
	</db:qandaentry>
	</db:qandaset>
</xsl:template>
<xsl:template match="c:problem">
	<db:question>
		<xsl:call-template name="id-and-children"/>
	</db:question>
</xsl:template>
<xsl:template match="c:solution">
	<db:answer>
		<xsl:call-template name="id-and-children"/>
	</db:answer>
</xsl:template>

<!-- According to eip-help/definition -->
<xsl:template match="c:definition">
	<db:variablelist>
		<xsl:if test="c:title">
			<xsl:apply-templates select="c:title"/>
		</xsl:if>
		<db:varlistentry>
			<xsl:apply-templates select="c:term"/>
			<db:listitem>
				<xsl:apply-templates select="*[preceding-sibling::c:term]"/>
			</db:listitem>
		</db:varlistentry>
	</db:variablelist>
</xsl:template>
<xsl:template match="c:definition/c:term">
	<db:term><xsl:apply-templates /></db:term>
</xsl:template>
<xsl:template match="c:definition/c:meaning">
	<db:para><xsl:apply-templates/></db:para>
</xsl:template>


<xsl:template match="c:preformat">
	<db:programlisting>
		<xsl:call-template name="id-and-children"/>
	</db:programlisting>
</xsl:template>

<xsl:template match="c:foreign">
	<xsl:call-template name="debug"><xsl:with-param name="str">WARNING: Ignoring c:foreign element for conversion</xsl:with-param></xsl:call-template>
	<xsl:apply-templates/>
</xsl:template>

<!-- MathML -->
<xsl:template match="c:equation/mml:math">
	<db:mediaobject>
		<db:imageobject>
			<!-- <db:imagedata format="svg"> --> 
				<xsl:apply-templates mode="copy" select="."/>
			<!-- </db:imagedata> -->
		</db:imageobject>
	</db:mediaobject>
</xsl:template>
<xsl:template match="mml:math">
	<db:inlinemediaobject>
		<db:imageobject>
			<!-- TODO: Docbook BUG. SVG should be in db:imagedata
			<db:imagedata format="svg"> --> 
				<xsl:apply-templates mode="copy" select="."/>
			<!-- </db:imagedata> -->
		</db:imageobject>
	</db:inlinemediaobject>
</xsl:template>







<!-- Partially supported -->
<xsl:template match="c:figure[c:subfigure]">
	<xsl:call-template name="debug">
		<xsl:with-param name="str">ERROR: Subfigures are not really supported. Only the 1st subfigure is used</xsl:with-param>
	</xsl:call-template>
	<db:figure>
		<xsl:call-template name="copy-attributes-to-docbook"/>
		<xsl:apply-templates select="*[local-name()!='subfigure']"/>
		<xsl:apply-templates select="c:subfigure[1]/*"/>
	</db:figure>
</xsl:template>

<xsl:template match="c:figure/c:subfigure[1]">
	<xsl:apply-templates select="*|text()|node()|comment()"/>
</xsl:template>



<!-- Convert CALS Table -->
<xsl:template match="c:table">
	<db:table><xsl:call-template name="calsHelper"/></db:table>
</xsl:template>
<xsl:template match="c:tgroup">
	<db:tgroup><xsl:call-template name="calsHelper"/></db:tgroup>
</xsl:template>
<xsl:template match="c:thead">
	<db:thead><xsl:call-template name="calsHelper"/></db:thead>
</xsl:template>
<xsl:template match="c:tfoot">
	<db:tfoot><xsl:call-template name="calsHelper"/></db:tfoot>
</xsl:template>
<xsl:template match="c:tbody">
	<db:tbody><xsl:call-template name="calsHelper"/></db:tbody>
</xsl:template>
<xsl:template match="c:colspec">
	<db:colspec><xsl:call-template name="calsHelper"/></db:colspec>
</xsl:template>
<xsl:template match="c:row">
	<db:row><xsl:call-template name="calsHelper"/></db:row>
</xsl:template>
<xsl:template match="c:entry">
	<db:entry><xsl:call-template name="calsHelper"/></db:entry>
</xsl:template>
<xsl:template match="c:entrytbl">
	<db:entrytbl><xsl:call-template name="calsHelper"/></db:entrytbl>
</xsl:template>

<xsl:template name="calsHelper">
	<xsl:if test="@id">
		<xsl:attribute name="xml:id">
			<xsl:value-of select="$moduleId"/>
			<xsl:value-of select="$moduleSeparator"/>
			<xsl:value-of select="@id"/>
		</xsl:attribute>
	</xsl:if>
	<xsl:copy-of select="@*"/>
	<xsl:apply-templates/>
</xsl:template>


<xsl:template match="c:document/c:title">
	<db:title>
		<xsl:call-template name="copy-attributes-to-docbook"/>
		<xsl:apply-templates select="*|text()|node()|comment()"/>
		<!-- TODO: Remove debugging line. -->
		<xsl:text> [</xsl:text>
		<xsl:value-of select="$moduleId"/>
		<xsl:text>]</xsl:text>
	</db:title>
</xsl:template>


<xsl:template match="comment()">
    <xsl:copy-of select="."/>comment
</xsl:template>


</xsl:stylesheet>
