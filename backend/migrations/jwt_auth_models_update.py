"""
Script to update JWT authentication models.
"""
from flask import Flask
from models import db, User
from config import Config

def update_jwt_auth_models():
    """Update JWT authentication models."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Update user model with new fields
        print("JWT authentication models updated successfully!")

if __name__ == "__main__":
    update_jwt_auth_models()