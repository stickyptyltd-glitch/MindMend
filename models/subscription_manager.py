"""
Subscription Management for Mind Mend
===================================
Comprehensive subscription and billing management with Stripe integration
"""

import stripe
import os
from datetime import datetime, timezone, timedelta
from flask import current_app
from models.database import db, Subscription, Payment, Invoice, User
import json
import logging

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class SubscriptionTiers:
    """Define subscription tiers and pricing"""
    
    TIERS = {
        'free': {
            'name': 'Free',
            'description': 'Basic AI therapy sessions',
            'price_monthly': 0.00,
            'price_yearly': 0.00,
            'features': [
                '5 AI therapy sessions per month',
                'Basic mood tracking',
                'Self-guided exercises',
                'Community support'
            ],
            'limits': {
                'sessions_per_month': 5,
                'ai_models': ['gpt-3.5'],
                'video_analysis': False,
                'biometric_tracking': False,
                'priority_support': False
            }
        },
        'premium': {
            'name': 'Premium',
            'description': 'Advanced AI therapy with human counselor access',
            'price_monthly': 29.99,
            'price_yearly': 299.99,
            'stripe_price_id_monthly': 'price_1S6Vh5GmYbTnUy09lEiI83xD',
            'stripe_price_id_yearly': 'price_1S6VjkGmYbTnUy09LLVBWLXQ',
            'features': [
                'Unlimited AI therapy sessions',
                'Advanced mood and progress tracking',
                'Video emotion analysis',
                'Biometric integration (Apple Watch, Fitbit)',
                '2 human counselor sessions per month',
                'Priority AI models (GPT-4, Claude)',
                'Crisis detection and intervention',
                'Personalized therapy plans',
                'Priority support'
            ],
            'limits': {
                'sessions_per_month': -1,  # Unlimited
                'counselor_sessions_per_month': 2,
                'ai_models': ['gpt-4o', 'claude-3'],
                'video_analysis': True,
                'biometric_tracking': True,
                'priority_support': True
            }
        },
        'enterprise': {
            'name': 'Enterprise',
            'description': 'Complete mental health platform for organizations',
            'price_monthly': 99.99,
            'price_yearly': 999.99,
            'stripe_price_id_monthly': 'price_1S6VlVGmYbTnUy09dzKyosOA',
            'stripe_price_id_yearly': 'price_1S6VmwGmYbTnUy09jnNLbO4C',
            'features': [
                'Everything in Premium',
                'Unlimited human counselor sessions',
                'Advanced analytics and reporting',
                'Team/organizational insights',
                'Custom AI model training',
                'API access',
                'White-label options',
                'Dedicated account manager',
                '24/7 priority support'
            ],
            'limits': {
                'sessions_per_month': -1,  # Unlimited
                'counselor_sessions_per_month': -1,  # Unlimited
                'ai_models': 'all',
                'video_analysis': True,
                'biometric_tracking': True,
                'priority_support': True,
                'analytics_dashboard': True,
                'api_access': True
            }
        }
    }
    
    @classmethod
    def get_tier_info(cls, tier):
        """Get information for a specific tier"""
        return cls.TIERS.get(tier, cls.TIERS['free'])
    
    @classmethod
    def get_all_tiers(cls):
        """Get all available tiers"""
        return cls.TIERS


class SubscriptionManager:
    """Manage user subscriptions and billing"""
    
    def __init__(self):
        self.stripe_key = os.environ.get('STRIPE_SECRET_KEY')
        
    def create_customer(self, user):
        """Create or retrieve Stripe customer for user"""
        try:
            # Check if user already has a subscription with customer ID
            if user.subscription and user.subscription.stripe_customer_id:
                return stripe.Customer.retrieve(user.subscription.stripe_customer_id)
            
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=user.email,
                name=user.get_full_name(),
                phone=user.phone,
                metadata={
                    'user_id': user.id,
                    'platform': 'mindmend'
                }
            )
            
            return customer
            
        except Exception as e:
            current_app.logger.error(f"Error creating Stripe customer: {e}")
            raise
    
    def create_subscription(self, user, tier, billing_cycle='monthly', trial_days=7):
        """Create a new subscription for user"""
        try:
            tier_info = SubscriptionTiers.get_tier_info(tier)
            
            if tier == 'free':
                return self._create_free_subscription(user)
            
            # Get or create Stripe customer
            customer = self.create_customer(user)
            
            # Get price ID based on billing cycle
            price_id = tier_info.get(f'stripe_price_id_{billing_cycle}')
            if not price_id:
                raise ValueError(f"No price ID found for {tier} {billing_cycle}")
            
            # Calculate trial end
            trial_end = None
            if trial_days > 0:
                trial_end = int((datetime.now(timezone.utc) + timedelta(days=trial_days)).timestamp())
            
            # Create Stripe subscription
            stripe_subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                trial_end=trial_end,
                metadata={
                    'user_id': user.id,
                    'tier': tier,
                    'platform': 'mindmend'
                }
            )
            
            # Create or update local subscription record
            subscription = user.subscription
            if not subscription:
                subscription = Subscription(user_id=user.id)
                db.session.add(subscription)
            
            # Update subscription details
            subscription.stripe_customer_id = customer.id
            subscription.stripe_subscription_id = stripe_subscription.id
            subscription.tier = tier
            subscription.status = stripe_subscription.status
            subscription.price_per_month = tier_info[f'price_{billing_cycle}']
            subscription.billing_cycle = billing_cycle
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_subscription.current_period_start, tz=timezone.utc
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_subscription.current_period_end, tz=timezone.utc
            )
            
            if trial_days > 0:
                subscription.is_trial = True
                subscription.trial_start = datetime.now(timezone.utc)
                subscription.trial_end = datetime.fromtimestamp(trial_end, tz=timezone.utc)
            
            subscription.extra_data = json.dumps({
                'stripe_subscription': stripe_subscription,
                'created_via': 'subscription_manager'
            })
            
            # Update user's subscription tier
            user.subscription_tier = tier
            
            db.session.commit()
            
            return subscription
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating subscription: {e}")
            raise
    
    def _create_free_subscription(self, user):
        """Create free tier subscription"""
        subscription = user.subscription
        if not subscription:
            subscription = Subscription(user_id=user.id)
            db.session.add(subscription)
        
        subscription.tier = 'free'
        subscription.status = 'active'
        subscription.price_per_month = 0.00
        subscription.billing_cycle = 'monthly'
        subscription.current_period_start = datetime.now(timezone.utc)
        subscription.current_period_end = datetime.now(timezone.utc) + timedelta(days=30)
        
        user.subscription_tier = 'free'
        
        db.session.commit()
        return subscription
    
    def upgrade_subscription(self, user, new_tier, billing_cycle='monthly'):
        """Upgrade user's subscription"""
        try:
            subscription = user.subscription
            if not subscription:
                return self.create_subscription(user, new_tier, billing_cycle)
            
            if new_tier == 'free':
                return self.cancel_subscription(user, at_period_end=False)
            
            new_tier_info = SubscriptionTiers.get_tier_info(new_tier)
            price_id = new_tier_info.get(f'stripe_price_id_{billing_cycle}')
            
            if not price_id:
                raise ValueError(f"No price ID found for {new_tier} {billing_cycle}")
            
            # Update Stripe subscription
            if subscription.stripe_subscription_id:
                stripe_subscription = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    items=[{
                        'id': stripe.Subscription.retrieve(subscription.stripe_subscription_id).items.data[0].id,
                        'price': price_id,
                    }],
                    proration_behavior='always_invoice',
                    metadata={
                        'user_id': user.id,
                        'tier': new_tier,
                        'upgraded_at': datetime.now(timezone.utc).isoformat()
                    }
                )
                
                # Update local subscription
                subscription.tier = new_tier
                subscription.status = stripe_subscription.status
                subscription.price_per_month = new_tier_info[f'price_{billing_cycle}']
                subscription.billing_cycle = billing_cycle
                subscription.current_period_start = datetime.fromtimestamp(
                    stripe_subscription.current_period_start, tz=timezone.utc
                )
                subscription.current_period_end = datetime.fromtimestamp(
                    stripe_subscription.current_period_end, tz=timezone.utc
                )
                subscription.updated_at = datetime.now(timezone.utc)
            else:
                # No Stripe subscription exists, create new one
                return self.create_subscription(user, new_tier, billing_cycle, trial_days=0)
            
            user.subscription_tier = new_tier
            db.session.commit()
            
            return subscription
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error upgrading subscription: {e}")
            raise
    
    def cancel_subscription(self, user, at_period_end=True):
        """Cancel user's subscription"""
        try:
            subscription = user.subscription
            if not subscription:
                return None
            
            if subscription.stripe_subscription_id:
                if at_period_end:
                    # Cancel at end of billing period
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True
                    )
                    subscription.cancel_at_period_end = True
                else:
                    # Cancel immediately
                    stripe.Subscription.cancel(subscription.stripe_subscription_id)
                    subscription.status = 'canceled'
                    subscription.canceled_at = datetime.now(timezone.utc)
                    
                    # Downgrade to free tier
                    user.subscription_tier = 'free'
                    subscription.tier = 'free'
                    subscription.price_per_month = 0.00
            else:
                # Local subscription only
                subscription.status = 'canceled'
                subscription.canceled_at = datetime.now(timezone.utc)
                user.subscription_tier = 'free'
                subscription.tier = 'free'
            
            subscription.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return subscription
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error canceling subscription: {e}")
            raise
    
    def handle_payment_success(self, stripe_payment_intent):
        """Handle successful payment from Stripe webhook"""
        try:
            # Find user by customer ID or payment intent metadata
            customer_id = stripe_payment_intent.get('customer')
            user = None
            
            if customer_id:
                subscription = Subscription.query.filter_by(stripe_customer_id=customer_id).first()
                user = subscription.user if subscription else None
            
            if not user:
                metadata = stripe_payment_intent.get('metadata', {})
                user_id = metadata.get('user_id')
                if user_id:
                    user = User.query.get(user_id)
            
            if not user:
                current_app.logger.error(f"Could not find user for payment intent: {stripe_payment_intent.get('id')}")
                return
            
            # Create payment record
            payment = Payment(
                user_id=user.id,
                subscription_id=user.subscription.id if user.subscription else None,
                stripe_payment_intent_id=stripe_payment_intent.get('id'),
                stripe_charge_id=stripe_payment_intent.get('latest_charge'),
                amount=stripe_payment_intent.get('amount') / 100,  # Convert from cents
                currency=stripe_payment_intent.get('currency', 'usd').upper(),
                status='succeeded',
                payment_type='subscription',
                billing_reason=stripe_payment_intent.get('metadata', {}).get('billing_reason', 'subscription_cycle'),
                paid_at=datetime.now(timezone.utc),
                extra_data=json.dumps(stripe_payment_intent)
            )
            
            db.session.add(payment)
            db.session.commit()
            
            current_app.logger.info(f"Payment recorded for user {user.email}: ${payment.amount} {payment.currency}")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error handling payment success: {e}")
            raise
    
    def get_user_billing_info(self, user):
        """Get comprehensive billing information for user"""
        try:
            subscription = user.subscription
            if not subscription:
                return {
                    'subscription': None,
                    'tier_info': SubscriptionTiers.get_tier_info('free'),
                    'payments': [],
                    'invoices': [],
                    'next_payment': None,
                    'total_spent': 0.0
                }
            
            # Get recent payments
            payments = Payment.query.filter_by(user_id=user.id)\
                .order_by(Payment.created_at.desc()).limit(10).all()
            
            # Get recent invoices
            invoices = Invoice.query.filter_by(user_id=user.id)\
                .order_by(Invoice.created_at.desc()).limit(10).all()
            
            # Calculate total spent
            total_spent = db.session.query(db.func.sum(Payment.amount))\
                .filter(Payment.user_id == user.id, Payment.status == 'succeeded').scalar() or 0.0
            
            # Get next payment date
            next_payment = None
            if subscription.is_active() and subscription.current_period_end:
                next_payment = subscription.current_period_end
            
            return {
                'subscription': subscription,
                'tier_info': SubscriptionTiers.get_tier_info(subscription.tier),
                'payments': payments,
                'invoices': invoices,
                'next_payment': next_payment,
                'total_spent': total_spent,
                'days_until_renewal': subscription.days_until_renewal()
            }
            
        except Exception as e:
            current_app.logger.error(f"Error getting billing info: {e}")
            raise


# Initialize global subscription manager
subscription_manager = SubscriptionManager()
