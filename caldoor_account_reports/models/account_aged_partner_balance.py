# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import format_date


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
            col_list = [_("CreditLimit"), _("LastPayment"), _("Open Items"),  _("Age Days")]
            col_day_list = [("1 - 30"), _("31 - 60"), _("61 - 90"), _("91 - 120"), _("Older"), _("Total")]
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
        results, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(include_nullified_amount=True)._get_aged_partner_move_lines(account_types, self._context['date_to'], 'posted', 30)
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
            values_list = [values['4'], values['3'], values['2'], values['1'], values['0'], values['total']]
            invoice_dates = [line['line'].invoice_id.date_invoice for line in amls[values['partner_id']] if line.get('line', False) and line['line'].invoice_id]
            max_age = invoice_dates and (datetime.strptime(self._context['date_to'], '%Y-%m-%d').date() - min(invoice_dates)).days or 0
            vals = {
                'id': 'partner_%s' % (values['partner_id'],),
                'name': ResPartner and (ResPartner.x_custno or team) and "%s (%s / %s)" % (values['name'], ResPartner.x_custno or '', ResPartner.property_payment_term_id and ResPartner.property_payment_term_id.name or '') or values['name'],
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
                    if aml.invoice_id and aml.invoice_id.name:
                        line_name = line_name + ' ' + aml.invoice_id.name
                    if aml.invoice_id and aml.invoice_id.origin:
                        line_name = line_name + ' ' + aml.invoice_id.origin
                    if not self._context.get('no_format'):
                        line_date = line_name
                    col_list = [aml.journal_id.code, aml.account_id.code, self._format_aml_name(aml)]
                    if receivable:
                        payment_term = receivable and aml.invoice_id and aml.invoice_id.payment_term_id and aml.invoice_id.payment_term_id.x_termscode or ''
                        date_invoice = aml.invoice_id and aml.invoice_id.date_invoice
                        datetime_obj = datetime.strptime(self._context['date_to'], '%Y-%m-%d')
                        days = date_invoice and (datetime_obj.date() - date_invoice).days or 0
                        col_list = ['', '', ''] + [days]
                    vals = {
                        'id': aml.id,
                        'name': line_date,
                        'class': 'date',
                        'caret_options': caret_type,
                        'level': 4,
                        'parent_id': 'partner_%s' % (values['partner_id'],),
                        'columns': [{'name': v} for v in  col_list] + \
                                   [{'name': v} for v in [line['period'] == 5-i and self.format_value(sign * line['amount']) or '' for i in range(6)]],
                        'action_context': aml.get_action_context(),
                    }
                    lines.append(vals)
        if total and not line_id:
            totals = [total[4], total[3], total[2], total[1], total[0], total[5]]
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


class ReportAgedPartnerBalance(models.AbstractModel):
    _inherit = 'report.account.report_agedpartnerbalance'

    def _get_aged_partner_move_lines(self, account_type, date_from, target_move, period_length):
        # <<<<<<<<<<<<<Copy of _get_partner_move_lines()>>>>>>>>>>>>>>>>
        # This method can receive the context key 'include_nullified_amount' {Boolean}
        # Do an invoice and a payment and unreconcile. The amount will be nullified
        # By default, the partner wouldn't appear in this report.
        # The context key allow it to appear
        # In case of a period_length of 30 days as of 2019-02-08, we want the following periods:
        # Name       Stop         Start
        # 1 - 30   : 2019-02-07 - 2019-01-09
        # 31 - 60  : 2019-01-08 - 2018-12-10
        # 61 - 90  : 2018-12-09 - 2018-11-10
        # 91 - 120 : 2018-11-09 - 2018-10-11
        # +120     : 2018-10-10
        ctx = self._context
        periods = {}
        date_from = fields.Date.from_string(date_from)
        start = date_from
        for i in range(5)[::-1]:
            stop = start - relativedelta(days=period_length)
            period_name = str((5-(i+1)) * period_length + 1) + '-' + str((5-i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        partner_clause = ''
        cr = self.env.cr
        user_company = self.env.user.company_id
        user_currency = user_company.currency_id
        company_ids = self._context.get('company_ids') or [user_company.id]
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type), date_from, date_from,)
        if ctx.get('partner_ids'):
            partner_clause = 'AND (l.partner_id IN %s)'
            arg_list += (tuple(ctx['partner_ids'].ids),)
        if ctx.get('partner_categories'):
            partner_clause += 'AND (l.partner_id IN %s)'
            partner_ids = self.env['res.partner'].search([('category_id', 'in', ctx['partner_categories'].ids)]).ids
            arg_list += (tuple(partner_ids or [0]),)
        arg_list += (date_from, tuple(company_ids))
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.internal_type IN %s)
                AND (
                        l.reconciled IS FALSE
                        OR l.id IN(
                            SELECT credit_move_id FROM account_partial_reconcile where max_date > %s
                            UNION ALL
                            SELECT debit_move_id FROM account_partial_reconcile where max_date > %s
                        )
                    )
                    ''' + partner_clause + '''
                AND (l.date <= %s)
                AND l.company_id IN %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()
        # put a total of 0
        for i in range(7):
            total.append(0)

        # Build a string like (1,2,3) for easy use in SQL query
        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        # Use one query per period and store results in history (a list variable)
        # Each history will contain: history[1] = {'<partner_id>': <partner_debit-credit>}
        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            # CUSTOM: removed date_maturity from the query, in order to remove not due column.
            # ORIGINAL: dates_query = '(COALESCE(l.date_maturity,l.date)'
            dates_query = '(COALESCE(l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.internal_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s
                    ORDER BY COALESCE(l.date)'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids).with_context(prefetch_fields=False):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = line.company_id.currency_id._convert(line.balance, user_currency, user_company, date_from)
                if user_currency.is_zero(line_amount):
                    continue
                for partial_line in line.matched_debit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
                for partial_line in line.matched_credit_ids:
                    if partial_line.max_date <= date_from:
                        line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines.setdefault(partner_id, [])
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                        })
            history.append(partners_amount)

        #  This dictionary will store the not due amount of all partners
        # CUSTOM: Commenting code that generates not due amount in aged parter receivable report
        undue_amounts = {}
        # query = '''SELECT l.id
        #         FROM account_move_line AS l, account_account, account_move am
        #         WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
        #             AND (am.state IN %s)
        #             AND (account_account.internal_type IN %s)
        #             AND (COALESCE(l.date) >= %s)\
        #             AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
        #         AND (l.date <= %s)
        #         AND l.company_id IN %s
        #         ORDER BY COALESCE(l.date_maturity, l.date)'''
        # cr.execute(query, (tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        # aml_ids = cr.fetchall()
        # aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        # for line in self.env['account.move.line'].browse(aml_ids):
        #     partner_id = line.partner_id.id or False
        #     if partner_id not in undue_amounts:
        #         undue_amounts[partner_id] = 0.0
        #     line_amount = line.company_id.currency_id._convert(line.balance, user_currency, user_company, date_from)
        #     if user_currency.is_zero(line_amount):
        #         continue
        #     for partial_line in line.matched_debit_ids:
        #         if partial_line.max_date <= date_from:
        #             line_amount += partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
        #     for partial_line in line.matched_credit_ids:
        #         if partial_line.max_date <= date_from:
        #             line_amount -= partial_line.company_id.currency_id._convert(partial_line.amount, user_currency, user_company, date_from)
        #     if not self.env.user.company_id.currency_id.is_zero(line_amount):
        #         undue_amounts[partner_id] += line_amount
        #         lines.setdefault(partner_id, [])
        #         lines[partner_id].append({
        #             'line': line,
        #             'amount': line_amount,
        #             'period': 6,
        #         })

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            # CUSTOM: Commenting code block that add not_due colum to report.
            # undue_amt = 0.0
            # if partner['partner_id'] in undue_amounts:  # Making sure this partner actually was found by the query
            #     undue_amt = undue_amounts[partner['partner_id']]
            #
            # total[6] = total[6] + undue_amt
            # values['direction'] = undue_amt
            # if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
            #     at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]
                # Adding counter
                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            # CUSTOM: removed not_due column from the final list of values.
            # ORIGINAL: values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])
            values['total'] = sum([values[str(i)] for i in range(5)])
            ## Add for total
            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                #browse the partner name and trust field in sudo, as we may not have full access to the record (but we still have to see it in the report)
                browsed_partner = self.env['res.partner'].sudo().browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)

        return res, total, lines
