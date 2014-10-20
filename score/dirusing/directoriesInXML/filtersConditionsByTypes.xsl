<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	version="2.0">

	<xsl:variable name="conditions" select="document('filtersConditions.xml')" />
	<xsl:variable name="types" select="document('fieldsTypes.xml')" />
	
	<xsl:template match="/">
		<filtersConditionsByTypes>
		 <xsl:for-each select="$conditions//row">
		 	<xsl:variable name="cond" select="." />	
		 	<xsl:for-each select="$types//row">
		 	<xsl:variable name="type" select="." />	
            <row>
            	<id><xsl:value-of select="position()+count($cond/preceding-sibling::row)*count($types//row)" /></id>
				<filterConditionId><xsl:value-of select="$cond/id" /></filterConditionId>
				<fieldTypeId><xsl:value-of select="$type/id" /></fieldTypeId>
			</row>
			</xsl:for-each>
			</xsl:for-each>
		</filtersConditionsByTypes>
	</xsl:template>
</xsl:stylesheet>