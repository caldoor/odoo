# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Caldoor:Authorize convenience fee',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
Authorize convenience fee
=========================

TASK-ID: 2026410
----------------

*Business Use Case:
We want to add a convenience fee to the transactions charged through Authorize. When customer wants to pay using Credit card, we will charge him a % convenience fee and want this to refelct on the SO as well as the invoice. This amount needs to be captured separately to a different GL account as we will be paying this to Authorize.

* Settings:
On the Authorize setup page, provide a field to define the "Convenience Fee" product and percentage of fee. We will define the "Income Account" on this product (to be used for journal entries)

* Convenience Fee calculation:
Convenience fee is a % of the total sales quote or Invoice amount, as the case may be. It includes all the order/ invoice lines including taxes and shipping/ freight/ handling charges. Thus, it is a percentage of the final amount communicated on the Total field of sales quote or Invoice. 
Convenience fee % x Total amount = Convenience Fee value to be charged to customer

* Case 1:

a) Create Sales quote, click on "Send by email", click on "Preview" button. When customer is ready to make a payment here, he selects "Authorize" or any saved token from Authorize - the "Pay Now" button should be greyed out.
b) Show a pop-up message that displays the additional convenience fee and asks the customer if he wants to proceed. If he clicks "No", he is not allowed to use Authorize or his saved tokens. If he clicks "Yes", he should be charged for order total + convenience fee
c) In the database backend, add a line on sales quote for product convenience fee and the calculated fee value. This order is now confirmed.
d) When this is converted to Invoice, the order lines including convenience fee will translate to Invoice lines, the Income account setup on convenience fee product should be used for the journal entries. We will use the automated invoicing feature so when the SO is confirmed, the invoice should be validated, confirmed and marked as paid.


* Case 2:

a) We have a payment term "C50" which means customer has the option to pay 50% on the sales quote or the complete 100% amount. Create Sales quote with this payment method, click on "Send by email", click on "Preview" button. 
When customer is ready to make a payment here, he selects "Authorize", he should be able to see an option for "Payment Amount" . The possible amounts would be 50% of the SO total or 100% of the SO total. See attached mockup.
b) If he selects 50%, grey out the "Pay Now" button, show him 50% amount and the convenience fee%, if he accepts the amount then he can make the payment else do not allow using Authorize for payment.
c) If he selects 100% , show him full amount, convenience fee and do the same as above.
d) If a customer chooses to pay 50% now and the rest later, we will charge him convenience fee twice as Authorize charges fee per transaction. These cases apply for only those customers who have C50 payment terms.


* Case 3:

a) Create an invoice and validate it. Click on "Register Payment", when "Authorize" is selected as a payment method, grey out the "Validate" button, show a pop-up message for the extra convenience fee and provide options to accept or reject
b) Accepting should add a new Invoice line with the convenience fee product and amount and mark the invoice as paid.
c) Rejecting will not allow Authorize to be used for payment.

""",
    'depends': ['sale', 'payment_authorize'],
    'data': [
        'views/payment_views.xml',
        'views/templates.xml',
    ],
    'demo': [],
    'installable': True,
}
