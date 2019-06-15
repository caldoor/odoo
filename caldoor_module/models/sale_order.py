# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_category_id = fields.Many2one("product.category", string="Category", delegate=True, domain=[('is_for_sale_order', '=', True)])
    is_drawerbox = fields.Boolean(string="DrawerBox", compute="_check_drawerbox")

    def _check_drawerbox(self):
        for rec in self:
            db = False
            if rec.x_category_id.name == 'Drawer Box':
                db = True
            rec.is_drawerbox = db