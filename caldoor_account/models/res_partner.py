# -*- coding: utf-8 -*-
from ast import literal_eval

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_open_amount = fields.Monetary(string="Open Invoices", currency_field='currency_id', compute='_compute_open_invoice_amount')

    @api.multi
    def action_view_open_invoices(self):
        self.ensure_one()
        action = self.env.ref('caldoor_account.action_view_open_invoices').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.id))
        return action

    @api.depends('invoice_ids', 'invoice_ids.amount_total', 'invoice_ids.state', 'invoice_ids.type')
    def _compute_open_invoice_amount(self):
        for partner in self:
            self.invoice_open_amount = sum(partner.invoice_ids.filtered(lambda i: i.state not in ('done', 'draft', 'cancel') and i.type in ('out_invoice', 'out_refund')).mapped('residual_signed'))
