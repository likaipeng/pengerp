{
    'name': 'Anonymous portal',
    'description': """
Allow anonymous to Access Portal.
=================================
 """,
    'author': 'PengERP SA',
    'version': '1.0',
    'category': 'Hidden',
    'website': 'http://www.pengerp.com',
    'installable': True,
    'depends': ['portal', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'portal_anonymous_data.xml',
    ],
    'js': ['static/src/js/portal_anonymous.js'],
    'qweb': ['static/src/xml/portal_anonymous.xml'],
}
