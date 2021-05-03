# -*- coding: utf-8 -*-
{
    'name': 'CalDoor: Add "Work In Progress" Stat Button on Contact',
    'summary': 'Add "Work In Progress" Stat Button on Contact',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
        Task ID: 2459299
        - Display the dollar amount of open orders that have not been invoiced yet on the WorkInProgress status button.
        - Quotation and Quotation Sent are considered WorkInProgress.
    """,
    'category': 'Custom Development',
    'depends': ['sale', 'sale_stock'],
    'data': [
        'views/res_partner.xml',
        'views/sale.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}