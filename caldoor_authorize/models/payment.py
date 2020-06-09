# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from datetime import datetime

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare
from .authorize_request import AuthorizeAPI

_logger = logging.getLogger(__name__)


class PaymentAcquirerAuthorize(models.Model):
    _inherit = 'payment.acquirer'

    convenience_fee_product_id = fields.Many2one('product.product', string='Convenience Fee (Product)')
    convenience_fee_percent = fields.Float(string='Convenience Fee(%)')
    restricted_group_ids = fields.Many2many("res.groups", help="Hide payment method for users belongs to these groups.")


class PaymentToken(models.Model):
    _inherit = "payment.token"

    convenience_fee_product_id = fields.Many2one(related="acquirer_id.convenience_fee_product_id")
    convenience_fee_percent = fields.Float(related="acquirer_id.convenience_fee_percent")

    @api.model
    def authorize_create(self, values):
        if values.get('cc_number'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            acquirer = self.env['payment.acquirer'].browse(values['acquirer_id'])
            expiry = str(values['cc_expiry'][:2]) + str(values['cc_expiry'][-2:])
            partner = self.env['res.partner'].browse(values['partner_id'])
            transaction = AuthorizeAPI(acquirer)
            res = transaction.create_customer_profile(partner, values['cc_number'], expiry, values['cc_cvc'])
            if res.get('profile_id') and res.get('payment_profile_id'):
                card_type = "????"
                last_digits = values['cc_number'][-4:]
                first_two = values['cc_number'][:2]
                first_four = values['cc_number'][:4]
                first_six = values['cc_number'][:6]
                if values['cc_number'][0] == "4":
                    card_type = "VISA"
                elif first_four == "6011" or first_two == "65":
                    card_type = "DISC"
                elif (int(first_two) >= 51 and int(first_two) <= 55) or (int(first_six) >= 222100 and int(first_six) <= 272099):
                    card_type = "MSTR"
                elif first_two == "34" or first_two == "37":
                    card_type = "AMEX"
                    last_digits = values['cc_number'][-5:]

                return {
                    'authorize_profile': res.get('profile_id'),
                    'name': '%s - %s' % (card_type, last_digits),
                    'acquirer_ref': res.get('payment_profile_id'),
                }
            else:
                raise ValidationError(_('The Customer Profile creation in Authorize.NET failed.'))
        else:
            return values

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
        amount = order.amount_total - order.partner_id._get_outstanding_credit()
        if self.acquirer_id.provider == 'authorize' and order.payment_option == 'c50':
            amount = self.amount - order.partner_id._get_outstanding_credit()
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
        if status_code == self._authorize_valid_tx_status:
            if tree.get('x_type').lower() == 'refund':
                self.write({
                    'acquirer_reference': tree.get('x_trans_id'),
                    'date': fields.Datetime.now(),
                })
                self._set_transaction_done()
            elif tree.get('x_type').lower() == 'void' and self.state == 'done':
                self.write({
                    'state': 'cancel',
                    'date': fields.Date.today()
                })
                self._log_payment_transaction_received()

            result = True
        return result
    
###############my changes
    @api.multi
    def authorize_s2s_void_transaction(self):
        self.ensure_one()
        transaction = AuthorizeAPI(self.acquirer_id)
        tree = transaction.void(self.acquirer_reference or '')
        if tree['x_response_code'] == 3:
            raise ValidationError( ("The status of the transaction you are trying to void is not 'Unsettled'! Can not void this transaction."))
        return self._authorize_s2s_validate_tree(tree)
##############################

    @api.multi
    def authorize_s2s_do_refund(self):
        self.ensure_one()
        transaction = AuthorizeAPI(self.acquirer_id)
        res = transaction.credit(self.payment_token_id, self.amount, self.acquirer_reference)
        return self._authorize_s2s_validate_tree(res)

    def _check_amount_and_confirm_order(self):
        self.ensure_one()
        for order in self.sale_order_ids.filtered(lambda so: so.state in ('draft', 'sent')):
            amount_total = order.amount_total - order.partner_id._get_outstanding_credit()
            if (self.acquirer_id.provider == 'authorize' and order.payment_option == 'c50') or (float_compare(self.amount, amount_total, 2) == 0):
                order.with_context(send_email=True).action_confirm()
            else:
                _logger.warning(
                    '<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r',
                    self.acquirer_id.provider, order.name, order.id,
                    order.amount_total, self.amount,
                )
                order.message_post(
                    subject=_("Amount Mismatch (%s)") % self.acquirer_id.provider,
                    body=_("The order was not confirmed despite response from the acquirer (%s): order total is %r but acquirer replied with %r.") % (
                        self.acquirer_id.provider,
                        order.amount_total,
                        self.amount,
                    )
                )


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'portal.mixin']

    authorize_refund_transaction_id = fields.Many2one('payment.transaction')
    authorize_payment_token_id = fields.Many2one('payment.token', related='authorize_refund_transaction_id.payment_token_id', string="Authorize stored credit card")

    @api.multi
    def add_payment(self):
        self.access_url = "/partner/{}/{}/payment_method/".format(self.partner_id.id, self.id)
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

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

    #TODO:fix 
    @api.multi
    def cancel(self):
        electronic_payments = self.filtered(lambda p: (p.payment_method_code == 'electronic') and p.payment_transaction_id)
        # if any([p.payment_date < fields.Date.context_today(p) for p in electronic_payments]):
        #     raise ValidationError(_("You can not cancel electronic payment 24 hour after validation."))
        res = super(AccountPayment, self).cancel()
        for payment in electronic_payments:
            payment.payment_transaction_id.s2s_void_transaction()
        return res


    @api.multi
    def post(self):
        # Add convenience_fee
        if not self.invoice_ids and self.payment_token_id and self.payment_token_id.acquirer_id.provider == 'authorize' and self.payment_method_id.code == 'electronic':
            con_fee = self.convenience_fee
            if con_fee > 0:
                # Separate convenience fees from direct electronic payments
                Invoice = self.env['account.invoice'].with_context(company_id=self.company_id.id or self.env.user.company_id.id)
                journal_id = (Invoice.default_get(['journal_id'])['journal_id'])
                if not journal_id:
                    raise ValidationError(_("journal is not set"))
                account_invoice = Invoice.new({'partner_id': self.partner_id.id})
                account_invoice._onchange_partner_id()
                accountinvoice = account_invoice._convert_to_write({name: account_invoice[name] for name in account_invoice._cache})
                accountinvoice.update({
                    'journal_id': journal_id,
                    'company_id': self.company_id.id or self.env.user.company_id.id,
                    'type': 'out_invoice',
                    'name': 'Convenience Fee',
                    })
                invoice = Invoice.create(accountinvoice)
                product_id = self.payment_token_id.acquirer_id.convenience_fee_product_id
                InvoiceLine = self.env['account.invoice.line']
                inv_line = {
                    'invoice_id': invoice.id,
                    'product_id': product_id.id, 'quantity': 1}
                invoice_line = InvoiceLine.new(inv_line)
                invoice_line._onchange_product_id()
                inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
                inv_line.update(price_unit=con_fee, invoice_line_tax_ids=False)
                invoice_line = InvoiceLine.create(inv_line)
                invoice.action_invoice_open()
                self.message_post(body=_("Convenience Fee invoice created for payment matching: '<a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>'" % (invoice.id, invoice.number)))

            self.amount += con_fee
        payments_need_trans = self.filtered(lambda pay: pay.payment_token_id and not pay.payment_transaction_id)
        transactions = payments_need_trans._create_payment_transaction()
        done_transactions = transactions.filtered(lambda trans: trans.state == 'done')
        done_transactions.write({'state': 'posted'})
        transactions.s2s_do_transaction()
        transactions.write({'is_processed': True})
        payments_need_refund = self.filtered(lambda pay: pay.authorize_payment_token_id and not pay.payment_transaction_id)
        refund_transactions = False
        if payments_need_refund and payments_need_refund.ids:
            refund_transactions = payments_need_refund._create_refund_payment_transaction()
        res = super(AccountPayment, self - payments_need_refund).post()
        if refund_transactions:
            refund_transactions.authorize_s2s_do_refund()
        transactions._log_payment_transaction_received()
        # applying outstanding credits if the automatic invoice creation is configured
        if self.env['ir.config_parameter'].sudo().get_param('sale.automatic_invoice') and not self.env.context.get('bypass_credit_payment'):
            for invoice in self.mapped('invoice_ids').filtered(lambda i: i.type == 'out_invoice' and i.state == 'open'):
                invoice._get_outstanding_info_JSON()
                datas = json.loads(invoice.outstanding_credits_debits_widget)
                if datas and datas.get('content'):
                    credit_line = [line for line in datas['content'] if line['amount'] == invoice.residual]
                    if credit_line:
                        invoice.assign_outstanding_credit(credit_line[0]['id'])
                    else:
                        for line in datas['content']:
                            if not float_is_zero(invoice.residual, precision_rounding=invoice.currency_id.rounding):
                                invoice.assign_outstanding_credit(line['id'])
        return res
