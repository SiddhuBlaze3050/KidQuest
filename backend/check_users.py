"""
Script to check the users in the database.
"""
from flask import Flask
from models import db, User
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def check_users():
    """Check the users in the database."""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Count users
        user_count = User.query.count()
        print(f"Found {user_count} users in the database.")
        
        # List all users
        users = User.query.all()
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Password hash: {user.password_hash}")
            print()

if __name__ == "__main__":
    check_users()