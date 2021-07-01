# -*- coding:'utf-8' -*-

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def open_action_followup(self):
        if self.env.user.has_group('caldoor_button_access.inside_sales_caldoor'):
            return
        return super(ResPartner, self).open_action_followup()

    def action_view_open_invoices(self):
        if self.env.user.has_group('caldoor_button_access.inside_sales_caldoor'):
            return
        return super(ResPartner, self).action_view_open_invoices()
