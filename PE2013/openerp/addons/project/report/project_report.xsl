<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
    <xsl:template match="/">
        <xsl:apply-templates select="projects"/>
    </xsl:template>

    <xsl:template match="projects">
        <document xmlns:fo="http://www.w3.org/1999/XSL/Format">
            <template leftMargin="2.0cm" rightMargin="2.0cm" topMargin="2.0cm" bottomMargin="2.0cm" title="Project" author="Generated by PengERP.com" allowSplitting="20">
                <pageTemplate id="all">
                    <pageGraphics/>
                    <frame id="list" x1="1.0cm" y1="2.0cm" width="19.0cm" height="27cm"/>
                </pageTemplate>
            </template>

            <stylesheet>
                <paraStyle name="title" fontName="Helvetica-Bold" fontSize="18" alignment="center"/>
                <paraStyle name="notes" fontName="Helvetica" fontSize="8" alignment="justify"/>
                <blockTableStyle id="project">
                    <blockFont name="Helvetica-Bold" size="10" start="0,0" stop="0,-1"/>
                    <blockFont name="Helvetica-Bold" size="10" start="2,0" stop="2,-1"/>
                     <blockValign value="TOP"/>
                </blockTableStyle>
                <blockTableStyle id="tasks">
                    <blockValign value="TOP"/>
                    <blockAlignment value="LEFT"/>
                    <blockFont name="Helvetica-Bold" size="10" start="0,0" stop="-1,0"/>
                    <lineStyle kind="LINEABOVE" thickness="0.5" colorName="black" start="0,0" stop="-1,0"/>
                    <lineStyle kind="LINEBELOW" thickness="0.5" colorName="black" start="0,0" stop="-1,0"/>
                    <blockBackground colorName="(0.72,0.72,0.72)" start="0,0" stop="-1,0"/>
                     <blockValign value="TOP"/>
                     <blockAlignment value="CENTER" start="1,0" stop="-1,-1"/>
                </blockTableStyle>
            </stylesheet>

            <story>
                <xsl:apply-templates select="project"/>
            </story>
        </document>
    </xsl:template>

    <xsl:template match="members">
        <xsl:value-of select="member_name"/> (<i><xsl:value-of select="member_login"/></i>),
    </xsl:template>

    <xsl:template match="task">
        <tr>
            <td>
                <para><xsl:value-of select="task_name"/></para>
                    <para style="notes"><xsl:value-of select="task_description"/></para>
            </td>
            <td><xsl:value-of select="task_planned_hours"/></td>
            <td><xsl:value-of select="task_effective_hours"/></td>
            <td><xsl:value-of select="task_deadline"/></td>
            <td><xsl:value-of select="task_user_id"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="tasks">
        <blockTable style="tasks" colWidths="10cm,1.6cm,1.6cm,2cm,2.5cm">
        <tr>
            <td t="True">Tasks</td>
            <td t="True">Hours</td>
            <td t="True">Done</td>
            <td t="True">Deadline</td>
            <td t="True">Responsible</td>
        </tr>
        <xsl:apply-templates select="task"/>
        </blockTable>
    </xsl:template>

    <xsl:template match="project">
        <para style="title">
            <xsl:value-of select="name"/>
        </para>
        <spacer length="1cm"/>
        <blockTable colWidths="3cm,6cm,3cm,6cm" style="project">
        <tr>
            <td t="True">Manager:</td>
            <td><para><b><xsl:value-of select="manager"/></b></para></td>
            <td t="True">Members:</td>
            <td><para><xsl:apply-templates select="members"/></para></td>
        </tr><tr>
            <td t="True">Project:</td>
            <td><xsl:value-of select="parent"/></td>
            <td></td>
            <td></td>
        </tr><tr>
            <td t="True">Date Start:</td>
            <td><xsl:value-of select="date_start"/></td>
            <td t="True">Date Stop:</td>
            <td><xsl:value-of select="date_stop"/></td>
        </tr><tr>
            <td t="True">Planned Hours:</td>
            <td><xsl:value-of select="planned_hours"/></td>
            <td t="True">Effective Hours:</td>
            <td><xsl:value-of select="effective_hours"/></td>
        </tr>
        </blockTable>
        <spacer length="0.3cm"/>
        <pre>
            <xsl:value-of select="notes"/>
        </pre>
        <spacer length="0.7cm"/>
        <xsl:apply-templates select="tasks"/>
        <pageBreak/>
    </xsl:template>
</xsl:stylesheet>
