# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"

    payment_token_id = fields.Many2one('payment.token', string="Saved payment token", domain=[('acquirer_id.capture_manually', '=', False)],
                                       help="Note that tokens from acquirers set to only authorize transactions (instead of capturing the amount) are not available.")
    convenience_fee = fields.Monetary(compute='_compute_convenience_fee')

    @api.multi
    @api.depends('payment_token_id', 'amount')
    def _compute_convenience_fee(self):
        for payment in self:
            if payment.payment_token_id.acquirer_id.provider == 'authorize':
                payment.convenience_fee = (payment.amount * payment.payment_token_id.acquirer_id.convenience_fee_percent) / 100

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

    @api.onchange('payment_token_id')
    def onchange_payment_token_id(self):
        if self.payment_token_id.acquirer_id.provider == 'authorize':
            fee = (self.amount * self.payment_token_id.acquirer_id.convenience_fee_percent) / 100
            message = _('Convenience fee of amount %.2f will be added if you select authorize payment') % (fee)
            return {'warning': {'title': '', 'message': message}}

    @api.multi
    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''
        values = super(account_register_payments, self)._prepare_payment_vals(invoices)
        if self.payment_token_id:
            values.update({'payment_token_id': self.payment_token_id.id, })
        return values

    @api.multi
    def create_payments(self):
        InvoiceLine = self.env['account.invoice.line']
        for invoice in self.invoice_ids:
            if invoice.state == 'open' and self.payment_token_id.acquirer_id.provider == 'authorize' and self.convenience_fee:
                product_id = self.payment_token_id.acquirer_id.convenience_fee_product_id
                invoice_line = invoice.invoice_line_ids.filtered(lambda l: l.product_id.id == product_id.id)
                # with authorize payment method, we charge customer convenince fee on total amount of invoice and hence
                # we need to add the convenince fee on invoice, but at this stage invoice state would be open, so we can not
                # update invoice line of validated invoice as it has posted entry
                # so for now we follow this process to update the validated invoice
                # cancel -> reset to draft -> add conveninece fee -> validate -> register payment
                # TODO: any other way to update the open invoice??
                invoice.action_invoice_cancel()
                invoice.action_invoice_draft()
                # since in action invoice draft , we processed some invoice in open state in cache when we invoice having some
                # attachements, we so we have to make state into draft forcefully here
                conv_fees = ((invoice.amount_total * self.payment_token_id.acquirer_id.convenience_fee_percent) / 100)
                if invoice.state != 'draft':
                    invoice.state = 'draft'
                if invoice_line:
                    price = invoice_line.price_unit + conv_fees
                    invoice_line.write({'price_unit': price, 'sequence': 9999})
                else:
                    inv_line = {
                        'invoice_id': invoice.id,
                        'sequence': 9999,  # Always Last Line
                        'product_id': product_id.id, 'quantity': 1}
                    invoice_line = InvoiceLine.new(inv_line)
                    invoice_line._onchange_product_id()
                    inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
                    inv_line.update(price_unit=conv_fees, invoice_line_tax_ids=False)
                    invoice_line = InvoiceLine.create(inv_line)
                invoice.action_invoice_open()
        self.amount = self.amount + self.convenience_fee
        self = self.with_context(bypass_credit_payment=True)
        action_data = super(account_register_payments, self).create_payments()
        payment_id = action_data.get('res_id', False)
        if payment_id:
            payment = self.env['account.payment'].browse(payment_id)
            payment.post()
            if payment.payment_transaction_id:
                payment.payment_transaction_id._log_payment_transaction_received()
        return action_data
