# -*- coding:utf-8 -*-

from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI


class AuthorizeAPI(AuthorizeAPI):
    
    def error_check(elem):
        """Check if the response sent by Authorize.net contains an error.
        Errors can be a failure to try the transaction (in that case, the transasctionResponse
        is empty, and the meaningful error message will be in message/code) or a failure to process
        the transaction (in that case, the message/code content will be generic and the actual error
        message is in transactionResponse/errors/error/errorText).
        :param etree._Element elem: the root element of the response that will be parsed
        :rtype: tuple (bool, str)
        :return: tuple containnig a boolean indicating if the response should be considered
                 as an error and the most meaningful error message found in it.
        """
        result_code = elem.find('messages/resultCode')
        msg = 'No meaningful error message found, please check logs or the Authorize.net backend'
        
        #-----------------custom code starts here---------------------
        
        transaction_errors = elem.find('transactionResponse/errors')
        has_error = result_code.text == 'Error' or transaction_errors is not None
        
        #-----------------custom code ends here-----------------------

        if has_error:
            # accumulate the most meangingful error
            error = elem.find('transactionResponse/errors/error')
            error = error if error is not None else elem.find('messages/message')
            if error is not None:
                code = error[0].text
                text = error[1].text
                msg = '%s: %s' % (code, text)
        return (has_error, msg)

