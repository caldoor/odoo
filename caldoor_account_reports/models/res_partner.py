from datetime import timedelta
from odoo import api, fields, models, _
from odoo.tools.misc import format_date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def open_action_followup(self):
        if self.parent_id:
            return super(ResPartner, self.parent_id).open_action_followup()
        return super(ResPartner, self).open_action_followup()

    def _compute_for_followup(self):
        for s in self.filtered(lambda x: x.parent_id):
            s.total_due = s.parent_id.total_due
        for s in self.filtered(lambda x: not x.parent_id):
            super(ResPartner, s)._compute_for_followup()