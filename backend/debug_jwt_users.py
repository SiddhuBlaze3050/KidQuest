"""
Debug script for JWT RBAC authentication in KidQuest application.
This script checks the user records in the database and tests login for each user.
"""
from flask import Flask
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ParentChild
import requests
import json
import sys
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Configuration
BASE_URL = "http://localhost:5000"
USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "parent": {"username": "parent", "password": "parentparent", "role": "parent"},
    "child": {"username": "child", "password": "childchild", "role": "child"},
    "teacher": {"username": "teacher", "password": "teacherteacher", "role": "teacher"}
}

def check_users_in_database():
    """Check if the test users exist in the database."""
    print("Checking users in database...")
    with app.app_context():
        # Verify database connection and tables
        try:
            # Create tables if they don't exist
            db.create_all()
            print("Database tables created successfully!")
            
            # Check if User table exists
            user_count = User.query.count()
            print(f"Found {user_count} users in the database.")
            
            # Check each user
            for user_type, user_data in USERS.items():
                user = User.query.filter_by(username=user_data["username"]).first()
                if user:
                    print(f"✅ {user_type.capitalize()} user exists in database:")
                    print(f"   - ID: {user.id}")
                    print(f"   - Username: {user.username}")
                    print(f"   - Email: {user.email}")
                    print(f"   - Role: {user.role}")
                    
                    # Check password hash
                    print(f"   - Password: {user_data['password']}")
                    print(f"   - Password hash: {user.password_hash}")
                    
                    # Force update password hash
                    user.password_hash = generate_password_hash(user_data["password"])
                    db.session.commit()
                    print(f"   - Password hash updated to: {user.password_hash}")
                    
                    # Verify password hash
                    password_match = check_password_hash(user.password_hash, user_data["password"])
                    print(f"   - Password match after update: {'✅' if password_match else '❌'}")
                else:
                    print(f"❌ {user_type.capitalize()} user does not exist in database")
                    
                    # Create the user
                    new_user = User(
                        username=user_data["username"],
                        email=f"{user_data['username']}@example.com",
                        password_hash=generate_password_hash(user_data["password"]),
                        role=user_data["role"]
                    )
                    db.session.add(new_user)
                    print(f"   - Created {user_type} user")
            
            # Create parent-child relationship if needed
            parent = User.query.filter_by(username="parent").first()
            child = User.query.filter_by(username="child").first()
            if parent and child:
                relationship = ParentChild.query.filter_by(
                    parent_id=parent.id,
                    child_id=child.id
                ).first()
                
                if not relationship:
                    relationship = ParentChild(
                        parent_id=parent.id,
                        child_id=child.id,
                        relationship_type="parent"
                    )
                    db.session.add(relationship)
                    print("Created parent-child relationship")
            
            # Commit changes
            db.session.commit()
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise

def test_login():
    """Test login for each user."""
    print("\nTesting login for each user...")
    for user_type, user_data in USERS.items():
        print(f"\nTesting login for {user_type}...")
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": user_data["username"], "password": user_data["password"]}
        )
        
        if response.status_code == 200:
            print(f"✅ Login successful for {user_type}")
            data = response.json()
            print(f"   - Access token: {'Present' if 'access_token' in data else 'Missing'}")
            print(f"   - Refresh token: {'Present' if 'refresh_token' in data else 'Missing'}")
        else:
            print(f"❌ Login failed for {user_type}")
            print(f"   - Status code: {response.status_code}")
            print(f"   - Response: {response.text}")

def main():
    """Main function."""
    try:
        check_users_in_database()
        test_login()
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())