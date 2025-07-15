<?xml version="1.0" encoding="UTF-8" ?>

<!--
 * ============================================================
 *
 * This file is a part of digiKam project
 * https://www.digikam.org
 *
 * Date        : 2011-03-30
 * Description : A date framed theme for the digiKam html gallery tool.
 *
 * Copyright (C) 2011 by Elizabeth Marmorstein <purplegamba at cox dot net>
 *
 * This program is free software; you can redistribute it
 * and/or modify it under the terms of the GNU General
 * Public License as published by the Free Software Foundation;
 * either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * ============================================================
 -->

<!DOCTYPE stylesheet [
<!ENTITY raquo "&#187;" >
<!ENTITY blank "&#160;" >
]>

<!--
Points to check when an error appears:
- check that all the  '  href="dateframesthomas/style.css" '  are pointing to the correct "dateframesthomas" folder

-->

<xsl:transform version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:exsl="http://exslt.org/common"
	xmlns:dt="http://xsltsl.org/date-time"
	extension-element-prefixes="exsl">

	<xsl:import href="http://xsltsl.sourceforge.net/modules/date-time.xsl"/>

<!-- ********************************************************************* -->
<!-- ** Create single image page for each image                         ** -->
<!-- ********************************************************************* -->
<xsl:template name="createImagePage">
	<xsl:param name="prevPic"/>
	<xsl:param name="nextPic"/>
	<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<title><xsl:value-of select="title"/></title>
		<link rel="stylesheet" type="text/css" href="../dateframesthomas/style.css"/>
	</head>
	<body id="imagePage">
		<!-- Add Previous/Next Links --> 
		<xsl:if test="string($prevPic)">
			<a href="{$prevPic}.html">
				<xsl:value-of select="$i18nPrevious"/>
			</a>
		</xsl:if>
		<xsl:if test="string($prevPic) and string($nextPic)">
			|
		</xsl:if>
		<xsl:if test="string($nextPic)">
			<a href="{$nextPic}.html"> 
				<xsl:value-of select="$i18nNext"/>
			</a>
		</xsl:if>
		<br/>
		
		<!-- Draw the picture -->
	<xsl:choose>
		<!-- Check the orientation of the picture -->
		<xsl:when test="full/@width &gt; full/@height">
			<!-- Picture is landscape oriented -->
						<img src="{full/@fileName}" width="100%" /><br/>
		</xsl:when>
		<xsl:otherwise>
			<!-- Picture is portrait oriented -->
						<img src="{full/@fileName}" width="70%" /><br/>
		</xsl:otherwise>
	</xsl:choose>
	<div id="caption">
		<a align="left">
			<xsl:value-of select="description"/> <!-- description = legende -->
		</a>
		<a align="right">
			<xsl:value-of select="exif/exifimagedatetime"/><br />
		</a>
	</div>
	<br />
	<!-- Add Original File Link, if present -->
	<xsl:if test="original/@fileName != ''">
		<a href="{original/@fileName}"><xsl:attribute name="download"><xsl:value-of select="title"/></xsl:attribute>
			<img src="http://icons.iconarchive.com/icons/custom-icon-design/pretty-office-7/64/Save-icon.png" width="24" heigh="24" style="border:0px;vertical-align:middle"/>  
			<xsl:value-of select="$i18nOriginalImage"/>: 
			<xsl:value-of select="title"/><br/> <!-- title = original file name -->
		</a>
	</xsl:if>
	<small>
	<br />
		<xsl:value-of select="original/@width"/> x <xsl:value-of select="original/@height"/><br />
<!--		<b><xsl:value-of select="$i18nexifphotoexposuretime"/>:</b> <xsl:value-of select="exif/exifphotoexposuretime"/><br />
		<b><xsl:value-of select="$i18nexifphotofnumber"/>:</b> <xsl:value-of select="exif/exifphotofnumber"/><br /> -->
		<xsl:value-of select="exif/exifphotoshutterspeedvalue"/>&blank;-&blank;<xsl:value-of select="exif/exifphotoaperturevalue"/><br />

		<xsl:if test="string(number(translate(exif/exifphotofocallength,' mm',''))) != 'NaN'">
			<!-- If the focal length is defined (only): -->
			<!-- focal length is a number -->
			<xsl:value-of select="exif/exifphotofocallength"/> 
			<!-- EFL / 35 mm equivalent focal length // DFE / distance focale équivalente en 35 mm -->
			<!-- https://www.dpreview.com/products/canon/slrs/canon_eos550d/specifications -->
			<!-- https://fr.wikipedia.org/wiki/APS-C -->
			<xsl:variable name="efl">
				<xsl:choose>
					<xsl:when test="exif/exifimagemodel = 'Canon EOS 550D'">1.62</xsl:when>
					<xsl:when test="exif/exifimagemodel = 'Canon EOS 5D Mark II'">1</xsl:when>
					<xsl:when test="exif/exifimagemodel = 'Canon IXUS 240 HS'">5.62</xsl:when>
					<xsl:when test="exif/exifimagemodel = 'Canon PowerShot SX520 HS'">5.62</xsl:when>
					<xsl:when test="exif/exifimagemodel = 'Canon PowerShot SX610 HS'">5.62</xsl:when>
					<xsl:when test="exif/exifimagemodel = 'SM-J500F'">8.05</xsl:when> <!-- 1/2.5"»6.0248?; 1/2.6"»6.2657?; 7.5676 pour 28mm -->
					<xsl:otherwise>0</xsl:otherwise>
				</xsl:choose>
			</xsl:variable> <!-- Closure of name="efl" definition -->
			<a	style="cursor:pointer; color:white;"
				title="EFL = 35 mm Equivalent Focal Length (24x36)">
			<xsl:choose>
				<xsl:when test="$efl = 1.0">
					<!-- EFL is known for this camera -->
					(full frame / <xsl:value-of select="exif/exifimagemodel"/> )
				</xsl:when>
				<xsl:when test="$efl &gt; 1">
					<!-- EFL is known for this camera -->
					(x<xsl:value-of select="$efl"/> for <xsl:value-of select="exif/exifimagemodel"/> -&gt; EFL ≈
					<xsl:value-of select="round( $efl * (translate(exif/exifphotofocallength,' mm','')) )"/> mm)
				</xsl:when>
				<xsl:otherwise>
					<!-- EFL is unknown for this camera -->
					<small>(focal length multiplier unknown for <xsl:value-of select="exif/exifimagemodel"/>)</small>
				</xsl:otherwise>
			</xsl:choose>
			</a>
			<br />
		</xsl:if>

		<xsl:value-of select="exif/exifphotoisospeedratings"/> ISO<br />
	</small>

		<!-- Add  Date (formatted) -->
		<div id="caption">
			<xsl:call-template name="dt:format-date-time">
				<xsl:with-param name="xsd-date-time" select="date"/>
				<xsl:with-param name="format" select="$longformat"/>
			</xsl:call-template>
			<br/>
		</div>


		<br/>

		<!-- Add Previous/Next Links --> 
		<xsl:if test="string($prevPic)">
			<a href="{$prevPic}.html">
				<xsl:value-of select="$i18nPrevious"/>
			</a>
		</xsl:if>
		<xsl:if test="string($prevPic) and string($nextPic)">
			|
		</xsl:if>
		<xsl:if test="string($nextPic)">
			<a href="{$nextPic}.html"> 
				<xsl:value-of select="$i18nNext"/>
			</a>
		</xsl:if>
		<br/>

	</body>
	</html>
</xsl:template>

<!-- ********************************************************************* -->
<!-- ** Create thumbnail page for each collection                       ** -->
<!-- ********************************************************************* -->
<xsl:template name="createThumbnailPage">
	<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<title><xsl:value-of select="name"/></title>
		<link rel="stylesheet" type="text/css" href="dateframesthomas/style.css"/>
	</head>
		<h1>
		<span>
			<xsl:value-of select="name"/>
		</span>
		</h1>

	<body id="collectionPage">
	<div id="comment">
		<xsl:value-of select="comment"/><br/>
	</div>
	<ul>
			<xsl:variable name="folder" select='fileName'/>
			<xsl:for-each select="image">
				<xsl:variable name="cur" select="position()"/>
				<li>
					<a href="{$folder}/{full/@fileName}.html" target="image">
						<img src="{$folder}/{thumbnail/@fileName}" width="{thumbnail/@width}" height="{thumbnail/@height}"/>
					</a><br/>
					<xsl:call-template name="dt:format-date-time">
                        			<xsl:with-param name="xsd-date-time" select="date"/>
                        			<xsl:with-param name="format" select="$shortformat"/>
					</xsl:call-template>
					<br/>
				</li>
				<exsl:document href='{$folder}/{full/@fileName}.html'>
					<xsl:call-template name="createImagePage">
						<xsl:with-param name="prevPic" select="preceding-sibling::*[1]/full/@fileName"/>
						<xsl:with-param name="nextPic" select="following-sibling::*[1]/full/@fileName"/>
					</xsl:call-template>
				</exsl:document>
			</xsl:for-each>
	</ul>
	</body>
	</html>
</xsl:template>


<!-- ********************************************************************* -->
<!-- ** Create the collection index page when more than one collection  ** -->
<!-- ********************************************************************* -->
<xsl:template name="createCollectionIndexPage">
	<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<title><xsl:value-of select="$i18nCollectionList"/></title>
		<link rel="stylesheet" type="text/css" href="dateframesthomas/style.css"/>
	</head>
	<body id="collectPage">
			<xsl:for-each select="collections/collection">
					<xsl:sort select="name" order="ascending" data-type="text" />
					&blank;
					<a href="Thmbs{fileName}.html" target="mythmbs">
						<img src="http://icons.iconarchive.com/icons/media-design/hydropro/48/HP-Pictures-Folder-icon.png" alt="Album" width="24" height="24" style="border:0px;vertical-align:middle"/>
						<xsl:value-of select="name"/>

					</a>
					<xsl:for-each select="image">
						<xsl:choose>
							<xsl:when test="position()=last()">
								(<xsl:value-of select="position()"/>)
							</xsl:when>
						</xsl:choose>
					</xsl:for-each>
					<exsl:document href="Thmbs{fileName}.html">
						<xsl:call-template name="createThumbnailPage"/>
					</exsl:document>
				
			</xsl:for-each>
	</body>
	</html>
	
</xsl:template>

<!-- ********************************************************************* -->
<!-- ** Create the frameset page			                ** -->
<!-- ********************************************************************* -->
<xsl:template name="createCollectionFrameSetPage">
<!-- ** create variable tsize for the width of the thumbnails frame            ** -->
<!-- ** add 10 pixel to tsize for the border around the thumbnail              ** -->
	<xsl:variable name="tsize" select="3*(collections/collection[1]/image[1]/thumbnail/@width + 18) + 65"/>
	<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>
		<xsl:value-of select="name"/>
		</title>
		<link rel="stylesheet" type="text/css" href="dateframesthomas/style.css"/>
	</head>
	<frameset rows="40,*" noresize="1" border="1">
		<frame src="collect.html" name="collection"/>
		<frameset cols="{$tsize},*" border="3">
			<frame src="blank.html" name="mythmbs"/>
			<frame src="intro.html" name="image"/>
		</frameset>
	</frameset>
	</html>
	<exsl:document href="collect.html">
		<xsl:call-template name="createCollectionIndexPage"/>
	</exsl:document>
</xsl:template>

<!-- ********************************************************************* -->
<!-- ** Create a blank page                                             ** -->
<!-- ** as a starting page when more than one collection is used        ** -->
<!-- ********************************************************************* -->
<xsl:template name="createBlankPage">
	<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>
		<xsl:value-of select="name"/>
		</title>
		<link rel="stylesheet" type="text/css" href="dateframesthomas/style.css"/>
	</head>
	<body id="blankPage">
		<xsl:value-of select="title"/>
		<br/><br/><br/><br/>

		<!-- Pt
		<p>
		Clique no titulo do album em cima para comecar <img src="http://icons.iconarchive.com/icons/media-design/hydropro/48/HP-Pictures-Folder-icon.png" alt="Album" width="24" height="24" style="border:0px;vertical-align:middle"/>.<br/><br/>
		Clique na miniatura ao lado para ver a imagem.<br/><br/>
		Clique no icon <img src="http://icons.iconarchive.com/icons/custom-icon-design/pretty-office-7/64/Save-icon.png" width="24" heigh="24" style="border:0px;vertical-align:middle"/> abaixo da imagem para baixar o tamanho original.<br/><br/>
		<img src="http://perso0.proxad.net/cgi-bin/wwwcount.cgi?df=t.baeckeroot.dat&ft=0&dd=E" />
		</p>
		<!- - Fr -->
		<p>
		Cliquez sur le titre de l'album en haut pour commencer <img src="http://icons.iconarchive.com/icons/media-design/hydropro/48/HP-Pictures-Folder-icon.png" alt="Album" width="24" height="24" style="border:0px;vertical-align:middle"/>.<br/><br/>
		Cliquez sur les miniatures à gauche pour voir l'image.<br/><br/>
		Cliquez sur l'icone <img src="http://icons.iconarchive.com/icons/custom-icon-design/pretty-office-7/64/Save-icon.png" width="24" heigh="24" style="border:0px;vertical-align:middle"/> sous l'image pour télécharger l'image originale.<br/><br/>
		<img src="http://perso0.proxad.net/cgi-bin/wwwcount.cgi?df=t.baeckeroot.dat&amp;ft=0&amp;dd=E" />
		</p>

	</body>

	</html>
</xsl:template>

<!-- ********************************************************************* -->
<!-- ** Create the intro page                                           ** -->
<!-- ********************************************************************* -->
<xsl:template name="createIntroPage">
	<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />

		<title>
		<xsl:value-of select="name"/>
		</title>
		<link rel="stylesheet" type="text/css" href="dateframesthomas/style.css"/>
	</head>
	<body id="intro">
		<xsl:value-of select="$intro"/><br/>
<!--
		<br/>
		INCLUDE HERE THE LINK TO DOWNLOAD THEM ALL AT ONCE WHEN USING A ZIP!<br/>
-->
	</body>

	</html>
</xsl:template>


<!-- ********************************************************************* -->
<!-- ** Create css style sheet                                       ** -->
<!-- ********************************************************************* -->
<xsl:template name="createStyleSheet">
body {
	background-color: <xsl:value-of select="$color1"/>; /*background behind thumbnails, outside boxes*/
    	color: <xsl:value-of select="$color2"/>; /*default text color*/
    	font-size: 14pt;
    	text-align: center;
    	font-family: Bitstream Vera Serif, serif;
    	margin: 0in;
    	padding: 0in;
}

a { /*links (album titles)*/
    	color: #FFFFFF; 
    	text-decoration: none;
}

a:hover { /*links when mouse is over them (album titles)*/
    	color: #5555FF;
	text-decoration: underline;
}

h1 { /*album title above thumbnails*/
	padding-top: 0.1em;
	color: <xsl:value-of select="$color2"/>; 
	font-size: 14pt;
	text-align: center;
}

/* Collection page */
#collectionPage {
	background-color: <xsl:value-of select="$color1"/>;
	color: <xsl:value-of select="$color2"/>; 
	padding-left: 2%;
	text-align: center;
	width: 95%;
}

#comment {
	width: 95%;
	text-align: center;
}

#collectionPage h1 {
	margin-top: 12px;
} 

#collectionPage ul { /*affects list of thumbnails*/
	padding: 0;
}

#collectionPage li { /*affects stuff in boxes with thumbnails*/
        display: block;
        float: left;
        margin-left: 6px;
	margin-top: 6px;
	padding: 5px;
	color: <xsl:value-of select="$color1"/>;
	font-size: 8pt;
	background-color: <xsl:value-of select="$color2"/>;
	border: 1px solid #000000;
}

/* Blank Page */
#blankPage {
	background-color: <xsl:value-of select="$color1"/>;
}

#intro {
	padding: 10%;
	background-color: <xsl:value-of select="$color2"/>;
	color: <xsl:value-of select="$color1"/>;
	font-size: 16pt;
	text-align: center;
}

/*  Collect Page */
#collectPage { /*album titles at top*/
    	background-color: <xsl:value-of select="$color3"/>;
	font-size: 12pt;
	padding-top: 0.5em;
	margin: 0 auto;
	width: 95%;
    	color: #AAAAAA; /*number of pics in collection*/
	text-align: center;
}


/* Image page */
#imagePage {
	padding:.5em;
	background-color:<xsl:value-of select="$color2"/>; /*background color behind the big image*/
	text-align: center;
	color: <xsl:value-of select="$color1"/>; 
}


#caption { /*caption below photo*/
	padding-bottom:1em;
	padding-top:1em;
	color: <xsl:value-of select="$color1"/>;
	font-size: 16pt;
}

#imagePage img {
	border: 1px solid #CECECE; /*border around picture*/
}

#imagePage a { /*links*/
    	color: <xsl:value-of select="$color1"/>; 
    	text-decoration: none;
}

#imagePage a:hover { /*links when mouse is over them*/
    	color: <xsl:value-of select="$color1"/>;
	text-decoration: underline;
}

	
</xsl:template>

<!-- ********************************************************************* -->
<!-- ** the beginning of all                                            ** -->
<!-- ********************************************************************* -->
<xsl:template match="/">
	<xsl:call-template name="createCollectionFrameSetPage"/>
	<exsl:document href="blank.html">
		<xsl:call-template name="createBlankPage"/>
	</exsl:document>
	<exsl:document href="intro.html">
		<xsl:call-template name="createIntroPage"/>
	</exsl:document>
	<exsl:document href="dateframesthomas/style.css">
		<xsl:call-template name="createStyleSheet"/>
	</exsl:document>
</xsl:template>

</xsl:transform>
