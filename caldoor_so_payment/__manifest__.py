# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Caldoor: Sale order direct Pay Now Function",
    'version': '1.0',
    'depends': ['portal', 'sale'],
    'author': 'Odoo Inc',
    'license': 'OEEL-1',
    'mainainer': 'Odoo Inc',
    'category': 'Category',
    'description': """
Caldoor: Sale order direct Pay Now Function
===========================================
- Module to provide functionality to pay the sale order directly by clicking 'Pay Now' button
  on a sale order. 
- Idea is to skip the whole process of SO>Send by E-mail>Preview>Sign>Pay Now.
    """,
    # data files always loaded at installation
    'data': [
        'views/portal_templates.xml',
        'views/sales_team_views.xml',
        'views/sale_order_views.xml',
    ],
}