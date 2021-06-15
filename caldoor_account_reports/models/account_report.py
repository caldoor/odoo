# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, models, api
from odoo.exceptions import UserError
from odoo.tools import append_content_to_html, DEFAULT_SERVER_DATE_FORMAT


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

class AccountFollowupReport(models.AbstractModel):
    _inherit = 'account.followup.report'

    @api.model
    def send_email(self, options):
        """
        Send by mail the followup to the customer
        """
        partner = self.env['res.partner'].browse(options.get('partner_id'))
        emails = partner.due_invoice_emails.split(';')
        email = self.env['res.partner'].browse(partner.address_get(['invoice'])['invoice']).email
        options['keep_summary'] = True
        if email and email.strip():
            # When printing we need te replace the \n of the summary by <br /> tags
            body_html = self.with_context(print_mode=True, mail=True, lang=partner.lang or self.env.user.lang).get_html(options)
            start_index = body_html.find(b'<span>', body_html.find(b'<div class="o_account_reports_summary">'))
            end_index = start_index > -1 and body_html.find(b'</span>', start_index) or -1
            if end_index > -1:
                replaced_msg = body_html[start_index:end_index].replace(b'\n', b'')
                body_html = body_html[:start_index] + replaced_msg + body_html[end_index:]
            msg = _('Follow-up email sent to %s') % ', '.join(emails)
            # Remove some classes to prevent interactions with messages
            msg += '<br>' + body_html.decode('utf-8')\
                .replace('o_account_reports_summary', '')\
                .replace('o_account_reports_edit_summary_pencil', '')\
                .replace('fa-pencil', '')
            msg_id = partner.message_post(body=msg, message_type='email')
            email = self.env['mail.mail'].create({
                'mail_message_id': msg_id.id,
                'subject': _('%s Payment Reminder') % (self.env.user.company_id.name) + ' - ' + partner.name,
                'body_html': append_content_to_html(body_html, self.env.user.signature or '', plaintext=False),
                'email_from': self.env.user.email or '',
                'email_to': emails,
                'body': msg,
            })
            partner.message_subscribe(partner.due_invoice_partner_ids.ids)
            return True
        raise UserError(_('Could not send mail to partner because it does not have any email address defined'))

    def _get_lines(self, options, line_id=None):
        lines = super(AccountFollowupReport, self)._get_lines(options, line_id=line_id)
        overdue_lines = [line for line in lines if len(line['columns']) >= 2 and line['columns'][-2]['name'] == _('Total Overdue')]
        for line in overdue_lines:
            line['columns'][-2].update(name=_('Past Due'))
        return lines
