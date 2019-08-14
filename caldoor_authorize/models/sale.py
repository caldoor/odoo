# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_option = fields.Selection([('c50', '50 %'), ('c100', '100 %')], defualt='c100')

    def _remove_convenience_fee(self, product_id):
        self.ensure_one()
        self.order_line.filtered(lambda l: l.product_id.id == product_id).unlink()

    def has_convenience_fee_applied(self):
        return True if self.order_line.filtered(lambda l: l.is_cf_line) else False

    def _add_convenience_fee(self, acquirer_id):
        self.ensure_one()
        acquirer = self.env['payment.acquirer'].browse(acquirer_id).exists()
        if acquirer.provider == 'authorize':
            product_id = acquirer.convenience_fee_product_id.id
            convenience_fee_percent = acquirer.convenience_fee_percent
            if self.state in ('draft', 'sent'):
                self._remove_convenience_fee(product_id)
                if self.payment_option == 'c50':
                    amount = self.amount_total / 2
                else:
                    amount = self.amount_total
                fee = ((amount * convenience_fee_percent) / 100)
                self.write({'order_line': [(0, 0, {'product_id': product_id, 'product_uom_qty': 1, 'price_unit': fee, 'is_cf_line': True, 'sequence': 9999})]})

    @api.multi
    def _create_payment_transaction(self, vals):
        '''Similar to self.env['payment.transaction'].create(vals) but the values are filled with the
        current sales orders fields (e.g. the partner or the currency).
        :param vals: The values to create a new payment.transaction.
        :return: The newly created payment.transaction record.
        '''
        # Ensure the currencies are the same.
        currency = self[0].pricelist_id.currency_id
        if any([so.pricelist_id.currency_id != currency for so in self]):
            raise ValidationError(_('A transaction can\'t be linked to sales orders having different currencies.'))

        # Ensure the partner are the same.
        partner = self[0].partner_id
        if any([so.partner_id != partner for so in self]):
            raise ValidationError(_('A transaction can\'t be linked to sales orders having different partners.'))

        # Try to retrieve the acquirer. However, fallback to the token's acquirer.
        acquirer_id = vals.get('acquirer_id')
        acquirer = False
        payment_token_id = vals.get('payment_token_id')

        if payment_token_id:
            payment_token = self.env['payment.token'].sudo().browse(payment_token_id)

            # Check payment_token/acquirer matching or take the acquirer from token
            if acquirer_id:
                acquirer = self.env['payment.acquirer'].browse(acquirer_id)
                if payment_token and payment_token.acquirer_id != acquirer:
                    raise ValidationError(_('Invalid token found! Token acquirer %s != %s') % (
                    payment_token.acquirer_id.name, acquirer.name))
                if payment_token and payment_token.partner_id != partner:
                    raise ValidationError(_('Invalid token found! Token partner %s != %s') % (
                    payment_token.partner.name, partner.name))
            else:
                acquirer = payment_token.acquirer_id

        # Check an acquirer is there.
        if not acquirer_id and not acquirer:
            raise ValidationError(_('A payment acquirer is required to create a transaction.'))

        if not acquirer:
            acquirer = self.env['payment.acquirer'].browse(acquirer_id)

        # Check a journal is set on acquirer.
        if not acquirer.journal_id:
            raise ValidationError(_('A journal must be specified of the acquirer %s.' % acquirer.name))

        if not acquirer_id and acquirer:
            vals['acquirer_id'] = acquirer.id

        vals.update({
            'amount': sum(self.mapped('amount_total')),
            'currency_id': currency.id,
            'partner_id': partner.id,
            'sale_order_ids': [(6, 0, self.ids)],
        })

        # custom code start
        if len(self) == 1:  # we expect to have one order
            self.sudo()._add_convenience_fee(vals['acquirer_id'])
            if self.payment_option == 'c50':
                amount = vals['amount'] / 2
                vals['amount'] = amount + (acquirer.convenience_fee_percent * amount / 100)
            else:
                vals['amount'] = sum(self.mapped('amount_total'))
        # custom code end
        transaction = self.env['payment.transaction'].create(vals)

        # Process directly if payment_token
        if transaction.payment_token_id:
            transaction.s2s_do_transaction()

        return transaction


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_cf_line = fields.Boolean()
