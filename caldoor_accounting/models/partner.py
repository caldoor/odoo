# -*- coding: utf-8 -*-

from odoo import models, api, _

class Partner(models.Model):
    _inherit = "res.partner"
##call super()
    @api.multi
    def name_get(self):
        res = []       
        for partner in self:
            if partner.name:                  
                display_value = partner.name               
                if partner.ref and self.env.context.get('show_attribute'):
                    display_value += ' (Cust# '                   
                    display_value += partner.ref 
                    display_value += ')'           
                res.append((partner.id, display_value))        
        return res

