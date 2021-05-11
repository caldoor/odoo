# -*- coding: utf-8 -*-

from dateutil import tz

from odoo import api, fields, models


class PaymentToken(models.Model):
    _inherit = 'payment.token'

    last_successful_transaction_date = fields.Datetime(compute='_compute_last_successful_transaction_date')
    contact_name = fields.Char(string='Contact Name')

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
            if token.contact_name:
                token_name += ' %s' % token.contact_name
            if token.last_successful_transaction_date:
                token_name += ' %s' % token._get_formatted_time()
            names.append((token.id, token_name))
        return names

    def _get_formatted_time(self):
        self.ensure_one()
        if self.last_successful_transaction_date:
            timezone = tz.gettz('America/Los_Angeles')
            transaction_date_pacific = self.last_successful_transaction_date.astimezone(timezone)
            return transaction_date_pacific.strftime('%m/%d/%Y %I:%M%p')
        else:
            return None
