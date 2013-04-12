# -*- encoding: utf-8 -*-
##############################################################################
#
#    PengERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from tools.config import config
import report
import os

import reportlab.pdfbase.pdfmetrics
import reportlab.pdfbase.ttfonts
adp = os.path.abspath(config['addons_path'])
fonts = ('SimSun', 'SimHei')
for font in fonts:
    fntp = os.path.normcase(os.path.join(adp, 'base_report_cn', 'fonts', font+'.ttf'))
    reportlab.pdfbase.pdfmetrics.registerFont(reportlab.pdfbase.ttfonts.TTFont( font,fntp))

def wrap_trml2pdf(method):
    """We have to wrap the original parseString() to modify the rml data
    before it generates the pdf."""
    def convert2TrueType(*args, **argv):
        """This function replaces the type1 font names with their truetype
        substitutes and puts a font registration section at the beginning
        of the rml file. The rml file is acually a string (data)."""
        data = args[0]
        fontmap = {
            'Times-Roman':                   'SimSun',
            'Times-BoldItalic':              'SimSun',
            'Times-Bold':                    'SimSun',
            'Times-Italic':                  'SimSun',

            'Helvetica':                     'SimHei',
            'Helvetica-BoldItalic':          'SimHei',
            'Helvetica-Bold':                'SimHei',
            'Helvetica-BoldOblique':         'SimHei',
            'Helvetica-Oblique':             'SimHei',
            'Helvetica-Italic':              'SimHei',

            'Courier':                       'SimSun',
            'Courier-Bold':                  'SimSun',
            'Courier-BoldItalic':            'SimSun',
            'Courier-BoldOblique':           'SimSun',
            'Courier-Oblique':               'SimSun',
            'Courier-Italic':                'SimSun',

            'Helvetica-ExtraLight':          'SimHei',

            'TimesCondensed-Roman':          'SimSun',
            'TimesCondensed-BoldItalic':     'SimSun',
            'TimesCondensed-Bold':           'SimSun',
            'TimesCondensed-Italic':         'SimSun',

            'HelveticaCondensed':            'SimHei',
            'HelveticaCondensed-BoldItalic': 'SimHei',
            'HelveticaCondensed-Bold':       'SimHei',
            'HelveticaCondensed-Italic':     'SimHei',
        }
        while len(fontmap)>0:
            ck=max(fontmap)
            data = data.replace(ck,fontmap.pop(ck))
        return method(data, args[1:] if len(args) > 2 else args[1], **argv)
    return convert2TrueType

report.render.rml2pdf.parseString = wrap_trml2pdf(report.render.rml2pdf.parseString)

report.render.rml2pdf.parseNode = wrap_trml2pdf(report.render.rml2pdf.parseNode)
