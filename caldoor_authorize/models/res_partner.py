# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_outstanding_credit(self):
        self.ensure_one()
        domain = [('partner_id', '=', self.id), ('type', '=', 'out_refund'), ('state', '=', 'open')]
        credit_notes = self.env['account.invoice'].sudo().read_group(domain, ['partner_id', 'amount_total'], ['partner_id', 'amount_total'])
        if credit_notes:
            return credit_notes[0]['amount_total']
        return 0.00

    @api.multi
    def _get_pending_orders(self):
        self.ensure_one()
        domain = [('invoice_id.partner_id', '=', self.id), ('invoice_type', '=', 'out_invoice'), ('invoice_id.state', '=', 'open')]
        invoice_lines = self.env['account.invoice.line'].search(domain)
        sale_order_lines = invoice_lines.mapped('sale_line_ids')
        if sale_order_lines:
            return ','.join(sale_order_lines.mapped('order_id.name'))
        return ''
