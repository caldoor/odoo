# -*- coding: utf-8 -*-

{
    'name': 'CalDoor: Last Successful Transaction Date next to Token Name',
    'summary': 'Last Successful Transaction Date next to Token Name',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
        Task ID: 2502924
        - Add last successful Transaction Date
    """,
    'category': 'Custom Development',

    # any module necessary for this one to work correctly
    'depends': ['account', 'sale', 'payment', 'caldoor_authorize'],
    'data': [
        'views/payment_portal_templates.xml',
        'views/payment_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
