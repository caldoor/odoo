# -*- coding: utf-8 -*-
from odoo import http

# class CaldoorModule(http.Controller):
#     @http.route('/caldoor_module/caldoor_module/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/caldoor_module/caldoor_module/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('caldoor_module.listing', {
#             'root': '/caldoor_module/caldoor_module',
#             'objects': http.request.env['caldoor_module.caldoor_module'].search([]),
#         })

#     @http.route('/caldoor_module/caldoor_module/objects/<model("caldoor_module.caldoor_module"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('caldoor_module.object', {
#             'object': obj
#         })