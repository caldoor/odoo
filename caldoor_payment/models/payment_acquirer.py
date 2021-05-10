# -*- coding: utf-8 -*-

from dateutil import tz

from odoo import api, fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    last_successful_transaction_date = fields.Datetime(compute='_compute_last_successful_transaction_date')
    contact_name = fields.Char(string='Contact Name')

    @api.depends('payment_ids')
    def _compute_last_successful_transaction_date(self):
        timezone = tz.gettz('America/Los_Angeles')
        for token in self:
            last_date = None
            for payment in token.payment_ids:
                if payment.state == 'done' and (not last_date or payment.date > last_date):
                    last_date = payment.date
            token.last_successful_transaction_date = last_date.astimezone(timezone) if last_date else None

    @api.multi
    def name_get(self):
        names = []
        for token in self:
            token_name = token.name
            if token.contact_name:
                token_name += ' %s' % token.contact_name
            if token.last_successful_transaction_date:
                date_str = token.last_successful_transaction_date.strftime('%m/%d/%Y %I:%M%p')
                token_name += ' %s' % date_str
            names.append((token.id, token_name))
        return names
