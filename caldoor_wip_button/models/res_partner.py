# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wip_status = fields.Monetary(compute='_compute_wip_status', string="WorkInProgress Status")

    def _compute_wip_status(self):
        for rec in self:
            res = self.env['sale.order'].search([('partner_id', '=', rec.id)])
            sum_total = sum(order.amount_total for order in res)
            rec.wip_status = sum_total