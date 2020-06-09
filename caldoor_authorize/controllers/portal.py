# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import WebsitePayment

class WebsitePayment(WebsitePayment):
    @http.route(['/partner/<int:p_id>/<int:record_id>/payment_method/'], type='http', auth="user", website=True)
    def partner_payment_method(self, p_id, record_id, **kwargs):
        acquirers = list(request.env['payment.acquirer'].search([
            ('website_published', '=', True), ('registration_view_template_id', '!=', False),
            ('payment_flow', '=', 's2s'), ('company_id', '=', request.env.user.company_id.id)
        ]))
        partner = request.env["res.partner"].browse([p_id])
        payment_tokens = partner.payment_token_ids
        payment_tokens |= partner.commercial_partner_id.sudo().payment_token_ids
        return_url = request.params.get('redirect', '/web#id={}&action=148&model=account.payment&view_type=form&menu_id=175'.format(record_id))
        values = {
            'pms': payment_tokens,
            'acquirers': acquirers,
            'error_message': [kwargs['error']] if kwargs.get('error') else False,
            'return_url': return_url,
            'bootstrap_formatting': True,
            'partner_id': partner.id
        }
        return request.render("caldoor_authorize.pay_methods", values)