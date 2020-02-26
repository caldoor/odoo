# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'CalDoor: Account Reports',
    'summary': 'Aged Receivable Report',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.0',
    'author': 'Odoo Inc',
    'description': """
CalDoor: Aged Receivable Report
===============================
- Add 'Age Days' and 'Payment Terms' of the invoice on the report (i.e. screen and in excel export).
- Change the reference with just Invoice Number so that it won’t be too long of a string and the total amount at the end will show.
- See all the data without scrolling to the right.
    """,
    'category': 'Custom Development',
    'depends': ['account', 'account_reports'],
    'data': [
        'views/template.xml',
    ],
    'demo': [],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
