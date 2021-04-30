# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    last_successful_transaction_date = fields.Datetime(compute='_compute_last_successful_transaction_date')

    @api.depends('payment_ids')
    def _compute_last_successful_transaction_date(self):
        for token in self:
            last_date = None
            for payment in token.payment_ids:
                if payment.state == 'done' and (not last_date or payment.date > last_date):
                    last_date = payment.date
            token.last_successful_transaction_date = last_date

    @api.multi
    def name_get(self):
        names = []
        for token in self:
            token_name = token.name
            if token.last_successful_transaction_date:
                token_name += ' %s' % token.last_successful_transaction_date
            names.append((token.id, token_name))
        return names
