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


{
    'name': 'Attendances',
    'version': '1.1',
    'category': 'Human Resources',
    'description': """
This module aims to manage employee's attendances.
==================================================

Keeps account of the attendances of the employees on the basis of the
actions(Sign in/Sign out) performed by them.
       """,
    'author': 'LKP',
    'images': ['images/hr_attendances.jpeg'],
    'depends': ['hr'],
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'hr_attendance_view.xml',
        'hr_attendance_report.xml',
        'wizard/hr_attendance_bymonth_view.xml',
        'wizard/hr_attendance_byweek_view.xml',
        'wizard/hr_attendance_error_view.xml',
        'res_config_view.xml',
    ],
    'demo': ['hr_attendance_demo.xml'],
    'test': [
        'test/attendance_process.yml',
        'test/hr_attendance_report.yml',
    ],
    'installable': True,
    'auto_install': False,
    
    #web
    "js": ["static/src/js/attendance.js"],
    'qweb' : ["static/src/xml/attendance.xml"],
    'css' : ["static/src/css/slider.css"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
