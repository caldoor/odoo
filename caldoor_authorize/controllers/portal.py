# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import WebsitePayment

class WebsitePayment(WebsitePayment):
    @http.route(['/partner/payment_method'], type='http', auth="user", website=True)
    def partner_payment_method(self, **kwargs):
        acquirers = list(request.env['payment.acquirer'].search([
            ('website_published', '=', True), ('registration_view_template_id', '!=', False),
            ('payment_flow', '=', 's2s'), ('company_id', '=', request.env.user.company_id.id)
        ]))

        account = request.env['account.payment'].search([
            ('access_token', '=', request.params["access_token"])
        ])
        partner = account.partner_id
        payment_tokens = partner.payment_token_ids
        payment_tokens |= partner.commercial_partner_id.sudo().payment_token_ids
        return_url = request.params.get('redirect', '/partner/payment_method')
        values = {
            'pms': payment_tokens,
            'acquirers': acquirers,
            'error_message': [kwargs['error']] if kwargs.get('error') else False,
            'return_url': return_url,
            'bootstrap_formatting': True,
            'partner_id': partner.id
        }
        return request.render("caldoor_authorize.pay_methods", values)