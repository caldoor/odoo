odoo.define('caldoor_account_reports.FollowupFormRenderer', function (require) {
    "use strict";

    var FormRenderer = require('accountReports.FollowupFormRenderer');
    
    var FollowupFormRenderer = FormRenderer.include({
        events: _.extend({}, FormRenderer.prototype.events, {
            'click .o_account_reports_contact_info_remove': '_onClickTrash',
            'click .o_account_reports_contact_info_add': '_onClickPlus',
        }),
        /**
         * Adds user email to view.
         *
         * @private
         * @param {String} email
         */
        _addEmail: function (email) {
            var self = this;
            var p = $('<p></p>').append(`
                <a t-att-href="'mailto:' + ${email}" title="Send an email">
                    <i class='fa fa-envelope' role="img" aria-label="Email"/>${email}
                </a>
            `);

            var button = $(`
                <button name="delete" arial-label="Delete email" class="btn btn-secondary o_account_reports_contact_info_remove">
                    <i class="fa fa-trash"/>
                </button>
            `).click(function (event) {
                self._onClickTrash(event);    
            });

            p.append(button);

            $("#o_account_reports_add_email").before(p);
        },
        /**
         * When the user click on trash, trigger an event to call delete using rpc.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickTrash: function (ev) {
            ev.preventDefault();
            var self = this;
            var partnerID = this.state.res_id;
            this.options = {};
            this.options.partner_id = partnerID;

            var elm = ev.target;
            if (elm.localName === 'i')
                elm = elm.parentElement;
            elm = elm.previousElementSibling;

            var email = elm.innerText.trim();
            this.options.email = email;
            this._rpc({
                model: 'res.partner',
                method: 'delete_due_invoice_email',
                args: [this.options],
            }).then(function () {
                var elm = ev.target;
                if (elm.localName === 'i')
                    elm.parentElement.parentElement.setAttribute('hidden', true);
                else
                    elm.parentElement.setAttribute('hidden', true);

                if (!self.cached_emails) this.cached_emails = {};
                if (self.cached_emails[email]) delete self.cached_emails[email];
            });
        },
        /**
         * When the user click on plus, trigger an event to call add using rpc.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onClickPlus: function (ev) {
            ev.preventDefault();
            var self = this;
            if (!this.cached_emails) this.cached_emails = {};

            var partnerID = this.state.res_id;
            this.options = {};
            this.options.partner_id = partnerID;

            var elm = ev.target;
            if (elm.localName === 'i')
                elm = elm.parentElement;
            elm = elm.previousElementSibling;

            var email = elm.value;
            if (this.cached_emails[email]) {
                elm.value = '';
                return;
            }

            this.options.email = email;
            this._rpc({
                model: 'res.partner',
                method: 'add_due_invoice_email',
                args: [this.options],
            }).then(function () {
                elm.value = '';
                self._addEmail(email);
                self.cached_emails[email] = true;
            });
        },
    });
    
    return FollowupFormRenderer;
});
    