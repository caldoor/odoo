# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields, _


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    is_c50_term = fields.Boolean(string='C50 Term')


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    convenience_fee = fields.Monetary(compute='_compute_convenience_fee')

    @api.multi
    @api.depends('payment_token_id', 'amount')
    def _compute_convenience_fee(self):
        for payment in self:
            if payment.payment_token_id.acquirer_id.provider == 'authorize':
                payment.convenience_fee = (payment.amount * payment.payment_token_id.acquirer_id.convenience_fee_percent) / 100

    @api.onchange('payment_token_id')
    def onchange_payment_token_id(self):
        if self.payment_token_id.acquirer_id.provider == 'authorize':
            fee = (self.amount * self.payment_token_id.acquirer_id.convenience_fee_percent) / 100
            message = _('Convenience fee of amount %s will be added if you select authorize payment') % (fee)
            return {'warning': {'title': '', 'message': message}}

    def action_validate_invoice_payment(self):
        InvoiceLine = self.env['account.invoice.line']
        for payment in self:
            invoice = payment.invoice_ids and payment.invoice_ids[0]
            if invoice.state == 'open' and payment.payment_token_id.acquirer_id.provider == 'authorize' and invoice and payment.convenience_fee:
                product_id = payment.payment_token_id.acquirer_id.convenience_fee_product_id
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
                if invoice.state != 'draft':
                    invoice.state = 'draft'
                if invoice_line:
                    price = invoice_line.price_unit + payment.convenience_fee
                    invoice_line.write({'price_unit': price})
                else:
                    inv_line = {
                        'invoice_id': invoice.id,
                        'product_id': product_id.id, 'quantity': 1}
                    invoice_line = InvoiceLine.new(inv_line)
                    invoice_line._onchange_product_id()
                    inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
                    inv_line.update(price_unit=payment.convenience_fee, invoice_line_tax_ids=False)
                    invoice_line = InvoiceLine.create(inv_line)

                invoice.action_invoice_open()
                payment.amount = payment.amount + payment.convenience_fee
        return super(AccountPayment, self).action_validate_invoice_payment()
