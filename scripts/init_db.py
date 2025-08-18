#!/usr/bin/env python3
"""Database initialization script for development setup.

This script:
1. Creates the database and runs migrations
2. Applies SQLite optimizations
3. Optionally inserts sample data for testing
"""
from app.models import User, Language
from app import create_app, db
import os
import sys
from pathlib import Path
import sqlite3

# Add project root to path so we can import app modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def apply_sqlite_optimizations(db_path):
    """Apply SQLite optimization settings as per architecture requirements."""
    if not db_path:
        return {"error": "Database path not provided"}

    print("Applying SQLite optimizations...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    except Exception as e:
        error_msg = f"Failed to connect to database: {e}"
        print(error_msg)
        return {"status": "error", "error": error_msg}

    try:
        # Apply optimizations from architecture/database-schema.md
        optimizations = [
            ("journal_mode", "WAL"),
            ("synchronous", "NORMAL"),
            ("cache_size", "10000"),
            ("temp_store", "memory"),
            ("mmap_size", "268435456")  # 256MB
        ]

        results = {}

        for setting, value in optimizations:
            try:
                pragma_cmd = f"PRAGMA {setting} = {value};"
                cursor.execute(pragma_cmd)

                # Get the current value to verify
                cursor.execute(f"PRAGMA {setting};")
                current_value = cursor.fetchone()

                results[setting] = {
                    "applied": value,
                    "current": current_value[0] if current_value else None,
                    "success": True
                }
                print(f"  {pragma_cmd} -> {current_value}")

            except Exception as e:
                results[setting] = {
                    "applied": value,
                    "error": str(e),
                    "success": False
                }
                print(f"  {setting} failed: {e}")

        conn.commit()
        print("SQLite optimizations applied successfully")
        return {"status": "success", "optimizations": results}

    except Exception as e:
        error_msg = f"Failed to apply SQLite optimizations: {e}"
        print(error_msg)
        return {"status": "error", "error": error_msg}
    finally:
        conn.close()


def create_sample_languages():
    """Create sample languages for testing."""
    print("Creating sample languages...")

    try:
        # Common languages for language learning
        sample_languages = [
            {'name': 'english', 'display_name': 'English', 'code': 'en'},
            {'name': 'spanish', 'display_name': 'Spanish', 'code': 'es'},
            {'name': 'french', 'display_name': 'French', 'code': 'fr'},
            {'name': 'german', 'display_name': 'German', 'code': 'de'},
            {'name': 'italian', 'display_name': 'Italian', 'code': 'it'},
            {'name': 'portuguese', 'display_name': 'Portuguese', 'code': 'pt'},
            {'name': 'russian', 'display_name': 'Russian', 'code': 'ru'},
            {'name': 'chinese', 'display_name': 'Chinese (Mandarin)', 'code': 'zh'},
            {'name': 'japanese', 'display_name': 'Japanese', 'code': 'ja'},
            {'name': 'korean', 'display_name': 'Korean', 'code': 'ko'},
            {'name': 'arabic', 'display_name': 'Arabic', 'code': 'ar'},
            {'name': 'hindi', 'display_name': 'Hindi', 'code': 'hi'},
            {'name': 'dutch', 'display_name': 'Dutch', 'code': 'nl'},
            {'name': 'swedish', 'display_name': 'Swedish', 'code': 'sv'},
            {'name': 'norwegian', 'display_name': 'Norwegian', 'code': 'no'},
        ]
        
        languages = []
        for lang_data in sample_languages:
            # Check if language already exists
            existing = Language.query.filter_by(code=lang_data['code']).first()
            if not existing:
                language = Language(
                    name=lang_data['name'],
                    display_name=lang_data['display_name'],
                    code=lang_data['code']
                )
                languages.append(language)
        
        if languages:
            db.session.add_all(languages)
            db.session.commit()
            print(f"Created {len(languages)} sample languages:")
            for lang in languages:
                print(f"  - {lang.display_name} ({lang.code})")
        else:
            print("Languages already exist, skipping creation")

    except Exception as e:
        print(f"Error creating sample languages: {e}")
        db.session.rollback()


def create_sample_users():
    """Create sample users for testing."""
    print("Creating sample test users...")

    try:
        # Test user with password authentication
        test_user = User(
            email="test@example.com",
            is_active=True
        )
        test_user.set_password("testpassword123")

        # Test OAuth user
        oauth_user = User(
            email="oauth@example.com",
            oauth_provider="google",
            oauth_id="12345",
            is_active=True
        )

        # Inactive test user
        inactive_user = User(
            email="inactive@example.com",
            is_active=False
        )
        inactive_user.set_password("inactive123")

        # Add to database
        db.session.add_all([test_user, oauth_user, inactive_user])
        db.session.commit()

        print("Sample users created:")
        print("  - test@example.com (password: testpassword123)")
        print("  - oauth@example.com (Google OAuth)")
        print("  - inactive@example.com (inactive account)")

    except Exception as e:
        print(f"Error creating sample users: {e}")
        db.session.rollback()


def main():
    """Main initialization function."""
    print("Starting database initialization...")

    # Check command line arguments
    create_samples = "--with-samples" in sys.argv

    # Create Flask app
    app = create_app()

    with app.app_context():
        print("Flask app context established")

        # Create all tables (in case migrations haven't run)
        print("Creating database tables...")
        db.create_all()

        # Get database path for optimization
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_path = db_uri[10:]  # Remove 'sqlite:///' prefix

            # Apply SQLite optimizations
            apply_sqlite_optimizations(db_path)

            print(f"Database initialized at: {db_path}")
        else:
            print(f"Database URI: {db_uri}")

        # Create sample data if requested
        if create_samples:
            create_sample_languages()
            create_sample_users()

        print("\nDatabase initialization complete!")
        print("You can now run the Flask application.")
        if not create_samples:
            print("Tip: Run with --with-samples to create test users")


if __name__ == "__main__":
    main()
