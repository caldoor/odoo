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
            col_list = [_("CreditLimit"), _("LastPayment"), _("WorkInProgress"),  _("Age Days")]
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
        if 'account_type' in context and context.get('account_type') == 'receivable':
            receivable = True
        else:
            return super()._get_lines(options, line_id)
        sign = -1.0 if self.env.context.get('aged_balance') else 1.0
        lines = []
        account_types = [self.env.context.get('account_type')]
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(include_nullified_amount=True)._get_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)
        for values in results:
            if line_id and 'partner_%s' % (values['partner_id'],) != line_id:
                continue
            ResPartner = self.env['res.partner'].browse(values['partner_id'])
            payment = self.env['account.payment'].search([('partner_id', '=', values['partner_id'])], limit=1)
            payment_date = False
            open_orders = self.env['sale.order'].search([('partner_id', 'child_of', values['partner_id']),
                                                                 ('invoice_status', '!=', 'invoiced')])
            order_total = open_orders and sum(open_orders.mapped('amount_total')) or 0.00
            if payment:
                payment_date = payment.payment_date
            team = ResPartner.team_id and ResPartner.team_id.name or ''
            values_list = [values['direction'], values['4'], values['3'], values['2'], values['1'], values['0'], values['total']]
            invoice_dates = [line['line'].invoice_id.date_invoice for line in amls[values['partner_id']] if line.get('line', False) and line['line'].invoice_id]
            max_age = invoice_dates and (datetime.datetime.strptime(self._context['date_to'], '%Y-%m-%d').date() - min(invoice_dates)).days or 0
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': ResPartner and (ResPartner.x_custno or team) and "%s (%s / %s)" % (values['name'], ResPartner.x_custno or '', team) or values['name'],
                'level': 2,
                'columns': [{'name': ResPartner.credit_limit}, {'name': format_date(self.env, payment_date)}] + [{'name': self.format_value(order_total)}, {'name': max_age}] + [{'name': self.format_value(sign * v)} for v in values_list],
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
                    line_name = format_date(self.env, line_date) + ' ' + self._format_aml_name(aml)
                    if receivable:
                        payment_term = receivable and aml.invoice_id and aml.invoice_id.payment_term_id and aml.invoice_id.payment_term_id.x_termscode or ''
                        line_name = line_name + ' ' + payment_term
                    if not self._context.get('no_format'):
                        line_date = line_name
                    col_list = [aml.journal_id.code, aml.account_id.code, self._format_aml_name(aml)]
                    if receivable:
                        payment_term = receivable and aml.invoice_id and aml.invoice_id.payment_term_id and aml.invoice_id.payment_term_id.x_termscode or ''
                        date_invoice = aml.invoice_id and aml.invoice_id.date_invoice
                        datetime_obj = datetime.datetime.strptime(self._context['date_to'], '%Y-%m-%d')
                        days = date_invoice and (datetime_obj.date() - date_invoice).days or 0
                        col_list = ['', '', ''] + [days]
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
            total_line = {
                'id': 0,
                'name': _('Total'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': self.format_value(sign * v)} for v in totals],
            }
            lines.append(total_line)
            total_percent_line = {
                'id': 0,
                'name': _('Total Percent'),
                'class': 'total',
                'level': 2,
                'columns': [{'name': ''}] * 4 + [{'name': '{:.2f}'.format(sign * v/total[5]*100) + ' %'} for v in totals],
            }
            lines.append(total_percent_line)
        return lines
