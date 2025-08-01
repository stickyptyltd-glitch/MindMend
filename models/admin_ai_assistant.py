"""
Admin AI Assistant for Fraud Detection and Management
===================================================
AI-powered assistant for business management, fraud detection, and administrative tasks
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re
from collections import defaultdict

class AdminAIAssistant:
    def __init__(self):
        self.fraud_patterns = {
            'payment_anomalies': {
                'rapid_transactions': {'threshold': 5, 'timeframe': 60},  # 5 transactions in 60 seconds
                'unusual_amounts': {'min': 0.01, 'max': 10000},
                'duplicate_attempts': {'threshold': 3, 'timeframe': 300},  # 3 attempts in 5 minutes
                'suspicious_locations': ['high_risk_countries'],
                'card_testing': {'small_amount_threshold': 1.00, 'attempts': 3}
            },
            'account_anomalies': {
                'rapid_registrations': {'threshold': 10, 'timeframe': 3600},  # 10 registrations per hour from same IP
                'suspicious_emails': ['temp-mail', 'guerrillamail', '10minutemail'],
                'unusual_login_patterns': {'locations': 3, 'timeframe': 3600},  # 3 different locations in 1 hour
                'credential_stuffing': {'failed_attempts': 5, 'timeframe': 300}
            },
            'usage_anomalies': {
                'api_abuse': {'requests_per_minute': 100},
                'data_scraping': {'page_views_per_minute': 50},
                'session_hijacking': {'concurrent_sessions': 3}
            }
        }
        
        self.risk_scores = defaultdict(float)
        self.blocked_ips = set()
        self.flagged_users = set()
        
    def analyze_fraud_risk(self, activity_data: Dict) -> Dict:
        """
        Analyze activity for fraud risk
        Returns risk assessment with score and recommendations
        """
        risk_assessment = {
            'risk_score': 0,
            'risk_level': 'low',
            'fraud_indicators': [],
            'recommendations': [],
            'auto_actions': []
        }
        
        # Payment fraud detection
        if 'payment' in activity_data:
            payment_risk = self._analyze_payment_fraud(activity_data['payment'])
            risk_assessment['risk_score'] += payment_risk['score']
            risk_assessment['fraud_indicators'].extend(payment_risk['indicators'])
            risk_assessment['recommendations'].extend(payment_risk['recommendations'])
            
        # Account fraud detection
        if 'account' in activity_data:
            account_risk = self._analyze_account_fraud(activity_data['account'])
            risk_assessment['risk_score'] += account_risk['score']
            risk_assessment['fraud_indicators'].extend(account_risk['indicators'])
            risk_assessment['recommendations'].extend(account_risk['recommendations'])
            
        # Usage fraud detection
        if 'usage' in activity_data:
            usage_risk = self._analyze_usage_fraud(activity_data['usage'])
            risk_assessment['risk_score'] += usage_risk['score']
            risk_assessment['fraud_indicators'].extend(usage_risk['indicators'])
            risk_assessment['recommendations'].extend(usage_risk['recommendations'])
            
        # Calculate risk level
        if risk_assessment['risk_score'] >= 80:
            risk_assessment['risk_level'] = 'critical'
            risk_assessment['auto_actions'].append('block_immediately')
        elif risk_assessment['risk_score'] >= 60:
            risk_assessment['risk_level'] = 'high'
            risk_assessment['auto_actions'].append('require_verification')
        elif risk_assessment['risk_score'] >= 40:
            risk_assessment['risk_level'] = 'medium'
            risk_assessment['auto_actions'].append('monitor_closely')
        else:
            risk_assessment['risk_level'] = 'low'
            
        return risk_assessment
        
    def _analyze_payment_fraud(self, payment_data: Dict) -> Dict:
        """Analyze payment data for fraud indicators"""
        risk_result = {
            'score': 0,
            'indicators': [],
            'recommendations': []
        }
        
        # Check for rapid transactions
        if payment_data.get('transaction_count', 0) > self.fraud_patterns['payment_anomalies']['rapid_transactions']['threshold']:
            risk_result['score'] += 30
            risk_result['indicators'].append('Rapid transaction pattern detected')
            risk_result['recommendations'].append('Review transaction history for card testing')
            
        # Check for unusual amounts
        amount = payment_data.get('amount', 0)
        if amount < self.fraud_patterns['payment_anomalies']['unusual_amounts']['min'] or \
           amount > self.fraud_patterns['payment_anomalies']['unusual_amounts']['max']:
            risk_result['score'] += 20
            risk_result['indicators'].append(f'Unusual payment amount: ${amount}')
            risk_result['recommendations'].append('Verify payment method and user identity')
            
        # Check for card testing patterns
        if amount <= self.fraud_patterns['payment_anomalies']['card_testing']['small_amount_threshold']:
            risk_result['score'] += 15
            risk_result['indicators'].append('Possible card testing pattern')
            risk_result['recommendations'].append('Monitor for subsequent larger transactions')
            
        return risk_result
        
    def _analyze_account_fraud(self, account_data: Dict) -> Dict:
        """Analyze account activity for fraud indicators"""
        risk_result = {
            'score': 0,
            'indicators': [],
            'recommendations': []
        }
        
        # Check email domain
        email = account_data.get('email', '')
        for suspicious_domain in self.fraud_patterns['account_anomalies']['suspicious_emails']:
            if suspicious_domain in email:
                risk_result['score'] += 25
                risk_result['indicators'].append(f'Suspicious email domain: {email}')
                risk_result['recommendations'].append('Require email verification')
                break
                
        # Check login patterns
        failed_logins = account_data.get('failed_login_attempts', 0)
        if failed_logins >= self.fraud_patterns['account_anomalies']['credential_stuffing']['failed_attempts']:
            risk_result['score'] += 35
            risk_result['indicators'].append(f'Multiple failed login attempts: {failed_logins}')
            risk_result['recommendations'].append('Enable 2FA and temporarily lock account')
            
        # Check IP reputation
        ip_address = account_data.get('ip_address', '')
        if ip_address in self.blocked_ips:
            risk_result['score'] += 40
            risk_result['indicators'].append(f'Login from blocked IP: {ip_address}')
            risk_result['recommendations'].append('Block access and investigate account')
            
        return risk_result
        
    def _analyze_usage_fraud(self, usage_data: Dict) -> Dict:
        """Analyze usage patterns for fraud indicators"""
        risk_result = {
            'score': 0,
            'indicators': [],
            'recommendations': []
        }
        
        # Check API abuse
        api_calls = usage_data.get('api_calls_per_minute', 0)
        if api_calls > self.fraud_patterns['usage_anomalies']['api_abuse']['requests_per_minute']:
            risk_result['score'] += 30
            risk_result['indicators'].append(f'Excessive API calls: {api_calls}/min')
            risk_result['recommendations'].append('Implement rate limiting')
            
        # Check for data scraping
        page_views = usage_data.get('page_views_per_minute', 0)
        if page_views > self.fraud_patterns['usage_anomalies']['data_scraping']['page_views_per_minute']:
            risk_result['score'] += 25
            risk_result['indicators'].append(f'Possible data scraping: {page_views} pages/min')
            risk_result['recommendations'].append('Enable CAPTCHA verification')
            
        return risk_result
        
    def get_management_recommendations(self, context: str) -> Dict:
        """
        Provide AI-powered recommendations for management tasks
        """
        recommendations = {
            'upgrades': [],
            'security': [],
            'optimization': [],
            'compliance': []
        }
        
        if context == 'subscription_management':
            recommendations['upgrades'] = [
                "Consider implementing tiered pricing with feature gates",
                "Add usage-based billing for API calls",
                "Implement automatic upgrade prompts at usage limits",
                "Create bundle offers for counselor + AI features"
            ]
            
        elif context == 'security_audit':
            recommendations['security'] = [
                "Enable mandatory 2FA for admin accounts",
                "Implement IP whitelisting for admin access",
                "Set up automated security scanning",
                "Create audit logs for all admin actions",
                "Implement session timeout policies"
            ]
            
        elif context == 'performance_optimization':
            recommendations['optimization'] = [
                "Enable CDN for static assets",
                "Implement database query caching",
                "Set up auto-scaling for peak usage",
                "Optimize image delivery with lazy loading",
                "Enable compression for API responses"
            ]
            
        elif context == 'compliance_check':
            recommendations['compliance'] = [
                "Ensure HIPAA compliance documentation is current",
                "Review data retention policies",
                "Update privacy policy for GDPR compliance",
                "Implement consent management system",
                "Schedule security audit with third party"
            ]
            
        return recommendations
        
    def automated_error_checking(self, system_logs: List[Dict]) -> Dict:
        """
        Analyze system logs for errors and provide fixes
        """
        error_analysis = {
            'critical_errors': [],
            'warnings': [],
            'performance_issues': [],
            'suggested_fixes': [],
            'auto_fixed': []
        }
        
        error_patterns = {
            'database_connection': r'database.*connection.*failed',
            'api_timeout': r'api.*timeout|request.*timed out',
            'memory_leak': r'memory.*exceeded|out of memory',
            'authentication': r'auth.*failed|invalid.*token',
            'payment_gateway': r'payment.*failed|stripe.*error'
        }
        
        for log in system_logs:
            log_message = log.get('message', '').lower()
            
            for error_type, pattern in error_patterns.items():
                if re.search(pattern, log_message):
                    if log.get('level') == 'ERROR':
                        error_analysis['critical_errors'].append({
                            'type': error_type,
                            'message': log['message'],
                            'timestamp': log.get('timestamp'),
                            'suggested_fix': self._get_error_fix(error_type)
                        })
                    else:
                        error_analysis['warnings'].append({
                            'type': error_type,
                            'message': log['message']
                        })
                        
        return error_analysis
        
    def _get_error_fix(self, error_type: str) -> str:
        """Get suggested fix for error type"""
        fixes = {
            'database_connection': "Check DATABASE_URL environment variable and ensure PostgreSQL is running",
            'api_timeout': "Increase timeout limits and check API endpoint health",
            'memory_leak': "Restart application and review recent code changes for memory management",
            'authentication': "Verify API keys and check token expiration settings",
            'payment_gateway': "Verify Stripe/PayPal API keys and webhook configuration"
        }
        return fixes.get(error_type, "Review logs and contact support if issue persists")
        
    def generate_admin_insights(self, analytics_data: Dict) -> Dict:
        """
        Generate business insights from analytics data
        """
        insights = {
            'revenue_insights': [],
            'user_insights': [],
            'platform_insights': [],
            'action_items': []
        }
        
        # Revenue insights
        if 'revenue' in analytics_data:
            monthly_revenue = analytics_data['revenue'].get('monthly', 0)
            growth_rate = analytics_data['revenue'].get('growth_rate', 0)
            
            if growth_rate > 20:
                insights['revenue_insights'].append("Excellent revenue growth! Consider scaling infrastructure")
            elif growth_rate < 5:
                insights['revenue_insights'].append("Revenue growth is slow. Consider promotional campaigns")
                
        # User insights
        if 'users' in analytics_data:
            churn_rate = analytics_data['users'].get('churn_rate', 0)
            engagement = analytics_data['users'].get('engagement_score', 0)
            
            if churn_rate > 10:
                insights['user_insights'].append("High churn rate detected. Implement retention strategies")
                insights['action_items'].append("Survey churned users for feedback")
                
            if engagement < 50:
                insights['user_insights'].append("Low user engagement. Consider adding gamification")
                
        # Platform insights
        if 'platform' in analytics_data:
            uptime = analytics_data['platform'].get('uptime_percentage', 100)
            error_rate = analytics_data['platform'].get('error_rate', 0)
            
            if uptime < 99.9:
                insights['platform_insights'].append("Uptime below SLA. Review infrastructure reliability")
                
            if error_rate > 1:
                insights['platform_insights'].append("High error rate. Prioritize bug fixes")
                
        return insights