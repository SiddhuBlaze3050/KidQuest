from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Achievement, ChatSession,ChildProfile, DoodleSession, Story, LLMInteractions, ParentChild, SavingGoal, Transaction, HomeworkSchedule, PomodoroSession, ScreenTime, Notification, HealthTask, HealthStreak, WaterLog, LoginStreak, LoginHistory, PsychometricTestResult, UserModuleProgress, get_current_ist_time, IST
import re
import requests
import os
import random
import glob
import base64
import time
import traceback
from config import Config
from groq import Groq
import secrets
from datetime import datetime, date, UTC, timedelta
import json
from collections import defaultdict

# NEW: JWT imports
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Import our psychometry module
from services.psychometry import PsychometryService

def get_today_ist():
    """Get today's date in IST timezone"""
    return datetime.now(IST).date()

def get_current_ist_datetime():
    """Get current datetime in IST timezone"""
    return datetime.now(IST)

app = Flask(__name__)
app.config.from_object(Config)
# Use consistent secret key from config instead of random one
# app.secret_key = secrets.token_hex(16)  # This was causing JWT tokens to become invalid on restart

# Ensure instance directory exists on app startup
instance_dir = getattr(app.config, 'INSTANCE_DIR', None)
if instance_dir:
    os.makedirs(instance_dir, exist_ok=True)

# Configure CORS for Vue.js frontend - Development and Production
CORS(app, 
     origins=[
         # Local development
         "http://localhost:5173", 
         "http://127.0.0.1:5173", 
         "http://localhost:5000",
         "http://localhost:4173",  # Vite preview
         # Production - Netlify domains (specific URL - wildcards don't work with credentials)
         "https://kidquest.netlify.app",
         # Swagger for API testing
         "https://editor.swagger.io"
         # Note: Cannot use "*" or wildcards with supports_credentials=True
     ], 
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"])

db.init_app(app)

# Initialize database tables on startup
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            # Create default admin user
            admin_password = generate_password_hash('admin123')  # Change this password!
            admin_user = User(
                username='admin',
                email='admin@kidquest.com',
                password_hash=admin_password,
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin user created successfully")
            print("📧 Admin credentials: username='admin', password='admin123'")
            print("🔒 Please change the admin password after first login!")
        else:
            print("✅ Admin user already exists")
            
        # Create sample users for testing (only if no users exist except admin)
        user_count = User.query.filter(User.role != 'admin').count()
        if user_count == 0:
            sample_users = [
                {
                    'username': 'demo_child',
                    'email': 'child@demo.com',
                    'password': 'demo123',
                    'role': 'child'
                },
                {
                    'username': 'demo_parent',
                    'email': 'parent@demo.com', 
                    'password': 'demo123',
                    'role': 'parent'
                },
                {
                    'username': 'demo_teacher',
                    'email': 'teacher@demo.com',
                    'password': 'demo123',
                    'role': 'teacher'
                }
            ]
            
            for user_data in sample_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    role=user_data['role']
                )
                db.session.add(user)
            
            db.session.commit()
            print("✅ Sample demo users created successfully")
            print("👶 Demo Child: username='demo_child', password='demo123'")
            print("👨‍👩‍👧 Demo Parent: username='demo_parent', password='demo123'") 
            print("👩‍🏫 Demo Teacher: username='demo_teacher', password='demo123'")
        else:
            print("✅ Sample users already exist or users found")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

# NEW: Initialize JWT with proper configuration
jwt = JWTManager(app)

# NEW: JWT error handlers with better debugging
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token has expired',
        'error_type': 'token_expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Invalid token',
        'error_type': 'token_invalid'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Missing authorization token',
        'error_type': 'token_missing'
    }), 401

# NEW: Add additional JWT error handlers
@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token has been revoked',
        'error_type': 'token_revoked'
    }), 401

@jwt.token_verification_failed_loader
def token_verification_failed_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token verification failed',
        'error_type': 'token_verification_failed'
    }), 401

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+") 

# Initialize Groq client
client = Groq(api_key=app.config['GROQ_API_KEY'])

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
        else:
            pass  # Admin already exists

# ---------------------------
# Chatbot System Setup
# ---------------------------

def load_chatbot_prompt():
    """Load the chatbot system prompt from markdown file"""
    try:
        with open('chatbot_prompt.md', 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return """You are a caring emotional companion chatbot for children and teens. 
        Provide empathetic support, teach coping strategies, and educate about safety."""

# Load system prompt from markdown file
SYSTEM_PROMPT = load_chatbot_prompt()

@app.route('/api/chat/sessions/<int:user_id>', methods=['GET'])
@jwt_required()
def api_chat_sessions(user_id):
    """Get all chat sessions for a user"""
    try:
        sessions = ChatSession.query.filter_by(user_id=user_id)\
                                   .order_by(ChatSession.updated_at.desc()).all()
        
        sessions_data = []
        for session in sessions:
            interaction_count = LLMInteractions.query.filter_by(session_id=session.id).count()
            last_message = LLMInteractions.query.filter_by(session_id=session.id)\
                                                .order_by(LLMInteractions.user_timestamp.desc()).first()
            
            sessions_data.append({
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat() if session.updated_at else session.created_at.isoformat(),
                'mood_tag': session.mood_tag,
                'interaction_count': interaction_count,
                'last_message_preview': last_message.user_message[:50] + '...' if last_message and len(last_message.user_message) > 50 else last_message.user_message if last_message else '',
                'summary': session.summary
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions_data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/session/<int:session_id>', methods=['GET'])
@jwt_required()
def api_get_session(session_id):
    """Get detailed session with all interactions"""
    try:
        current_user_id = int(get_jwt_identity())
        
        session = db.session.get(ChatSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Authorization: only allow access to own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        interactions = LLMInteractions.query.filter_by(session_id=session_id)\
                                           .order_by(LLMInteractions.user_timestamp.asc()).all()
        
        messages = []
        for interaction in interactions:
            # Add user message
            messages.append({
                'id': f"user_{interaction.id}",
                'message': interaction.user_message,
                'sender': 'user',
                'timestamp': interaction.user_timestamp.isoformat(),
                'mood_tag': interaction.mood_tag
            })
            
            # Add bot response if available
            if interaction.llm_response:
                messages.append({
                    'id': f"bot_{interaction.id}",
                    'message': interaction.llm_response,
                    'sender': 'assistant',
                    'timestamp': interaction.llm_timestamp.isoformat() if interaction.llm_timestamp else interaction.user_timestamp.isoformat()
                })
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat() if session.updated_at else session.created_at.isoformat(),
                'mood_tag': session.mood_tag,
                'summary': session.summary,
                'messages': messages
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/session/<int:session_id>/summary', methods=['PUT'])
@jwt_required()
def update_session_summary(session_id):
    """Update session summary"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        summary = data.get('summary')
        
        session = db.session.get(ChatSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Authorization: only allow users to update their own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        session.summary = summary
        session.updated_at = datetime.now(UTC)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Session summary updated'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ---------------------------
# Legacy Chatbot Routes (for backward compatibility)
# ---------------------------

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('user_message')

    if not user_id or not user_message:
        return jsonify({'error': 'user_id and message are required'}), 400

    try:
        response_data = chatbot_logic(user_id, user_message)
        return jsonify(response_data), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/sessions/<int:user_id>', methods=['GET'])
@jwt_required()
def get_chat_sessions(user_id):
    """Get all chat sessions for a user with metadata"""
    try:
        sessions = ChatSession.query.filter_by(user_id=user_id)\
                                   .order_by(ChatSession.updated_at.desc()).all()
        
        session_list = []
        for session in sessions:
            # Get interaction count
            interaction_count = LLMInteractions.query.filter_by(session_id=session.id).count()
            
            # Get last message preview
            last_interaction = LLMInteractions.query.filter_by(session_id=session.id)\
                                                   .order_by(LLMInteractions.user_timestamp.desc()).first()
            
            last_message_preview = "New conversation"
            if last_interaction:
                preview_text = last_interaction.user_message
                last_message_preview = (preview_text[:50] + "...") if len(preview_text) > 50 else preview_text
            
            session_list.append({
                'id': session.id,
                'updated_at': session.updated_at.isoformat(),
                'interaction_count': interaction_count,
                'last_message_preview': last_message_preview,
                'mood_tag': session.mood_tag  # Include mood_tag from session
            })
        
        return jsonify({
            'success': True,
            'sessions': session_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/chat-history/<int:user_id>', methods=['GET'])
@jwt_required()
def get_chat_history(user_id):
    """Legacy route - updated for new model"""
    try:
        # Get recent interactions across all sessions
        interactions = db.session.query(LLMInteractions)\
                                 .join(ChatSession)\
                                 .filter(ChatSession.user_id == user_id)\
                                 .order_by(LLMInteractions.user_timestamp.asc())\
                                 .limit(50).all()
        
        chat_history = []
        for interaction in interactions:
            # Add user message
            chat_history.append({
                'id': f"user_{interaction.id}",
                'message': interaction.user_message,
                'sender': 'user',
                'timestamp': interaction.user_timestamp.isoformat()
            })
            
            # Add bot response if available
            if interaction.llm_response:
                chat_history.append({
                    'id': f"bot_{interaction.id}",
                    'message': interaction.llm_response,
                    'sender': 'assistant',
                    'timestamp': interaction.llm_timestamp.isoformat() if interaction.llm_timestamp else interaction.user_timestamp.isoformat()
                })
        
        return jsonify({'chat_history': chat_history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-chat/<int:user_id>', methods=['DELETE'])
@jwt_required()
def clear_chat_history(user_id):
    """Legacy route - updated for new model"""
    try:
        # Delete all sessions and their interactions for user
        sessions = ChatSession.query.filter_by(user_id=user_id).all()
        for session in sessions:
            LLMInteractions.query.filter_by(session_id=session.id).delete()
            db.session.delete(session)
        
        db.session.commit()
        return jsonify({'message': 'Chat history cleared successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ---------------------------
# API Routes for Vue.js Frontend
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
            parent_relationship = ParentChild(
                parent_id=user.id,
                child_id=child.id if child else None,
                relationship_type=relationship_type
            )
            db.session.add(parent_relationship)

        elif role == 'teacher':
            relationship_type = data.get('relationship_type', 'Teacher')
            selected_students = data.get('selectedStudents', [])

            if not selected_students:
                return jsonify({'success': False, 'error': 'At least one student must be selected for teacher registration'}), 400

            # Create teacher-student relationships for each selected student
            for student_id in selected_students:
                # Verify student exists and has 'child' role
                student = User.query.filter_by(id=student_id, role='child').first()
                if student:
                    teacher_relationship = ParentChild(
                        parent_id=user.id,
                        child_id=student.id,
                        relationship_type=relationship_type
                    )
                    db.session.add(teacher_relationship)

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
    """API endpoint for user login with JWT token"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            # Generate JWT token with explicit expiration
            from datetime import timedelta
            expires = timedelta(hours=8)  # Explicit 8-hour expiration
            
            access_token = create_access_token(
                identity=str(user.id),
                expires_delta=expires,
                additional_claims={
                    'username': user.username,
                    'role': user.role,
                    'login_time': datetime.now(IST).isoformat()
                }
            )
            
            # Update login streak for successful login
            update_login_streak(user.id)
            
            # Record login history for analytics
            record_login_history(user.id, request)
            
            # Generate notifications for the user
            generate_notifications(user.id)
            
            return jsonify({
                'success': True,
                'message': 'Login successful', 
                'access_token': access_token,
                'expires_in': int(expires.total_seconds()),  # Send expiration time to frontend
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

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def api_logout():
    """API endpoint for user logout - clears any server-side session data"""
    try:
        user_id = get_jwt_identity()
        
        # Clear any server-side session data if needed
        # For now, just return success since JWT is stateless
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET'])
@jwt_required()
def api_verify_token():
    """Verify if the current JWT token is valid and get user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Get JWT claims for debugging
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            },
            'token_info': {
                'expires_at': claims.get('exp'),
                'issued_at': claims.get('iat'),
                'login_time': claims.get('login_time')
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
@jwt_required()
def api_chat():
    """API endpoint for chat interface with session support"""
    try:
        data = request.get_json()
        message = data.get('message')
        user_id = data.get('user_id', get_jwt_identity())  # Use JWT identity
        session_id = data.get('session_id')  # Add session_id support
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Use existing chatbot logic with session support
        response_data = chatbot_logic(user_id, message, session_id)
        return jsonify({
            'success': True,
            'response': response_data['response'],
            'timestamp': response_data['timestamp'],
            'session_id': response_data['session_id']  # Include session_id in response
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/history/<int:user_id>', methods=['GET'])
@jwt_required()
def api_chat_history(user_id):
    """API endpoint to get chat history with new session-based model"""
    try:
        # Get recent chat sessions for user (last 5 sessions)
        sessions = ChatSession.query.filter_by(user_id=user_id)\
                                   .order_by(ChatSession.updated_at.desc())\
                                   .limit(5).all()
        
        messages = []
        for session in reversed(sessions):  # Show oldest sessions first
            interactions = LLMInteractions.query.filter_by(session_id=session.id)\
                                               .order_by(LLMInteractions.user_timestamp.asc()).all()
            
            for interaction in interactions:
                # Add user message
                messages.append({
                    'id': f"user_{interaction.id}",
                    'message': interaction.user_message,
                    'sender': 'user',
                    'timestamp': interaction.user_timestamp.isoformat(),
                    'session_id': session.id
                })
                
                # Add bot response if available
                if interaction.llm_response:
                    messages.append({
                        'id': f"bot_{interaction.id}",
                        'message': interaction.llm_response,
                        'sender': 'assistant',
                        'timestamp': interaction.llm_timestamp.isoformat() if interaction.llm_timestamp else interaction.user_timestamp.isoformat(),
                        'session_id': session.id
                    })
        
        return jsonify({
            'success': True,
            'messages': messages[-50:]  # Limit to last 50 messages
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/api/user/profile/<int:user_id>', methods=['GET'])
@jwt_required()
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

# NEW: Protected endpoint using JWT
@app.route('/api/user/profile', methods=['GET'])
@jwt_required()
def get_current_user_profile():
    """Get current user's profile - requires JWT token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
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
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Student Management Routes
# ---------------------------

@app.route('/api/students/available', methods=['GET'])
def get_available_students():
    """Get list of available students for teacher registration"""
    try:
        # Get all users with role 'child'
        students = User.query.filter_by(role='child').all()
        
        student_list = []
        for student in students:
            student_list.append({
                'id': student.id,
                'username': student.username,
                'email': student.email,
                'avatar': '🎓'  # Default avatar for students
            })
        
        return jsonify({
            'success': True,
            'data': student_list
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ---------------------------
# Health Tracker
# ---------------------------

@app.route('/api/health/tasks/<int:user_id>', methods=['GET'])
@jwt_required()
def get_health_tasks(user_id):
    """Get health tasks for a user"""
    try:
        today = date.today()
        tasks = HealthTask.query.filter_by(user_id=user_id, date=today).all()

        if not tasks:
            # Default tasks if none exist for today
            default_tasks = ['Running', 'Yoga', 'Meditation', 'Eat Fruits','Helping in household chores']
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
@jwt_required()
def toggle_task_completion(task_id):
    try:
        # Verify user has access to this task
        task = db.session.get(HealthTask, task_id)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Security check: ensure user can only toggle their own tasks
        current_user_id = int(get_jwt_identity())
        if task.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

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

@app.route('/api/health/streak/<int:user_id>', methods=['GET'])
@jwt_required()
def get_streak(user_id):
    """Get health streak for a user"""
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
@jwt_required()
def increment_water(user_id):
    """Increment water intake for a user"""
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
    
@app.route('/api/health/water/<int:user_id>', methods=['DELETE'])
@jwt_required()
def decrement_water(user_id):
    """Decrement water intake for a user"""
    try:
        today = date.today()
        log = WaterLog.query.filter_by(user_id=user_id, date=today).first()

        if not log:
            return jsonify({'success': False, 'error': 'No water log for today'}), 404

        if log.count > 0:
            log.count -= 1
            db.session.commit()

        return jsonify({'success': True, 'count': log.count}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health/water/<int:user_id>', methods=['GET'])
@jwt_required()
def get_today_water_count(user_id):
    """Get today's water intake count for a user"""
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
@jwt_required()
def get_water_log(user_id):
    """Get water intake log for a user"""
    try:
        logs = WaterLog.query.filter_by(user_id=user_id).order_by(WaterLog.date.desc()).limit(8).all()
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
        pass  # Silent error handling for streak evaluation

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
        
    except Exception as e:
        db.session.rollback()

def record_login_history(user_id, request):
    """Record login history for analytics"""
    try:
        today = date.today()
        
        # Check if user already logged in today (to avoid duplicate records)
        existing_login = LoginHistory.query.filter_by(
            user_id=user_id, 
            login_date=today
        ).first()
        
        if not existing_login:
            # Record new login
            login_record = LoginHistory(
                user_id=user_id,
                login_date=today,
                login_time=datetime.now(UTC),
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent') if request else None
            )
            db.session.add(login_record)
            db.session.commit()
        
    except Exception as e:
        # Don't fail login if history recording fails
        print(f"Failed to record login history: {e}")
        db.session.rollback()

# -----------------------
# Motivational Quotes
# -----------------------        

@app.route('/api/quote/<int:user_id>', methods=['GET'])
@jwt_required()
def get_motivational_quote(user_id):
    """Get a motivational quote for a user"""
    try:
        response = requests.get('https://zenquotes.io/api/today')
        if response.status_code == 200:
            quote_data = response.json()[0]
            quote = f"{quote_data['q']} — {quote_data['a']}"
            return jsonify({'success': True, 'quote': quote}), 200
        else:
            raise Exception("API call failed")
    except Exception as e:
        fallback_quote = "Believe in yourself and magic will happen! ✨"
        return jsonify({'success': False, 'quote': fallback_quote}), 200

@app.route('/api/login-streak/<int:user_id>', methods=['GET'])
@jwt_required()
def get_login_streak(user_id):
    """Get login streak for a user"""
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
        return jsonify({
            'success': False,
            'error': str(e),
            'current_streak': 0,
            'total_logins': 0,
            'longest_streak': 0,
            'last_login_date': None
        }), 500
            

# ---------------------------
# Dashboard Statistics Calculation Functions
# ---------------------------

def calculate_total_stars(user_id):
    """Calculate total stars earned by a user based on module completion and streaks ONLY"""
    try:
        stars = 0
        
        # Module star calculation based on your requirements:
        # - Single modules (no submodules): 10 stars per module completion
        # - Modules with submodules: 5 stars per submodule completion
        
        module_stars = 0
        
        # Single modules without submodules (10 stars each when completed)
        single_modules = ['math_magic', 'word_wizard', 'good_touch_bad_touch']
        for module_name in single_modules:
            completed_single = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=module_name, 
                completed=True
            ).first()
            if completed_single:
                module_stars += 10  # 10 stars per single module completion
        
        # Modules with submodules (5 stars per submodule completion)
        submodule_modules = ['safety_measures', 'science_explorer']
        for module_name in submodule_modules:
            completed_submodules = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=module_name, 
                completed=True
            ).count()
            module_stars += completed_submodules * 5  # 5 stars per submodule
        
        stars += module_stars
        
        # 1 star per login streak day
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        if login_streak:
            stars += login_streak.current_streak * 1
        
        # 2 stars per health streak day  
        health_streak = HealthStreak.query.filter_by(user_id=user_id).first()
        if health_streak:
            stars += health_streak.current_streak * 2
        
        return stars
    except Exception as e:
        return 0

def calculate_quests_completed(user_id):
    """Calculate total quests/activities completed by a user - includes modules and tasks ONLY"""
    try:
        quests = 0
        
        # 1. Count completed module submodules from UserModuleProgress
        module_progress = UserModuleProgress.query.filter_by(user_id=user_id, completed=True).all()
        quests += len(module_progress)
        
        # 2. Count completed tasks from HomeworkSchedule (task tracker)
        completed_tasks = HomeworkSchedule.query.filter_by(user_id=user_id, status='completed').all()
        quests += len(completed_tasks)
        
        # Note: Achievements are excluded from quest calculation
        
        return quests
    except Exception as e:
        return 0

def calculate_skills_mastered(user_id):
    """Calculate number of skills mastered by a user - based on completed modules ONLY"""
    try:
        # Count completed full modules (not individual submodules)
        skills = 0
        
        # Single modules without submodules (count if completed)
        single_modules = ['math_magic', 'word_wizard', 'good_touch_bad_touch']
        for module_name in single_modules:
            completed_single = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=module_name, 
                completed=True
            ).first()
            if completed_single:
                skills += 1  # 1 skill per completed single module
        
        # Modules with submodules (count if ALL submodules are completed)
        submodule_modules = ['safety_measures', 'science_explorer']
        for module_name in submodule_modules:
            if module_name == 'safety_measures':
                completed_submodules = UserModuleProgress.query.filter_by(
                    user_id=user_id, 
                    module_name=module_name, 
                    completed=True
                ).count()
                if completed_submodules >= 6:  # All 6 safety submodules completed
                    skills += 1
            elif module_name == 'science_explorer':
                completed_submodules = UserModuleProgress.query.filter_by(
                    user_id=user_id, 
                    module_name=module_name, 
                    completed=True
                ).count()
                if completed_submodules >= 6:  # All 6 science submodules completed
                    skills += 1
        
        return skills
    except Exception as e:
        return 0

def calculate_todays_goals(user_id, today):
    """Calculate goals completed today - includes modules, tasks, health, and streaks ONLY"""
    try:
        goals = 0
        
        # 1. Module progress completed today (filter by date)
        today_module_progress = UserModuleProgress.query.filter_by(user_id=user_id, completed=True).filter(
            db.func.date(UserModuleProgress.updated_at) == today
        ).count() if hasattr(UserModuleProgress, 'updated_at') else 0
        goals += today_module_progress
        
        # 2. Tasks completed today (filter by completion date)
        today_tasks = HomeworkSchedule.query.filter_by(user_id=user_id, status='completed').filter(
            db.func.date(HomeworkSchedule.updated_at) == today
        ).count() if hasattr(HomeworkSchedule, 'updated_at') else 0
        goals += today_tasks
        
        # 3. Health tasks completed today
        today_health_tasks = HealthTask.query.filter_by(user_id=user_id, completed=True, date=today).count()
        goals += today_health_tasks
        
        # 4. Login streak (if logged in today)
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        if login_streak and login_streak.last_login_date == today:
            goals += 1
        
        # 5. Water intake goal (if drank water today)
        water_log = WaterLog.query.filter_by(user_id=user_id, date=today).first()
        if water_log and water_log.count >= 8:  # 8 glasses goal
            goals += 1
        
        return goals
    except Exception as e:
        return 0

# ---------------------------
# Child Dashboard Routes
# ---------------------------

@app.route('/api/child/stats/<int:user_id>', methods=['GET'])
@jwt_required()
def api_child_stats(user_id):
    """Get child dashboard statistics"""
    try:
        today = get_today_ist()  # Use IST timezone for today's date
        
        # Calculate Stars Collected
        total_stars = calculate_total_stars(user_id)
        
        # Calculate Quests Completed
        quests_completed = calculate_quests_completed(user_id)
        
        # Calculate Skills Mastered
        skills_mastered = calculate_skills_mastered(user_id)
        
        # Calculate Today's Goals
        todays_goals = calculate_todays_goals(user_id, today)
        
        # Get login streak
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        streak_days = login_streak.current_streak if login_streak else 0
        
        # Calculate user level based on total stars
        user_level = max(1, total_stars // 50)  # Level up every 50 stars
        
        stats = {
            'totalStars': total_stars,
            'questsCompleted': quests_completed,
            'skillsLearned': skills_mastered,
            'todayGoals': todays_goals,
            'streakDays': streak_days,
            'userLevel': user_level
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/achievement/test', methods=['POST'])
@jwt_required()
def create_test_achievement():
    """Create a test achievement for testing dashboard stats"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', get_jwt_identity())  # Use JWT identity if not provided
        
        # Security check: ensure user can only create achievements for themselves
        current_user_id = int(get_jwt_identity())
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        # Create a test achievement
        achievement = Achievement(
            user_id=user_id,
            badge_name=data.get('badge_name', f"Test Achievement {datetime.now(UTC).timestamp()}"),
            description=data.get('description', 'Test achievement for dashboard stats'),
            date_awarded=datetime.now(UTC)
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        
        return jsonify({
            'success': True,
            'message': 'Test achievement created successfully',
            'achievement': {
                'id': achievement.id,
                'badge_name': achievement.badge_name,
                'description': achievement.description
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/achievements/special/<int:user_id>', methods=['GET'])
@jwt_required()
def get_special_achievements(user_id):
    """Get the three special achievements for display cards"""
    try:
        # Calculate achievements data
        achievements = []
        
        # 1. Knowledge Achievement (based on completed modules)
        # Count full modules completed, not individual submodules
        completed_modules = 0
        
        # Single modules without submodules (count if completed)
        single_modules = ['math_magic', 'word_wizard', 'good_touch_bad_touch']
        for module_name in single_modules:
            completed_single = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=module_name, 
                completed=True
            ).first()
            if completed_single:
                completed_modules += 1
        
        # Modules with submodules (count if ALL submodules are completed)
        submodule_modules = ['safety_measures', 'science_explorer']
        for module_name in submodule_modules:
            if module_name == 'safety_measures':
                completed_submodules = UserModuleProgress.query.filter_by(
                    user_id=user_id, 
                    module_name=module_name, 
                    completed=True
                ).count()
                if completed_submodules >= 6:  # All 6 safety submodules completed
                    completed_modules += 1
            elif module_name == 'science_explorer':
                completed_submodules = UserModuleProgress.query.filter_by(
                    user_id=user_id, 
                    module_name=module_name, 
                    completed=True
                ).count()
                if completed_submodules >= 6:  # All 6 science submodules completed
                    completed_modules += 1
        
        knowledge_titles = ["🌱 Beginner", "📚 Learner", "🎓 Scholar", "🧠 Expert", "🌟 Master", "🚀 Genius"]
        knowledge_level = min(completed_modules, len(knowledge_titles) - 1)
        knowledge_achievement = {
            "id": 1,
            "title": knowledge_titles[knowledge_level],
            "description": f"Completed {completed_modules} learning modules",
            "medal": "🥇",
            "earnedDate": datetime.now(IST).isoformat(),
            "type": "knowledge",
            "level": knowledge_level,
            "progress": completed_modules
        }
        
        # 2. Streak Achievement (based on login streak)
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        streak_days = login_streak.current_streak if login_streak else 0
        streak_titles = ["🔰 Newbie", "⚔️ Private", "🎖️ Corporal", "🏆 Sergeant", "👑 Lieutenant", "⭐ Captain", "🌟 Major", "🚀 Colonel"]
        streak_level = min(streak_days // 5, len(streak_titles) - 1)  # Level up every 5 days
        streak_achievement = {
            "id": 2,
            "title": streak_titles[streak_level],
            "description": f"Maintained {streak_days} day learning streak",
            "medal": "🥈",
            "earnedDate": datetime.now(IST).isoformat(),
            "type": "streak",
            "level": streak_level,
            "progress": streak_days
        }
        
        # 3. Task Achievement (based on completed tasks)
        completed_tasks = HomeworkSchedule.query.filter_by(user_id=user_id, status='completed').count()
        task_titles = ["🏃 Starter", "💪 Doer", "⚡ Achiever", "🎯 Champion", "🏆 Hero", "🌟 Legend"]
        task_level = min(completed_tasks // 5, len(task_titles) - 1)  # Level up every 5 tasks
        task_achievement = {
            "id": 3,
            "title": task_titles[task_level],
            "description": f"Completed {completed_tasks} tasks successfully",
            "medal": "🥉",
            "earnedDate": datetime.now(IST).isoformat(),
            "type": "tasks",
            "level": task_level,
            "progress": completed_tasks
        }
        
        achievements = [knowledge_achievement, streak_achievement, task_achievement]
        
        # Only update achievement records in database if user has meaningful progress
        # (Don't create achievements just for login streak - require actual completed modules or tasks)
        if completed_modules > 0 or completed_tasks > 0 or streak_days >= 5:
            for achievement_data in achievements:
                existing = Achievement.query.filter_by(
                    user_id=user_id, 
                    badge_name=f"{achievement_data['type']}_achievement"
                ).first()
                
                if existing:
                    existing.description = f"{achievement_data['title']}: {achievement_data['description']}"
                    existing.date_awarded = datetime.now(UTC)
                else:
                    new_achievement = Achievement(
                        user_id=user_id,
                        badge_name=f"{achievement_data['type']}_achievement",
                        description=f"{achievement_data['title']}: {achievement_data['description']}",
                        date_awarded=datetime.now(UTC)
                    )
                    db.session.add(new_achievement)
        
            db.session.commit()
        
        return jsonify({
            'success': True,
            'achievements': achievements
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/achievements/refresh/<int:user_id>', methods=['POST'])
@jwt_required()
def refresh_achievements(user_id):
    """Force refresh achievements for a user - for testing"""
    try:
        
        # Call the existing get_special_achievements function
        response = get_special_achievements(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Achievements refreshed successfully',
            'response': response[0].get_json() if hasattr(response[0], 'get_json') else 'Success'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/child/quests/<int:user_id>', methods=['GET'])
@jwt_required()
def api_child_quests(user_id):
    """Get today's quests for child"""
    try:
        # Mock data for now
        quests = [
            {
                'id': 1,
                'title': 'Math Adventure',
                'description': 'Solve 10 fun math puzzles',
                'icon': '🔢',
                'stars': 10,
                'completed': False
            },
            {
                'id': 2,
                'title': 'Reading Quest',
                'description': 'Read for 20 minutes',
                'icon': '📖',
                'stars': 8,
                'completed': True
            },
            {
                'id': 3,
                'title': 'Tidy Up Mission',
                'description': 'Clean your room',
                'icon': '🧹',
                'stars': 5,
                'completed': False
            }
        ]
        
        return jsonify({
            'success': True,
            'quests': quests
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/child/quest/<int:quest_id>/toggle', methods=['POST'])
@jwt_required()
def api_toggle_quest(quest_id):
    """Toggle quest completion status"""
    try:
        # Verify user authentication
        current_user_id = get_jwt_identity()
        
        # Mock implementation - in production, update database
        return jsonify({
            'success': True,
            'message': 'Quest status updated',
            'starsEarned': 10  # Mock stars earned
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def chatbot_logic(user_id, user_message, session_id=None):
    """Extracted chatbot logic for reuse with new session-based model"""
    
    # Get or create chat session
    if session_id:
        chat_session = db.session.get(ChatSession, session_id)
        if not chat_session:
            chat_session = ChatSession(user_id=user_id)
            db.session.add(chat_session)
            db.session.flush()
    else:
        # ALWAYS create a new session when session_id is None
        chat_session = ChatSession(user_id=user_id)
        db.session.add(chat_session)
        db.session.flush()
    
    # Save user message as interaction (mood will be updated after LLM response)
    user_interaction = LLMInteractions(
        session_id=chat_session.id,
        user_message=user_message,
        user_timestamp=datetime.now(UTC)
    )
    db.session.add(user_interaction)
    db.session.flush()
    
    # Get recent interactions for context (last 10)
    recent_interactions = LLMInteractions.query.filter_by(session_id=chat_session.id)\
                                              .order_by(LLMInteractions.user_timestamp.desc())\
                                              .limit(10).all()
    
    # Build conversation context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add recent chat history in chronological order
    for interaction in reversed(recent_interactions[1:]):  # Skip current interaction
        messages.append({"role": "user", "content": interaction.user_message})
        if interaction.llm_response:
            # Clean the LLM response to remove mood tags before adding to context
            clean_response = interaction.llm_response
            if '[MOOD:' in clean_response:
                clean_response = clean_response.split('[MOOD:')[0].strip()
            messages.append({"role": "assistant", "content": clean_response})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    # Get response from LLM
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=messages,
            max_tokens=250,
            temperature=0.7
        )
        
        bot_reply = response.choices[0].message.content.strip()
    except Exception as e:
        bot_reply = "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment. [MOOD: neutral]"
    
    # Extract mood from LLM response
    detected_mood = 'neutral'
    clean_bot_reply = bot_reply
    
    if '[MOOD:' in bot_reply:
        try:
            # Extract mood from the response
            mood_part = bot_reply.split('[MOOD:')[1].split(']')[0].strip().lower()
            detected_mood = mood_part
            # Remove mood tag from the response shown to user
            clean_bot_reply = bot_reply.split('[MOOD:')[0].strip()
        except (IndexError, AttributeError):
            detected_mood = 'neutral'
    
    # Update the interaction with bot response and detected mood
    user_interaction.llm_response = bot_reply  # Keep full response with mood tag
    user_interaction.llm_timestamp = datetime.now(UTC)
    user_interaction.mood_tag = detected_mood
    
    # Update session mood_tag (overwrite with latest mood)
    chat_session.mood_tag = detected_mood
    chat_session.updated_at = datetime.now(UTC)
    
    db.session.commit()
    
    return {
        'response': clean_bot_reply,  # Return clean response without mood tag
        'timestamp': user_interaction.llm_timestamp.isoformat(),
        'session_id': chat_session.id,
        'mood': detected_mood
    }

#Finance tracker APIs
@app.route('/api/parentchild', methods=['GET'])
def get_parent_child_links():
    """Get parent-child relationships"""
    try:
        links = ParentChild.query.all()
        return jsonify({
            "links": [
                {
                    "id": link.id,
                    "parent_id": link.parent_id,
                    "child_id": link.child_id,
                    "relationship_type": link.relationship_type
                }
                for link in links
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/finance/transactions/<int:user_id>', methods=['GET'])
@jwt_required()
def get_transactions(user_id):
    """Get financial transactions for a user - requires JWT token"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Authorization: users can only access their own transactions
        # or parents can access their children's transactions
        if current_user.id != user_id and current_user.role != 'parent':
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        transactions = Transaction.query.filter_by(user_id=user_id)\
                                     .order_by(Transaction.date.desc()).all()
        
        return jsonify({
            'success': True,
            'transactions': [{
                'id': t.id,
                'amount': t.amount,
                'type': t.type,
                'description': t.description,
                'date': t.date.isoformat()
            } for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/finance/transaction', methods=['POST'])
@jwt_required()
def add_transaction():
    """Add a new financial transaction - requires JWT token"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Ensure user can only add transactions for themselves
        if data.get('user_id') != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only add transactions for yourself'}), 403
        
        transaction = Transaction(
            user_id=data['user_id'],
            amount=data['amount'],
            type=data['type'],
            description=data['description']
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'transaction': {
                'id': transaction.id,
                'amount': transaction.amount,
                'type': transaction.type,
                'description': transaction.description,
                'date': transaction.date.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/finance/goals/<int:user_id>', methods=['GET'])
@jwt_required()
def get_savings_goals(user_id):
    """Get savings goals for a user - requires JWT token"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Authorization: users can only access their own goals
        # or parents can access their children's goals
        if current_user.id != user_id and current_user.role != 'parent':
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        goals = SavingGoal.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'goals': [{
                'id': g.id,
                'label': g.label,
                'target_amount': g.target_amount,
                'current_amount': g.current_amount
            } for g in goals]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/finance/goal', methods=['POST'])
@jwt_required()
def add_savings_goal():
    """Add a new savings goal - requires JWT token"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Ensure user can only add goals for themselves
        if data.get('user_id') != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only add goals for yourself'}), 403
        
        goal = SavingGoal(
            user_id=data['user_id'],
            label=data['label'],
            target_amount=data['target_amount'],
            current_amount=0
        )
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'goal': {
                'id': goal.id,
                'label': goal.label,
                'target_amount': goal.target_amount,
                'current_amount': goal.current_amount
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Psychometric test routes
# ---------------------------


# Configuration - Move these to environment variables in production
OPENROUTER_API_KEY = app.config['OPENROUTER_API_KEY']
OPENROUTER_API_URL = app.config['OPENROUTER_API_URL']

# Initialize Psychometry Service
psychometry_service = PsychometryService(OPENROUTER_API_KEY, OPENROUTER_API_URL)

# Psychometry Assessment Routes
@app.route('/api/psychometry/start', methods=['POST'])
def start_psychometry_test():
    """Initialize a new psychometry assessment test session"""
    try:
        print(f"🔍 PSYCHOMETRY START: Request received from {request.origin}")
        print(f"🔍 PSYCHOMETRY START: Headers: {dict(request.headers)}")
        
        # Get user ID from request body (no JWT required for psychometric test)
        data = request.get_json()
        print(f"🔍 PSYCHOMETRY START: Request data: {data}")
        
        user_id = data.get('user_id')
        
        if not user_id:
            print(f"🔍 PSYCHOMETRY START: ERROR - No user_id provided")
            return jsonify({'error': 'user_id is required'}), 400

        # Store user_id in session for later use (backup)
        session['psychometry_user_id'] = user_id

        # Initialize assessment
        test_questions = psychometry_service.initialize_assessment()
        
        # Debug: Check if questions are properly formatted
        print(f"DEBUG START: Generated {len(test_questions)} questions")
        print(f"DEBUG START: user_id={user_id} (type: {type(user_id)})")
        if test_questions:
            first_question = test_questions[0]
            print(f"DEBUG START: First question structure: {first_question}")
            print(f"DEBUG START: First question text: '{first_question.get('question', 'MISSING')}'")
        
        # Store in session (backup) and also in a more reliable way
        session['psychometry_questions'] = test_questions
        session['psychometry_current_index'] = 0
        session['psychometry_responses'] = []
        session['psychometry_start_time'] = time.time()
        session.permanent = True
        
        # ALSO store in a temporary way that's more reliable
        # We'll use a simple approach: store in the user's session as a JSON string in memory
        # For now, let's try to make sessions work by ensuring they're properly configured
        import json
        session_data = {
            'user_id': user_id,
            'questions': test_questions,
            'current_index': 0,
            'responses': [],
            'start_time': time.time()
        }
        # Store as a backup in session with a different key
        session[f'psychometry_session_{user_id}'] = json.dumps(session_data)
        
        # Debug: Verify session data was stored
        print(f"DEBUG START: Session keys after storage: {list(session.keys())}")
        print(f"DEBUG START: backup_session_key=psychometry_session_{user_id}")
        print(f"DEBUG START: backup session data stored successfully: {bool(session.get(f'psychometry_session_{user_id}'))}")
        print(f"DEBUG START: regular session data - questions count: {len(session.get('psychometry_questions', []))}")
        print(f"DEBUG START: regular session data - current_index: {session.get('psychometry_current_index', 'NOT_SET')}")
        
        # Return first question
        return get_next_psychometry_question()
        
    except Exception as e:

        return jsonify({'error': 'Failed to start psychometry test', 'message': str(e)}), 500

@app.route('/api/psychometry/submit', methods=['POST'])
def submit_psychometry_answer():
    """Submit an answer for psychometry assessment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # Basic validation: check if user_id matches session (if session exists)
        session_user_id = session.get('psychometry_user_id')
        if session_user_id and str(user_id) != str(session_user_id):
            print(f"DEBUG SUBMIT: ERROR - Session user ID mismatch: session={session_user_id}, request={user_id}")
            return jsonify({'error': 'Session user ID mismatch'}), 400
        
        user_answer = data.get('answer')
        if not user_answer:
            print(f"DEBUG SUBMIT: ERROR - No answer provided in request")
            return jsonify({'error': 'No answer provided'}), 400
        
        # Get current question - try backup session data first
        import json
        backup_session_key = f'psychometry_session_{user_id}'
        backup_session_data = session.get(backup_session_key)
        
        print(f"DEBUG SUBMIT: user_id={user_id} (type: {type(user_id)})")
        print(f"DEBUG SUBMIT: session_user_id={session_user_id} (type: {type(session_user_id)})")
        print(f"DEBUG SUBMIT: backup_session_key={backup_session_key}")
        print(f"DEBUG SUBMIT: backup_session_data exists={bool(backup_session_data)}")
        print(f"DEBUG SUBMIT: regular session keys={list(session.keys())}")
        print(f"DEBUG SUBMIT: all session data={dict(session)}")
        print(f"DEBUG SUBMIT: request data={data}")
        print(f"DEBUG SUBMIT: user_answer={user_answer}")
        
        if backup_session_data:
            try:
                session_data = json.loads(backup_session_data)
                current_index = session_data.get('current_index', 0)
                questions = session_data.get('questions', [])
                responses = session_data.get('responses', [])
                print(f"DEBUG SUBMIT: Using backup session - index={current_index}, questions_count={len(questions)}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"DEBUG SUBMIT: Backup session parse error: {e}")
                # Fallback to regular session
                current_index = session.get('psychometry_current_index', 0)
                questions = session.get('psychometry_questions', [])
                responses = session.get('psychometry_responses', [])
                print(f"DEBUG SUBMIT: Using regular session fallback - index={current_index}, questions_count={len(questions)}")
        else:
            # Fallback to regular session
            current_index = session.get('psychometry_current_index', 0)
            questions = session.get('psychometry_questions', [])
            responses = session.get('psychometry_responses', [])
            print(f"DEBUG SUBMIT: Using regular session - index={current_index}, questions_count={len(questions)}")
        
        if current_index >= len(questions):
            print(f"DEBUG SUBMIT: ERROR - Invalid question index: {current_index}/{len(questions)}")
            return jsonify({'error': f'Invalid question index: {current_index}/{len(questions)}. Session may have expired.'}), 400
            
        current_question = questions[current_index]
        
        # Process answer through psychometry service
        psychometry_service.process_answer(current_question, user_answer)
        
        # Record response in session
        session['psychometry_responses'].append({
            'question': current_question['question'],
            'user_answer': user_answer,
            'correct_answer': current_question['correct_answer'],
            'category': current_question['category'],
            'is_correct': user_answer == current_question['correct_answer']
        })
        
        # Update session
        session['psychometry_current_index'] = current_index + 1
        
        # Also update backup session data
        if backup_session_data:
            try:
                session_data = json.loads(backup_session_data)
                session_data['current_index'] = current_index + 1
                session_data['responses'] = responses
                session[backup_session_key] = json.dumps(session_data)
            except (json.JSONDecodeError, KeyError):
                pass  # If backup fails, continue with regular session
        
        # Check if test is complete
        if session['psychometry_current_index'] >= len(questions):
            return complete_psychometry_assessment()
        
        # Get next question
        return get_next_psychometry_question()
        
    except Exception as e:

        return jsonify({'error': 'Failed to submit answer', 'message': str(e)}), 500

def get_next_psychometry_question():
    """Get the next question in the psychometry assessment"""
    try:
        current_index = session.get('psychometry_current_index', 0)
        questions = session.get('psychometry_questions', [])
        
        if current_index >= len(questions):
            return complete_psychometry_assessment()
        
        current_question = questions[current_index]
        
        return jsonify({
            'question': current_question['question'],
            'options': current_question['options'],
            'correct_answer': current_question['correct_answer'],
            'category': current_question['category'],
            'question_number': current_index + 1,
            'total_questions': len(questions),
            'progress': round((current_index / len(questions)) * 100, 1)
        })
        
    except Exception as e:

        return jsonify({'error': 'Failed to get next question', 'message': str(e)}), 500


def complete_psychometry_assessment():
    """Complete the psychometry assessment and generate results"""
    try:
        # Get results from psychometry service
        assessment_results = psychometry_service.get_results()
        
        # Calculate additional metrics
        responses = session.get('psychometry_responses', [])
        total_questions = len(responses)
        total_correct = sum(1 for response in responses if response['is_correct'])
        accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        
        start_time = session.get('psychometry_start_time', time.time())
        test_duration = round(time.time() - start_time, 1)

        # Optionally clear session data (uncomment if you want to reset after completion)
        # session.pop('psychometry_questions', None)
        # session.pop('psychometry_current_index', None)
        # session.pop('psychometry_responses', None)
        # session.pop('psychometry_start_time', None)
        # ---  Save result to DB
        child_id = session.get('psychometry_user_id')  # You must store this earlier from login/session

        if child_id:
            test_result = PsychometricTestResult(
                child_id=child_id,
                learning_style=assessment_results['learning_style'],
                personality_type=assessment_results['personality_type'],
                top_interest=assessment_results['top_interest'],
                concentration_level=assessment_results['concentration_level'],
                memory_strength=assessment_results['memory_strength'],
                detailed_scores=assessment_results['detailed_scores'],
                personality_breakdown=assessment_results['personality_breakdown'],
                feedback=assessment_results['feedback'],
                duration_seconds=test_duration
            )
            db.session.add(test_result)
            db.session.commit()
        return jsonify({
            'results': assessment_results,
            'responses': responses,
            'total_questions': total_questions,
            'total_correct': total_correct,
            'accuracy': round(accuracy, 1),
            'duration_seconds': test_duration
        })
    except Exception as e:

        return jsonify({'error': 'Failed to complete assessment', 'message': str(e)}), 500

# Psychometric Test Stats for parent Dashboard
@app.route('/api/psychometry/results/<int:child_id>', methods=['GET'])
def get_psychometry_results(child_id):
    """Get the latest psychometric test result for a child"""
    try:
        result = PsychometricTestResult.query.filter_by(child_id=child_id).order_by(PsychometricTestResult.taken_at.desc()).first()
        if not result:
            return jsonify({'success': False, 'error': 'No result found'}), 404
        print(result)
        return jsonify({
            'success': True,
            'result': {
                'id': result.id,
                'child_id': result.child_id,
                'taken_at': result.taken_at.strftime('%Y-%m-%d %H:%M:%S') if result.taken_at else None,
                'learning_style': result.learning_style,
                'personality_type': result.personality_type,
                'top_interest': result.top_interest,
                'concentration_level': result.concentration_level,
                'memory_strength': result.memory_strength,
                'detailed_scores': result.detailed_scores,
                'personality_breakdown': result.personality_breakdown,
                'duration_seconds': result.duration_seconds,
                'feedback': result.feedback
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# ---------------------------
# Task Tracker (Homework) Routes
# ---------------------------
@app.route('/api/tasks/<int:user_id>', methods=['GET'])
@jwt_required()
def get_tasks(user_id):
    """Get all tasks for a specific user"""
    try:
        # Security check: ensure user can only access their own tasks
        current_user_id = int(get_jwt_identity())
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        
        # Simple authorization: users can only access their own tasks
        # or parents can access their children's tasks
        # if current_user.id != user_id and current_user.role != 'parent':
        #     return jsonify({'error': 'Unauthorized access'}), 403
        
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        
        tasks_data = []
        for task in tasks:
            # Get session statistics and calculate totals
            sessions = PomodoroSession.query.filter_by(homework_id=task.id)
            total_work_time = sum(s.work_duration for s in sessions)
            total_break_time = sum(s.break_duration for s in sessions)
            total_time_spent_minutes = total_work_time // 60  # Convert to minutes
            
            session_stats = {
                'total_sessions': sessions.count(),
                'completed_sessions': sessions.filter_by(completed=True).count(),
                'incomplete_sessions': sessions.filter_by(completed=False).count(),
                'total_work_time': total_work_time // 60,  # Convert to minutes
                'total_break_time': total_break_time // 60   # Convert to minutes
            }
            
            tasks_data.append({
                'id': task.id,
                'user_id': task.user_id,  # Add user_id to response
                'subject': task.subject,
                'task': task.task,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'time_spent': total_time_spent_minutes,
                'session_stats': session_stats
            })

        return jsonify({
            'success': True,
            'tasks': tasks_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tasks-for-parent/<int:user_id>', methods=['GET'])
@jwt_required()
def get_tasks_for_parents(user_id):
    """Get all tasks for a specific user - only accessible by parents"""
    try:
        # Security check: ensure current user is a parent and can access child's tasks
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
            
        # Check if current user is a parent
        if current_user.role != 'parent':
            return jsonify({'success': False, 'error': 'Unauthorized access - parent role required'}), 403
        
        # Check if there's a parent-child relationship
        parent_child_link = ParentChild.query.filter_by(
            parent_id=current_user_id, 
            child_id=user_id
        ).first()
        if not parent_child_link:
            return jsonify({'success': False, 'error': 'Unauthorized access - no parent-child relationship'}), 403
        
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        
        # Simple authorization: users can only access their own tasks
        # or parents can access their children's tasks
        # if current_user.id != user_id and current_user.role != 'parent':
        #     return jsonify({'error': 'Unauthorized access'}), 403
        
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        
        tasks_data = []
        for task in tasks:
            # Get session statistics and calculate totals
            sessions = PomodoroSession.query.filter_by(homework_id=task.id)
            total_work_time = sum(s.work_duration for s in sessions)
            total_break_time = sum(s.break_duration for s in sessions)
            total_time_spent_minutes = total_work_time // 60  # Convert to minutes
            
            session_stats = {
                'total_sessions': sessions.count(),
                'completed_sessions': sessions.filter_by(completed=True).count(),
                'incomplete_sessions': sessions.filter_by(completed=False).count(),
                'total_work_time': total_work_time // 60,  # Convert to minutes
                'total_break_time': total_break_time // 60   # Convert to minutes
            }
            
            tasks_data.append({
                'id': task.id,
                'user_id': task.user_id,  # Add user_id to response
                'subject': task.subject,
                'task': task.task,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'status': task.status,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'time_spent': total_time_spent_minutes,
                'session_stats': session_stats
            })

        return jsonify({
            'success': True,
            'tasks': tasks_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tasks', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Security check: ensure user can only create tasks for themselves
        user_id = data.get('user_id')
        current_user_id = int(get_jwt_identity())
        
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
            
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access - can only create tasks for yourself'}), 403
        
        # Handle empty due_date string properly
        due_date_str = data.get('due_date')
        due_date = None
        if due_date_str and due_date_str.strip():  # Check if not empty or whitespace
            try:
                due_date = date.fromisoformat(due_date_str)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        current_time = datetime.now(UTC)
        # Create task with current timestamp
        new_task = HomeworkSchedule(
           user_id=data['user_id'],
            subject=data.get('subject'),
            task=data['task'],
            due_date=due_date,  # Use the properly handled due_date variable
            created_at=current_time,
            assigned_by_teacher=data.get('assigned_by_teacher')  # Set teacher assignment if provided
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Task created successfully',
            'task': {
                'id': new_task.id,
                'subject': new_task.subject,
                'task': new_task.task,
                'due_date': new_task.due_date.isoformat() if new_task.due_date else None,
                'status': new_task.status,
                'created_at': current_time.strftime('%Y-%m-%d %H:%M:%S')  # Human readable time
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
@jwt_required()
def update_task_status(task_id):
    """Update a task's status"""
    try:
        # Security check: get current user
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        data = request.get_json()
        new_status = data.get('status')

        task = db.session.get(HomeworkSchedule, task_id)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        # Authorization: users can only update their own tasks or parents can update their children's tasks
        if task.user_id != current_user_id and current_user.role != 'parent':
            return jsonify({'success': False, 'error': 'Unauthorized: Can only update your own tasks'}), 403

        task.status = new_status
        # Note: updated_at will be automatically set by SQLAlchemy if the column exists
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Task status updated to {new_status}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        # Security check: get current user
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        task = db.session.get(HomeworkSchedule, task_id)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        # Authorization: users can only delete their own tasks or teachers can delete tasks they assigned
        if task.user_id != current_user_id and task.assigned_by_teacher != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only delete your own tasks or tasks you assigned'}), 403

        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Task deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Teacher Management Routes
# ---------------------------
@app.route('/api/teacher/students/<int:teacher_id>', methods=['GET'])
def get_teacher_students(teacher_id):
    """Get all students assigned to a specific teacher"""
    try:
        
        
        # Simple authorization check using Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing authorization token'}), 401
        
        # For now, accept any valid format Bearer token (fix JWT later)
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        
        
        # Get students through ParentChild table where parent_id is the teacher
        student_relationships = ParentChild.query.filter_by(parent_id=teacher_id).all()
        students_data = []
        
        
        
        for relationship in student_relationships:
            student = User.query.get(relationship.child_id)
            if student:
                
                students_data.append({
                    'id': student.id,
                    'username': student.username,
                    'email': student.email,
                    'role': student.role
                })
        
        return jsonify({
            'success': True,
            'students': students_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/student-tasks/<int:teacher_id>', methods=['GET'])
@jwt_required()
def get_student_tasks_for_teacher(teacher_id):
    """Get all tasks created by students under a specific teacher"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Authorization: only the teacher themselves can access their students' tasks
        if current_user.id != teacher_id or current_user.role != 'teacher':
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Get students under this teacher
        student_relationships = ParentChild.query.filter_by(parent_id=teacher_id).all()
        student_ids = [rel.child_id for rel in student_relationships]
        
        # Get all tasks for these students
        all_tasks = []
        for student_id in student_ids:
            tasks = HomeworkSchedule.query.filter_by(user_id=student_id).order_by(HomeworkSchedule.due_date.asc()).all()
            
            for task in tasks:
                # Get session statistics
                sessions = PomodoroSession.query.filter_by(homework_id=task.id)
                total_work_time = sum(s.work_duration for s in sessions if s.work_duration)
                total_time_spent_minutes = total_work_time // 60 if total_work_time else 0
                
                all_tasks.append({
                    'id': task.id,
                    'user_id': task.user_id,
                    'subject': task.subject,
                    'task': task.task,
                    'due_date': task.due_date.isoformat() if task.due_date else None,
                    'status': task.status,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                    'time_spent': total_time_spent_minutes
                })
        
        return jsonify({
            'success': True,
            'tasks': all_tasks
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/homework/<int:teacher_id>', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_teacher_homework(teacher_id):
    """Get all homework assigned by a specific teacher - temporarily disabled JWT for testing"""
    try:
        # Get Authorization header to extract user info for testing
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing authorization token'}), 401
        
        # For now, accept any valid format Bearer token (fix JWT later)
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        
        
        # current_user_id = get_jwt_identity()
        # current_user = User.query.get(current_user_id)
        
        # Authorization: only the teacher themselves can access their assigned homework
        # if current_user.id != teacher_id or current_user.role != 'teacher':
        #     return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        # Get homework assigned by this teacher
        # Using a custom field to track teacher-assigned homework
        homework_tasks = HomeworkSchedule.query.filter_by(assigned_by_teacher=teacher_id).order_by(HomeworkSchedule.due_date.asc()).all()
        
        homework_data = []
        for task in homework_tasks:
            homework_data.append({
                'id': task.id,
                'subject': task.subject,
                'task': task.task,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'status': task.status,
                'assigned_to': [task.user_id],  # Currently single user, could be extended for multiple
                'created_at': task.created_at.isoformat() if task.created_at else None
            })
        
        return jsonify({
            'success': True,
            'homework': homework_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/teacher/assign-homework', methods=['POST'])
@jwt_required()
def assign_homework():
    """Allow teacher to assign homework to multiple students"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        data = request.get_json()
        
        # Authorization: only teachers can assign homework
        if current_user.role != 'teacher':
            return jsonify({'success': False, 'error': 'Only teachers can assign homework'}), 403
        
        # Validate required fields
        required_fields = ['subject', 'task', 'due_date', 'assigned_to']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Parse due date
        try:
            due_date = date.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Verify students belong to this teacher
        student_ids = data['assigned_to']
        teacher_relationships = ParentChild.query.filter_by(parent_id=current_user_id).all()
        teacher_student_ids = [rel.child_id for rel in teacher_relationships]
        
        unauthorized_students = [sid for sid in student_ids if sid not in teacher_student_ids]
        if unauthorized_students:
            return jsonify({'success': False, 'error': f'Unauthorized to assign homework to students: {unauthorized_students}'}), 403
        
        # Create homework tasks for each student
        created_tasks = []
        current_time = datetime.now(UTC)
        
        for student_id in student_ids:
            new_task = HomeworkSchedule(
                user_id=student_id,
                subject=data['subject'],
                task=data['task'],
                due_date=due_date,
                assigned_by_teacher=current_user_id,
                created_at=current_time,
                status='pending'
            )
            db.session.add(new_task)
            created_tasks.append(new_task)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Homework assigned to {len(student_ids)} students',
            'assigned_tasks': len(created_tasks)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Pomodoro Session Routes
# ---------------------------
@app.route('/api/pomodoro/start', methods=['POST'])
@jwt_required()
def start_pomodoro():
    """Start a new pomodoro session for a task - requires JWT token"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()

        # Ensure user can only start sessions for themselves
        if data.get('user_id') != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only start sessions for yourself'}), 403

        # Validate required fields
        if 'user_id' not in data:
            return jsonify({'success': False, 'error': 'Missing user_id'}), 400
        if 'homework_id' not in data:
            return jsonify({'success': False, 'error': 'Missing homework_id'}), 400
            
        session = PomodoroSession(
            user_id=data['user_id'],
            homework_id=data['homework_id'],
            start_time=datetime.now(UTC)
        )
        db.session.add(session)

        # Update task status to 'in-progress'
        task = db.session.get(HomeworkSchedule, data['homework_id'])
        if task:
            task.status = 'in-progress'

        # Session started successfully

        db.session.commit()
        return jsonify({'success': True, 'session_id': session.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/complete/<int:session_id>', methods=['PUT'])
@jwt_required()
def complete_pomodoro(session_id):
    """Complete a pomodoro session - requires JWT token"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        duration = data.get('duration') # in minutes

        session = db.session.get(PomodoroSession, session_id)
        print(session.homework_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Authorization: users can only complete their own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only complete your own sessions'}), 403

        # Get work and break duration from request
        work_duration = data.get('work_duration', 0)
        break_duration = data.get('break_duration', 0)
        
        # Add any remaining active time
        #if session.start_time:
        #    remaining_work = int((datetime.now(UTC) - session.start_time).total_seconds())
        #   work_duration += remaining_work

        session.work_duration = work_duration
        session.break_duration = break_duration
        session.completed = True
        session.end_time = datetime.now(UTC)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Pomodoro session completed','focus_time':work_duration,'break_time':break_duration}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

    
@app.route('/api/pomodoro/last-session/<int:user_id>/<int:homework_id>', methods=['GET'])
@jwt_required()
def get_last_pomodoro_session(user_id, homework_id):
    current_user_id = int(get_jwt_identity())

    # Optional: Ensure the current user can only fetch their own session
    if current_user_id != user_id:
        return jsonify({'success': False, 'error': 'Unauthorized access'}), 403

    session = (PomodoroSession.query
        .filter_by(user_id=user_id, homework_id=homework_id)
        .order_by(PomodoroSession.end_time.desc())
        .first())

    if not session:
        return jsonify({'success': False, 'error': 'No session found'}), 404
    print(session.work_duration, session.break_duration, session.id, session.start_time, session.end_time)
    return jsonify({
        'success': True,
        'work_duration': session.work_duration,
        'break_duration': session.break_duration,
        'session_id': session.id,
        'start_time': session.start_time.isoformat() if session.start_time else None,
        'end_time': session.end_time.isoformat() if session.end_time else None
    })

@app.route('/api/pomodoro/pause/<int:session_id>', methods=['PUT'])
@jwt_required()
def pause_pomodoro(session_id):
    """Pause a pomodoro session"""
    try:
        current_user_id = int(get_jwt_identity())
        
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Authorization: users can only pause their own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only pause your own sessions'}), 403

        # Calculate work duration so far
        if session.start_time:
            work_duration = int((datetime.now(UTC) - session.start_time).total_seconds())
            session.work_duration += work_duration

        session.start_time = None  # Reset start time for next resume

        # Session is now paused

        db.session.commit()
        return jsonify({'success': True, 'message': 'Session paused'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/resume/<int:session_id>', methods=['PUT'])
@jwt_required()
def resume_pomodoro(session_id):
    """Resume a paused pomodoro session"""
    try:
        current_user_id = int(get_jwt_identity())
        
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Authorization: users can only resume their own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only resume your own sessions'}), 403

        session.start_time = datetime.now(UTC)

        # Session resumed - break time will be calculated when session ends

        db.session.commit()
        return jsonify({'success': True, 'message': 'Session resumed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/abandon/<int:session_id>', methods=['PUT'])
@jwt_required()
def abandon_pomodoro(session_id):
    """Abandon a pomodoro session"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Authorization: users can only abandon their own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only abandon your own sessions'}), 403

        # Get work and break duration from request
        work_duration = data.get('work_duration', 0) if data else 0
        break_duration = data.get('break_duration', 0) if data else 0
        
        # Add any remaining active time
        if session.start_time:
            remaining_work = int((datetime.now(UTC) - session.start_time).total_seconds())
            work_duration += remaining_work

        session.work_duration = work_duration
        session.break_duration = break_duration
        session.end_time = datetime.now(UTC)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Session abandoned'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/task-time/analytics/<int:user_id>', methods=['GET'])
@jwt_required()
def get_task_time_analytics(user_id):
    """Get time analytics for a user"""
    try:
        homework_id = request.args.get('homework_id', type=int)
        
        # Get session statistics
        sessions = PomodoroSession.query.filter_by(user_id=user_id)
        if homework_id:
            sessions = sessions.filter_by(homework_id=homework_id)
        
        # Calculate analytics from PomodoroSession data
        total_work_time = sum(s.work_duration for s in sessions)
        total_break_time = sum(s.break_duration for s in sessions)
        
        session_stats = {
            'total_sessions': sessions.count(),
            'completed_sessions': sessions.filter_by(completed=True).count(),
            'incomplete_sessions': sessions.filter_by(completed=False).count(),
            'average_work_time': sessions.with_entities(db.func.avg(PomodoroSession.work_duration)).scalar() or 0,
            'average_break_time': sessions.with_entities(db.func.avg(PomodoroSession.break_duration)).scalar() or 0
        }
        
        return jsonify({
            'success': True,
            'analytics': {
                'total_work_time': total_work_time,
                'total_break_time': total_break_time,
                'session_stats': session_stats,
                'recent_sessions': [{
                    'id': s.id,
                    'start_time': s.start_time.isoformat() if s.start_time else None,
                    'end_time': s.end_time.isoformat() if s.end_time else None,
                    'work_duration': s.work_duration,
                    'break_duration': s.break_duration,
                    'completed': s.completed
                } for s in sessions.order_by(PomodoroSession.start_time.desc()).limit(10).all()]
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Screen Time Routes
# ---------------------------
@app.route('/api/screen-time/log', methods=['POST'])
def log_screen_time():
    """Log screen time for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        duration_seconds = data.get('duration_seconds')
        
        if not user_id or duration_seconds is None:
            return jsonify({'success': False, 'error': 'user_id and duration_seconds are required'}), 400
        
        # Convert seconds to hours for storage
        duration_hours = duration_seconds / 3600.0
        today = date.today()
        
        # Check if there's already a record for today
        existing_record = ScreenTime.query.filter_by(user_id=user_id, date=today).first()
        
        if existing_record:
            # Add to existing record
            existing_record.hours += duration_hours
        else:
            # Create new record
            new_record = ScreenTime(
                user_id=user_id,
                hours=duration_hours,
                date=today
            )
            db.session.add(new_record)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Screen time logged successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/screen-time/<int:user_id>', methods=['GET'])
def get_screen_time(user_id):
    """Get screen time data for a user"""
    try:
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # Get today's screen time
        today_record = ScreenTime.query.filter_by(user_id=user_id, date=today).first()
        today_hours = today_record.hours if today_record else 0
        
        # Get week's average
        week_records = ScreenTime.query.filter(
            ScreenTime.user_id == user_id,
            ScreenTime.date >= week_ago,
            ScreenTime.date <= today
        ).all()
        
        week_total_hours = sum(record.hours for record in week_records)
        week_average_hours = week_total_hours / 7 if week_records else 0
        
        # Format display strings
        today_display = f"{int(today_hours)}h {int((today_hours % 1) * 60)}m"
        week_average_display = f"{int(week_average_hours)}h {int((week_average_hours % 1) * 60)}m"
        
        # Determine status
        if today_hours <= 2:
            status = "Great!"
        elif today_hours <= 4:
            status = "Good"
        else:
            status = "Too much"
        
        return jsonify({
            'success': True,
            'screen_time': {
                'today_hours': today_hours,
                'today_display': today_display,
                'week_average_hours': week_average_hours,
                'week_average_display': week_average_display,
                'status': status
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Module Progress Routes
# ---------------------------

# Module ID mapping for consistent module identification
MODULE_MAPPING = {
    'math_magic': {'id': 1, 'name': 'Math Magic', 'has_submodules': False},
    'word_wizard': {'id': 2, 'name': 'Word Wizard', 'has_submodules': False},
    'science_explorer': {'id': 3, 'name': 'Science Explorer', 'has_submodules': True},
    'safety_measures': {'id': 4, 'name': 'Safety Measures', 'has_submodules': True},
    'good_touch_bad_touch': {'id': 5, 'name': 'Good Touch Bad Touch', 'has_submodules': False},
    'psychometric_assessment': {'id': 6, 'name': 'Psychometric Assessment', 'has_submodules': False}
}

# Submodule ID mapping - only for modules that have submodules
SUBMODULE_MAPPING = {
    'science_explorer': {
        'balance_master': {'id': 1, 'name': 'Balance Master', 'progress_weight': 16.67},
        'force_detective': {'id': 2, 'name': 'Force Detective', 'progress_weight': 16.67},
        'space_explorer': {'id': 3, 'name': 'Space Explorer', 'progress_weight': 16.67},
        'wave_wizard': {'id': 4, 'name': 'Wave Wizard', 'progress_weight': 16.67},
        'matter_transformer': {'id': 5, 'name': 'Matter Transformer', 'progress_weight': 16.67},
        'energy_master': {'id': 6, 'name': 'Energy Master', 'progress_weight': 16.65}
    },
    'safety_measures': {
        'home_safety': {'id': 1, 'name': 'Home Safety', 'progress_weight': 16.67},
        'road_safety': {'id': 2, 'name': 'Road Safety', 'progress_weight': 16.67},
        'internet_safety': {'id': 3, 'name': 'Internet Safety', 'progress_weight': 16.67},
        'fire_safety': {'id': 4, 'name': 'Fire Safety', 'progress_weight': 16.67},
        'emergency_procedures': {'id': 5, 'name': 'Emergency Procedures', 'progress_weight': 16.67},
        'personal_safety': {'id': 6, 'name': 'Personal Safety', 'progress_weight': 16.65}
    }
}

def get_module_id(module_name):
    """Get module ID from module name"""
    module_info = MODULE_MAPPING.get(module_name)
    return module_info['id'] if module_info else None

def get_submodule_id(module_name, submodule_name):
    """Get submodule ID from module name and submodule name"""
    # Check if the module has submodules
    module_info = MODULE_MAPPING.get(module_name)
    if not module_info or not module_info.get('has_submodules', False):
        return None  # Module doesn't have submodules
    
    module_submodules = SUBMODULE_MAPPING.get(module_name, {})
    submodule_info = module_submodules.get(submodule_name)
    return submodule_info['id'] if submodule_info else None

def module_has_submodules(module_name):
    """Check if a module has submodules"""
    module_info = MODULE_MAPPING.get(module_name)
    return module_info.get('has_submodules', False) if module_info else False

@app.route('/api/module/progress', methods=['POST'])
@jwt_required()
def save_module_progress():
    """Save module progress for a user using UserModuleProgress table"""
    try:
        data = request.get_json()
        
        # Extract data from request
        user_id = data.get('user_id')
        
        # Security check: ensure user can only save their own progress
        current_user_id = int(get_jwt_identity())
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        module_type = data.get('module_type', 'Unknown Module')
        progress_percentage = data.get('progress_percentage', 0)
        is_completed = data.get('is_completed', False)
        progress_data = data.get('progress_data', {})
        submodule_name = data.get('submodule_name', '')
        
        
          # Log full request data
        
        # Validation
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get module and submodule IDs
        module_id = get_module_id(module_type)
        
        # Handle submodules based on module type
        if module_has_submodules(module_type):
            # Module has submodules, so submodule_name is required
            if not submodule_name:
                
                return jsonify({'success': False, 'error': f'Submodule name required for module: {module_type}'}), 400
            submodule_id = get_submodule_id(module_type, submodule_name)
            if not submodule_id:
                
                return jsonify({'success': False, 'error': f'Invalid submodule: {submodule_name}'}), 400
        else:
            # Module doesn't have submodules, so clear submodule fields
            submodule_name = None
            submodule_id = None
        
        
        
        # Find existing progress record for this module/submodule combination
        if module_has_submodules(module_type):
            # For modules with submodules, find by both module and submodule
            existing_progress = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=module_type,
                submodule_name=submodule_name
            ).first()
        else:
            # For modules without submodules, find by module only
            existing_progress = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=module_type
            ).first()
        
        if existing_progress:
            # Update existing progress
            existing_progress.progress = progress_percentage
            existing_progress.completed = is_completed
            existing_progress.submodule_name = submodule_name
            existing_progress.module_id = module_id
            existing_progress.submodule_id = submodule_id
            
        else:
            # Create new progress record
            new_progress = UserModuleProgress(
                user_id=user_id,
                module_name=module_type,
                submodule_name=submodule_name,
                module_id=module_id,
                submodule_id=submodule_id,
                progress=progress_percentage,
                completed=is_completed
            )
            db.session.add(new_progress)
            
        
        # Commit changes
        db.session.commit()
        
        
        return jsonify({
            'success': True, 
            'message': 'Progress saved successfully',
            'progress_percentage': progress_percentage,
            'is_completed': is_completed
        }), 200
        
    except Exception as e:
        
        import traceback
  # Print full traceback
        db.session.rollback()
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/module/progress/<int:user_id>/<module_type>', methods=['GET'])
@jwt_required()
def get_module_progress(user_id, module_type):
    """Get module progress for a user"""
    try:
        # URL decode the module type to handle spaces and special characters
        from urllib.parse import unquote
        decoded_module_type = unquote(module_type)
        
        
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Check if module exists
        module_info = MODULE_MAPPING.get(decoded_module_type)
        if not module_info:
            
            return jsonify({'success': False, 'error': f'Module not found: {decoded_module_type}'}), 404
        
        # Find progress record for this module using UserModuleProgress table
        if module_has_submodules(decoded_module_type):
            # For modules with submodules, get all submodule progress
            progress_records = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=decoded_module_type
            ).all()
            
            if progress_records:
                # Calculate overall progress for the module
                total_progress = sum(record.progress for record in progress_records)
                total_completed = sum(1 for record in progress_records if record.completed)
                avg_progress = total_progress / len(progress_records) if progress_records else 0
                all_completed = all(record.completed for record in progress_records)
                
                # Format submodule progress
                submodule_progress = []
                for record in progress_records:
                    submodule_progress.append({
                        'submodule_name': record.submodule_name,
                        'progress_percentage': record.progress,
                        'is_completed': record.completed,
                        'submodule_id': record.submodule_id
                    })
                
                progress_data = {
                    'module_name': decoded_module_type,
                    'progress_percentage': avg_progress,
                    'is_completed': all_completed,
                    'module_id': module_info['id'],
                    'submodule_progress': submodule_progress,
                    'total_submodules': len(progress_records),
                    'completed_submodules': total_completed
                }
                
                
                return jsonify({
                    'success': True,
                    'progress': progress_data
                }), 200
        else:
            # For modules without submodules, get single progress record
            progress_record = UserModuleProgress.query.filter_by(
                user_id=user_id, 
                module_name=decoded_module_type
            ).first()
            
            if progress_record:
                progress_data = {
                    'module_name': progress_record.module_name,
                    'submodule_name': None,
                    'progress_percentage': progress_record.progress,
                    'is_completed': progress_record.completed,
                    'module_id': progress_record.module_id,
                    'submodule_id': None
                }
                
                
                return jsonify({
                    'success': True,
                    'progress': progress_data
                }), 200
        
        
        # Return success with null progress instead of 404 for better UX
        return jsonify({
            'success': True, 
            'progress': None,
            'message': f'No progress found for module: {decoded_module_type}'
        }), 200
        
    except Exception as e:
        
        import traceback

        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/module/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_all_module_progress(user_id):
    """Get all module progress for a user"""
    try:
        
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get all progress records for this user
        progress_records = UserModuleProgress.query.filter_by(user_id=user_id).all()
        
        # Group progress by module
        module_progress = {}
        for record in progress_records:
            module_name = record.module_name
            if module_name not in module_progress:
                module_progress[module_name] = {
                    'module_name': module_name,
                    'module_id': record.module_id,
                    'has_submodules': module_has_submodules(module_name),
                    'submodules': [],
                    'overall_progress': 0,
                    'overall_completed': False
                }
            
            if module_has_submodules(module_name):
                # Add submodule progress
                module_progress[module_name]['submodules'].append({
                    'submodule_name': record.submodule_name,
                    'progress_percentage': record.progress,
                    'is_completed': record.completed,
                    'submodule_id': record.submodule_id
                })
            else:
                # Single module progress
                module_progress[module_name]['overall_progress'] = record.progress
                module_progress[module_name]['overall_completed'] = record.completed
        
        # Calculate overall progress for modules with submodules
        for module_name, progress_data in module_progress.items():
            if progress_data['has_submodules'] and progress_data['submodules']:
                total_progress = sum(sub['progress_percentage'] for sub in progress_data['submodules'])
                avg_progress = total_progress / len(progress_data['submodules'])
                all_completed = all(sub['is_completed'] for sub in progress_data['submodules'])
                
                progress_data['overall_progress'] = avg_progress
                progress_data['overall_completed'] = all_completed
                progress_data['total_submodules'] = len(progress_data['submodules'])
                progress_data['completed_submodules'] = sum(1 for sub in progress_data['submodules'] if sub['is_completed'])
        
        # Convert to list
        progress_list = list(module_progress.values())
        
        
        return jsonify({
            'success': True,
            'progress_list': progress_list,
            'total_modules': len(progress_list),
            'completed_modules': sum(1 for p in progress_list if p['overall_completed']),
            'modules_with_submodules': [p['module_name'] for p in progress_list if p['has_submodules']],
            'modules_without_submodules': [p['module_name'] for p in progress_list if not p['has_submodules']]
        }), 200
        
    except Exception as e:
        
        import traceback

        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/modules/info', methods=['GET'])
def get_modules_info():
    """Get information about all available modules and their submodules"""
    try:
        # Create enhanced module info
        enhanced_modules = {}
        for module_key, module_info in MODULE_MAPPING.items():
            enhanced_modules[module_key] = {
                'id': module_info['id'],
                'name': module_info['name'],
                'has_submodules': module_info.get('has_submodules', False),
                'submodules': SUBMODULE_MAPPING.get(module_key, {}) if module_info.get('has_submodules', False) else {}
            }
        
        return jsonify({
            'success': True,
            'modules': enhanced_modules,
            'modules_with_submodules': [key for key, info in MODULE_MAPPING.items() if info.get('has_submodules', False)],
            'modules_without_submodules': [key for key, info in MODULE_MAPPING.items() if not info.get('has_submodules', False)]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Child Progress Routes
# ---------------------------
@app.route('/api/child/progress/<int:user_id>', methods=['GET'])
def get_child_progress(user_id):
    """Get overall progress for a child"""
    try:
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Calculate overall progress based on multiple factors
        total_modules = len(MODULE_MAPPING)
        completed_modules = UserModuleProgress.query.filter_by(user_id=user_id, completed=True).count()
        
        # Get task completion rate
        total_tasks = HomeworkSchedule.query.filter_by(user_id=user_id).count()
        completed_tasks = HomeworkSchedule.query.filter_by(user_id=user_id, status='completed').count()
        
        # Get achievements count
        total_achievements = Achievement.query.filter_by(user_id=user_id).count()
        
        # Calculate overall percentage (weighted)
        module_weight = 0.6  # 60% weight for modules
        task_weight = 0.3    # 30% weight for tasks
        achievement_weight = 0.1  # 10% weight for achievements
        
        module_progress = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        task_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        achievement_progress = min(total_achievements * 10, 100)  # Cap at 100%
        
        overall_percentage = (
            module_progress * module_weight +
            task_progress * task_weight +
            achievement_progress * achievement_weight
        )
        
        return jsonify({
            'success': True,
            'progress': {
                'overall_percentage': round(overall_percentage, 1),
                'module_progress': round(module_progress, 1),
                'task_progress': round(task_progress, 1),
                'achievement_progress': round(achievement_progress, 1),
                'completed_modules': completed_modules,
                'total_modules': total_modules,
                'completed_tasks': completed_tasks,
                'total_tasks': total_tasks,
                'total_achievements': total_achievements
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/child/skill-progress/<int:user_id>', methods=['GET'])
def get_child_skill_progress(user_id):
    """Get skill progress for a child"""
    try:
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get module progress for skill calculation
        skill_progress = {}
        
        for module_key, module_info in MODULE_MAPPING.items():
            module_name = module_info['name']
            
            if module_info.get('has_submodules'):
                # For modules with submodules, calculate progress based on submodule completion
                submodules = SUBMODULE_MAPPING.get(module_key, {})
                if submodules:
                    completed_submodules = UserModuleProgress.query.filter_by(
                        user_id=user_id, 
                        module_name=module_key, 
                        completed=True
                    ).count()
                    total_submodules = len(submodules)
                    progress = (completed_submodules / total_submodules * 100) if total_submodules > 0 else 0
                else:
                    progress = 0
            else:
                # For single modules, check if completed
                completed = UserModuleProgress.query.filter_by(
                    user_id=user_id, 
                    module_name=module_key, 
                    completed=True
                ).first()
                progress = 100 if completed else 0
            
            # Map module to skill with appropriate icon
            icon_map = {
                'Math Magic': '🔢',
                'Word Wizard': '📚',
                'Science Explorer': '🔬',
                'Safety Measures': '🛡️',
                'Good Touch Bad Touch': '🤝',
                'Psychometric Assessment': '🧠'
            }
            
            skill_progress[module_name] = {
                'progress': round(progress, 1),
                'icon': icon_map.get(module_name, '🎯')
            }
        
        return jsonify({
            'success': True,
            'skill_progress': skill_progress
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/child/quest-stats/<int:user_id>', methods=['GET'])
@jwt_required()
def get_quest_statistics(user_id):
    """Get detailed quest statistics"""
    try:
        
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get module progress statistics
        module_progress = UserModuleProgress.query.filter_by(user_id=user_id).all()
        completed_modules = [m for m in module_progress if m.completed]
        
        # Get task statistics
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).all()
        completed_tasks = [t for t in tasks if t.status == 'completed']
        
        # Get achievement statistics
        achievements = Achievement.query.filter_by(user_id=user_id).all()
        non_module_achievements = [a for a in achievements if not a.badge_name or not a.badge_name.startswith('module_')]
        
        # Get today's statistics
        today = date.today()
        # Use date_awarded from Achievement for today's achievements
        today_achievements = [a for a in non_module_achievements if a.date_awarded and a.date_awarded.date() == today]
        
        # For module progress and tasks, we'll use a simpler approach
        # Count all completed modules and tasks (not just today's)
        today_module_progress = len(completed_modules)
        today_tasks = len(completed_tasks)
        
        # Get health task statistics
        today_health_tasks = HealthTask.query.filter_by(user_id=user_id, completed=True, date=today).count()
        
        # Get water intake
        water_log = WaterLog.query.filter_by(user_id=user_id, date=today).first()
        water_goal_met = water_log and water_log.count >= 8
        
        # Get login streak
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        logged_in_today = login_streak and login_streak.last_login_date == today
        
        stats = {
            'total_quests': {
                'modules': len(completed_modules),
                'tasks': len(completed_tasks),
                'achievements': len(non_module_achievements),
                'total': len(completed_modules) + len(completed_tasks) + len(non_module_achievements)
            },
            'todays_goals': {
                'modules': today_module_progress,
                'tasks': today_tasks,
                'achievements': len(today_achievements),
                'health_tasks': today_health_tasks,
                'water_goal': 1 if water_goal_met else 0,
                'login_streak': 1 if logged_in_today else 0,
                'total': today_module_progress + today_tasks + len(today_achievements) + today_health_tasks + (1 if water_goal_met else 0) + (1 if logged_in_today else 0)
            },
            'detailed_breakdown': {
                'module_progress': [
                    {
                        'module_name': m.module_name,
                        'submodule_name': m.submodule_name,
                        'progress': m.progress,
                        'completed': m.completed,
                        'module_id': m.module_id,
                        'submodule_id': m.submodule_id
                    } for m in module_progress
                ],
                'tasks': [
                    {
                        'subject': t.subject,
                        'task': t.task,
                        'status': t.status,
                        'created_at': t.created_at.isoformat() if t.created_at else None
                    } for t in tasks
                ],
                'achievements': [
                    {
                        'badge_name': a.badge_name,
                        'description': a.description,
                        'date_awarded': a.date_awarded.isoformat() if a.date_awarded else None
                    } for a in non_module_achievements
                ]
            }
        }
        
        
        
        return jsonify({
            'success': True,
            'quest_statistics': stats
        }), 200
        
    except Exception as e:
        
        import traceback

        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Notification Routes
# ---------------------------
@app.route('/api/notifications/<int:user_id>', methods=['GET'])
@jwt_required()
def get_notifications(user_id):
    """Get all notifications for a user"""
    try:
        # Security check: ensure user can only access their own notifications
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)
        
        # Allow users to access their own notifications
        if user_id == current_user_id:
            # User accessing their own notifications - allowed
            pass
        elif current_user.role == 'parent':
            # Parent accessing child's notifications - check if there's a parent-child relationship
            parent_child_link = ParentChild.query.filter_by(
                parent_id=current_user_id, 
                child_id=user_id
            ).first()
            if not parent_child_link:
                return jsonify({'success': False, 'error': 'Unauthorized access - no parent-child relationship'}), 403
        else:
            # Not own notifications and not a parent - deny access
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        notifications = Notification.query.filter_by(user_id=user_id)\
                                         .order_by(Notification.timestamp.desc()).all()
        
        return jsonify({
            'success': True,
            'notifications': [{
                'id': n.id,
                'content': n.content,
                'is_read': n.is_read,
                'timestamp': n.timestamp.isoformat()
            } for n in notifications]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    

@app.route('/api/notifications/mark-read', methods=['POST'])
@jwt_required()
def mark_notifications_read():
    """Mark notifications as read"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            return jsonify({'success': False, 'error': 'notification_ids are required'}), 400
        
        # Security check: ensure user can only mark their own notifications as read
        notifications = Notification.query.filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == current_user_id
        ).all()
        
        if len(notifications) != len(notification_ids):
            return jsonify({'success': False, 'error': 'Some notifications not found or unauthorized'}), 403
        
        # Update notifications
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'{len(notifications)} notifications marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



def generate_notifications(user_id):
    """Generate notifications for a user based on various conditions"""
    notifications = []
    
    try:
        today = date.today()
        
        # First, delete any existing old notifications for the user
        Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False,
            Notification.timestamp < today
        ).delete()
        
        # 1. Welcome/Login Notification with Streak
        login_streak = LoginStreak.query.filter_by(user_id=user_id).first()
        if login_streak:
            welcome_notif = f"Welcome back! You're on a {login_streak.current_streak}-day learning streak! 🔥"
            notifications.append({
                'content': welcome_notif,
                'is_read': False
            })
        
        # 2. Stars Earned Notification
        child_stats = calculate_total_stars(user_id)
        if child_stats > 0:
            stars_notif = f"⭐ You've earned {child_stats} stars! Keep up the great work!"
            notifications.append({
                'content': stars_notif,
                'is_read': False
            })
        
        # 3. Pending Tasks Notification
        pending_tasks = HomeworkSchedule.query.filter_by(
            user_id=user_id, 
            status='pending'
        ).filter(HomeworkSchedule.due_date >= today).all()
        
        if pending_tasks:
            # Create a separate notification for each pending task
            for task in pending_tasks:
                tasks_notif = f"🎯 Pending Task: '{task.task}' is due on {task.due_date.strftime('%b %d')}"
                notifications.append({
                    'content': tasks_notif,
                    'is_read': False
                })
        
        # Optional: Add a summary notification
        if len(pending_tasks) > 1:
            summary_notif = f"🎯 You have {len(pending_tasks)} pending tasks to complete!"
            notifications.append({
                'content': summary_notif,
                'is_read': False
            })
        
        # 4. Water Intake Reminder
        water_log = WaterLog.query.filter_by(user_id=user_id, date=today).first()
        
        # Only create water reminder if NO water log exists or water intake is less than recommended
        if not water_log or (water_log and water_log.count < 8):
            # Check if user has logged ANY water today
            if not water_log or water_log.count == 0:
                water_notif = "💧 Don't forget to drink water today!"
                notifications.append({
                    'content': water_notif,
                    'is_read': False
                })
            elif water_log.count < 8:
                remaining_glasses = 8 - water_log.count
                water_notif = f"💧 You've had {water_log.count} glasses. Drink {remaining_glasses} more to stay hydrated!"
                notifications.append({
                    'content': water_notif,
                    'is_read': False
                })
        
        # 5. Savings Goal Progress
        savings_goals = SavingGoal.query.filter_by(user_id=user_id).all()
        for goal in savings_goals:
            # Ensure target amount is not zero and goal is not yet completed
            if goal.target_amount > 0 and goal.current_amount < goal.target_amount:
                goal_notif = f"💰 Remember your savings goal: '{goal.label}'"
                notifications.append({
                    'content': goal_notif,
                    'is_read': False
                })
        
        # Save notifications to database
        for notif_data in notifications:
            notification = Notification(
                user_id=user_id,
                content=notif_data['content'],
                is_read=notif_data['is_read']
            )
            db.session.add(notification)
        
        db.session.commit()
        
        return len(notifications)
    
    except Exception as e:
        
        db.session.rollback()
        return 0

# ---------------------------
# Doodling/Drawing Routes
# ---------------------------

@app.route('/api/drawings/save', methods=['POST'])
def save_drawing():
    """Save a drawing to both local storage and database"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)  # Default to user 1 for testing
        
        # For now, allow any user_id for testing (remove security check)
        image_data = data.get('image_data')
        description = data.get('description', 'Untitled Drawing')
        time_taken = data.get('time_taken', 0)
        ref_image_path = data.get('ref_image_path')
        ref_image_title = data.get('ref_image_title')
        
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        
        # Create drawings directory if it doesn't exist
        drawings_dir = os.path.join('static', 'drawings')
        os.makedirs(drawings_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"drawing_{user_id}_{timestamp}.png"
        file_path = os.path.join(drawings_dir, filename)
        
        # Save image to local file system
        try:
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to save image file: {str(e)}'}), 500
        
        # Save to database
        try:
            user = db.session.get(User, user_id)
            if not user:
                user = User(
                    username=f"user_{user_id}",
                    email=f"user{user_id}@example.com",
                    password_hash="default_hash",
                    role="child"
                )
                db.session.add(user)
                db.session.flush()
                user_id = user.id
            
            doodle_session = DoodleSession(
                user_id=user_id,
                description=description,
                ref_image_path=ref_image_path,
                ref_image_title=ref_image_title,
                save_image_path=file_path,
                is_completed=True,
                timestamp=datetime.now(UTC),
                time_taken=time_taken
            )
            
            db.session.add(doodle_session)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Drawing saved successfully!',
                'drawing_id': doodle_session.id,
                'file_path': file_path,
                'file_size': len(image_bytes),
                'time_taken': time_taken,
                'ref_image_title': ref_image_title
            }), 200
            
        except Exception as e:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
            
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Failed to save to database: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Update the existing get_user_drawings function:
@app.route('/api/drawings/<int:user_id>', methods=['GET'])
# @jwt_required()
def get_user_drawings(user_id):
    """Get all drawings for a specific user"""
    try:
        drawings = DoodleSession.query.filter_by(user_id=user_id).order_by(DoodleSession.timestamp.desc()).all()
        
        drawings_data = []
        for drawing in drawings:
            file_exists = os.path.exists(drawing.save_image_path) if drawing.save_image_path else False
            
            drawings_data.append({
                'id': drawing.id,
                'description': drawing.description,
                'timestamp': drawing.timestamp.isoformat(),
                'file_path': drawing.save_image_path,
                'file_exists': file_exists,
                'is_completed': drawing.is_completed,
                'time_taken': drawing.time_taken,
                'ref_image_path': drawing.ref_image_path,
                'ref_image_title': drawing.ref_image_title
            })
        
        return jsonify({
            'success': True,
            'drawings': drawings_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drawings/start-session', methods=['POST'])
def start_drawing_session():
    """Start a new drawing session with timer"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        ref_image_path = data.get('ref_image_path')
        ref_image_title = data.get('ref_image_title')
        
        # Create a new drawing session
        doodle_session = DoodleSession(
            user_id=user_id,
            ref_image_path=ref_image_path,
            ref_image_title=ref_image_title,
            start_time=datetime.now(UTC),
            is_completed=False
        )
        
        db.session.add(doodle_session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session_id': doodle_session.id,
            'start_time': doodle_session.start_time.isoformat(),
            'ref_image_title': ref_image_title
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/drawings/image/<int:drawing_id>', methods=['GET'])
def get_drawing_image(drawing_id):
    """Get a specific drawing image"""
    try:
        drawing = db.session.get(DoodleSession, drawing_id)
        if not drawing:
            return jsonify({'success': False, 'error': 'Drawing not found'}), 404
        
        if not drawing.save_image_path or not os.path.exists(drawing.save_image_path):
            return jsonify({'success': False, 'error': 'Image file not found'}), 404
        
        # Read and encode image as base64
        with open(drawing.save_image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image_data': f"data:image/png;base64,{image_data}",
            'description': drawing.description,
            'timestamp': drawing.timestamp.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drawings/delete/<int:drawing_id>', methods=['DELETE'])
def delete_drawing(drawing_id):
    """Delete a drawing from both database and file system"""
    try:
        drawing = db.session.get(DoodleSession, drawing_id)
        if not drawing:
            return jsonify({'success': False, 'error': 'Drawing not found'}), 404
        
        # Delete file if it exists
        if drawing.save_image_path and os.path.exists(drawing.save_image_path):
            try:
                os.remove(drawing.save_image_path)
            except Exception as e:
                pass  # Continue even if file deletion fails
        
        # Delete from database
        db.session.delete(drawing)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Drawing deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

        
@app.route('/api/drawings/reference-images', methods=['GET'])
def get_reference_images():
    """Get available reference images for drawing inspiration"""
    try:
        # Create reference images directory if it doesn't exist
        ref_images_dir = os.path.join('static', 'reference_images')
        os.makedirs(ref_images_dir, exist_ok=True)
        
        # Get all image files from reference directory
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif']
        reference_images = []
        
        for extension in image_extensions:
            files = glob.glob(os.path.join(ref_images_dir, extension))
            reference_images.extend(files)
        
        # If no images found, create some default ones
        if not reference_images:
            reference_images = create_default_reference_images(ref_images_dir)
        
        # Convert to relative paths and create response
        images_data = []
        for img_path in reference_images:
            filename = os.path.basename(img_path)
            title = os.path.splitext(filename)[0].replace('_', ' ').title()
            
            images_data.append({
                'path': img_path.replace('\\', '/'),  # Normalize path for web
                'filename': filename,
                'title': title,
                'url': f"/static/reference_images/{filename}"
            })
        
        return jsonify({
            'success': True,
            'images': images_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/drawings/random-reference', methods=['GET'])
def get_random_reference_image():
    """Get a random reference image for inspiration"""
    try:
        ref_images_dir = os.path.join('static', 'reference_images')
        os.makedirs(ref_images_dir, exist_ok=True)
        
        # Get all image files
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif']
        reference_images = []
        
        for extension in image_extensions:
            files = glob.glob(os.path.join(ref_images_dir, extension))
            reference_images.extend(files)
        
        if not reference_images:
            reference_images = create_default_reference_images(ref_images_dir)
        
        if reference_images:
            # Pick a random image
            selected_image = random.choice(reference_images)
            filename = os.path.basename(selected_image)
            title = os.path.splitext(filename)[0].replace('_', ' ').title()
            
            return jsonify({
                'success': True,
                'reference': {
                    'path': selected_image.replace('\\', '/'),
                    'filename': filename,
                    'title': title,
                    'url': f"/static/reference_images/{filename}"
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No reference images available'
            }), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def create_default_reference_images(ref_images_dir):
    """Create some default reference image placeholders"""
    try:
        # Create simple colored placeholder images
        from PIL import Image, ImageDraw, ImageFont
        
        default_images = [
            {'name': 'house.png', 'color': '#FFB6C1', 'text': '🏠 House'},
            {'name': 'tree.png', 'color': '#90EE90', 'text': '🌳 Tree'},
            {'name': 'sun.png', 'color': '#FFD700', 'text': '☀️ Sun'},
            {'name': 'flower.png', 'color': '#FF69B4', 'text': '🌸 Flower'},
            {'name': 'cat.png', 'color': '#DDA0DD', 'text': '🐱 Cat'},
            {'name': 'car.png', 'color': '#87CEEB', 'text': '🚗 Car'},
            {'name': 'rainbow.png', 'color': '#FF6347', 'text': '🌈 Rainbow'},
            {'name': 'butterfly.png', 'color': '#FFA07A', 'text': '🦋 Butterfly'}
        ]
        
        created_files = []
        
        for img_info in default_images:
            # Create a simple colored image with text
            img = Image.new('RGB', (300, 300), color=img_info['color'])
            draw = ImageDraw.Draw(img)
            
            # Add text in center
            try:
                # Try to use a default font, fallback to basic if not available
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            text = img_info['text']
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (300 - text_width) // 2
            y = (300 - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # Save the image
            file_path = os.path.join(ref_images_dir, img_info['name'])
            img.save(file_path)
            created_files.append(file_path)
        
        return created_files
        
    except ImportError:
        # If PIL is not available, create empty files as placeholders
        default_files = [
            'house.png', 'tree.png', 'sun.png', 'flower.png',
            'cat.png', 'car.png', 'rainbow.png', 'butterfly.png'
        ]
        
        created_files = []
        for filename in default_files:
            file_path = os.path.join(ref_images_dir, filename)
            # Create empty file
            with open(file_path, 'w') as f:
                f.write('')
            created_files.append(file_path)
        
        return created_files
    except Exception:
        return []

# Add a route to serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return app.send_static_file(filename)

# ---------------------------
# Story Builder API Endpoints
# ---------------------------

@app.route('/api/stories/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_stories(user_id):
    """Get all stories for a specific user"""
    try:
        # Ensure user can only access their own stories
        current_user_id = int(get_jwt_identity())
        if current_user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only access your own stories'}), 403
        
        # Get all stories for the user, ordered by creation date (newest first)
        stories = Story.query.filter_by(user_id=user_id).order_by(Story.created_at.desc()).all()
        
        stories_data = []
        for story in stories:
            stories_data.append({
                'id': story.id,
                'title': story.title,
                'content': story.content,
                'prompt_used': story.prompt_used,
                'created_at': story.created_at.isoformat(),
                'updated_at': story.updated_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'stories': stories_data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stories', methods=['POST'])
@jwt_required()
def save_story():
    """Save a new story"""
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            return jsonify({'success': False, 'error': 'Title and content are required'}), 400
        
        # Create new story
        new_story = Story(
            user_id=user_id,
            title=data['title'].strip(),
            content=data['content'].strip(),
            prompt_used=data.get('prompt_used', '').strip() if data.get('prompt_used') else None
        )
        
        db.session.add(new_story)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Story saved successfully!',
            'story': {
                'id': new_story.id,
                'title': new_story.title,
                'content': new_story.content,
                'prompt_used': new_story.prompt_used,
                'created_at': new_story.created_at.isoformat(),
                'updated_at': new_story.updated_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stories/<int:story_id>', methods=['PUT'])
@jwt_required()
def update_story(story_id):
    """Update an existing story"""
    try:
        data = request.get_json()
        user_id = int(get_jwt_identity())
        
        # Find the story
        story = Story.query.filter_by(id=story_id, user_id=user_id).first()
        
        if not story:
            return jsonify({'success': False, 'error': 'Story not found or unauthorized'}), 404
        
        # Validate required fields
        if not data.get('title') or not data.get('content'):
            return jsonify({'success': False, 'error': 'Title and content are required'}), 400
        
        # Update story
        story.title = data['title'].strip()
        story.content = data['content'].strip()
        if 'prompt_used' in data:
            story.prompt_used = data['prompt_used'].strip() if data['prompt_used'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Story updated successfully!',
            'story': {
                'id': story.id,
                'title': story.title,
                'content': story.content,
                'prompt_used': story.prompt_used,
                'created_at': story.created_at.isoformat(),
                'updated_at': story.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stories/<int:story_id>', methods=['DELETE'])
@jwt_required()
def delete_story(story_id):
    """Delete a story"""
    try:
        user_id = int(get_jwt_identity())
        
        # Find the story
        story = Story.query.filter_by(id=story_id, user_id=user_id).first()
        
        if not story:
            return jsonify({'success': False, 'error': 'Story not found or unauthorized'}), 404
        
        db.session.delete(story)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Story deleted successfully!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stories/<int:story_id>', methods=['GET'])
@jwt_required()
def get_story(story_id):
    """Get a specific story"""
    try:
        user_id = int(get_jwt_identity())
        
        # Find the story
        story = Story.query.filter_by(id=story_id, user_id=user_id).first()
        
        if not story:
            return jsonify({'success': False, 'error': 'Story not found or unauthorized'}), 404
        
        return jsonify({
            'success': True,
            'story': {
                'id': story.id,
                'title': story.title,
                'content': story.content,
                'prompt_used': story.prompt_used,
                'created_at': story.created_at.isoformat(),
                'updated_at': story.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Error Handlers
# ------------------------# ---
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# ---------------------------
# Application Initialization
# ---------------------------

def initialize_database():
    """Initialize the database and create default users"""
    try:
        # Ensure instance directory exists
        instance_dir = app.config.get('INSTANCE_DIR')
        if instance_dir and not os.path.exists(instance_dir):
            os.makedirs(instance_dir, exist_ok=True)
            
        with app.app_context():
            # Create all database tables (won't recreate if they exist)
            db.create_all()
            
            # Create default admin user
            create_default_admin()
            
    except Exception as e:
        
        import traceback

        raise e

# ---------------------------
# Simple Activity Achievement Route
# ---------------------------

@app.route('/api/activity/complete', methods=['POST'])
def complete_activity():
    """Simple activity completion - creates an achievement"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        activity_name = data.get('activity_name')  # 'Memory Game', 'Music Player', etc.
        
        if not user_id or not activity_name:
            return jsonify({'success': False, 'error': 'user_id and activity_name are required'}), 400
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Create achievement for the activity
        achievement = Achievement(
            user_id=user_id,
            badge_name=f"{activity_name} Master",
            description=f"Completed {activity_name} successfully!"
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        # Calculate stars based on activity type
        stars_earned = 10  # Default
        if activity_name == 'Memory Game':
            stars_earned = 5  # Memory Game gives 5 stars
        
        
        
        return jsonify({
            'success': True,
            'message': f'{activity_name} completed successfully!',
            'stars_earned': stars_earned,
            'achievement_id': achievement.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        
        return jsonify({'success': False, 'error': str(e)}), 500

# Achievement Management Routes
@app.route('/api/achievements/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_achievements(user_id):
    """Get all achievements for a user"""
    try:
        
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get all achievements for the user
        achievements = Achievement.query.filter_by(user_id=user_id).order_by(Achievement.date_awarded.desc()).all()
        
        achievement_list = []
        for achievement in achievements:
            # Skip module progress records (they're stored as achievements but aren't user-facing achievements)
            if achievement.badge_name and achievement.badge_name.startswith('module_'):
                continue
                
            achievement_data = {
                'id': achievement.id,
                'badge# _name': achievement.badge_name,
                'description': achievement.description,
                'date_awarded': achievement.date_awarded.isoformat() if achievement.date_awarded else None,
                'badge_type': getattr(achievement, 'badge_type', 'general'),
                'icon': getattr(achievement, 'icon', '🏆')
            }
                
            achievement_list.append(achievement_data)
        
        
        
        return jsonify({
            'success': True,
            'achievements': achievement_list
        }), 200
        
    except Exception as e:
        
        import traceback

        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/achievement', methods=['POST'])
def create_achievement():
    """Create a new achievement for a user"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        badge_name = data.get('badge_name')
        description = data.get('description', '')
        badge_type = data.get('badge_type', 'general')
        icon = data.get('icon', '🏆')
        
        
        
        if not user_id or not badge_name:
            return jsonify({'success': False, 'error': 'user_id and badge_name are required'}), 400
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Create the achievement
        achievement = Achievement(
            user_id=user_id,
            badge_name=badge_name,
            description=description,
            date_awarded=datetime.now(UTC)
        )
        
        # Add additional fields if the Achievement model supports them
        if hasattr(Achievement, 'badge_type'):
            achievement.badge_type = badge_type
        if hasattr(Achievement, 'icon'):
            achievement.icon = icon
        
        db.session.add(achievement)
        db.session.commit()
        
        
        
        return jsonify({
            'success': True,
            'message': 'Achievement created successfully',
            'achievement': {
                'id': achievement.id,
                'badge_name': achievement.badge_name,
                'description': achievement.description,
                'date_awarded': achievement.date_awarded.isoformat(),
                'badge_type': badge_type,
                'icon': icon
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        
        import traceback

        return jsonify({'success': False, 'error': str(e)}), 500

# Add this function near other notification-related routes

# Add this method near other notification-related routes
def clear_user_notifications(user_id):
    """Clear all notifications for a specific user"""
    try:
        # Delete all existing notifications for the user
        Notification.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        
        return True
    except Exception as e:
        db.session.rollback()
        
        return False

# Modify the logout route to clear notifications
@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endp# oint that clears user notifications"""
    try:
        current_user_id = get_jwt_identity()
        
        # Clear user notifications
        clear_user_notifications(current_user_id)
        
        # Perform any additional logout logic
        # For example, you might want to invalidate the token
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/api/admin/dashboard-stats', methods=['GET'])
def get_admin_dashboard_stats():
    try:
        today = date.today()

        # Count users by role
        total_users = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        parent_count = User.query.filter_by(role='parent').count()
        child_count = User.query.filter_by(role='child').count()
        teacher_count = User.query.filter_by(role='teacher').count()
        
        # Count active users today (based on login history)
        active_today = LoginHistory.query.filter_by(login_date=today).distinct(LoginHistory.user_id).count()
        
        # Active in last hour (simplified - use a subset of active today)
        active_last_hour = max(0, active_today - 1)
        
        # Calculate average screen time (in minutes)
        average_screen_time = 0
        screen_time_records = ScreenTime.query.filter_by(date=today).all()
        if screen_time_records:
            total_hours = sum(record.hours or 0 for record in screen_time_records)
            average_screen_time = round((total_hours / len(screen_time_records)) * 60)  # Convert to minutes
        
        # If no data for today, get average from recent week
        if average_screen_time == 0:
            from datetime import timedelta
            week_ago = today - timedelta(days=7)
            recent_screen_time = ScreenTime.query.filter(ScreenTime.date >= week_ago).all()
            if recent_screen_time:
                total_hours = sum(record.hours or 0 for record in recent_screen_time)
                average_screen_time = round((total_hours / len(recent_screen_time)) * 60)  # Convert to minutes

        stats = {
            "total_users": total_users,
            "admin_count": admin_count,
            "parent_count": parent_count,
            "child_count": child_count,
            "teacher_count": teacher_count,
            "active_today": active_today,
            "active_last_hour": active_last_hour,
            "average_screen_time": average_screen_time,
            "chat_sessions": ChatSession.query.count(),
            "achievements": Achievement.query.count(),
            "completed_tasks": HomeworkSchedule.query.filter_by(status='completed').count()
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Comprehensive Analytics Endpoint
@app.route('/api/admin/analytics', methods=['GET'])
def get_comprehensive_analytics():
    """Get detailed analytics data for admin dashboard"""
    try:
        today = date.today()
        from datetime import timedelta
        
        # Basic user statistics
        total_users = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        parent_count = User.query.filter_by(role='parent').count()
        child_count = User.query.filter_by(role='child').count()
        teacher_count = User.query.filter_by(role='teacher').count()
        
        # Activity statistics
        total_chat_sessions = ChatSession.query.count()
        total_achievements = Achievement.query.count()
        
        # Screen time analysis
        avg_screen_time = 0
        screen_time_records = ScreenTime.query.filter_by(date=today).all()
        if screen_time_records:
            total_hours = sum(record.hours or 0 for record in screen_time_records)
            avg_screen_time = round((total_hours / len(screen_time_records)) * 60)
        
        # Weekly activity data - fetch actual user activity from database using LoginHistory
        weekly_activity = []
        for i in range(7):
            target_date = today - timedelta(days=6-i)
            # Get actual users who logged in on this date using LoginHistory table
            active_users = LoginHistory.query.filter_by(login_date=target_date).distinct(LoginHistory.user_id).count()
            weekly_activity.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'day': target_date.strftime('%a'),
                'active_users': active_users  # Use actual count from login history
            })
        
        # Task completion statistics - fetch actual data from database
        completed_tasks = HomeworkSchedule.query.filter_by(status='completed').count()
        
        # Health and wellness data
        total_health_tasks = HealthTask.query.count()
        water_logs_today = WaterLog.query.filter_by(date=today).count()
        
        # Doodling and creativity
        total_doodle_sessions = DoodleSession.query.count()
        
        # Financial education
        total_transactions = Transaction.query.count()
        total_saving_goals = SavingGoal.query.count()
        
        # Demographics data from child profiles
        child_profiles = ChildProfile.query.all()
        age_distribution = {}
        gender_distribution = {}
        
        for profile in child_profiles:
            if profile.date_of_birth:
                # Calculate age
                age = today.year - profile.date_of_birth.year
                if today.month < profile.date_of_birth.month or (today.month == profile.date_of_birth.month and today.day < profile.date_of_birth.day):
                    age -= 1
                
                # Group by age ranges
                if age < 6:
                    age_group = "5 and under"
                elif age < 9:
                    age_group = "6-8 years"
                elif age < 12:
                    age_group = "9-11 years"
                elif age < 15:
                    age_group = "12-14 years"
                else:
                    age_group = "15+ years"
                
                age_distribution[age_group] = age_distribution.get(age_group, 0) + 1
            
            if profile.gender:
                gender_distribution[profile.gender] = gender_distribution.get(profile.gender, 0) + 1
        
        analytics_data = {
            "user_statistics": {
                "total_users": total_users,
                "admin_count": admin_count,
                "parent_count": parent_count,
                "child_count": child_count,
                "teacher_count": teacher_count
            },
            "activity_data": {
                "total_chat_sessions": total_chat_sessions,
                "completed_tasks": completed_tasks,
                "total_achievements": total_achievements,
                "weekly_activity": weekly_activity
            },
            "screen_time": {
                "average_minutes": avg_screen_time,
                "total_records": len(screen_time_records)
            },
            "health_wellness": {
                "total_health_tasks": total_health_tasks,
                "water_logs_today": water_logs_today
            },
            "creativity": {
                "total_doodle_sessions": total_doodle_sessions
            },
            "financial": {
                "total_transactions": total_transactions,
                "total_saving_goals": total_saving_goals
            },
            "demographics": {
                "age_distribution": age_distribution,
                "gender_distribution": gender_distribution,
                "total_profiles": len(child_profiles)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return jsonify(analytics_data), 200
        
    except Exception as e:
        print(f"Analytics error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# User Activity Analytics Endpoint
@app.route('/api/admin/user-activity', methods=['GET'])
def get_user_activity_analytics():
    """Get detailed user activity analytics for admin dashboard"""
    try:
        today = date.today()
        from datetime import timedelta
        
        # Get activity data for the last 7 days
        weekly_activity = []
        for i in range(7):
            target_date = today - timedelta(days=6-i)
            
            # Count users who logged in on this date using LoginHistory
            login_activity = LoginHistory.query.filter_by(login_date=target_date).distinct(LoginHistory.user_id).count()
            
            # Count tasks completed on this date
            tasks_completed = HomeworkSchedule.query.filter(
                HomeworkSchedule.status == 'completed',
                db.func.date(HomeworkSchedule.updated_at) == target_date
            ).count()
            
            # Count chat sessions created on this date
            chat_activity = ChatSession.query.filter(
                db.func.date(ChatSession.created_at) == target_date
            ).count()
            
            # Count achievements awarded on this date
            achievements_earned = Achievement.query.filter(
                db.func.date(Achievement.date_awarded) == target_date
            ).count()
            
            # Count health tasks completed on this date
            health_activity = HealthTask.query.filter(
                HealthTask.completed == True,
                HealthTask.date == target_date
            ).count()
            
            # Total activity score (weighted combination)
            total_activity = (
                login_activity * 1 +      # Login = 1 point
                tasks_completed * 2 +     # Task completion = 2 points
                chat_activity * 1 +       # Chat session = 1 point
                achievements_earned * 3 + # Achievement = 3 points
                health_activity * 1       # Health task = 1 point
            )
            
            weekly_activity.append({
                'date': target_date.strftime('%Y-%m-%d'),
                'day': target_date.strftime('%a'),
                'active_users': login_activity,
                'tasks_completed': tasks_completed,
                'chat_sessions': chat_activity,
                'achievements_earned': achievements_earned,
                'health_tasks': health_activity,
                'total_activity_score': total_activity
            })
        
        # Get overall activity statistics using LoginHistory
        total_users = User.query.count()
        active_users_today = LoginHistory.query.filter_by(login_date=today).distinct(LoginHistory.user_id).count()
        active_users_week = LoginHistory.query.filter(
            LoginHistory.login_date >= today - timedelta(days=7)
        ).distinct(LoginHistory.user_id).count()
        
        # Get activity by user role using LoginHistory
        role_activity = {}
        for role in ['child', 'parent', 'teacher', 'admin']:
            users_with_role = User.query.filter_by(role=role).count()
            active_users_with_role = db.session.query(LoginHistory).join(User).filter(
                User.role == role,
                LoginHistory.login_date >= today - timedelta(days=7)
            ).distinct(LoginHistory.user_id).count()
            
            role_activity[role] = {
                'total_users': users_with_role,
                'active_users': active_users_with_role,
                'activity_rate': round((active_users_with_role / users_with_role * 100) if users_with_role > 0 else 0, 1)
            }
        
        activity_data = {
            'weekly_activity': weekly_activity,
            'overall_stats': {
                'total_users': total_users,
                'active_today': active_users_today,
                'active_this_week': active_users_week,
                'activity_rate_today': round((active_users_today / total_users * 100) if total_users > 0 else 0, 1),
                'activity_rate_week': round((active_users_week / total_users * 100) if total_users > 0 else 0, 1)
            },
            'role_activity': role_activity,
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(activity_data), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Task Statistics Endpoint
@app.route('/api/admin/task-stats', methods=['GET'])
def get_task_statistics():
    """Get task completion statistics for admin dashboard"""
    try:
        # Get total tasks and completed tasks
        total_tasks = HomeworkSchedule.query.count()
        completed_tasks = HomeworkSchedule.query.filter_by(status='completed').count()
        pending_tasks = HomeworkSchedule.query.filter_by(status='pending').count()
        in_progress_tasks = HomeworkSchedule.query.filter_by(status='in-progress').count()
        
        # Calculate completion rate
        completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        
        # Get tasks by subject
        tasks_by_subject = db.session.query(
            HomeworkSchedule.subject,
            db.func.count(HomeworkSchedule.id).label('total'),
            db.func.sum(db.case([(HomeworkSchedule.status == 'completed', 1)], else_=0)).label('completed')
        ).group_by(HomeworkSchedule.subject).all()
        
        subject_stats = []
        for subject, total, completed in tasks_by_subject:
            subject_stats.append({
                'subject': subject or 'Other',
                'total': total,
                'completed': completed,
                'completion_rate': round((completed / total * 100) if total > 0 else 0, 1)
            })
        
        # Get recent task activity (last 7 days)
        from datetime import timedelta
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        recent_completed = HomeworkSchedule.query.filter(
            HomeworkSchedule.status == 'completed',
            HomeworkSchedule.updated_at >= week_ago
        ).count()
        
        stats = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'completion_rate': completion_rate,
            'recent_completed': recent_completed,
            'subject_statistics': subject_stats,
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Migration endpoint to populate LoginHistory from existing LoginStreak data
@app.route('/api/admin/migrate-login-history', methods=['POST'])
def migrate_login_history():
    """Migrate existing LoginStreak data to LoginHistory for historical analytics"""
    try:
        # Get all users with login streaks
        login_streaks = LoginStreak.query.all()
        migrated_count = 0
        
        for streak in login_streaks:
            # Check if this user already has login history for their last login date
            existing_history = LoginHistory.query.filter_by(
                user_id=streak.user_id,
                login_date=streak.last_login_date
            ).first()
            
            if not existing_history and streak.last_login_date:
                # Create login history record
                login_history = LoginHistory(
                    user_id=streak.user_id,
                    login_date=streak.last_login_date,
                    login_time=datetime.now(UTC),  # Use current time as approximation
                    ip_address=None,
                    user_agent=None
                )
                db.session.add(login_history)
                migrated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Migrated {migrated_count} login records to history table',
            'migrated_count': migrated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Child Profile Endpoints
@app.route('/api/child-profile/<int:user_id>', methods=['GET'])
def get_child_profile(user_id):
    """Get child profile by user ID"""
    try:
        profile = ChildProfile.query.filter_by(user_id=user_id).first()
        
        if profile:
            return jsonify({
                'success': True,
                'profile': {
                    'id': profile.id,
                    'user_id': profile.user_id,
                    'grade_level': profile.grade_level,
                    'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                    'gender': profile.gender,
                    'interests': profile.interests,
                    'avatar_url': profile.avatar_url
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/child-profile', methods=['POST'])
def create_child_profile():
    """Create or update child profile"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'grade_level', 'date_of_birth', 'gender', 'interests']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Check if profile already exists
        existing_profile = ChildProfile.query.filter_by(user_id=data['user_id']).first()
        
        if existing_profile:
            # Update existing profile
            existing_profile.grade_level = data['grade_level']
            existing_profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            existing_profile.gender = data['gender']
            existing_profile.interests = data['interests']
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'profile_id': existing_profile.id
            })
        else:
            # Create new profile
            new_profile = ChildProfile(
                user_id=data['user_id'],
                grade_level=data['grade_level'],
                date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
                gender=data['gender'],
                interests=data['interests']
            )
            
            db.session.add(new_profile)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Profile created successfully',
                'profile_id': new_profile.id
            })
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/child-profile/<int:user_id>', methods=['PUT'])
def update_child_profile(user_id):
    """Update child profile by user ID"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['grade_level', 'date_of_birth', 'gender', 'interests']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Find existing profile
        profile = ChildProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Update profile
        profile.grade_level = data['grade_level']
        profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        profile.gender = data['gender']
        profile.interests = data['interests']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile_id': profile.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Demographics Analytics Endpoint
@app.route('/api/admin/demographics', methods=['GET'])
def get_demographics_analytics():
    """Get detailed demographics data for admin dashboard"""
    try:
        today = date.today()
        
        # Get all child profiles
        child_profiles = ChildProfile.query.all()
        
        # Initialize distribution objects
        age_distribution = {}
        gender_distribution = {}
        grade_distribution = {}
        
        # Process each profile
        for profile in child_profiles:
            # Age distribution
            if profile.date_of_birth:
                age = today.year - profile.date_of_birth.year
                if today.month < profile.date_of_birth.month or (today.month == profile.date_of_birth.month and today.day < profile.date_of_birth.day):
                    age -= 1
                
                # Group by age ranges
                if age < 6:
                    age_group = "5 and under"
                elif age < 9:
                    age_group = "6-8 years"
                elif age < 12:
                    age_group = "9-11 years"
                elif age < 15:
                    age_group = "12-14 years"
                else:
                    age_group = "15+ years"
                
                age_distribution[age_group] = age_distribution.get(age_group, 0) + 1
            
            # Gender distribution
            if profile.gender:
                gender_distribution[profile.gender] = gender_distribution.get(profile.gender, 0) + 1
            
            # Grade distribution
            if profile.grade_level:
                grade_distribution[f"Grade {profile.grade_level}"] = grade_distribution.get(f"Grade {profile.grade_level}", 0) + 1
        
        # Calculate percentages
        total_profiles = len(child_profiles)
        
        demographics_data = {
            "total_profiles": total_profiles,
            "age_distribution": age_distribution,
            "gender_distribution": gender_distribution,
            "grade_distribution": grade_distribution,
            "age_percentages": {k: round((v / total_profiles * 100), 1) for k, v in age_distribution.items()} if total_profiles > 0 else {},
            "gender_percentages": {k: round((v / total_profiles * 100), 1) for k, v in gender_distribution.items()} if total_profiles > 0 else {},
            "grade_percentages": {k: round((v / total_profiles * 100), 1) for k, v in grade_distribution.items()} if total_profiles > 0 else {},
            "generated_at": datetime.now().isoformat()
        }
        
        return jsonify(demographics_data), 200
        
    except Exception as e:
        print(f"Demographics analytics error: {str(e)}")
        return jsonify({"error": str(e)}), 500

# System Health Check Endpoint
@app.route('/api/health', methods=['GET'])
def system_health_check():
    """System health check endpoint"""
    try:
        # Basic database connectivity check
        user_count = User.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'users': user_count,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Admin User Management Endpoints
@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users for admin dashboard"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if user is admin
        if not current_user or current_user.role != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        users = User.query.all()
        users_data = []
        
        for user in users:
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
            }
            
            # Add profile status for children
            if user.role == 'child':
                child_profile = ChildProfile.query.filter_by(user_id=user.id).first()
                user_data['profile_complete'] = bool(child_profile)
            else:
                user_data['profile_complete'] = True
                
            users_data.append(user_data)
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total': len(users_data)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['POST'])
@jwt_required()
def create_user_admin():
    """Create a new user - admin only (simplified version without complex relationships)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if user is admin
        if not current_user or current_user.role != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        # Validate required fields
        if not username or not password or not role:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Validate role
        valid_roles = ['parent', 'child', 'teacher']
        if role not in valid_roles:
            return jsonify({'success': False, 'error': 'Invalid role'}), 400
        
        # Validate email format if provided
        if email and not EMAIL_REGEX.match(email):
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Check for existing username
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'error': 'Username already exists'}), 409
        
        # Check for existing email if provided
        if email and User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already exists'}), 409
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User "{username}" created successfully',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create user error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user - admin only"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if user is admin
        if not current_user or current_user.role != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
            
        # Prevent admin from deleting themselves
        if current_user_id == user_id:
            return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
        
        # Find the user to delete
        user_to_delete = User.query.get(user_id)
        if not user_to_delete:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Store username for response
        username = user_to_delete.username
        
        # Delete related data first (to maintain referential integrity)
        try:
            # Delete child profile if exists
            if user_to_delete.role == 'child':
                ChildProfile.query.filter_by(user_id=user_id).delete()
                
            # Delete parent-child relationships
            ParentChild.query.filter(
                (ParentChild.parent_id == user_id) | (ParentChild.child_id == user_id)
            ).delete()
            
            # Delete user's achievements
            Achievement.query.filter_by(user_id=user_id).delete()
            
            # Delete user's module progress
            UserModuleProgress.query.filter_by(user_id=user_id).delete()
            
            # Delete user's tasks
            HomeworkSchedule.query.filter_by(user_id=user_id).delete()
            
            # Delete user's health data
            HealthTask.query.filter_by(user_id=user_id).delete()
            HealthStreak.query.filter_by(user_id=user_id).delete()
            WaterLog.query.filter_by(user_id=user_id).delete()
            
            # Delete user's streaks and logs
            LoginStreak.query.filter_by(user_id=user_id).delete()
            ScreenTime.query.filter_by(user_id=user_id).delete()
            
            # Delete user's notifications
            Notification.query.filter_by(user_id=user_id).delete()
            
            # Delete chat sessions and their interactions
            chat_sessions = ChatSession.query.filter_by(user_id=user_id).all()
            for session in chat_sessions:
                # Delete LLM interactions for this session
                LLMInteractions.query.filter_by(session_id=session.id).delete()
            # Delete the chat sessions
            ChatSession.query.filter_by(user_id=user_id).delete()
            
            # Delete savings goals and transactions
            SavingGoal.query.filter_by(user_id=user_id).delete()
            Transaction.query.filter_by(user_id=user_id).delete()
            
            # Delete pomodoro sessions
            PomodoroSession.query.filter_by(user_id=user_id).delete()
            
            # Delete psychometric test results (uses child_id)
            PsychometricTestResult.query.filter_by(child_id=user_id).delete()
            
            # Delete doodle sessions
            DoodleSession.query.filter_by(user_id=user_id).delete()
            
            # Finally, delete the user
            db.session.delete(user_to_delete)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'User "{username}" and all associated data deleted successfully'
            }), 200
            
        except Exception as cleanup_error:
            db.session.rollback()
            print(f"Error during cleanup: {str(cleanup_error)}")
            return jsonify({
                'success': False, 
                'error': f'Error deleting user data: {str(cleanup_error)}'
            }), 500
        
    except Exception as e:
        print(f"Delete user error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update a user - admin only"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if user is admin
        if not current_user or current_user.role != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        # Find the user to update
        user_to_update = User.query.get(user_id)
        if not user_to_update:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'username' in data:
            # Check if username is already taken by another user
            existing = User.query.filter(User.username == data['username'], User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Username already exists'}), 409
            user_to_update.username = data['username']
            
        if 'email' in data:
            # Validate email format
            if data['email'] and not EMAIL_REGEX.match(data['email']):
                return jsonify({'success': False, 'error': 'Invalid email address'}), 400
            # Check if email is already taken by another user
            existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'error': 'Email already exists'}), 409
            user_to_update.email = data['email']
            
        if 'role' in data:
            # Validate role
            if data['role'] not in ['admin', 'parent', 'child', 'teacher']:
                return jsonify({'success': False, 'error': 'Invalid role'}), 400
            user_to_update.role = data['role']
            
        if 'password' in data and data['password']:
            # Update password if provided
            user_to_update.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User "{user_to_update.username}" updated successfully',
            'user': {
                'id': user_to_update.id,
                'username': user_to_update.username,
                'email': user_to_update.email,
                'role': user_to_update.role
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Test/Development Routes
@app.route('/api/test/clear-user-data/<int:user_id>', methods=['DELETE'])
@jwt_required()
def clear_user_data_for_testing(user_id):
    """Clear all user data for testing - DEVELOPMENT ONLY"""
    try:
        # Security check: ensure user can only clear their own data
        current_user_id = int(get_jwt_identity())
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Can only clear your own data'}), 403
        
        
        
        # Clear achievements
        Achievement.query.filter_by(user_id=user_id).delete()
        
        # Clear module progress
        UserModuleProgress.query.filter_by(user_id=user_id).delete()
        
        # Clear tasks
        HomeworkSchedule.query.filter_by(user_id=user_id).delete()
        
        # Clear health tasks
        HealthTask.query.filter_by(user_id=user_id).delete()
        
        # Clear streaks
        HealthStreak.query.filter_by(user_id=user_id).delete()
        LoginStreak.query.filter_by(user_id=user_id).delete()
        
        # Clear water logs
        WaterLog.query.filter_by(user_id=user_id).delete()
        
        # Clear notifications
        Notification.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'All data cleared for user {user_id}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/api/chat/mood-summary/<int:user_id>', methods=['GET'])
def get_child_mood_summary(user_id):
    """
    Get the overall mood summary, latest mood tag, and associated user messages for a child (user_id) for today.
    - overall_mood: Uses LLM to summarize all mood tags for today.
    - latest_mood: Most recent mood tag from today's chat sessions.
    - mood_messages: User messages associated with each mood tag.
    """
    try:
        from datetime import datetime, time, timedelta

        # Get today's IST date and start/end datetime
        today = get_today_ist()
        start_dt = datetime.combine(today, time.min).replace(tzinfo=IST)
        end_dt = datetime.combine(today, time.max).replace(tzinfo=IST)

        # Get all chat sessions for the user created today (IST)
        sessions = ChatSession.query.filter(
            ChatSession.user_id == user_id,
            ChatSession.updated_at >= start_dt,
            ChatSession.updated_at <= end_dt
        ).order_by(ChatSession.updated_at.desc()).all()
        
        print("Sessions found:", sessions)
        
        mood_tags = []
        mood_messages = []  # New: Store messages with their mood tags
        
        for session in sessions:
            print("Session ID:", session.id, "Interactions:", session.interactions)
            for interaction in session.interactions:
                mood_tag = getattr(interaction, 'mood_tag', None)
                print("Interaction mood_tag:", mood_tag)
                
                if mood_tag and interaction.user_message:
                    mood_tags.append(mood_tag)
                    
                    # Store message with mood context
                    mood_messages.append({
                        'mood_tag': mood_tag,
                        'user_message': interaction.user_message,
                        'timestamp': interaction.user_timestamp.isoformat() if interaction.user_timestamp else None,
                        'session_id': session.id
                    })

        # Get latest mood tag (from most recent interaction)
        latest_mood = None
        latest_message = None
        if sessions:
            for session in sessions:
                last_interaction = (
                    LLMInteractions.query
                    .filter_by(session_id=session.id)
                    .order_by(LLMInteractions.user_timestamp.desc())
                    .first()
                )
                if last_interaction and last_interaction.mood_tag:
                    latest_mood = last_interaction.mood_tag
                    latest_message = last_interaction.user_message
                    break
 
        # Use LLM to summarize overall mood if mood_tags exist
        overall_mood = None
        if mood_tags:
            # Include some sample messages in the prompt for better context
            sample_messages = [msg['user_message'][:100] + "..." if len(msg['user_message']) > 100 
                             else msg['user_message'] for msg in mood_messages[:3]]
            
            prompt = (
                "Given the following mood tags and sample messages from a child throughout the day, "
                "summarize the child's overall emotional state in a short sentence. "
                "Focus on the dominant emotion and provide a brief reason. "
                "Avoid special characters, use plain text only. "
                f"Mood tags: {', '.join(mood_tags)}. "
                f"Sample messages: {'; '.join(sample_messages) if sample_messages else 'No messages available'}."
            )
            try:
                llm_response = client.chat.completions.create(
                    model="meta-llama/llama-4-maverick-17b-128e-instruct",
                    messages=[{"role": "system", "content": prompt}],
                    max_tokens=80,
                    temperature=0.5
                )
                overall_mood = llm_response.choices[0].message.content.strip()
            except Exception as e:
                print(f"LLM Error: {e}")
                overall_mood = "Unable to summarize mood at this time."

        # Group mood messages by mood tag for better organization
        mood_groups = {}
        for msg in mood_messages:
            mood = msg['mood_tag']
            if mood not in mood_groups:
                mood_groups[mood] = []
            mood_groups[mood].append(msg)

        # Sort messages by timestamp (most recent first)
        for mood in mood_groups:
            mood_groups[mood].sort(key=lambda x: x['timestamp'] or '', reverse=True)

        print("Overall mood:", overall_mood)
        print("Latest mood:", latest_mood)
        print("Mood tags:", mood_tags)
        print("Mood groups:", mood_groups)
        
        return jsonify({
            "success": True,
            "user_id": user_id,
            "date": str(today),
            "overall_mood": overall_mood,
            "latest_mood": latest_mood,
            "latest_message": latest_message,
            "mood_tags": mood_tags,
            "mood_messages": mood_messages,
            "mood_groups": mood_groups,
            "total_messages": len(mood_messages),
            "unique_moods": len(mood_groups)
        }), 200

    except Exception as e:
        print(f"Error in get_child_mood_summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database when running directly
    initialize_database()
    app.run(debug=True, port=5000)
