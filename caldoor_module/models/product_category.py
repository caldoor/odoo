# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductCategory(models.Model):
    _inherit = "product.category"

    is_for_sale_order = fields.Boolean(string="Sale Order Category")