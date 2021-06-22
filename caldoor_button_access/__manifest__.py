# -*- coding:'utf-8' -*-

{
    'name': 'Caldoor - Stat Buttons Access',

    'description': """Sales:All document group users should be able to view open invoices and due stat buttons""",

    'summary': """Due and Open Invoices stat buttons on the contact form are regulated for the sales group""",

    'author': 'Odoo Inc.',

    'website': 'https://www.odoo.com/',

    'version': '1.0',

    'license': 'OEEL-1',

    'category': 'Custom',

    'depends': ['sales_team', 'caldoor_account', 'account_reports'],

    'data': [
        'security/res_partner.xml',
        'data/res_partner.xml'
    ],

    'demo': [

    ]
}
