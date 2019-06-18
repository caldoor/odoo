# -*- coding: utf-8 -*-

from odoo import models, fields, api

class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    x_doorlister_code = fields.Char(string="Doorlister Code")
    x_doorlister_include_freight = fields.Boolean(string="Doorlister Include Freight")