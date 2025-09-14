"""
🔐 Advanced OAuth Authentication System for MindMend
===================================================
Comprehensive OAuth integration with Google, Facebook, Apple, Microsoft
and custom enterprise SSO solutions
"""

from flask import Blueprint, request, jsonify, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required, current_user
import requests
import secrets
import hashlib
import base64
import json
import jwt
from datetime import datetime, timedelta, timezone
import logging
from urllib.parse import urlencode, parse_qs, urlparse
from models.database import db, Patient
import os

# Configure logging
logger = logging.getLogger(__name__)

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

class OAuthConfig:
    """OAuth provider configurations"""
    
    # Google OAuth 2.0
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/oauth/google/callback')
    
    # Facebook OAuth 2.0
    FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID', '')
    FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET', '')
    FACEBOOK_REDIRECT_URI = os.environ.get('FACEBOOK_REDIRECT_URI', 'http://localhost:5000/oauth/facebook/callback')
    
    # Microsoft OAuth 2.0
    MICROSOFT_CLIENT_ID = os.environ.get('MICROSOFT_CLIENT_ID', '')
    MICROSOFT_CLIENT_SECRET = os.environ.get('MICROSOFT_CLIENT_SECRET', '')
    MICROSOFT_REDIRECT_URI = os.environ.get('MICROSOFT_REDIRECT_URI', 'http://localhost:5000/oauth/microsoft/callback')
    
    # Apple Sign In
    APPLE_CLIENT_ID = os.environ.get('APPLE_CLIENT_ID', '')
    APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID', '')
    APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID', '')
    APPLE_PRIVATE_KEY = os.environ.get('APPLE_PRIVATE_KEY', '')
    APPLE_REDIRECT_URI = os.environ.get('APPLE_REDIRECT_URI', 'http://localhost:5000/oauth/apple/callback')
    
    # JWT Settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', secrets.token_urlsafe(32))
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_DELTA = timedelta(hours=24)

class OAuthManager:
    """Centralized OAuth management system"""
    
    def __init__(self):
        self.config = OAuthConfig()
        self.providers = {
            'google': self._handle_google_oauth,
            'facebook': self._handle_facebook_oauth,
            'microsoft': self._handle_microsoft_oauth,
            'apple': self._handle_apple_oauth
        }
    
    def generate_state_token(self):
        """Generate cryptographically secure state token for OAuth"""
        return secrets.token_urlsafe(32)
    
    def verify_state_token(self, state):
        """Verify OAuth state token"""
        stored_state = session.get('oauth_state')
        return stored_state and stored_state == state
    
    def generate_pkce_challenge(self):
        """Generate PKCE code challenge for OAuth 2.1"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        session['pkce_code_verifier'] = code_verifier
        return code_challenge
    
    def create_oauth_user(self, provider_data, provider_name):
        """Create or update user from OAuth provider data"""
        try:
            email = provider_data.get('email')
            if not email:
                raise ValueError("Email is required for OAuth registration")
            
            # Check if user already exists
            existing_user = Patient.query.filter_by(email=email).first()
            
            if existing_user:
                # Update existing user's OAuth info
                oauth_info = json.loads(existing_user.oauth_providers or '{}')
                oauth_info[provider_name] = {
                    'provider_id': provider_data.get('id'),
                    'access_token': provider_data.get('access_token'),
                    'refresh_token': provider_data.get('refresh_token'),
                    'last_login': datetime.now(timezone.utc).isoformat()
                }
                existing_user.oauth_providers = json.dumps(oauth_info)
                existing_user.last_login = datetime.now(timezone.utc)
                db.session.commit()
                
                logger.info(f"Updated OAuth info for user {email} with {provider_name}")
                return existing_user
            
            # Create new user (map to existing Patient schema)
            full_name = " ".join([
                provider_data.get('given_name', provider_data.get('first_name', '')),
                provider_data.get('family_name', provider_data.get('last_name', ''))
            ]).strip() or email.split('@')[0]

            new_user = Patient(
                name=full_name,
                email=email,
                phone=None,
                oauth_providers=json.dumps({
                    provider_name: {
                        'provider_id': provider_data.get('id'),
                        'access_token': provider_data.get('access_token'),
                        'refresh_token': provider_data.get('refresh_token'),
                        'registered_at': datetime.now(timezone.utc).isoformat()
                    }
                }),
                created_at=datetime.now(timezone.utc),
                last_session=None
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"Created new OAuth user {email} via {provider_name}")
            return new_user
            
        except Exception as e:
            logger.error(f"Error creating OAuth user: {e}")
            db.session.rollback()
            raise
    
    def _handle_google_oauth(self, code, state):
        """Handle Google OAuth callback"""
        try:
            # Exchange code for access token
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'client_id': self.config.GOOGLE_CLIENT_ID,
                'client_secret': self.config.GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.GOOGLE_REDIRECT_URI
            }
            
            if 'pkce_code_verifier' in session:
                token_data['code_verifier'] = session.pop('pkce_code_verifier')
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            # Get user info from Google
            user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token_info['access_token']}"
            user_response = requests.get(user_info_url)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Add token info to user data
            user_data.update({
                'access_token': token_info.get('access_token'),
                'refresh_token': token_info.get('refresh_token')
            })
            
            return self.create_oauth_user(user_data, 'google')
            
        except Exception as e:
            logger.error(f"Google OAuth error: {e}")
            raise
    
    def _handle_facebook_oauth(self, code, state):
        """Handle Facebook OAuth callback"""
        try:
            # Exchange code for access token
            token_url = 'https://graph.facebook.com/v18.0/oauth/access_token'
            token_params = {
                'client_id': self.config.FACEBOOK_APP_ID,
                'client_secret': self.config.FACEBOOK_APP_SECRET,
                'code': code,
                'redirect_uri': self.config.FACEBOOK_REDIRECT_URI
            }
            
            token_response = requests.get(token_url, params=token_params)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            # Get user info from Facebook
            user_info_url = f"https://graph.facebook.com/me?fields=id,first_name,last_name,email&access_token={token_info['access_token']}"
            user_response = requests.get(user_info_url)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Add token info to user data
            user_data.update({
                'access_token': token_info.get('access_token')
            })
            
            return self.create_oauth_user(user_data, 'facebook')
            
        except Exception as e:
            logger.error(f"Facebook OAuth error: {e}")
            raise
    
    def _handle_microsoft_oauth(self, code, state):
        """Handle Microsoft OAuth callback"""
        try:
            # Exchange code for access token
            token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
            token_data = {
                'client_id': self.config.MICROSOFT_CLIENT_ID,
                'client_secret': self.config.MICROSOFT_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.MICROSOFT_REDIRECT_URI,
                'scope': 'openid profile email'
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            # Get user info from Microsoft Graph
            user_info_url = 'https://graph.microsoft.com/v1.0/me'
            headers = {'Authorization': f"Bearer {token_info['access_token']}"}
            user_response = requests.get(user_info_url, headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Standardize user data format
            standardized_data = {
                'id': user_data.get('id'),
                'email': user_data.get('mail') or user_data.get('userPrincipalName'),
                'given_name': user_data.get('givenName'),
                'family_name': user_data.get('surname'),
                'access_token': token_info.get('access_token'),
                'refresh_token': token_info.get('refresh_token')
            }
            
            return self.create_oauth_user(standardized_data, 'microsoft')
            
        except Exception as e:
            logger.error(f"Microsoft OAuth error: {e}")
            raise
    
    def _handle_apple_oauth(self, code, state):
        """Handle Apple Sign In callback"""
        try:
            # Apple Sign In requires JWT for client authentication
            now = datetime.now(timezone.utc)
            payload = {
                'iss': self.config.APPLE_TEAM_ID,
                'iat': now,
                'exp': now + timedelta(seconds=300),
                'aud': 'https://appleid.apple.com',
                'sub': self.config.APPLE_CLIENT_ID
            }
            
            # Sign JWT with Apple private key
            client_secret = jwt.encode(payload, self.config.APPLE_PRIVATE_KEY, algorithm='ES256', headers={'kid': self.config.APPLE_KEY_ID})
            
            # Exchange code for access token
            token_url = 'https://appleid.apple.com/auth/token'
            token_data = {
                'client_id': self.config.APPLE_CLIENT_ID,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.config.APPLE_REDIRECT_URI
            }
            
            token_response = requests.post(token_url, data=token_data)
            token_response.raise_for_status()
            token_info = token_response.json()
            
            # Decode the identity token to get user info
            id_token = token_info.get('id_token')
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
            
            user_data = {
                'id': decoded_token.get('sub'),
                'email': decoded_token.get('email'),
                'given_name': decoded_token.get('given_name', ''),
                'family_name': decoded_token.get('family_name', ''),
                'access_token': token_info.get('access_token'),
                'refresh_token': token_info.get('refresh_token')
            }
            
            return self.create_oauth_user(user_data, 'apple')
            
        except Exception as e:
            logger.error(f"Apple OAuth error: {e}")
            raise

# Initialize OAuth manager
oauth_manager = OAuthManager()

@oauth_bp.route('/login/<provider>')
def oauth_login(provider):
    """Initiate OAuth login with specified provider"""
    try:
        if provider not in oauth_manager.providers:
            return jsonify({'error': 'Unsupported OAuth provider'}), 400
        
        state = oauth_manager.generate_state_token()
        session['oauth_state'] = state
        
        # Generate authorization URL based on provider
        if provider == 'google':
            params = {
                'client_id': oauth_manager.config.GOOGLE_CLIENT_ID,
                'redirect_uri': oauth_manager.config.GOOGLE_REDIRECT_URI,
                'scope': 'openid profile email',
                'response_type': 'code',
                'state': state,
                'code_challenge': oauth_manager.generate_pkce_challenge(),
                'code_challenge_method': 'S256'
            }
            auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
            
        elif provider == 'facebook':
            params = {
                'client_id': oauth_manager.config.FACEBOOK_APP_ID,
                'redirect_uri': oauth_manager.config.FACEBOOK_REDIRECT_URI,
                'scope': 'email,public_profile',
                'response_type': 'code',
                'state': state
            }
            auth_url = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(params)}"
            
        elif provider == 'microsoft':
            params = {
                'client_id': oauth_manager.config.MICROSOFT_CLIENT_ID,
                'redirect_uri': oauth_manager.config.MICROSOFT_REDIRECT_URI,
                'scope': 'openid profile email',
                'response_type': 'code',
                'state': state
            }
            auth_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{urlencode(params)}"
            
        elif provider == 'apple':
            params = {
                'client_id': oauth_manager.config.APPLE_CLIENT_ID,
                'redirect_uri': oauth_manager.config.APPLE_REDIRECT_URI,
                'scope': 'name email',
                'response_type': 'code',
                'response_mode': 'form_post',
                'state': state
            }
            auth_url = f"https://appleid.apple.com/auth/authorize?{urlencode(params)}"
        
        logger.info(f"Redirecting to {provider} OAuth: {auth_url}")
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"OAuth login error: {e}")
        flash('OAuth authentication failed. Please try again.', 'error')
        return redirect(url_for('login'))

@oauth_bp.route('/<provider>/callback')
def oauth_callback(provider):
    """Handle OAuth provider callback"""
    try:
        # Verify state parameter
        state = request.args.get('state')
        if not oauth_manager.verify_state_token(state):
            flash('Invalid OAuth state parameter', 'error')
            return redirect(url_for('login'))
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error = request.args.get('error', 'Unknown error')
            flash(f'OAuth authorization failed: {error}', 'error')
            return redirect(url_for('login'))
        
        # Handle provider-specific callback
        if provider not in oauth_manager.providers:
            flash('Unsupported OAuth provider', 'error')
            return redirect(url_for('login'))
        
        user = oauth_manager.providers[provider](code, state)
        
        # Log the user in
        login_user(user, remember=True)
        session.pop('oauth_state', None)
        
        flash(f'Successfully logged in with {provider.title()}!', 'success')
        logger.info(f"Patient {user.email} logged in via {provider}")
        
        # Redirect to original page or dashboard
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"OAuth callback error for {provider}: {e}")
        flash(f'OAuth login with {provider} failed. Please try again.', 'error')
        return redirect(url_for('login'))

@oauth_bp.route('/unlink/<provider>', methods=['POST'])
@login_required
def unlink_oauth(provider):
    """Unlink OAuth provider from user account"""
    try:
        if not current_user.oauth_providers:
            return jsonify({'error': 'No OAuth providers linked'}), 400
        
        oauth_info = json.loads(current_user.oauth_providers)
        
        if provider not in oauth_info:
            return jsonify({'error': f'{provider} not linked to account'}), 400
        
        # Remove provider from user's OAuth providers
        del oauth_info[provider]
        current_user.oauth_providers = json.dumps(oauth_info) if oauth_info else None
        db.session.commit()
        
        logger.info(f"Patient {current_user.email} unlinked {provider}")
        return jsonify({
            'success': True,
            'message': f'{provider.title()} successfully unlinked from account'
        })
        
    except Exception as e:
        logger.error(f"OAuth unlink error: {e}")
        return jsonify({'error': 'Failed to unlink OAuth provider'}), 500

@oauth_bp.route('/status')
@login_required
def oauth_status():
    """Get user's OAuth provider status"""
    try:
        oauth_info = json.loads(current_user.oauth_providers or '{}')
        
        status = {}
        for provider in ['google', 'facebook', 'microsoft', 'apple']:
            status[provider] = {
                'linked': provider in oauth_info,
                'last_login': oauth_info.get(provider, {}).get('last_login')
            }
        
        return jsonify({
            'success': True,
            'oauth_providers': status
        })
        
    except Exception as e:
        logger.error(f"OAuth status error: {e}")
        return jsonify({'error': 'Failed to get OAuth status'}), 500
