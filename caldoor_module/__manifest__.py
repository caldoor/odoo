# -*- coding: utf-8 -*-
{
    'name': "Cal Door Module",

    'summary': """
        Customization module solely for Cal Door & Drawer""",

    'description': """
        ERP for Cal Door & Drawer
    """,

    'author': "IT Support",
    'website': "http://www.caldoor.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','account_accountant','stock','delivery','website_sale','delivery_hs_code'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/res_partner_form_inherit.xml',
        'views/sale_order_form_inherit.xml',
        'views/product_category_form_inherit.xml',
        'views/account_invoice_form.xml',
        'views/delivery_carrier_form_inherit.xml',
        'views/product_template_form_inherit.xml',
        'views/account_payment_term_inherit.xml',
        'data/account_payment_terms_data.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}