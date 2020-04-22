from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import format_date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    due_invoice_partner_ids = fields.One2many(string='Other contacts', comodel_name='res.partner', compute='_compute_due_invoice_partner_ids')
    due_invoice_emails = fields.Char(string='Additional emails')

    def reset_due_invoice_emails(self):
        for s in self:
            s.due_invoice_emails = ';'.join(s.due_invoice_partner_ids.mapped(lambda x: x.email))

    @api.model
    def delete_due_invoice_email(self, options): 
        Partner = self.env['res.partner']
        for s in Partner.search([('id', '=', options['partner_id'])]):
            if options['email'] in s.due_invoice_emails:
                s.due_invoice_emails = ';'.join(list(filter(lambda x: not options['email'] in x, s.due_invoice_emails.split(';'))))

    @api.model
    def add_due_invoice_email(self, options): 
        Partner = self.env['res.partner']
        for s in Partner.search([('id', '=', options['partner_id'])]):
            if options['email'] in s.due_invoice_emails:
                continue
            if s.due_invoice_emails != '':
                s.due_invoice_emails += ';' + options['email']
            else:
                s.due_invoice_emails = options['email']

    def _compute_due_invoice_partner_ids(self):
        Partner = self.env['res.partner']
        Invoice = self.env['account.invoice']
        for s in self:
            ins = None
            partners = None
            contacts = []
            
            if s.parent_id:
                partners = Partner.search(['|', ('id', '=', s.parent_id.id), '&', ('type', '=', 'invoice'), ('parent_id', '=', s.parent_id.id)])
                ins = Invoice.search(['&', ('partner_id', 'in', partners.ids), ('state', '=', 'open')])
            else:
                partners = Partner.search(['|', ('id', '=', s.id),'&', ('type', '=', 'invoice'), ('parent_id', '=', s.id)])
                ins = Invoice.search(['&', ('partner_id', 'in', partners.ids), ('state', '=', 'open')])
            
            if (not ins is None) and (not partners is None):
                for i in ins.filtered(lambda x: x.partner_id.id in partners.ids):
                    contacts.append(i.partner_id.id)
                
                partners = partners.filtered(lambda x: x.id in contacts)

            s.due_invoice_partner_ids = partners
            s.due_invoice_emails = ";".join(partners.mapped(lambda x: x.email))

    def open_action_followup(self):
        if self.parent_id:
            self.parent_id.reset_due_invoice_emails()
            return super(ResPartner, self.parent_id).open_action_followup()
        self.reset_due_invoice_emails()
        return super(ResPartner, self).open_action_followup()

    def _compute_for_followup(self):
        for s in self.filtered(lambda x: x.parent_id):
            s.total_due = s.parent_id.total_due
        for s in self.filtered(lambda x: not x.parent_id):
            super(ResPartner, s)._compute_for_followup()