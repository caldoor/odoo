# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def _format_aml_name(self, aml):
        name = super()._format_aml_name(aml)
        context = self.env.context
        if 'account_type' in context and context.get('account_type') == 'receivable':
            name = aml.invoice_id and aml.invoice_id.number or aml.move_id.name
        if len(name) > 35 and not self.env.context.get('no_format'):
            name = name[:32] + "..."
        return name

    def print_xlsx(self, options):
        options.update(self.env.context)
        return super().print_xlsx(options)
