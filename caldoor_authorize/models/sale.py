# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _create_payment_transaction(self, vals):
        acquirer_id = vals.get('acquirer_id', False)
        if not acquirer_id and vals.get('payment_token_id'):
            acquirer_id = self.env['payment.token'].sudo().browse(vals.get('payment_token_id')).acquirer_id.id
        if acquirer_id:
            self.sudo()._addConvenienceFee(acquirer_id)
        return super(SaleOrder, self)._create_payment_transaction(vals)

    def _addConvenienceFee(self, acquirer_id):
        acquirer = self.env['payment.acquirer'].browse(acquirer_id).exists()
        if acquirer.provider == 'authorize':
            product_id = acquirer.convenience_fee_product_id.id
            convenience_fee_percent = acquirer.convenience_fee_percent
            for order in self.filtered(lambda o: o.state in ('draft', 'sent')):
                fee = ((order.amount_total * convenience_fee_percent) / 100)
                order.write({
                    'order_line': [(0, 0, {'product_id': product_id, 'product_uom_qty': 1, 'price_unit': fee})]
                })
