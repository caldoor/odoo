# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    signature = fields.Binary('Signature', help='Signature for Sale orders with advance payment term.', copy=False, attachment=True)