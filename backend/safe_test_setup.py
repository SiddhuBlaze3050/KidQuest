# Safe Test Setup Template
# Use this in your test files to prevent database wiping

import pytest
import os
import tempfile
from backend.app import app, db
from backend.models import User

@pytest.fixture(autouse=True, scope="function")
def setup_isolated_test_db():
    """Setup completely isolated test database that won't affect production"""
    
    # Create temporary database file for this test
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_path = temp_db.name
    temp_db.close()
    
    # Store original configuration
    original_database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    original_testing = app.config.get('TESTING', False)
    
    try:
        # Apply test configuration
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db_path}'
        
        # Create test app context
        with app.app_context():
            # Create tables in isolated database
            db.create_all()
            
            # Create test admin user
            admin_user = User(
                username="admin",
                password_hash="$pbkdf2-sha256$29000$...",  # Hashed password
                email="admin@test.com",
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            
            yield  # Run the test
            
            # Cleanup after test
            db.session.remove()
            db.drop_all()
    
    finally:
        # Restore original configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = original_database_uri
        app.config['TESTING'] = original_testing
        
        # Remove temporary database file
        try:
            os.unlink(temp_db_path)
        except FileNotFoundError:
            pass  # File already deleted

# Usage in your test files:
# Just import this fixture and it will automatically isolate your tests
