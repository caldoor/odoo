# -*- coding: utf-8 -*-

from lxml import etree
from uuid import uuid4

from odoo.exceptions import ValidationError, UserError
from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI, error_check


class AuthorizeAPI(AuthorizeAPI):

    def credit(self, token, amount, transaction_id):
        """ Refund a payment for the given amount.

        :param record token: the payment.token record that must be refunded.
        :param str amount: transaction amount
        :param str transaction_id: the reference of the transacation that is going to be refunded.

        :return: a dict containing the response code, transaction id and transaction type
        :rtype: dict
        """
        root = self._base_tree('createTransactionRequest')
        tx = etree.SubElement(root, "transactionRequest")
        etree.SubElement(tx, "transactionType").text = "refundTransaction"
        etree.SubElement(tx, "amount").text = str(amount)
        payment = etree.SubElement(tx, "payment")
        credit_card = etree.SubElement(payment, "creditCard")
        token_names = token.name.split('-')
        etree.SubElement(credit_card, "cardNumber").text = token_names[1][-4:]
        etree.SubElement(credit_card, "expirationDate").text = "XXXX"
        etree.SubElement(tx, "refTransId").text = transaction_id
        response = self._authorize_request(root)
        res = dict()
        (has_error, error_msg) = error_check(response)
        if has_error:
            res['x_response_code'] = self.AUTH_ERROR_STATUS
            res['x_response_reason_text'] = error_msg
            return res
        res['x_response_code'] = response.find('transactionResponse/responseCode').text
        res['x_trans_id'] = response.find('transactionResponse/transId').text
        res['x_type'] = 'refund'

        return res
 
    def create_customer_profile(self, partner, cardnumber, expiration_date, card_code, full_name):
        """Create a payment and customer profile in the Authorize.net backend.

        Creates a customer profile for the partner/credit card combination and links
        a corresponding payment profile to it. Note that a single partner in the Odoo
        database can have multiple customer profiles in Authorize.net (i.e. a customer
        profile is created for every res.partner/payment.token couple).

        :param record partner: the res.partner record of the customer
        :param str cardnumber: cardnumber in string format (numbers only, no separator)
        :param str expiration_date: expiration date in 'YYYY-MM' string format
        :param str card_code: three- or four-digit verification number

        :return: a dict containing the profile_id and payment_profile_id of the
                 newly created customer profile and payment profile
        :rtype: dict
        """
        root = self._base_tree('createCustomerProfileRequest')
        profile = etree.SubElement(root, "profile")
        if partner.x_custno:
            etree.SubElement(profile, "merchantCustomerId").text = ('%s' % (partner.x_custno))
        else:
            etree.SubElement(profile, "merchantCustomerId").text = ('ODOO-%s-%s' % (partner.id, uuid4().hex[:8]))[:20]
        etree.SubElement(profile, "description").text = partner.name
        etree.SubElement(profile, "email").text = partner.email or ''
        payment_profile = etree.SubElement(profile, "paymentProfiles")
        etree.SubElement(payment_profile, "customerType").text = 'business' if partner.is_company else 'individual'
        billTo = etree.SubElement(payment_profile, "billTo")
        etree.SubElement(billTo, "firstName").text = full_name[0]
        etree.SubElement(billTo, "lastName").text = full_name[1]
        etree.SubElement(billTo, "address").text = (partner.street or '' + (partner.street2 if partner.street2 else '')) or None
        
        missing_fields = [partner._fields[field].string for field in ['city', 'country_id'] if not partner[field]]
        if missing_fields:
            raise ValidationError({'missing_fields': missing_fields})
        
        etree.SubElement(billTo, "city").text = partner.city
        etree.SubElement(billTo, "state").text = partner.state_id.name or None
        etree.SubElement(billTo, "zip").text = partner.zip or ''
        etree.SubElement(billTo, "country").text = partner.country_id.name or None
        payment = etree.SubElement(payment_profile, "payment")
        creditCard = etree.SubElement(payment, "creditCard")
        etree.SubElement(creditCard, "cardNumber").text = cardnumber
        etree.SubElement(creditCard, "expirationDate").text = expiration_date
        etree.SubElement(creditCard, "cardCode").text = card_code
        etree.SubElement(root, "validationMode").text = 'liveMode'
        response = self._authorize_request(root)

        # If the user didn't set up authorize.net properly then the response
        # won't contain stuff like customerProfileId and accessing text
        # will raise a NoneType has no text attribute
        msg = response.find('messages')
        if msg is not None:
            rc = msg.find('resultCode')
            if rc is not None and rc.text == 'Error':
                err = msg.find('message')
                err_code = err.find('code').text
                err_msg = err.find('text').text
                raise UserError(
                    "Authorize.net Error:\nCode: %s\nMessage: %s"
                    % (err_code, err_msg)
                )

        res = dict()
        res['profile_id'] = response.find('customerProfileId').text
        if not partner._get_payment_tokens():
            res['payment_profile_id'] = response.find('customerPaymentProfileIdList/numericString').text
        else:
            res['payment_profile_id'] = partner._get_payment_tokens().authorize_profile
        return res