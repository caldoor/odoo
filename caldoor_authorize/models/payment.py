# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from .authorize_request import AuthorizeAPI


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

    @api.multi
    def _authorize_s2s_validate(self, tree):
        result = super(PaymentTransaction, self)._authorize_s2s_validate(tree)
        status_code = int(tree.get('x_response_code', '0'))
        if status_code == self._authorize_valid_tx_status and tree.get('x_type').lower() == 'refund':
            self.write({
                'acquirer_reference': tree.get('x_trans_id'),
                'date': fields.Datetime.now(),
            })
            self._set_transaction_done()
            result = True
        return result

    @api.multi
    def authorize_s2s_do_refund(self):
        self.ensure_one()
        transaction = AuthorizeAPI(self.acquirer_id)
        res = transaction.credit(self.payment_token_id, self.amount, self.acquirer_reference)
        return self._authorize_s2s_validate_tree(res)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    authorize_refund_transaction_id = fields.Many2one('payment.transaction')
    authorize_payment_token_id = fields.Many2one('payment.token', related='authorize_refund_transaction_id.payment_token_id', string="Authorize stored credit card")

    @api.onchange('partner_id', 'payment_method_id', 'journal_id')
    def _onchange_set_payment_token_id(self):
        res = super(AccountPayment, self)._onchange_set_payment_token_id()
        if not res.get('domain'):
            res['domain'] = {}
        partners = self.partner_id | self.partner_id.commercial_partner_id | self.partner_id.commercial_partner_id.child_ids
        if self.partner_id:
            res['domain'].update({'authorize_refund_transaction_id': [('partner_id', 'in', partners.ids), ('acquirer_id.capture_manually', '=', False), ('acquirer_id.provider', '=', 'authorize')]})
        if self.payment_method_code == 'authorize_ct':
            refund_invoice_id = self.invoice_ids.mapped('refund_invoice_id')
            if refund_invoice_id:
                res['domain'].update({'authorize_refund_transaction_id': [('invoice_ids', 'in', refund_invoice_id.ids)]})
        return res

    @api.multi
    def _create_refund_payment_transaction(self, vals=None):
        for pay in self:
            if pay.payment_transaction_id:
                raise ValidationError(_('A payment transaction already exists.'))
            elif not pay.authorize_payment_token_id:
                raise ValidationError(_('Authorize payment token is required to create a new refund payment transaction.'))

        transactions = self.env['payment.transaction']
        for pay in self:
            transaction_vals = pay._prepare_auth_refund_payment_transaction_vals()

            if vals:
                transaction_vals.update(vals)

            transaction = self.env['payment.transaction'].create(transaction_vals)
            transactions += transaction

            # Link the transaction to the payment.
            pay.payment_transaction_id = transaction

        return transactions

    @api.multi
    def _prepare_auth_refund_payment_transaction_vals(self):
        self.ensure_one()
        return {
            'amount': self.amount,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_country_id': self.partner_id.country_id.id,
            'invoice_ids': [(6, 0, self.invoice_ids.ids)],
            'payment_token_id': self.authorize_payment_token_id.id,
            'acquirer_id': self.authorize_payment_token_id.acquirer_id.id,
            'payment_id': self.id,
            'acquirer_reference': self.authorize_refund_transaction_id.acquirer_reference,
            'type': 'server2server',
        }

    @api.multi
    def post(self):
        payments_need_refund = self.filtered(lambda pay: pay.authorize_payment_token_id and not pay.payment_transaction_id)
        transactions = False
        if payments_need_refund and payments_need_refund.ids:
            transactions = payments_need_refund._create_refund_payment_transaction()
        res = super(AccountPayment, self - payments_need_refund).post()
        if transactions:
            transactions.authorize_s2s_do_refund()
        return res
