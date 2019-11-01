# -*- coding: utf-8 -*-

from lxml import etree

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
        etree.SubElement(credit_card, "cardNumber").text = token_names[1]
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
        res['x_trans_id'] = transaction_id
        res['x_type'] = 'refund'

        return res
