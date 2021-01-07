# -*- coding: utf-8 -*-
{
    'name': "CalDoor: Set Default Payment Method",

    'summary': """
            Sets a default payment method when creating a new payment.
    """,

    'description': """
        Task ID: 2416241 jsz
        
        Go to accounting module > Customers > Payments > Create
        Batch deposit should be pre-selected by default
    """,

    'author': "Odoo, Inc",
    'website': "http://www.yourcompany.com",

    'category': 'Custom Development',
    'version': '0.1',

    'depends': ['account_accountant'],

    'data': [
        'views/account_views_inherit.xml',
    ],

    'license': 'OEEL-1'
}