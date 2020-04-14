# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_template_id = fields.Integer(string="Template ID")
    x_template_path = fields.Char(string="	Template Path")