from flask import Flask, request, jsonify, session, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Achievement, ChatSession, ChildProfile, DoodleSession, LLMInteractions, ParentChild, SavingGoal, Transaction, HomeworkSchedule, PomodoroSession, ScreenTime, Notification, HealthTask, HealthStreak, WaterLog, LoginStreak, PsychometricTestResult, UserModuleProgress, TokenBlacklist, RefreshToken
import re, requests
import os
import random
import glob
import base64
from config import Config
from datetime import datetime, date, timedelta
import json
import traceback

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'se_project_key')

# Ensure instance directory exists on app startup
instance_dir = getattr(app.config, 'INSTANCE_DIR', None)
if instance_dir:
    os.makedirs(instance_dir, exist_ok=True)

# Configure CORS for Vue.js frontend
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5000", "https://editor.swagger.io", "*"], 
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Accept"])

db.init_app(app)

# Import and initialize JWT authentication
try:
    from app_jwt import init_jwt_auth
    app = init_jwt_auth(app)
    print("JWT Authentication initialized successfully!")
except ImportError as e:
    print(f"Warning: JWT Authentication not initialized - {str(e)}")

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+") 

# ---------------------------
# Utility Functions
# ---------------------------

def create_default_admin():
    """Ensures a default admin user exists in the database"""
    with app.app_context():
        if not User.query.filter_by(role="admin").first():
            admin_user = User(
                username="admin",
                password_hash=generate_password_hash("admin123"),
                email="admin123@gmail.com",
                role="admin"
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Database tables created successfully!")
            print("Default admin created successfully!")
        else:
            print("Admin already exists!")

def update_login_streak(user_id):
    """Update login streak for a user"""
    try:
        today = date.today()
        
        # Get or create login streak record
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        
        if not login_streak:
            # First time login - create new streak record
            login_streak = LoginStreak(
                user_id=user_id,
                current_streak=1,
                last_login_date=today,
                total_logins=1,
                longest_streak=1
            )
            db.session.add(login_streak)
        else:
            # Check if this is a new login day
            if login_streak.last_login_date != today:
                yesterday = date.fromordinal(today.toordinal() - 1)
                
                if login_streak.last_login_date == yesterday:
                    # Consecutive day login - increment streak
                    login_streak.current_streak += 1
                elif login_streak.last_login_date < yesterday:
                    # Break in streak - reset to 1
                    login_streak.current_streak = 1
                # If last_login_date is today, don't update (already logged in today)
                
                # Update last login date and total logins
                login_streak.last_login_date = today
                login_streak.total_logins += 1
                
                # Update longest streak if current is longer
                if login_streak.current_streak > login_streak.longest_streak:
                    login_streak.longest_streak = login_streak.current_streak
        
        db.session.commit()
        print(f"Updated login streak for user {user_id}: {login_streak.current_streak} days")
        
    except Exception as e:
        print(f"Error updating login streak: {e}")
        db.session.rollback()

# ---------------------------
# Authentication Routes
# ---------------------------

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API endpoint for simplified kid/parent registration"""
    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        role = data.get('role','user')
        email = data.get('email', None)  # Optional

        if not username or not password or not role:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        if email and not EMAIL_REGEX.match(email):
            return jsonify({'success': False, 'error': 'Invalid email address'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 409
        if email and User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 409

        password_hash = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        db.session.add(user)
        db.session.flush()  # Get user.id before commit

        if role == 'parent':
            relationship_type = data.get('relationship_type')
            child_username = data.get('child_username')

            if not relationship_type:
                return jsonify({'success': False, 'error': 'Relationship type is required'}), 400

            # Optional: Link to child if username exists
            child = User.query.filter_by(username=child_username, role='child').first()
            if child:
                parent_relationship = ParentChild(
                    parent_id=user.id,
                    child_id=child.id,
                    relationship_type=relationship_type
                )
                db.session.add(parent_relationship)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            # Update login streak for successful login
            update_login_streak(user.id)
            
            # Store user info in session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            return jsonify({
                'success': True,
                'message': 'Login successful', 
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/session/logout', methods=['POST'])
def api_session_logout():
    """API endpoint for session-based user logout"""
    try:
        # Clear session
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# User Profile Routes
# ---------------------------

@app.route('/api/user/profile/<int:user_id>', methods=['GET'])
def api_user_profile(user_id):
    """API endpoint to get user profile"""
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ---------------------------
# Health Tracker Routes
# ---------------------------

@app.route('/api/health/tasks/<int:user_id>', methods=['GET'])
def get_health_tasks(user_id):
    try:
        today = date.today()
        tasks = HealthTask.query.filter_by(user_id=user_id, date=today).all()

        if not tasks:
            # Default tasks if none exist for today
            default_tasks = ['Running', 'Yoga', 'Meditation', 'Helping in household chores']
            for name in default_tasks:
                db.session.add(HealthTask(user_id=user_id, task_name=name, date=today))
            db.session.commit()
            tasks = HealthTask.query.filter_by(user_id=user_id, date=today).all()

        return jsonify({
            'success': True,
            'tasks': [
                {'id': t.id, 'name': t.task_name, 'completed': t.completed} for t in tasks
            ]
        }), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e) 
        }), 500

@app.route('/api/health/tasks/<int:task_id>/toggle', methods=['POST'])
def toggle_task_completion(task_id):
    try:
        task = db.session.get(HealthTask, task_id)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        task.completed = not task.completed
        db.session.commit()

        # Automatically evaluate streak after toggling
        evaluate_streak_internal(task.user_id)

        return jsonify({'success': True, 'completed': task.completed}), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e) 
        }), 500

def evaluate_streak_internal(user_id):
    try:
        today = date.today()
        streak = HealthStreak.query.filter_by(user_id=user_id).first()

        # --- Reset if the child skipped a day ---
        if streak and streak.last_updated:
            missed_days = (today - streak.last_updated).days
            if missed_days > 1:
                streak.current_streak = 0
                streak.last_updated = today
                db.session.commit()
                return

        # --- Count today's completed tasks ---
        completed_count = HealthTask.query.filter_by(user_id=user_id, date=today, completed=True).count()

        if completed_count >= 2:
            if not streak:
                streak = HealthStreak(user_id=user_id, current_streak=1, last_updated=today)
                db.session.add(streak)
            elif streak.last_updated != today:
                streak.current_streak += 1
                streak.last_updated = today

            db.session.commit()
    except Exception as e:
        print("Streak Eval Error:", traceback.format_exc())

@app.route('/api/health/streak/<int:user_id>', methods=['GET'])
def get_streak(user_id):
    try:
        streak = HealthStreak.query.filter_by(user_id=user_id).first()
        return jsonify({
            'success': True,
            'streak': streak.current_streak if streak else 0
        }), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e) 
        }), 500        

@app.route('/api/health/water/<int:user_id>', methods=['POST'])
def increment_water(user_id):
    try:
        today = date.today()
        log = WaterLog.query.filter_by(user_id=user_id, date=today).first()

        if not log:
            log = WaterLog(user_id=user_id, count=1, date=today)
            db.session.add(log)
        else:
            log.count += 1

        db.session.commit()
        return jsonify({'success': True, 'count': log.count}), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e) 
        }), 500

@app.route('/api/health/water/<int:user_id>', methods=['GET'])
def get_today_water_count(user_id):
    try:
        today = date.today()
        entry = WaterLog.query.filter_by(user_id=user_id, date=today).first()
        count = entry.count if entry else 0
        return jsonify({'success': True, 'count': count}), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e) 
        }), 500

@app.route('/api/health/water/log/<int:user_id>', methods=['GET'])
def get_water_log(user_id):
    try:
        logs = WaterLog.query.filter_by(user_id=user_id).order_by(WaterLog.date.desc()).limit(7).all()
        log_data = [
            {
                'date': log.date.strftime('%a'),  # "Mon", "Tue", etc.
                'count': log.count
            } for log in reversed(logs)
        ]
        return jsonify({'success': True, 'log': log_data}), 200
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e) 
        }), 500

# -----------------------
# Motivational Quotes
# -----------------------        

@app.route('/api/quote/<int:user_id>', methods=['GET'])
def get_motivational_quote(user_id):
    try:
        response = requests.get('https://zenquotes.io/api/today')
        if response.status_code == 200:
            quote_data = response.json()[0]
            quote = f"{quote_data['q']} — {quote_data['a']}"
            return jsonify({'success': True, 'quote': quote}), 200
        else:
            raise Exception("API call failed")
    except Exception as e:
        print("Error fetching quote:", e)
        fallback_quote = "Believe in yourself and magic will happen! ✨"
        return jsonify({'success': False, 'quote': fallback_quote}), 200

@app.route('/api/login-streak/<int:user_id>', methods=['GET'])
def get_login_streak(user_id):
    """Get current login streak for a user"""
    try:
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        
        if login_streak:
            return jsonify({
                'success': True,
                'current_streak': login_streak.current_streak,
                'total_logins': login_streak.total_logins,
                'longest_streak': login_streak.longest_streak,
                'last_login_date': login_streak.last_login_date.isoformat()
            }), 200
        else:
            # No login streak record found - return defaults
            return jsonify({
                'success': True,
                'current_streak': 0,
                'total_logins': 0,
                'longest_streak': 0,
                'last_login_date': None
            }), 200
            
    except Exception as e:
        print(f"Error fetching login streak: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'current_streak': 0,
            'total_logins': 0,
            'longest_streak': 0,
            'last_login_date': None
        }), 500

# ---------------------------
# JWT Authentication Routes
# ---------------------------

try:
    # Import JWT and RBAC services
    import jwt
    from services.jwt_service import generate_access_token, generate_refresh_token, validate_access_token, refresh_access_token, blacklist_token, revoke_all_user_tokens
    from middleware.auth_middleware import jwt_required, role_required, permission_required, rate_limit

    print("JWT Authentication routes registered successfully!")
except ImportError as e:
    print(f"Warning: JWT Authentication not available - {str(e)}")
    print("Install required packages with: pip install PyJWT")

# ---------------------------
# Main Entry Point
# ---------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_admin()
    app.run(debug=True)