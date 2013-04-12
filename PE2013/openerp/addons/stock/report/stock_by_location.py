# -*- coding: utf-8 -*-
##############################################################################
#    
#    PengERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import pooler
from openerp.report.interface import report_rml
from openerp.report.interface import toxml

#FIXME: we should use toxml

class report_custom(report_rml):
    def create_xml(self, cr, uid, ids, datas, context=None):
        config = """
        <config>
            <date>09/09/2005</date>
            <PageSize>210.00mm,297.00mm</PageSize>
            <PageWidth>595.27</PageWidth>
            <PageHeight>841.88</PageHeight>
            <tableSize>60.00mm,60.00mm,60.00mm</tableSize>
            <report-header>Stock by location</report-header>
            <report-footer>Generated by PengERP</report-footer>
        </config>
        """
        header = """
        <header>
            <field>Location</field>
            <field>Product name</field>
            <field>Product quantity</field>
        </header>
        """

        def process(location_id, level):
            xml = '<row>'
            location_name = pooler.get_pool(cr.dbname).get('stock.location').read(cr, uid, [location_id], ['name'])
            xml += "<col para='yes' tree='yes' space='" + str(3*level) + "mm'>"
            xml += location_name[0]['name'] + '</col>'

            prod_info = pooler.get_pool(cr.dbname).get('stock.location')._product_get(cr, uid, location_id)
            xml += "<col>"
            for prod_id in prod_info.keys():
                if prod_info[prod_id] != 0.0:
                    prod_name = pooler.get_pool(cr.dbname).get('product.product').read(cr, uid, [prod_id], ['name'])
                    xml +=  prod_name[0]['name'] + '\n'
            xml += '</col>'

            xml += "<col>"
            for prod_id in prod_info.keys():
                if prod_info[prod_id] != 0.0:
                    xml +=  str(prod_info[prod_id]) + '\n'
            xml += '</col></row>'

            location_child = pooler.get_pool(cr.dbname).get('stock.location').read(cr, uid, [location_id], ['child_ids'])
            for child_id in location_child[0]['child_ids']:
                xml += process(child_id, level+1)
            return xml

        for location_id in ids:
            xml = '<lines>' + process(location_id, 0) + '</lines>'

        xml = '<?xml version="1.0" ?>' '<report>'+ config + header + xml + '</report>'

        return self.post_process_xml_data(cr, uid, xml, context)

report_custom('report.stock.lot.location', 'stock.location', '', 'addons/stock/report/stock_by_location.xsl')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

