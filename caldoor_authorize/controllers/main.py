# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo.addons.sale.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>/update/payment_option'], type='json', auth="public", website=True)
    def update_payment_option(self, order_id, payment_option):
        order = request.env['sale.order'].sudo().browse(order_id).exists()
        if order and payment_option:
            order.payment_option = payment_option
        return True

    # @http.route()
    # def payment_transaction_token(self, acquirer_id, order_id, save_token=False, access_token=None, **kwargs):
    #     order = request.env['sale.order'].sudo().browse(order_id)
    #     if order and order.order_line and order.has_to_be_paid() and kwargs.get('payment_option'):
    #         order.write({'payment_option': kwargs['payment_option']})
    #     return super(CustomerPortal, self).payment_transaction_token(acquirer_id=acquirer_id, order_id=order_id, save_token=save_token, access_token=access_token, **kwargs)

    # @http.route()
    # def payment_token(self, order_id, pm_id=None, **kwargs):
    #     order = request.env['sale.order'].sudo().browse(order_id)
    #     if order and order.order_line and order.has_to_be_paid() and kwargs.get('payment_option'):
    #         order.write({'payment_option': kwargs['payment_option']})
    #     return super(CustomerPortal, self).payment_token(order_id, pm_id, **kwargs)
