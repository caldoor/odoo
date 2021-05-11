# -*- coding: utf-8 -*-

{
    'name': 'CalDoor: Make "Credit Hold" RED when it\'s flagged',
    'summary': 'Make "Credit Hold" RED when it\'s flagged',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
        Task ID: 2475049
        - Make Credit Hold label red when checked
    """,
    'category': 'Custom Development',

    # any module necessary for this one to work correctly
    'depends': ['caldoor_module'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
