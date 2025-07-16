"""
Script to set up test users for JWT RBAC testing.
This script creates admin, parent, and child users if they don't exist.
"""
from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User, ParentChild
import os
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def setup_test_users():
    """Set up test users for JWT RBAC testing."""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Verify tables were created
        try:
            user_count = User.query.count()
            print(f"Database initialized successfully. Found {user_count} existing users.")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            # Ensure tables are created
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
            print("Created admin user")
        else:
            # Update admin password if it exists
            admin.password_hash = generate_password_hash("admin123")
            print("Updated admin user password")
        
        # Create parent user if it doesn't exist
        parent = User.query.filter_by(username="parent").first()
        if not parent:
            parent = User(
                username="parent",
                email="parent@example.com",
                password_hash=generate_password_hash("parentparent"),
                role="parent"
            )
            db.session.add(parent)
            print("Created parent user")
        else:
            # Update parent password if it exists
            parent.password_hash = generate_password_hash("parentparent")
            print("Updated parent user password")
        
        # Create child user if it doesn't exist
        child = User.query.filter_by(username="child").first()
        if not child:
            child = User(
                username="child",
                email="child@example.com",
                password_hash=generate_password_hash("childchild"),
                role="child"
            )
            db.session.add(child)
            print("Created child user")
        else:
            # Update child password if it exists
            child.password_hash = generate_password_hash("childchild")
            print("Updated child user password")
        
        # Create teacher user if it doesn't exist
        teacher = User.query.filter_by(username="teacher").first()
        if not teacher:
            teacher = User(
                username="teacher",
                email="teacher@example.com",
                password_hash=generate_password_hash("teacherteacher"),
                role="teacher"
            )
            db.session.add(teacher)
            print("Created teacher user")
        else:
            # Update teacher password if it exists
            teacher.password_hash = generate_password_hash("teacherteacher")
            print("Updated teacher user password")
        
        # Create parent-child relationship if it doesn't exist
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
            else:
                print("Parent-child relationship already exists")
        
        # Commit changes
        db.session.commit()
        print("Test users setup complete")

if __name__ == "__main__":
    setup_test_users()