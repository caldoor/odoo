odoo.define('caldoor_authorize.payment_form', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var PaymentForm = require('payment.payment_form');
    PaymentForm.include({
        events: _.extend({}, PaymentForm.prototype.events, {
            'change .fee_decision': '_onClickFeeDecision'
        }), 

        _onClickFeeDecision: function(ev) {
            var $checkbox = $(ev.currentTarget);
            this.$(".fee_decision").prop('checked', false);
            $checkbox.prop('checked', true);
            var disabled = $checkbox.val() === 'yes' ? false : true;
            this._disablePayButton(disabled);
        },
        _disablePayButton: function(disabled) {
            this.$('#o_payment_form_pay').attr('disabled', disabled);
        },
        updateNewPaymentDisplayStatus: function () {
            this.$(".fee_decision").prop('checked', false);
            var checked_radio = this.$('input[type="radio"]:checked');
            var provider = $(checked_radio).data('provider');
            if (provider === 'authorize') {
                this.$('.convenience_fee').show();
                this.$('#o_payment_form_pay').attr('disabled', true);
            } else {
                this.$('.convenience_fee').hide();
                this.$('#o_payment_form_pay').attr('disabled', false);
            }
            this._super.apply(this, arguments);
        },
    });
});