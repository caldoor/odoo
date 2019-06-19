# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    x_credit_hold = fields.Boolean(string="Credit Hold")
    x_custno = fields.Char(string="CustNo")
    x_discount = fields.Float(string="Discount %")
    x_fax = fields.Char(string="Fax")
    x_h_type = fields.Char(string="H Type")
    x_shipping_notes = fields.Text(string="Shipping Notes")
    x_shipvia = fields.Char(string="Ship Via")
    x_tax_id = fields.Many2one("account.tax", string="Tax Code")
    x_tax_exempt = fields.Char(string="Tax Exempt #")