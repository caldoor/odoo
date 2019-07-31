# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    x_width = fields.Char(string="Width", related="sale_line_ids.x_width", store=True)
    x_depth = fields.Char(string="Depth", related="sale_line_ids.x_depth", store=True)
    x_height = fields.Char(string="Height", related="sale_line_ids.x_height", store=True)
    x_sqft = fields.Float(string="SqFt/Box", related="sale_line_ids.x_sqft", store=True)
    x_sqft_price = fields.Float(string="SqFt Price", related="sale_line_ids.x_sqft_price", store=True)