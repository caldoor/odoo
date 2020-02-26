# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.tools.misc import format_date
import datetime


class report_account_aged_partner(models.AbstractModel):
    _inherit = "account.aged.partner"

    filter_date = {'date': '', 'filter': 'today'}
    filter_unfold_all = False
    filter_partner = True

    def _get_columns_name(self, options):
        columns = super()._get_columns_name(options)
        context = self.env.context
        receivable = 'model' in options and options.get('model') == 'account.aged.receivable'
        if receivable or 'account_type' in context and context.get('account_type') == 'receivable':
            columns = [{}]
            col_list = [_("Payment Terms"), _("Reference"),  _("Age Days")]
            col_day_list = [_("Not due on: %s") % format_date(self.env, options['date']['date']), ("1 - 30"), _("31 - 60"), _("61 - 90"), _("91 - 120"), _("Older"), _("Total")]
            cols_list = col_list + col_day_list
            columns += [
                {'name': v, 'class': 'number', 'style': 'white-space:nowrap;'}
                for v in cols_list]
        return columns

    @api.model
    def _get_lines(self, options, line_id=None):
        receivable = False
        context = self.env.context
        col_num = 3
        if 'account_type' in context and context.get('account_type') == 'receivable':
            receivable = True
            col_num = 5
        else:
            return super()._get_lines(options, line_id)
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(include_nullified_amount=True)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)
        for values in results:
            if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                continue
            values_list = [values['direction'], values['4'], values['3'], values['2'], values['1'], values['0'], values['total']]
            if receivable:
                values_list = values_list[2:]
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': values['name'],
                'level': 2,
                'columns': [{'name': ''}] * col_num + [{'name': self.format_value(sign * v)} for v in values_list],
                'trust': values['trust'],
                'unfoldable': True,
                'unfolded': 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'),
            }
            lines.append(vals)
            if 'partner_%s' % (values['partner_id'],) in options.get('unfolded_lines'):
                for line in amls[values['partner_id']]:
                    aml = line['line']
                    caret_type = 'account.move'
                    if aml.invoice_id:
                        caret_type = 'account.invoice.in' if aml.invoice_id.type in ('in_refund', 'in_invoice') else 'account.invoice.out'
                    elif aml.payment_id:
                        caret_type = 'account.payment'
                    line_date = aml.date_maturity or aml.date
                    if not self._context.get('no_format'):
                        line_date = format_date(self.env, line_date)
                    col_list = [aml.journal_id.code, aml.account_id.code, self._format_aml_name(aml)]
                    if receivable:
                        payment_term = receivable and aml.invoice_id and aml.invoice_id.payment_term_id and aml.invoice_id.payment_term_id.name or ''
                        date_invoice = aml.invoice_id and aml.invoice_id.date_invoice
                        datetime_obj = datetime.datetime.strptime(self._context['date_to'], '%Y-%m-%d')
                        days = date_invoice and (datetime_obj.date() - date_invoice).days or 0
                        col_list = [payment_term] + col_list[2:] + [days]
                    vals = {
                        'id': aml.id,
                        'name': line_date,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in  col_list]+\
                                   [{'name': v} for v in [line['period'] == 6-i and self.format_value(sign * line['amount']) or '' for i in range(7)]],
                        'action_context': aml.get_action_context(),
                    }
                    lines.append(vals)
        if total and not line_id:
            totals = [total[6], total[4], total[3], total[2], total[1], total[0], total[5]]
            if receivable:
                totals = totals[2:]
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * col_num + [{'name': self.format_value(sign * v)} for v in totals],
            }
            lines.append(total_line)
        return lines
