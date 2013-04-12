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

from openerp.osv import osv,fields

class company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'po_lead': fields.float('Purchase Lead Time', required=True,
            help="This is the leads/security time for each purchase order."),
    }
    _defaults = {
        'po_lead': lambda *a: 1.0,
    }
company()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
