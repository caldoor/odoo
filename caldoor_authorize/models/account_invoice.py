# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def _refund_cleanup_lines(self, lines):
        lines = lines.filtered(lambda l: not any([sol.is_cf_line for sol in l.sale_line_ids]))
        return super(AccountInvoice, self)._refund_cleanup_lines(lines)
