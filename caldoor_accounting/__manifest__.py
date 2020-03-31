# -*- coding: utf-8 -*-
{
    'name': "CalDoor: Partner Search Dropdown",

    'summary': """
       Add the customer number to the dropdown
    """,

    'description': """
        Task ID: 2223405 - AAL
        
The client would like to use the Reference field "ref"  available in the model "res.partner" 
to store Customer Number. They would then like to see this number against the partner name in 
the search drop-down of the Payments screen in the Accounting App. They would like this 
functionality as they have more than one customer with the same name, and hence they will use 
this reference number to distinguish them from one another.
    """,

    'author': "Odoo PS-US",
    'website': "http://www.odoo.com",
    'license': 'OEEL-1',

    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'views/inherit_view_account_payment.xml',
    ],
}