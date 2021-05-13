# -*- coding: utf-8 -*-
import json
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    wip_status = fields.Monetary(
        compute="_compute_wip_status", string="WorkInProgress Status"
    )

    def _compute_wip_status(self):
        for rec in self:
            res = self.env["sale.order"].search(
                [
                    ("partner_id", "=", rec.id),
                    ("invoice_status", "!=", "invoiced"),
                    ("state", "!=", "cancel"),
                ]
            )
            sum_total = sum(order.amount_total for order in res)
            rec.wip_status = sum_total

    def view_open_orders(self):
        action_data = self.env.ref("sale.act_res_partner_2_sale_order").read()[0]
        action_data.update({"domain": [("invoice_status", "!=", "invoiced"), ("state", "!=", "cancel")]})
        return action_data
