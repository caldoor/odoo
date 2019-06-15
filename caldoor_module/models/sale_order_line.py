# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_width = fields.Char(string="Width")
    x_depth = fields.Char(string="Depth")
    x_height = fields.Char(string="Height")
    x_sqft = fields.Float(string="SqFt/Box")
    x_sqft_price = fields.Float(string="SqFt Price")
