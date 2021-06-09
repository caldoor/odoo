# -*- coding:utf-8 -*-

from odoo.addons.payment_authorize.models.authorize_request import AuthorizeAPI


class AuthorizeAPI(AuthorizeAPI):
    
    def _authorize_request(self, data):
        """Encode, send and process the request to the Authorize.net API.
        Encodes the xml data and process the response. Note that only a basic
        processing is done at this level (namespace cleanup, basic error management).
        :param etree._Element data: etree data to process
        """
        logged_data = data
        data = etree.tostring(data, encoding='utf-8')
        for node_to_remove in ['//merchantAuthentication', '//creditCard']:
            for node in logged_data.xpath(node_to_remove):
                node.getparent().remove(node)
        logged_data = str(etree.tostring(logged_data, encoding='utf-8', pretty_print=True)).replace(r'\n', '\n')
        _logger.info('_authorize_request: Sending values to URL %s, values:\n%s', self.url, logged_data)

        r = requests.post(self.url, data=data, headers={'Content-Type': 'text/xml'})
        r.raise_for_status()
        response = strip_ns(r.content, XMLNS)

        logged_data = etree.XML(r.content)
        logged_data = str(etree.tostring(logged_data, encoding='utf-8', pretty_print=True)).replace(r'\n', '\n')
        _logger.info('_authorize_request: Values received\n%s', logged_data)
        
        #-------------custom code starts here---------------
        
        #if transacation response has errors, then resultcode type is changed to error.
        transaction_errors = response.find('transactionResponse/errors')
        if transaction_errors is not None:
            response.find('messages/resultCode').text = 'Error'
        
        #-------------custom code ends here------------------
        
        return response
