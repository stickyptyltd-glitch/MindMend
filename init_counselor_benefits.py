#!/usr/bin/env python3
"""
Initialize Counselor Benefits Database
=====================================
This script sets up the initial counselor positions and benefits in the database
for the configurable benefits system.

Run this once to populate the database with default positions.
"""

from app import app
from models.database import db, CounselorPosition, CounselorBenefit, CounselorRequirement
from datetime import datetime

def init_counselor_benefits():
    """Initialize the counselor benefits database with default positions"""

    with app.app_context():
        # Create the database tables if they don't exist
        db.create_all()

        # Check if positions already exist
        if CounselorPosition.query.count() > 0:
            print("Counselor positions already exist in database. Skipping initialization.")
            return

        print("Initializing counselor benefits database...")

        # Define the default positions
        positions_data = [
            {
                'position_type': 'full_time',
                'title': 'Senior Mental Health Counselor',
                'salary_range_min': 85000,
                'salary_range_max': 110000,
                'currency': 'AUD',
                'benefits': [
                    {'name': 'Health insurance', 'category': 'health'},
                    {'name': 'Professional development allowance', 'category': 'professional'},
                    {'name': 'Flexible working arrangements', 'category': 'lifestyle'},
                    {'name': 'Equipment provided', 'category': 'professional'},
                    {'name': '4 weeks annual leave', 'category': 'lifestyle'}
                ],
                'requirements': [
                    {'text': 'Masters in Psychology/Counseling', 'category': 'education', 'mandatory': True},
                    {'text': 'Current AHPRA registration', 'category': 'legal', 'mandatory': True},
                    {'text': '3+ years clinical experience', 'category': 'experience', 'mandatory': True},
                    {'text': 'Telehealth experience preferred', 'category': 'experience', 'mandatory': False}
                ]
            },
            {
                'position_type': 'contract',
                'title': 'Contract Therapist',
                'hourly_rate_min': 100,
                'hourly_rate_max': 150,
                'currency': 'AUD',
                'benefits': [
                    {'name': 'Flexible schedule', 'category': 'lifestyle'},
                    {'name': 'Platform support', 'category': 'professional'},
                    {'name': 'Client matching service', 'category': 'professional'},
                    {'name': 'Payment processing included', 'category': 'financial'}
                ],
                'requirements': [
                    {'text': 'Valid counseling license', 'category': 'legal', 'mandatory': True},
                    {'text': 'Professional indemnity insurance', 'category': 'legal', 'mandatory': True},
                    {'text': 'Reliable internet connection', 'category': 'technical', 'mandatory': True},
                    {'text': 'Quiet, professional space', 'category': 'technical', 'mandatory': True}
                ]
            },
            {
                'position_type': 'part_time',
                'title': 'Part-Time Crisis Counselor',
                'hourly_rate_min': 45,
                'hourly_rate_max': 55,
                'currency': 'AUD',
                'benefits': [
                    {'name': 'Crisis intervention training provided', 'category': 'professional'},
                    {'name': '24/7 supervisor support', 'category': 'professional'},
                    {'name': 'Continuing education credits', 'category': 'professional'},
                    {'name': 'Employee assistance program', 'category': 'health'}
                ],
                'requirements': [
                    {'text': 'Crisis counseling certification', 'category': 'education', 'mandatory': True},
                    {'text': 'Available for weekend/evening shifts', 'category': 'experience', 'mandatory': True},
                    {'text': 'Experience with high-risk clients', 'category': 'experience', 'mandatory': True},
                    {'text': 'Strong emotional resilience', 'category': 'experience', 'mandatory': True}
                ]
            }
        ]

        # Create positions and their associated benefits/requirements
        for pos_data in positions_data:
            print(f"Creating position: {pos_data['title']}")

            # Create the position
            position = CounselorPosition(
                position_type=pos_data['position_type'],
                title=pos_data['title'],
                salary_range_min=pos_data.get('salary_range_min', 0),
                salary_range_max=pos_data.get('salary_range_max', 0),
                hourly_rate_min=pos_data.get('hourly_rate_min', 0),
                hourly_rate_max=pos_data.get('hourly_rate_max', 0),
                currency=pos_data['currency'],
                is_active=True,
                updated_by='system_initialization'
            )
            db.session.add(position)
            db.session.flush()  # Get the ID

            # Add benefits
            for i, benefit_data in enumerate(pos_data['benefits']):
                benefit = CounselorBenefit(
                    position_id=position.id,
                    benefit_name=benefit_data['name'],
                    benefit_category=benefit_data['category'],
                    is_active=True,
                    display_order=i
                )
                db.session.add(benefit)

            # Add requirements
            for i, req_data in enumerate(pos_data['requirements']):
                requirement = CounselorRequirement(
                    position_id=position.id,
                    requirement_text=req_data['text'],
                    requirement_category=req_data['category'],
                    is_mandatory=req_data['mandatory'],
                    is_active=True,
                    display_order=i
                )
                db.session.add(requirement)

        # Commit all changes
        db.session.commit()
        print("✅ Counselor benefits database initialized successfully!")
        print(f"Created {len(positions_data)} positions with benefits and requirements.")
        print("\nDayle can now access the admin panel at /admin/counselor-benefits to modify:")
        print("- Position titles and compensation")
        print("- Benefits for each position")
        print("- Requirements for each position")
        print("\nChanges will automatically appear on the counselor employment page.")

if __name__ == '__main__':
    init_counselor_benefits()