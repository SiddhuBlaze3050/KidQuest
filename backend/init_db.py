"""
Script to initialize the database for KidQuest application.
This script creates all necessary tables and sets up initial data.
"""
from flask import Flask
from models import db, User, ParentChild, TokenBlacklist, RefreshToken
from werkzeug.security import generate_password_hash
import os
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def init_database():
    """Initialize the database with tables and initial data."""
    with app.app_context():
        # Drop all tables and recreate them
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating all tables...")
        db.create_all()
        
        # Create test users
        print("Creating test users...")
        
        # Admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        
        # Parent user
        parent = User(
            username="parent",
            email="parent@example.com",
            password_hash=generate_password_hash("parentparent"),
            role="parent"
        )
        db.session.add(parent)
        
        # Child user
        child = User(
            username="child",
            email="child@example.com",
            password_hash=generate_password_hash("childchild"),
            role="child"
        )
        db.session.add(child)
        
        # Teacher user
        teacher = User(
            username="teacher",
            email="teacher@example.com",
            password_hash=generate_password_hash("teacherteacher"),
            role="teacher"
        )
        db.session.add(teacher)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create parent-child relationship
        relationship = ParentChild(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
        db.session.add(relationship)
        
        # Commit all changes
        db.session.commit()
        
        print(f"Database initialized successfully!")
        print(f"Created users: admin, parent, child, teacher")
        print(f"Admin ID: {admin.id}")
        print(f"Parent ID: {parent.id}")
        print(f"Child ID: {child.id}")
        print(f"Teacher ID: {teacher.id}")

if __name__ == "__main__":
    init_database()