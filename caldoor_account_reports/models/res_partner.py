from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import format_date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    due_invoice_partner_ids = fields.One2many(string='Other contacts', comodel_name='res.partner', compute='_compute_due_invoice_partner_ids')

    def _compute_due_invoice_partner_ids(self):
        Partner = self.env['res.partner']
        Invoice = self.env['account.invoice']
        for s in self:
            ins = None
            partners = None
            contacts = []
            
            if s.parent_id:
                partners = Partner.search(['|', ('parent_id', '=', s.parent_id.id), ('id', '=', s.parent_id.id)])
                ins = Invoice.search(['&', ('partner_id', 'in', s.parts.ids), ('status', '=', 'open')])
            else:
                partners = Partner.search(['|', ('parent_id', '=', s.id), ('id', '=', s.id)])
                ins = Invoice.search(['&', ('partner_id', 'in', s.parts.ids), ('status', '=', 'open')])
            
            if (not ins is None) and (not partners is None):
                for i in ins.filtered(lambda x: x.partner_id.id in partners.ids):
                    contacts.append(i.partner_id.id)
                
                partners.filtered(lambda x: x.id in contacts)

            s.due_invoice_partner_ids = partners

    def open_action_followup(self):
        if self.parent_id:
            return super(ResPartner, self.parent_id).open_action_followup()
        return super(ResPartner, self).open_action_followup()

    def _compute_for_followup(self):
        for s in self.filtered(lambda x: x.parent_id):
            s.total_due = s.parent_id.total_due
        for s in self.filtered(lambda x: not x.parent_id):
            super(ResPartner, s)._compute_for_followup()