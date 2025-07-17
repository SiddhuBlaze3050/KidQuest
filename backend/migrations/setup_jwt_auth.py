"""
Script to set up JWT authentication.
"""
from flask import Flask
from models import db, User, TokenBlacklist, RefreshToken
from werkzeug.security import generate_password_hash
from config import Config

def setup_jwt_auth():
    """Set up JWT authentication."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
        
        print("JWT authentication setup completed successfully!")

if __name__ == "__main__":
    setup_jwt_auth()