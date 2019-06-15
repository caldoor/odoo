# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    x_category_id = fields.Many2one("product.category", string="Category", delegate=True)
