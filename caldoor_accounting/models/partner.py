# -*- coding: utf-8 -*-

from odoo import models, api, _

class Partner(models.Model):
    _inherit = "res.partner"
##call super()
    @api.multi
    @api.depends('name', 'ref')
    def name_get(self):
        rec = super(Partner,self).name_get()
        if self.env.context.get('show_attribute'):  
            res = []    
            for partner in rec:
                partner_id = self.env['res.partner'].browse([ partner[0]])
                 
                display_value = partner[1]              
                if partner_id.ref:
                    display_value += ' (Cust# '                   
                    display_value += partner_id.ref 
                    display_value += ')'           
                res.append((partner[0], display_value))        
            return res
        return rec


