# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    default_payment_method_id = fields.Many2one(string="Default Payment Method",
                                                comodel_name="account.payment.method")


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        if self.journal_id.default_payment_method_id:
            self.payment_method_id = self.journal_id.default_payment_method_id
