# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountTax(models.Model):
    _inherit = "account.tax"

    x_tax_description = fields.Char(string="Tax Description")