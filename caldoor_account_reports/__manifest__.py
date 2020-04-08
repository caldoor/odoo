# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'CalDoor: Account Reports',
    'summary': 'Aged Receivable Report',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '2.0',
    'author': 'Odoo Inc',
    'description': """
CalDoor: Aged Receivable Report
===============================
- Add 'Age Days' and 'Payment Terms' of the invoice on the report (i.e. screen and in excel export).
- Change the reference with just Invoice Number so that it won’t be too long of a string and the total amount at the end will show.
- See all the data without scrolling to the right.

CalDoor: Due Invoices
===============================
1. Add a "Due" stat Button on res.partner - refer to image attached "odoo-customer-due-invoices.jpg"
- “Due” button will go to screen where you can send the customer all the due invoices (or exclude some)
- We can have multiple email addresses (type = “invoice address”) per customer

2. Update "email address" functionality - refer to image attached  "odoo-customer-due-invoices-send-email.jpg"
- Currently, only one email address is chosen as the recipient of the email.
- We want all of the “invoice” type email addresses to be the default recipients of the email (in this example it should pick up josephsteve08@gmail.com as well)
- We want to be able to add email address on the fly – or remove what’s on the default

1. List all email ID of the type "Invoice Address" ONLY upon clicking on the DUE button (Note: Other email Ids from different "types" under child contact will not be displayed)
2. "trash" icon (button) will allow to remove the email Ids or provide pick and chose functionality - click action will exclude the email from the recipients' list 
3. A new text field can be created that will accept the input "email ID" however it won't be stored anywhere - it will be a one-time functionality - This field should be able to accept more than one email ID (should be of nature many to many) 
    """,
    'category': 'Custom Development',
    'depends': ['account', 'account_reports', 'contacts'],
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
