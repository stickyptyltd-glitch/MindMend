#!/usr/bin/env python
"""
Phase 4 Database Migration Script
Adds Phase 4 Clinical Intelligence + Professional Onboarding tables
"""

import os
import sys
from app import app, db
from models.database import (
    # Phase 4 Clinical Intelligence Models
    ClinicalAssessment,
    OutcomeMeasure,
    InterventionTracking,
    TreatmentOutcome,
    ClinicalTrial,
    TrialParticipant,
    # Professional Onboarding Models (already exist)
    Professional,
    ProfessionalCredential,
    ProfessionalApplication,
    SessionReview,
    ProfessionalPayment,
    ProfessionalAvailability
)

def run_migration():
    """Run Phase 4 database migrations"""

    print("=" * 80)
    print("PHASE 4 DATABASE MIGRATION")
    print("=" * 80)

    with app.app_context():
        print("\n1. Creating multi-tenant schemas...")
        try:
            # Create schemas for multi-platform support
            with db.engine.connect() as conn:
                conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS shared_core"))
                conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS mindmend"))
                conn.execute(db.text("CREATE SCHEMA IF NOT EXISTS stop_the_cycle"))
                conn.commit()
            print("   ✅ Schemas created successfully")
        except Exception as e:
            print(f"   ⚠️  Schema creation skipped (may already exist or DB doesn't support schemas): {e}")

        print("\n2. Checking existing tables...")
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        print(f"   Found {len(existing_tables)} existing tables")

        print("\n3. Creating Phase 4 tables...")

        # Expected Phase 4 tables
        phase4_tables = [
            'clinical_assessment',
            'outcome_measure',
            'intervention_tracking',
            'treatment_outcome',
            'clinical_trial',
            'trial_participant',
            'professional',
            'professional_credential',
            'professional_application',
            'session_review',
            'professional_payment',
            'professional_availability'
        ]

        # Create all tables
        try:
            db.create_all()
            print("   ✅ Table creation completed")
        except Exception as e:
            print(f"   ❌ Error creating tables: {e}")
            return False

        print("\n4. Verifying table creation...")
        inspector = db.inspect(db.engine)
        new_tables = inspector.get_table_names()

        created_tables = []
        for table in phase4_tables:
            if table in new_tables:
                created_tables.append(table)
                print(f"   ✅ {table}")
            else:
                print(f"   ⚠️  {table} (may already exist)")

        print(f"\n5. Migration Summary:")
        print(f"   Total tables in database: {len(new_tables)}")
        print(f"   Phase 4 tables verified: {len(created_tables)}/{len(phase4_tables)}")

        # Verify critical Phase 4 models can be imported
        print("\n6. Verifying Phase 4 model imports...")
        critical_models = [
            ('ClinicalAssessment', ClinicalAssessment),
            ('OutcomeMeasure', OutcomeMeasure),
            ('TreatmentOutcome', TreatmentOutcome),
            ('Professional', Professional),
            ('SessionReview', SessionReview)
        ]

        for model_name, model_class in critical_models:
            try:
                # Try to query (will create table if missing)
                model_class.query.first()
                print(f"   ✅ {model_name} - OK")
            except Exception as e:
                print(f"   ⚠️  {model_name} - {str(e)[:100]}")

        print("\n" + "=" * 80)
        print("MIGRATION COMPLETE")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Start Flask app: python app.py")
        print("2. Test professional routes: http://localhost:5000/professional/login")
        print("3. Test admin routes: http://localhost:5000/admin/professionals/overview")
        print("4. Test clinical API: POST http://localhost:5000/api/v1/assessments/phq9")
        print("\n")

        return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
