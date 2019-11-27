# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_token_id = fields.Many2one('payment.token', string="Saved payment token", domain=[('acquirer_id.capture_manually', '=', False)],
                                       help="Note that tokens from acquirers set to only authorize transactions (instead of capturing the amount) are not available.")

    @api.onchange('invoice_ids', 'payment_method_id')
    def onchange_invoice_ids(self):
        result = {'domain': {}, 'value': {}, 'warning': {}}
        if self.invoice_ids:
            if len(self.invoice_ids.mapped('partner_id')) > 1:
                raise UserError(_("You can not process payments for invoices belongs to multiple customers."))
            partners = self.invoice_ids.mapped('partner_id') | self.invoice_ids.mapped('partner_id.commercial_partner_id') | self.invoice_ids.mapped('partner_id.commercial_partner_id').mapped('child_ids')
            if partners:
                result['domain'].update({'payment_token_id': [('partner_id', 'in', partners.ids), ('acquirer_id.capture_manually', '=', False)]})
        return result

    @api.multi
    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''
        values = super(account_register_payments, self)._prepare_payment_vals(invoices)
        if self.payment_token_id:
            values.update({'payment_token_id': self.payment_token_id.id})
        return values

    @api.multi
    def create_payments(self):
        self = self.with_context(bypass_credit_payment=True)
        action_data = super(account_register_payments, self).create_payments()
        payment_id = action_data.get('res_id', False)
        if payment_id:
            payment = self.env['account.payment'].browse(payment_id)
            payment.post()
            if payment.payment_transaction_id:
                payment.payment_transaction_id._log_payment_transaction_received()
        return action_data
