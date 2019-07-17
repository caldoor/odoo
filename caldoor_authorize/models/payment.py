# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, _


class PaymentAcquirerAuthorize(models.Model):
    _inherit = 'payment.acquirer'

    convenience_fee_product_id = fields.Many2one('product.product', string='Convenience Fee (Product)')
    convenience_fee_percent = fields.Float(string='Convenience Fee(%)')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def render_sale_button(self, order, submit_txt=None, render_values=None):
        """
            complete override to update the amount when user select 50% payment option
        """
        values = {
            'partner_id': order.partner_shipping_id.id or order.partner_invoice_id.id,
            'billing_partner_id': order.partner_invoice_id.id,
        }
        if render_values:
            values.update(render_values)
        # Not very elegant to do that here but no choice regarding the design.
        self._log_payment_transaction_sent()
        # Custom changes start
        amount = order.amount_total
        if self.acquirer_id.provider == 'authorize' and order.payment_option == 'c50':
            amount = self.amount
        # Custom changes end
        return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            amount,
            order.pricelist_id.currency_id.id,
            values=values,
        )
