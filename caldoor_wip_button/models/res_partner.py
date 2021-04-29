# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    wip_status = fields.Monetary(compute='_compute_wip_status', string="WorkInProgress Status")

    def _compute_wip_status(self):
        for rec in self:
            rec.wip_status = 0.0