# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        invoice['x_category_id'] = order.x_category_id.id or False
        if order.x_category_id.id:
            invoice['x_category_id'] = order.x_category_id.id
        return invoice