from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import format_date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    total_due = fields.Monetary(compute='_compute_for_followup', store=False, readonly=True)

    def _compute_for_followup(self):
        for s in self.filtered(lambda x: x.parent_id):
            print(s)
        for s in self.filtered(lambda x: not x.parent_id):
            super(ResPartner, s)._compute_for_followup()