# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Multiple invoice payment via authorize token",
    'version': '1.0',
    'depends': ['payment_authorize'],
    'website': 'https://www.odoo.com',
    'author': 'Odoo Inc',
    'maintainer': 'Odoo Inc',
    'category': 'Accounting',
    'license': 'OEEL-1',
    'description': """
Multiple invoice payment via authorize token
============================================
    """,
    # data files always loaded at installation
    'data': [
        'views/account_register_payments.xml',
    ],
}