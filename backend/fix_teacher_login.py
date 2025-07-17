"""
Script to fix the teacher login issue.
"""
from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

def fix_teacher_login():
    """Fix the teacher login issue."""
    with app.app_context():
        # Check if teacher user exists
        teacher = User.query.filter_by(username="teacher").first()
        
        if teacher:
            print(f"Teacher user found with ID: {teacher.id}")
            print(f"Current role: {teacher.role}")
            print(f"Current password hash: {teacher.password_hash}")
            
            # Update teacher password
            new_password_hash = generate_password_hash("teacherteacher")
            teacher.password_hash = new_password_hash
            db.session.commit()
            
            print(f"Teacher password updated to: {new_password_hash}")
            
            # Verify password hash
            from werkzeug.security import check_password_hash
            password_match = check_password_hash(teacher.password_hash, "teacherteacher")
            print(f"Password match after update: {'✅' if password_match else '❌'}")
        else:
            print("Teacher user not found, creating...")
            teacher = User(
                username="teacher",
                email="teacher@example.com",
                password_hash=generate_password_hash("teacherteacher"),
                role="teacher"
            )
            db.session.add(teacher)
            db.session.commit()
            print(f"Teacher user created with ID: {teacher.id}")

if __name__ == "__main__":
    fix_teacher_login()