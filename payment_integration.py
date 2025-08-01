"""
Payment Integration for Mind Mend
===============================
Stripe, PayPal, Google Pay, Apple Pay Integration
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
import stripe
import paypalrestsdk
import os
import logging
from datetime import datetime
import json

payment_bp = Blueprint('payments', __name__, url_prefix='/payments')

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Initialize PayPal
paypalrestsdk.configure({
    "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),  # sandbox or live
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_CLIENT_SECRET')
})

class PaymentManager:
    def __init__(self):
        self.stripe_key = os.environ.get('STRIPE_SECRET_KEY')
        self.paypal_configured = bool(os.environ.get('PAYPAL_CLIENT_ID'))
        
    def create_stripe_checkout_session(self, plan_type, amount, currency='AUD'):
        """Create Stripe checkout session"""
        try:
            # Australian domain configuration
            domain = os.environ.get('DOMAIN', 'mindmend.com.au')
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Mind Mend {plan_type.title()} Plan',
                            'description': f'Mental health therapy - {plan_type} subscription',
                            'images': [f'https://{domain}/static/images/logo.png']
                        },
                        'unit_amount': int(amount * 100),  # Stripe uses cents
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'https://{domain}/payments/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'https://{domain}/payments/cancel',
                customer_email=session.get('user_email') if session.get('user_email') else None,
                automatic_tax={'enabled': True},
                billing_address_collection='required',
                metadata={
                    'plan_type': plan_type,
                    'company': 'Sticky Pty Ltd',
                    'country': 'Australia'
                }
            )
            return {'success': True, 'session_id': session.id, 'url': session.url}
            
        except Exception as e:
            logging.error(f"Stripe checkout error: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_paypal_payment(self, plan_type, amount, currency='AUD'):
        """Create PayPal payment"""
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": f"https://{os.environ.get('DOMAIN', 'mindmend.com.au')}/payments/paypal/success",
                    "cancel_url": f"https://{os.environ.get('DOMAIN', 'mindmend.com.au')}/payments/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"Mind Mend {plan_type.title()} Plan",
                            "sku": f"mindmend_{plan_type}",
                            "price": str(amount),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": f"Mental health therapy subscription - {plan_type}"
                }]
            })
            
            if payment.create():
                for link in payment.links:
                    if link.rel == "approval_url":
                        return {'success': True, 'payment_id': payment.id, 'approval_url': link.href}
            else:
                return {'success': False, 'error': payment.error}
                
        except Exception as e:
            logging.error(f"PayPal payment error: {e}")
            return {'success': False, 'error': str(e)}

payment_manager = PaymentManager()

@payment_bp.route('/plans')
def payment_plans():
    """Display payment plans with Australian pricing"""
    plans = {
        'basic': {
            'name': 'Basic Plan',
            'price_aud': 49,
            'price_usd': 32,
            'features': [
                '2 AI therapy sessions/month',
                'Basic progress tracking',
                'Crisis detection',
                'Email support'
            ]
        },
        'premium': {
            'name': 'Premium Plan',
            'price_aud': 99,
            'price_usd': 65,
            'features': [
                '4 AI therapy sessions/month',
                'Video assessment',
                'Advanced analytics',
                'Priority support',
                'Biometric integration'
            ]
        },
        'enterprise': {
            'name': 'Enterprise Plan',
            'price_aud': 199,
            'price_usd': 130,
            'features': [
                'Unlimited AI sessions',
                'Human counselor access',
                'Family accounts',
                'Custom integrations',
                '24/7 phone support'
            ]
        }
    }
    
    return render_template('payments/plans.html', 
                         plans=plans,
                         stripe_key=os.environ.get('STRIPE_PUBLISHABLE_KEY'),
                         paypal_client_id=os.environ.get('PAYPAL_CLIENT_ID'))

@payment_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create payment checkout session"""
    data = request.get_json()
    plan_type = data.get('plan_type')
    payment_method = data.get('payment_method', 'stripe')
    currency = data.get('currency', 'AUD')
    
    # Australian pricing
    pricing = {
        'basic': {'AUD': 49, 'USD': 32},
        'premium': {'AUD': 99, 'USD': 65},
        'enterprise': {'AUD': 199, 'USD': 130}
    }
    
    amount = pricing.get(plan_type, {}).get(currency, 49)
    
    if payment_method == 'stripe':
        result = payment_manager.create_stripe_checkout_session(plan_type, amount, currency)
    elif payment_method == 'paypal':
        result = payment_manager.create_paypal_payment(plan_type, amount, currency)
    else:
        result = {'success': False, 'error': 'Unsupported payment method'}
    
    return jsonify(result)

@payment_bp.route('/success')
def payment_success():
    """Payment success page"""
    session_id = request.args.get('session_id')
    payment_id = request.args.get('paymentId')
    
    if session_id:
        # Stripe success
        try:
            session_data = stripe.checkout.Session.retrieve(session_id)
            return render_template('payments/success.html', 
                                 payment_method='Stripe',
                                 session_data=session_data)
        except Exception as e:
            flash(f'Error retrieving payment details: {e}', 'error')
            
    elif payment_id:
        # PayPal success
        return render_template('payments/success.html', 
                             payment_method='PayPal',
                             payment_id=payment_id)
    
    return render_template('payments/success.html')

@payment_bp.route('/cancel')
def payment_cancel():
    """Payment cancelled page"""
    return render_template('payments/cancel.html')

@payment_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        # Handle successful payment
        logging.info(f"Payment completed: {session['id']}")
        
    elif event['type'] == 'invoice.payment_failed':
        # Handle failed payment
        logging.warning(f"Payment failed for invoice: {event['data']['object']['id']}")
    
    return jsonify({'status': 'success'})

@payment_bp.route('/apple-pay-domain-association')
def apple_pay_domain_association():
    """Apple Pay domain association file"""
    return """3614F12E51C78B5EEFA3F7CC7F1A0D5DFD22E96AE5BD2BB7A9DBDE2A7BB4F3C1

This file is required for Apple Pay domain verification.
Generated for: mindmend.com.au
Company: Sticky Pty Ltd
Date: 2025-01-01"""

@payment_bp.route('/google-pay-verify')
def google_pay_verify():
    """Google Pay merchant verification"""
    return jsonify({
        'merchantId': os.environ.get('GOOGLE_PAY_MERCHANT_ID'),
        'merchantName': 'Sticky Pty Ltd',
        'domainName': os.environ.get('DOMAIN', 'mindmend.com.au'),
        'countryCode': 'AU',
        'currencyCode': 'AUD'
    })

# Mobile payment endpoints
@payment_bp.route('/mobile/apple-pay', methods=['POST'])
def mobile_apple_pay():
    """Handle Apple Pay from mobile app"""
    data = request.get_json()
    payment_token = data.get('payment_token')
    amount = data.get('amount')
    
    # Process Apple Pay payment token with Stripe
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='aud',
            payment_method_data={
                'type': 'card',
                'card': {
                    'token': payment_token
                }
            },
            metadata={
                'payment_method': 'apple_pay',
                'platform': 'mobile'
            }
        )
        
        return jsonify({
            'success': True,
            'payment_intent_id': payment_intent.id,
            'client_secret': payment_intent.client_secret
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@payment_bp.route('/mobile/google-pay', methods=['POST'])
def mobile_google_pay():
    """Handle Google Pay from mobile app"""
    data = request.get_json()
    payment_token = data.get('payment_token')
    amount = data.get('amount')
    
    # Process Google Pay payment token
    try:
        # Similar to Apple Pay processing
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='aud',
            payment_method_data={
                'type': 'card',
                'card': {
                    'token': payment_token
                }
            },
            metadata={
                'payment_method': 'google_pay',
                'platform': 'mobile'
            }
        )
        
        return jsonify({
            'success': True,
            'payment_intent_id': payment_intent.id,
            'client_secret': payment_intent.client_secret
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400