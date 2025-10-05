
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
import stripe
import os
import logging

payment_bp = Blueprint('payment', __name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
YOUR_DOMAIN = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')

@payment_bp.route("/premium")
def premium():
    """Premium features and human counselor upgrade"""
    return render_template("premium.html")

@payment_bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@payment_bp.route("/subscribe")
def subscribe():
    """Stripe subscription page"""
    return render_template("subscribe.html", stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@payment_bp.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    """Create Stripe checkout session for subscriptions"""
    try:
        # Get the base URL for redirects
        if os.environ.get('REPLIT_DEPLOYMENT'):
            base_url = f"https://{YOUR_DOMAIN}"
        else:
            base_url = f"http://{YOUR_DOMAIN}"
            
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Mind Mend Premium',
                            'description': 'Premium AI therapy with advanced features'
                        },
                        'unit_amount': 2999,  # $29.99
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=base_url + '/dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=base_url + '/subscribe?canceled=true',
            automatic_tax={'enabled': True},
        )
        
        return redirect(checkout_session.url, code=303)
        
    except Exception as e:
        logging.error(f"Stripe checkout error: {e}")
        flash('Payment processing error. Please try again.', 'error')
        return redirect(url_for('subscribe'))

@payment_bp.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    return jsonify({'message': 'Coming soon'})
