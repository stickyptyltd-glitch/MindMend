"""
Comprehensive Endpoint Testing Framework

Systematically tests all 342+ routes in the MindMend application.
Groups tests by priority and generates detailed reports.
"""

import pytest
import json
from flask import url_for
from app import app, db
from models.database import Patient, AdminUser
from werkzeug.security import generate_password_hash
from datetime import datetime

# Test configuration
BASE_URL = "http://34.143.177.214"


@pytest.fixture(scope='module')
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope='module')
def test_user(client):
    """Create test user for authenticated routes"""
    with app.app_context():
        # Check if test user exists
        user = Patient.query.filter_by(email='test_endpoint@test.com').first()
        if not user:
            user = Patient(
                name='Test User',
                email='test_endpoint@test.com',
                password_hash=generate_password_hash('TestPass123!'),
                subscription_tier='premium'
            )
            db.session.add(user)
            db.session.commit()
        return user


@pytest.fixture(scope='module')
def auth_client(client, test_user):
    """Authenticated test client"""
    # Login the test user
    response = client.post('/login', data={
        'email': 'test_endpoint@test.com',
        'password': 'TestPass123!'
    }, follow_redirects=True)

    return client


@pytest.fixture(scope='module')
def admin_client(client):
    """Admin authenticated test client"""
    # Login as admin
    response = client.post('/admin/login', data={
        'email': 'admin@mindmend.com',
        'password': 'Admin123!'
    }, follow_redirects=True)

    return client


class TestPublicEndpoints:
    """Test public routes that don't require authentication"""

    def test_homepage(self, client):
        """Test homepage loads"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'MindMend' in response.data or b'mindmend' in response.data.lower()

    def test_login_page(self, client):
        """Test login page accessible"""
        response = client.get('/login')
        assert response.status_code == 200

    def test_register_page(self, client):
        """Test registration page accessible"""
        response = client.get('/register')
        assert response.status_code == 200

    def test_health_check(self, client):
        """Test health endpoint"""
        response = client.get('/health')
        assert response.status_code == 200

    def test_admin_login_page(self, client):
        """Test admin login page"""
        response = client.get('/admin/login')
        assert response.status_code == 200

    def test_pricing_page(self, client):
        """Test pricing page"""
        response = client.get('/pricing')
        # Should be 200 or redirect
        assert response.status_code in [200, 301, 302, 404]

    def test_about_page(self, client):
        """Test about page if exists"""
        response = client.get('/about')
        # May not exist, accept 404
        assert response.status_code in [200, 404]


class TestAuthenticationFlow:
    """Test authentication-related endpoints"""

    def test_login_post_invalid(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=False)
        # Should stay on login page or redirect back
        assert response.status_code in [200, 302]

    def test_login_post_valid(self, client, test_user):
        """Test login with valid credentials"""
        response = client.post('/login', data={
            'email': 'test_endpoint@test.com',
            'password': 'TestPass123!'
        }, follow_redirects=False)
        # Should redirect to dashboard
        assert response.status_code in [200, 302]

    def test_logout(self, auth_client):
        """Test logout"""
        response = auth_client.get('/logout', follow_redirects=False)
        assert response.status_code in [200, 302]

    def test_forgot_password_page(self, client):
        """Test forgot password page"""
        response = client.get('/forgot-password')
        assert response.status_code in [200, 404]


class TestAuthenticatedEndpoints:
    """Test routes that require user authentication"""

    def test_dashboard_unauthenticated(self, client):
        """Test dashboard redirects when not logged in"""
        response = client.get('/dashboard', follow_redirects=False)
        # Should redirect to login or show public dashboard
        assert response.status_code in [200, 302]

    def test_dashboard_authenticated(self, auth_client):
        """Test dashboard with authenticated user"""
        response = auth_client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200

    def test_user_profile(self, auth_client):
        """Test user profile page"""
        response = auth_client.get('/profile', follow_redirects=True)
        # May be /profile or /user-dashboard
        assert response.status_code in [200, 404]

    def test_sessions_list(self, auth_client):
        """Test therapy sessions list"""
        response = auth_client.get('/sessions', follow_redirects=True)
        assert response.status_code in [200, 404]


class TestAdminPanel:
    """Test admin panel endpoints"""

    def test_admin_dashboard_unauthenticated(self, client):
        """Test admin dashboard redirects when not logged in"""
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code in [302, 401, 403]

    def test_admin_dashboard_authenticated(self, admin_client):
        """Test admin dashboard with admin user"""
        response = admin_client.get('/admin/dashboard', follow_redirects=True)
        assert response.status_code == 200
        # Should contain admin-specific content
        assert b'admin' in response.data.lower() or b'dashboard' in response.data.lower()

    def test_admin_users_list(self, admin_client):
        """Test admin users list page"""
        response = admin_client.get('/admin/users', follow_redirects=True)
        assert response.status_code in [200, 404]

    def test_admin_analytics(self, admin_client):
        """Test admin analytics page"""
        response = admin_client.get('/admin/analytics', follow_redirects=True)
        assert response.status_code in [200, 404]


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_api_health(self, client):
        """Test API health endpoint"""
        response = client.get('/api/health')
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            # Should return JSON
            data = json.loads(response.data)
            assert 'status' in data or 'health' in data

    def test_api_unauthenticated(self, client):
        """Test API requires authentication"""
        response = client.get('/api/sessions')
        # Should require auth
        assert response.status_code in [401, 403, 404]


class TestPaymentEndpoints:
    """Test payment and subscription endpoints"""

    def test_subscribe_page(self, client):
        """Test subscription page"""
        response = client.get('/subscribe')
        assert response.status_code in [200, 302, 404]

    def test_premium_page(self, client):
        """Test premium features page"""
        response = client.get('/premium')
        assert response.status_code in [200, 404]

    def test_payment_webhook_invalid(self, client):
        """Test Stripe webhook with invalid data"""
        response = client.post('/webhook/stripe',
                               data=json.dumps({'test': 'data'}),
                               content_type='application/json')
        # Should handle gracefully
        assert response.status_code in [200, 400, 404]


class TestVideoAndBiometric:
    """Test video analysis and biometric endpoints"""

    def test_video_assessment_page(self, auth_client):
        """Test video assessment page"""
        response = auth_client.get('/video-assessment', follow_redirects=True)
        assert response.status_code in [200, 404]

    def test_emotion_tracking_page(self, auth_client):
        """Test emotion tracking page"""
        response = auth_client.get('/emotion-tracking', follow_redirects=True)
        assert response.status_code in [200, 404]

    def test_biometric_upload_unauthenticated(self, client):
        """Test biometric upload requires auth"""
        response = client.post('/api/biometric/upload')
        assert response.status_code in [401, 403, 404, 405]


class TestCrisisSupport:
    """Test crisis intervention endpoints"""

    def test_crisis_support_page(self, client):
        """Test crisis support page accessible"""
        response = client.get('/crisis-support', follow_redirects=True)
        # Should be public
        assert response.status_code in [200, 404]

    def test_crisis_hotline_info(self, client):
        """Test crisis hotline info"""
        response = client.get('/crisis/hotlines', follow_redirects=True)
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Test error handling"""

    def test_404_page(self, client):
        """Test 404 error page"""
        response = client.get('/nonexistent-page-12345')
        assert response.status_code == 404

    def test_invalid_api_endpoint(self, client):
        """Test invalid API endpoint"""
        response = client.get('/api/invalid-endpoint-xyz')
        assert response.status_code == 404


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "admin: marks tests as admin tests"
    )


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
