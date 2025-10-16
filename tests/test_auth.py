"""
Tests for authentication
"""

import pytest
from app import app, db
from models.database import Patient
from werkzeug.security import generate_password_hash
from flask_login import login_user, current_user

@pytest.fixture(scope='function')
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_login(client):
    """Test user login"""
    with client.application.test_request_context():
        user = Patient(
            id=123,
            name='Test User',
            email='test@test.com',
            password_hash=generate_password_hash('password')
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        assert current_user.is_authenticated

    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
