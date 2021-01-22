# -*- coding: utf-8 -*-

from odoo import models, api, _

class Partner(models.Model):
    _inherit = "res.partner"
##call super()
    @api.multi
    @api.depends('name', 'ref')
    def name_get(self):
        rec = super(Partner,self).name_get()
        invoice = self.env.context.get('show_attribute_inv')
        if self.env.context.get('show_attribute') or invoice:
            res = []    
            for partner in rec:
                partner_id = self.env['res.partner'].browse([ partner[0]])

                display_value = partner[1]
                if partner_id.ref:
                    ref = ' (Cust# %s)' % (partner_id.ref)
                    if invoice:
                        value_lst = display_value.split('\n')
                        value_lst[0] += ref
                        display_value = "\n".join(value_lst)
                    else:
                        display_value += ref
                res.append((partner[0], display_value))
            return res
        return rec


