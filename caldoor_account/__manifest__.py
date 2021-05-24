# -*- coding: utf-8 -*-

{
    'name': 'CalDoor: Open Invoices STAT on Contacts',
    'summary': 'Open Invoices STAT on Contacts',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
        Task ID: 2500278
        - Changes
    """,
    'category': 'Custom Development',

    # any module necessary for this one to work correctly
    'depends': ['account'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
