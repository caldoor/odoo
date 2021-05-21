# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    def _get_lines(self, options, line_id=None):
        lines = super(AccountFollowupReport, self)._get_lines(options, line_id=line_id)
        overdue_lines = [line for line in lines if len(line['columns']) >= 2 and line['columns'][-2]['name'] == _('Total Overdue')]
        for line in overdue_lines:
            line['columns'][-2].update(name=_('Past Due'))
        return lines
