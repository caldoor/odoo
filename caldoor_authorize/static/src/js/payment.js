odoo.define('caldoor_authorize.payment_form', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var PaymentForm = require('payment.payment_form');
    PaymentForm.include({
        events: _.extend({}, PaymentForm.prototype.events, {
            'change .fee_decision': '_onClickFeeDecision',
            'change .payment_choice': '_onClickPaymentChoice',
        }), 

        /* 
            HANDLERS
        */

        /* 
            @private
            @params {jquery event}
        */
        _onClickFeeDecision: function(ev) {
            var $checkbox = $(ev.currentTarget);
            this.$(".fee_decision").prop('checked', false);
            $checkbox.prop('checked', true);
            var disabled = $checkbox.val() === 'yes' ? false : true;
            this._disablePayButton(disabled);
        },
        /* 
            @private
            @params {jquery event}
        */
        _onClickPaymentChoice: function(ev) {
            var self = this;
            var $checkbox = $(ev.currentTarget);
            this.$(".payment_choice").prop('checked', false);
            $checkbox.prop('checked', true);
            var value = $checkbox.val();
            this._updatePaymentOption(value).then(function() {
                if(value === 'c50') {
                    self.$('.c100_term_field').addClass('d-none');
                    self.$('.c50_term_field').removeClass('d-none');
                } else {
                    self.$('.c100_term_field').removeClass('d-none');
                    self.$('.c50_term_field').addClass('d-none');
                }
                //this.$('input[name="payment_option"]').val(value);
            });
        },
        /* private */
        _updatePaymentOption: function (payment_option) {
            var orderId = this.options.orderId || parseInt(this.$('#sale_order_id').val());
            var url = '/my/orders/'+orderId+'/update/payment_option';
            return ajax.jsonRpc(url, 'call', {
                'payment_option': payment_option,
            });
        },
        /* 
            @private
            @params {boolean}
        */
        _disablePayButton: function(disabled) {
            this.$('#o_payment_form_pay').attr('disabled', disabled);
        },
        /*
            @override method from PaymentForm
        */
        updateNewPaymentDisplayStatus: function () {
            this.$(".fee_decision").prop('checked', false);
            var checked_radio = this.$('input[type="radio"]:checked');
            var provider = $(checked_radio).data('provider');
            if (provider === 'authorize' && this.$('#convenience_fee').length) {
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