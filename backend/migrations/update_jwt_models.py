"""
Script to update JWT models.
"""
from flask import Flask
from models import db, User, TokenBlacklist, RefreshToken
from config import Config

def update_jwt_models():
    """Update JWT models."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("JWT models updated successfully!")

if __name__ == "__main__":
    update_jwt_models()