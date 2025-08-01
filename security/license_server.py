#!/usr/bin/env python3
"""
Appo License Server
==================

Secure license management system for Appo applications.
Handles license key generation, verification, and tier management.

Author: Appo Security Team
License: Proprietary - All Rights Reserved
"""

import os
import sqlite3
import hashlib
import secrets
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('LICENSE_SECRET_KEY', secrets.token_hex(32))

# License tiers and their capabilities
LICENSE_TIERS = {
    'FREE': {
        'name': 'Free',
        'max_users': 1,
        'features': ['basic_app', 'community_support'],
        'api_calls_per_day': 100,
        'storage_gb': 1,
        'price': 0
    },
    'PRO': {
        'name': 'Professional',
        'max_users': 5,
        'features': ['basic_app', 'premium_features', 'priority_support', 'analytics'],
        'api_calls_per_day': 10000,
        'storage_gb': 50,
        'price': 29
    },
    'TEAM': {
        'name': 'Team',
        'max_users': 25,
        'features': ['basic_app', 'premium_features', 'team_management', 'priority_support', 'analytics', 'custom_branding'],
        'api_calls_per_day': 50000,
        'storage_gb': 200,
        'price': 99
    },
    'ENTERPRISE': {
        'name': 'Enterprise',
        'max_users': -1,  # Unlimited
        'features': ['all_features', 'dedicated_support', 'custom_integrations', 'white_label'],
        'api_calls_per_day': -1,  # Unlimited
        'storage_gb': -1,  # Unlimited
        'price': 499
    }
}

class LicenseDatabase:
    """Database manager for license keys and related data"""
    
    def __init__(self, db_path: str = 'security/licenses.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the license database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # License keys table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS license_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        license_key TEXT UNIQUE NOT NULL,
                        license_hash TEXT NOT NULL,
                        tier TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        customer_email TEXT,
                        customer_name TEXT,
                        app_identifier TEXT,
                        usage_count INTEGER DEFAULT 0,
                        last_used TIMESTAMP,
                        metadata TEXT  -- JSON string for additional data
                    )
                ''')
                
                # License usage logs
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS license_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        license_key TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        app_identifier TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        action TEXT,  -- verify, generate, revoke
                        success BOOLEAN,
                        details TEXT
                    )
                ''')
                
                # Brand verification table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS brand_checks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        license_key TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        branding_present BOOLEAN,
                        app_version TEXT,
                        checksum TEXT
                    )
                ''')
                
                conn.commit()
                logger.info("License database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def generate_license_key(self, tier: str, customer_email: str, 
                           customer_name: str, app_identifier: str,
                           duration_days: int = 365) -> str:
        """Generate a new license key for the specified tier"""
        
        if tier not in LICENSE_TIERS:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Generate cryptographically secure license key
        key_data = f"{tier}:{customer_email}:{app_identifier}:{secrets.token_hex(16)}"
        license_key = hashlib.sha256(key_data.encode()).hexdigest()[:32].upper()
        
        # Format license key with dashes for readability
        formatted_key = f"APPO-{license_key[:8]}-{license_key[8:16]}-{license_key[16:24]}-{license_key[24:32]}"
        
        # Hash the key for secure storage
        key_hash = generate_password_hash(formatted_key)
        
        # Calculate expiration date
        expires_at = datetime.now() + timedelta(days=duration_days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO license_keys 
                    (license_key, license_hash, tier, expires_at, customer_email, 
                     customer_name, app_identifier, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    formatted_key, key_hash, tier, expires_at,
                    customer_email, customer_name, app_identifier,
                    json.dumps({'generation_method': 'api', 'tier_info': LICENSE_TIERS[tier]})
                ))
                conn.commit()
                
                # Log the generation
                self.log_usage(formatted_key, app_identifier, '127.0.0.1', 
                             'License Server', 'generate', True, 
                             f"Generated {tier} license")
                
                logger.info(f"Generated {tier} license key for {customer_email}")
                return formatted_key
                
        except Exception as e:
            logger.error(f"License key generation failed: {e}")
            raise
    
    def verify_license_key(self, license_key: str, app_identifier: str,
                          ip_address: str = None, user_agent: str = None) -> Dict:
        """Verify a license key and return its details"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT license_hash, tier, expires_at, is_active, customer_email,
                           customer_name, usage_count, metadata
                    FROM license_keys 
                    WHERE license_key = ?
                ''', (license_key,))
                
                result = cursor.fetchone()
                
                if not result:
                    self.log_usage(license_key, app_identifier, ip_address,
                                 user_agent, 'verify', False, 'License key not found')
                    return {'valid': False, 'error': 'License key not found'}
                
                key_hash, tier, expires_at, is_active, customer_email, customer_name, usage_count, metadata = result
                
                # Check if license is active
                if not is_active:
                    self.log_usage(license_key, app_identifier, ip_address,
                                 user_agent, 'verify', False, 'License key inactive')
                    return {'valid': False, 'error': 'License key has been deactivated'}
                
                # Check expiration
                if expires_at:
                    expiry_date = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S.%f')
                    if datetime.now() > expiry_date:
                        self.log_usage(license_key, app_identifier, ip_address,
                                     user_agent, 'verify', False, 'License key expired')
                        return {'valid': False, 'error': 'License key has expired'}
                
                # Update usage statistics
                cursor.execute('''
                    UPDATE license_keys 
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE license_key = ?
                ''', (license_key,))
                conn.commit()
                
                # Log successful verification
                self.log_usage(license_key, app_identifier, ip_address,
                             user_agent, 'verify', True, f'Verified {tier} license')
                
                # Parse metadata
                metadata_dict = json.loads(metadata) if metadata else {}
                
                return {
                    'valid': True,
                    'tier': tier,
                    'tier_info': LICENSE_TIERS.get(tier, {}),
                    'expires_at': expires_at,
                    'customer_email': customer_email,
                    'customer_name': customer_name,
                    'usage_count': usage_count + 1,
                    'metadata': metadata_dict
                }
                
        except Exception as e:
            logger.error(f"License verification failed: {e}")
            self.log_usage(license_key, app_identifier, ip_address,
                         user_agent, 'verify', False, f'Verification error: {str(e)}')
            return {'valid': False, 'error': 'Verification failed'}
    
    def revoke_license_key(self, license_key: str, reason: str = 'Manual revocation') -> bool:
        """Revoke a license key"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE license_keys 
                    SET is_active = 0, metadata = json_set(COALESCE(metadata, '{}'), '$.revoked_at', ?, '$.revoke_reason', ?)
                    WHERE license_key = ?
                ''', (datetime.now().isoformat(), reason, license_key))
                
                if cursor.rowcount == 0:
                    return False
                
                conn.commit()
                
                # Log the revocation
                self.log_usage(license_key, 'admin', '127.0.0.1', 
                             'License Server', 'revoke', True, reason)
                
                logger.info(f"Revoked license key: {license_key}")
                return True
                
        except Exception as e:
            logger.error(f"License revocation failed: {e}")
            return False
    
    def log_usage(self, license_key: str, app_identifier: str, ip_address: str,
                  user_agent: str, action: str, success: bool, details: str):
        """Log license usage for audit purposes"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO license_usage 
                    (license_key, app_identifier, ip_address, user_agent, action, success, details)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (license_key, app_identifier, ip_address, user_agent, action, success, details))
                conn.commit()
        except Exception as e:
            logger.error(f"Usage logging failed: {e}")
    
    def log_brand_check(self, license_key: str, branding_present: bool, 
                       app_version: str, checksum: str):
        """Log brand verification check"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO brand_checks 
                    (license_key, branding_present, app_version, checksum)
                    VALUES (?, ?, ?, ?)
                ''', (license_key, branding_present, app_version, checksum))
                conn.commit()
        except Exception as e:
            logger.error(f"Brand check logging failed: {e}")

# Initialize database
db = LicenseDatabase()

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/generate_key', methods=['POST'])
def generate_key():
    """
    Generate a new license key
    
    Required JSON payload:
    {
        "tier": "FREE|PRO|TEAM|ENTERPRISE",
        "customer_email": "user@example.com",
        "customer_name": "John Doe",
        "app_identifier": "com.appo.myapp",
        "duration_days": 365,
        "admin_key": "your_admin_key"
    }
    """
    
    try:
        data = request.get_json()
        
        # Validate admin key (in production, use proper authentication)
        admin_key = data.get('admin_key')
        expected_admin_key = os.environ.get('APPO_ADMIN_KEY', 'admin123')
        
        if admin_key != expected_admin_key:
            return jsonify({'success': False, 'error': 'Invalid admin key'}), 401
        
        # Validate required fields
        required_fields = ['tier', 'customer_email', 'customer_name', 'app_identifier']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        tier = data['tier'].upper()
        if tier not in LICENSE_TIERS:
            return jsonify({'success': False, 'error': 'Invalid tier'}), 400
        
        # Generate license key
        license_key = db.generate_license_key(
            tier=tier,
            customer_email=data['customer_email'],
            customer_name=data['customer_name'],
            app_identifier=data['app_identifier'],
            duration_days=data.get('duration_days', 365)
        )
        
        return jsonify({
            'success': True,
            'license_key': license_key,
            'tier': tier,
            'tier_info': LICENSE_TIERS[tier],
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Key generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/verify_key', methods=['POST'])
def verify_key():
    """
    Verify a license key
    
    Required JSON payload:
    {
        "license_key": "APPO-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX",
        "app_identifier": "com.appo.myapp",
        "app_version": "1.0.0",
        "branding_checksum": "sha256_hash_of_branding_elements"
    }
    """
    
    try:
        data = request.get_json()
        
        license_key = data.get('license_key')
        app_identifier = data.get('app_identifier')
        app_version = data.get('app_version', 'unknown')
        branding_checksum = data.get('branding_checksum')
        
        if not license_key or not app_identifier:
            return jsonify({'success': False, 'error': 'Missing license_key or app_identifier'}), 400
        
        # Get client info
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Verify license key
        verification_result = db.verify_license_key(
            license_key=license_key,
            app_identifier=app_identifier,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not verification_result['valid']:
            return jsonify({
                'success': False,
                'valid': False,
                'error': verification_result['error']
            }), 200
        
        # Check branding integrity (BRAND LOCK feature)
        branding_valid = True
        if branding_checksum:
            # Expected branding elements checksum (configure this for your app)
            expected_branding_hash = os.environ.get('APPO_BRANDING_HASH', 'default_branding_hash')
            branding_valid = branding_checksum == expected_branding_hash
            
            # Log brand check
            db.log_brand_check(license_key, branding_valid, app_version, branding_checksum)
        
        response_data = {
            'success': True,
            'valid': True,
            'license_key': license_key,
            'tier': verification_result['tier'],
            'tier_info': verification_result['tier_info'],
            'expires_at': verification_result['expires_at'],
            'usage_count': verification_result['usage_count'],
            'branding_valid': branding_valid
        }
        
        # Add warning if branding is invalid
        if not branding_valid:
            response_data['warning'] = 'Invalid branding detected - app functionality may be limited'
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Key verification error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/revoke_key', methods=['POST'])
def revoke_key():
    """
    Revoke a license key
    
    Required JSON payload:
    {
        "license_key": "APPO-XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX",
        "reason": "Violation of terms",
        "admin_key": "your_admin_key"
    }
    """
    
    try:
        data = request.get_json()
        
        # Validate admin key
        admin_key = data.get('admin_key')
        expected_admin_key = os.environ.get('APPO_ADMIN_KEY', 'admin123')
        
        if admin_key != expected_admin_key:
            return jsonify({'success': False, 'error': 'Invalid admin key'}), 401
        
        license_key = data.get('license_key')
        reason = data.get('reason', 'Manual revocation')
        
        if not license_key:
            return jsonify({'success': False, 'error': 'Missing license_key'}), 400
        
        success = db.revoke_license_key(license_key, reason)
        
        return jsonify({
            'success': success,
            'revoked': success,
            'license_key': license_key,
            'reason': reason
        })
        
    except Exception as e:
        logger.error(f"Key revocation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/license_info/<license_key>', methods=['GET'])
def license_info(license_key):
    """Get public information about a license key (without sensitive data)"""
    
    try:
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT tier, expires_at, is_active, usage_count, last_used
                FROM license_keys 
                WHERE license_key = ?
            ''', (license_key,))
            
            result = cursor.fetchone()
            
            if not result:
                return jsonify({'success': False, 'error': 'License key not found'}), 404
            
            tier, expires_at, is_active, usage_count, last_used = result
            
            return jsonify({
                'success': True,
                'tier': tier,
                'tier_info': LICENSE_TIERS.get(tier, {}),
                'expires_at': expires_at,
                'is_active': bool(is_active),
                'usage_count': usage_count,
                'last_used': last_used
            })
            
    except Exception as e:
        logger.error(f"License info error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Appo License Server',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/', methods=['GET'])
def index():
    """License server status page"""
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Appo License Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; color: #333; margin-bottom: 30px; }
            .status { background: #e8f5e8; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50; }
            .endpoints { margin-top: 30px; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .method { background: #007bff; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }
            .tiers { margin-top: 30px; }
            .tier { background: #fff3cd; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #ffc107; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Appo License Server</h1>
                <p>Secure license management system</p>
            </div>
            
            <div class="status">
                <strong>Status:</strong> Online and operational<br>
                <strong>Version:</strong> 1.0.0<br>
                <strong>Time:</strong> {{ timestamp }}
            </div>
            
            <div class="endpoints">
                <h3>API Endpoints</h3>
                
                <div class="endpoint">
                    <span class="method">POST</span> <strong>/generate_key</strong><br>
                    Generate a new license key (requires admin authentication)
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <strong>/verify_key</strong><br>
                    Verify a license key and check branding integrity
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <strong>/revoke_key</strong><br>
                    Revoke a license key (requires admin authentication)
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <strong>/license_info/&lt;key&gt;</strong><br>
                    Get public information about a license key
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <strong>/health</strong><br>
                    Health check endpoint
                </div>
            </div>
            
            <div class="tiers">
                <h3>License Tiers</h3>
                {% for tier_id, tier_info in tiers.items() %}
                <div class="tier">
                    <strong>{{ tier_info.name }}</strong> ({{ tier_id }})<br>
                    Max Users: {{ tier_info.max_users if tier_info.max_users != -1 else 'Unlimited' }}<br>
                    API Calls/Day: {{ tier_info.api_calls_per_day if tier_info.api_calls_per_day != -1 else 'Unlimited' }}<br>
                    Storage: {{ tier_info.storage_gb if tier_info.storage_gb != -1 else 'Unlimited' }}GB<br>
                    Price: ${{ tier_info.price }}/month
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html_template, 
                                timestamp=datetime.now().isoformat(),
                                tiers=LICENSE_TIERS)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

if __name__ == '__main__':
    # Create security directory if it doesn't exist
    os.makedirs('security', exist_ok=True)
    
    # Initialize database
    db = LicenseDatabase()
    
    # Start server
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)