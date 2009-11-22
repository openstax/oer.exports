<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    >

<!-- The following parameters are used for batch processing and gathering statistics -->
<xsl:param name="outputBugsOnly">no</xsl:param> 
<xsl:param name="outputAggregateOnly">no</xsl:param>

<!-- Catch-all -->
<xsl:template match="*">
	<xsl:call-template name="debug">
		<xsl:with-param name="isBug">yes</xsl:with-param>
		<xsl:with-param name="str">
			<xsl:text>BUG: Could not match Element </xsl:text>
	  		<xsl:value-of select="local-name(..)"/>
			<xsl:text>/</xsl:text>
	  		<xsl:value-of select="local-name(.)"/>
		</xsl:with-param>
	</xsl:call-template>
</xsl:template>

<xsl:template name="debugPathPrinter">
	<xsl:if test="../.."><!-- Root is a node, and confuses the printing -->
		<xsl:for-each select="..">
			<xsl:call-template name="debugPathPrinter"/>
		</xsl:for-each>
	</xsl:if>
	<xsl:text>/</xsl:text>
	<xsl:value-of select="local-name(.)"/>
	<xsl:text>[</xsl:text>
	<xsl:choose>
		<xsl:when test="@xml:id">
			<xsl:text>@xml:id='</xsl:text>
			<xsl:value-of select="@xml:id"/>
			<xsl:text>'</xsl:text>
		</xsl:when>
		<xsl:when test="@id">
			<xsl:text>@id='</xsl:text>
			<xsl:value-of select="@id"/>
			<xsl:text>'</xsl:text>
		</xsl:when>
		<xsl:otherwise>
			<xsl:value-of select="position()"/>
		</xsl:otherwise>
	</xsl:choose>
	<xsl:text>]</xsl:text>
</xsl:template>

<xsl:template name="debug">
	<xsl:param name="str" />
	<xsl:param name="isBug">no</xsl:param>
	<xsl:param name="node" select="."/>
	<xsl:if test="($outputBugsOnly != 'no' and $isBug != 'no') or $outputBugsOnly = 'no'">
		<xsl:choose>
			<xsl:when test="$outputAggregateOnly != 'no'">
				<xsl:message>
					<xsl:text>DBG: </xsl:text>
				  	<xsl:value-of select="$str"/>
				</xsl:message>
			</xsl:when>
			<xsl:otherwise>
				<xsl:message>
					<xsl:text>DBG: </xsl:text>
					<xsl:text>{ module: "</xsl:text>
				  	<xsl:value-of select="$moduleId"/>
					<xsl:text>", message: "</xsl:text>
				  	<xsl:value-of select="$str"/>
				  	<xsl:text>", xpath: "</xsl:text>
				  	<xsl:call-template name="debugPathPrinter"/>
				  	<xsl:text>"}</xsl:text>
				</xsl:message>
			</xsl:otherwise>
		</xsl:choose> 
	</xsl:if>
</xsl:template>

</xsl:stylesheet>