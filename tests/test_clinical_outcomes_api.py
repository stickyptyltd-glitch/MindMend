"""
Tests for the Clinical Outcomes API
"""

import pytest
import json
from app import app, db
from models.database import Patient, ClinicalAssessment, OutcomeMeasure
from werkzeug.security import generate_password_hash
from flask_login import login_user

@pytest.fixture(scope='function')
def authed_client():
    """Create and authenticate a test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            user = Patient(
                id=123,
                name='Clinical Test User',
                email='clinical_test@test.com',
                password_hash=generate_password_hash('ClinicalPass123!'),
                subscription_tier='premium'
            )
            db.session.add(user)
            db.session.commit()

            with client.application.test_request_context():
                login_user(user)

            yield client
            db.session.remove()
            db.drop_all()


class TestClinicalOutcomesAPI:
    """Test the Clinical Outcomes API endpoints"""

    def test_submit_phq9_assessment(self, authed_client):
        """Test submitting a PHQ-9 assessment"""
        response = authed_client.post('/api/v1/assessments/phq9', json={
            "responses": [1, 2, 3, 1, 2, 3, 1, 2, 3]
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['score'] == 18
        assert data['severity'] == 'moderately_severe'
        assert 'assessment_id' in data
        assert 'outcome_id' in data

    def test_submit_gad7_assessment(self, authed_client):
        """Test submitting a GAD-7 assessment"""
        response = authed_client.post('/api/v1/assessments/gad7', json={
            "responses": [1, 2, 3, 1, 2, 3, 1]
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['score'] == 13
        assert data['severity'] == 'moderate'
        assert 'assessment_id' in data
        assert 'outcome_id' in data

    def test_submit_pss10_assessment(self, authed_client):
        """Test submitting a PSS-10 assessment"""
        response = authed_client.post('/api/v1/assessments/pss10', json={
            "responses": [1, 2, 3, 1, 2, 3, 1, 2, 3, 4]
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['score'] == 26
        assert data['severity'] == 'moderate'
        assert 'assessment_id' in data
        assert 'outcome_id' in data

    def test_get_patient_outcomes(self, authed_client):
        """Test getting patient outcomes"""
        # First, submit an assessment to have some data
        authed_client.post('/api/v1/assessments/phq9', json={
            "responses": [1, 1, 1, 1, 1, 1, 1, 1, 1]
        })

        response = authed_client.get(f'/api/v1/outcomes/patient/123')
        assert response.status_code == 200
        data = response.get_json()
        assert data['patient_id'] == 123
        assert len(data['outcomes']) > 0
        assert data['outcomes'][0]['outcome_name'] == 'PHQ-9'

    def test_get_treatment_effectiveness(self, authed_client):
        """Test getting treatment effectiveness"""
        # This endpoint requires admin/professional role, which the test user doesn't have
        # A proper test would require a different fixture for an admin user
        # For now, we expect a 403 Forbidden error
        response = authed_client.get('/api/v1/outcomes/treatment-effectiveness')
        assert response.status_code == 403
