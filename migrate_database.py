#!/usr/bin/env python3
"""
Database Migration Script for MindMend
Handles database migrations safely with backup and rollback capabilities
"""

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(message):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {message}")
    print("=" * 60 + "\n")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_database_connection():
    """Verify database is accessible"""
    print_header("Checking Database Connection")

    try:
        from app import app, db
        with app.app_context():
            # Try to execute a simple query
            db.session.execute(db.text("SELECT 1"))
            print_success("Database connection successful")
            return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False

def backup_database():
    """Create database backup before migrations"""
    print_header("Creating Database Backup")

    database_url = os.environ.get("DATABASE_URL")
    if not database_url or "sqlite" in database_url.lower():
        print_info("SQLite database detected, skipping backup")
        return True

    # Extract PostgreSQL connection details
    if database_url.startswith("postgresql://"):
        backup_file = f"/tmp/mindmend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"

        print_info(f"Creating backup: {backup_file}")

        try:
            # Use pg_dump for PostgreSQL
            subprocess.run(
                [
                    "pg_dump",
                    database_url,
                    "-f", backup_file
                ],
                check=True,
                capture_output=True
            )
            print_success(f"Backup created: {backup_file}")
            return backup_file
        except subprocess.CalledProcessError as e:
            print_error(f"Backup failed: {e}")
            return False
    else:
        print_info("Non-PostgreSQL database, skipping backup")
        return True

def get_current_schema():
    """Get list of current database tables"""
    from app import app, db

    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        return tables

def run_migrations():
    """Run database migrations"""
    print_header("Running Database Migrations")

    try:
        from app import app, db

        with app.app_context():
            # Get current tables before migration
            print_info("Current database schema:")
            current_tables = get_current_schema()
            print(f"  Tables: {', '.join(current_tables)}")

            # Create all tables
            print_info("Creating/updating database tables...")
            db.create_all()

            # Get tables after migration
            new_tables = get_current_schema()

            # Show what changed
            added_tables = set(new_tables) - set(current_tables)
            if added_tables:
                print_success(f"New tables created: {', '.join(added_tables)}")
            else:
                print_info("No new tables created")

            # Commit changes
            db.session.commit()
            print_success("Migrations completed successfully")

            return True

    except Exception as e:
        print_error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_migrations():
    """Verify migrations were successful"""
    print_header("Verifying Migrations")

    try:
        from app import app, db
        from models.database import Patient, Session

        with app.app_context():
            # Try to query each table
            tables_to_check = [
                ("patients", Patient),
                ("sessions", Session),
            ]

            for table_name, model in tables_to_check:
                try:
                    count = model.query.count()
                    print_success(f"Table '{table_name}': {count} rows")
                except Exception as e:
                    print_error(f"Table '{table_name}' verification failed: {e}")
                    return False

            print_success("All tables verified successfully")
            return True

    except Exception as e:
        print_error(f"Verification failed: {e}")
        return False

def rollback_migration(backup_file):
    """Rollback database to backup"""
    print_header("Rolling Back Database")

    if not backup_file or backup_file is True:
        print_error("No backup file available for rollback")
        return False

    database_url = os.environ.get("DATABASE_URL")

    try:
        print_info(f"Restoring from backup: {backup_file}")

        subprocess.run(
            [
                "psql",
                database_url,
                "-f", backup_file
            ],
            check=True,
            capture_output=True
        )

        print_success("Database restored from backup")
        return True

    except subprocess.CalledProcessError as e:
        print_error(f"Rollback failed: {e}")
        return False

def main():
    """Main migration execution"""
    print_header("MindMend Database Migration")

    # Check connection
    if not check_database_connection():
        print_error("Aborting: Cannot connect to database")
        sys.exit(1)

    # Create backup
    backup_file = backup_database()
    if backup_file is False:
        print_error("Aborting: Backup failed")
        sys.exit(1)

    # Run migrations
    migration_success = run_migrations()

    if not migration_success:
        print_error("Migration failed!")

        if backup_file and backup_file is not True:
            print_info("Attempting to rollback...")
            if rollback_migration(backup_file):
                print_success("Rollback completed")
            else:
                print_error("Rollback failed - manual intervention required!")

        sys.exit(1)

    # Verify migrations
    if not verify_migrations():
        print_error("Migration verification failed!")

        if backup_file and backup_file is not True:
            print_info("Attempting to rollback...")
            rollback_migration(backup_file)

        sys.exit(1)

    # Success!
    print_header("Migration Complete")
    print_success("Database migrations completed successfully! 🎉")

    if backup_file and backup_file is not True:
        print_info(f"Backup available at: {backup_file}")

    sys.exit(0)

if __name__ == "__main__":
    main()
