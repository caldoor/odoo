# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class PaymentAcquirerAuthorize(models.Model):
    _inherit = 'payment.acquirer'

    convenience_fee_product_id = fields.Many2one('product.product', string='Convenience Fee (Product)')
    convenience_fee_percent = fields.Float(string='Convenience Fee(%)')
