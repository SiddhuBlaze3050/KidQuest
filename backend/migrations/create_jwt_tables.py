"""
Script to create JWT authentication tables.
"""
from flask import Flask
from models import db, TokenBlacklist, RefreshToken
from config import Config

def create_jwt_tables():
    """Create JWT authentication tables."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        print("JWT authentication tables created successfully!")

if __name__ == "__main__":
    create_jwt_tables()