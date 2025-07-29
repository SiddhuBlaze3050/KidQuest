from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Achievement, ChatSession,ChildProfile, DoodleSession, LLMInteractions, ParentChild, SavingGoal, Transaction, HomeworkSchedule, PomodoroSession, ScreenTime, Notification, HealthTask, HealthStreak, WaterLog, LoginStreak, PsychometricTestResult, UserModuleProgress
import re, requests
import PIL
import os
import random
import glob
import base64
from config import Config
from openai import OpenAI
import secrets
import time
import traceback
from datetime import datetime, date
import json
from collections import defaultdict

# NEW: JWT imports
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Import our psychometry module
from services.psychometry import PsychometryService

app = Flask(__name__)
app.config.from_object(Config)
# Use consistent secret key from config instead of random one
# app.secret_key = secrets.token_hex(16)  # This was causing JWT tokens to become invalid on restart

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

# NEW: Initialize JWT
jwt = JWTManager(app)

# NEW: JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Invalid token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Missing authorization token'
    }), 401

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+") 

# Initialize OpenAI client
client = OpenAI(base_url="https://api.groq.com/openai/v1",api_key=app.config['GROQ_API_KEY'])

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
def api_get_session(session_id):
    """Get detailed session with all interactions"""
    try:
        session = db.session.get(ChatSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
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
def update_session_summary(session_id):
    """Update session summary"""
    try:
        data = request.get_json()
        summary = data.get('summary')
        
        session = db.session.get(ChatSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        session.summary = summary
        session.updated_at = datetime.utcnow()
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
            # Generate JWT token
            access_token = create_access_token(identity=user.id)
            
            # Update login streak for successful login
            update_login_streak(user.id)
            
            # Generate notifications for the user
            generate_notifications(user.id)
            
            return jsonify({
                'success': True,
                'message': 'Login successful', 
                'access_token': access_token,
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
        print(f"🔒 User {user_id} logged out")
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        current_user_id = get_jwt_identity()
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
        print("Streak Eval Error:", traceback.format_exc())

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
        print("Error fetching quote:", e)
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
        
        print(f"⭐ Stars calculation for user {user_id}: modules={module_stars}, login_streak={(login_streak.current_streak if login_streak else 0)}, health_streak={(health_streak.current_streak*2 if health_streak else 0)}, total={stars}")
        
        return stars
    except Exception as e:
        print(f"Error calculating total stars: {e}")
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
        
        print(f"📊 Quests calculated for user {user_id}: {quests} total (modules: {len(module_progress)}, tasks: {len(completed_tasks)})")
        
        return quests
    except Exception as e:
        print(f"Error calculating quests completed: {e}")
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
        
        print(f"🧠 Skills calculated for user {user_id}: {skills} skills mastered")
        
        return skills
    except Exception as e:
        print(f"Error calculating skills mastered: {e}")
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
        
        print(f"📊 Today's goals for user {user_id}: {goals} total (modules: {today_module_progress}, tasks: {today_tasks}, health: {today_health_tasks}, login: {1 if login_streak and login_streak.last_login_date == today else 0}, water: {1 if water_log and water_log.count >= 8 else 0})")
        
        return goals
    except Exception as e:
        print(f"Error calculating today's goals: {e}")
        return 0

# ---------------------------
# Child Dashboard Routes
# ---------------------------

@app.route('/api/child/stats/<int:user_id>', methods=['GET'])
@jwt_required()
def api_child_stats(user_id):
    """Get child dashboard statistics"""
    try:
        today = date.today()
        
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
        
        print(f"📊 Dashboard stats for user {user_id}: {stats}")
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
    except Exception as e:
        print(f"Error calculating stats for user {user_id}: {e}")
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
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        # Create a test achievement
        achievement = Achievement(
            user_id=user_id,
            badge_name=data.get('badge_name', f"Test Achievement {datetime.utcnow().timestamp()}"),
            description=data.get('description', 'Test achievement for dashboard stats'),
            date_awarded=datetime.utcnow()
        )
        
        db.session.add(achievement)
        db.session.commit()
        
        print(f"✅ Created test achievement for user {user_id}: {achievement.badge_name}")
        
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
        print(f"Error creating test achievement: {e}")
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
            "earnedDate": datetime.utcnow().isoformat(),
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
            "earnedDate": datetime.utcnow().isoformat(),
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
            "earnedDate": datetime.utcnow().isoformat(),
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
                    existing.date_awarded = datetime.utcnow()
                else:
                    new_achievement = Achievement(
                        user_id=user_id,
                        badge_name=f"{achievement_data['type']}_achievement",
                        description=f"{achievement_data['title']}: {achievement_data['description']}",
                        date_awarded=datetime.utcnow()
                    )
                    db.session.add(new_achievement)
        
            db.session.commit()
        else:
            print(f"🚫 No achievements created for user {user_id} - insufficient progress (modules: {completed_modules}, tasks: {completed_tasks}, streak: {streak_days})")
        
        print(f"📊 Special achievements for user {user_id}: {[a['title'] for a in achievements]}")
        print(f"🔍 Achievement calculation: modules={completed_modules}, tasks={completed_tasks}, streak={streak_days}")
        
        return jsonify({
            'success': True,
            'achievements': achievements
        }), 200
        
    except Exception as e:
        print(f"Error fetching special achievements for user {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/achievements/refresh/<int:user_id>', methods=['POST'])
@jwt_required()
def refresh_achievements(user_id):
    """Force refresh achievements for a user - for testing"""
    try:
        print(f"🔄 Force refreshing achievements for user {user_id}")
        
        # Call the existing get_special_achievements function
        response = get_special_achievements(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Achievements refreshed successfully',
            'response': response[0].get_json() if hasattr(response[0], 'get_json') else 'Success'
        }), 200
        
    except Exception as e:
        print(f"Error refreshing achievements for user {user_id}: {e}")
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
        user_timestamp=datetime.utcnow()
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
        print(f"Error getting AI response: {e}")
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
            print("Failed to parse mood from LLM response")
            detected_mood = 'neutral'
    
    # Update the interaction with bot response and detected mood
    user_interaction.llm_response = bot_reply  # Keep full response with mood tag
    user_interaction.llm_timestamp = datetime.utcnow()
    user_interaction.mood_tag = detected_mood
    
    # Update session mood_tag (overwrite with latest mood)
    chat_session.mood_tag = detected_mood
    chat_session.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    print(f"Updated session {chat_session.id} mood to: {detected_mood}")
    
    return {
        'response': clean_bot_reply,  # Return clean response without mood tag
        'timestamp': user_interaction.llm_timestamp.isoformat(),
        'session_id': chat_session.id,
        'mood': detected_mood
    }

#Finance tracker APIs
@app.route('/api/parentchild', methods=['GET'])
def get_parent_child_links():
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
        current_user_id = get_jwt_identity()
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
        current_user_id = get_jwt_identity()
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
        current_user_id = get_jwt_identity()
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
        current_user_id = get_jwt_identity()
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
        data = request.get_json()
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Store user_id in session for later use
        session['psychometry_user_id'] = user_id

        # Initialize assessment
        test_questions = psychometry_service.initialize_assessment()
        
        # Store in session
        session['psychometry_questions'] = test_questions
        session['psychometry_current_index'] = 0
        session['psychometry_responses'] = []
        session['psychometry_start_time'] = time.time()
        session.permanent = True
        
        print(f"Starting new psychometry assessment with {len(test_questions)} questions...")
        
        # Return first question
        return get_next_psychometry_question()
        
    except Exception as e:
        print(f"Error in start_psychometry_test: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to start psychometry test', 'message': str(e)}), 500

@app.route('/api/psychometry/submit', methods=['POST'])
def submit_psychometry_answer():
    """Submit an answer for psychometry assessment"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
        user_id = data.get('user_id')
        session_user_id = session.get('psychometry_user_id')
        if not user_id or not session_user_id or str(user_id) != str(session_user_id):
            return jsonify({'error': 'User ID mismatch or missing'}), 400
        
        user_answer = data.get('answer')
        if not user_answer:
            return jsonify({'error': 'No answer provided'}), 400
        
        # Get current question
        current_index = session.get('psychometry_current_index', 0)
        questions = session.get('psychometry_questions', [])
        
        if current_index >= len(questions):
            return jsonify({'error': 'Invalid question index'}), 400
            
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
        
        print(f"Answer submitted for {current_question['category']}: {user_answer} vs {current_question['correct_answer']}")
        
        # Check if test is complete
        if session['psychometry_current_index'] >= len(questions):
            return complete_psychometry_assessment()
        
        # Get next question
        return get_next_psychometry_question()
        
    except Exception as e:
        print(f"Error in submit_psychometry_answer: {e}")
        traceback.print_exc()
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
        print(f"Error in get_next_psychometry_question: {e}")
        traceback.print_exc()
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
        print(f"Error in complete_psychometry_assessment: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to complete assessment', 'message': str(e)}), 500

# Psychometric Test Stats for parent Dashboard
@app.route('/api/psychometry/results/<int:child_id>', methods=['GET'])
def get_psychometry_results(child_id):
    """Get the latest psychometric test result for a child"""
    try:
        result = PsychometricTestResult.query.filter_by(child_id=child_id).order_by(PsychometricTestResult.taken_at.desc()).first()
        if not result:
            return jsonify({'success': False, 'error': 'No result found'}), 404

        return jsonify({
            'success': True,
            'result': {
                'id': result.id,
                'child_id': result.child_id,
                'taken_at': result.taken_at.isoformat() if result.taken_at else None,
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
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        print(f"🔍 Getting tasks for user: {user_id}")
        
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        print(f"🔍 Found {len(tasks)} tasks in database for user {user_id}")
        
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
def get_tasks_for_parents(user_id):
    """Get all tasks for a specific user"""
    try:
        # Security check: ensure user can only access their own tasks
        # current_user_id = get_jwt_identity()
        # if user_id != current_user_id:
        #     return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        print(f"🔍 Getting tasks for user: {user_id}")
        
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        print(f"🔍 Found {len(tasks)} tasks in database for user {user_id}")
        
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
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        
        print(f"🔍 Creating task for user: {data.get('user_id')}")
        print(f"🔍 Task data: {data}")
        
        # Ensure user can only create tasks for themselves (simplified check)
        current_user_id = data.get('user_id')  # Use the user_id from the request data
        if not current_user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        # Handle empty due_date string properly
        due_date_str = data.get('due_date')
        due_date = None
        if due_date_str and due_date_str.strip():  # Check if not empty or whitespace
            try:
                due_date = date.fromisoformat(due_date_str)
            except ValueError:
                return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        current_time = datetime.utcnow()
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
        current_user_id = get_jwt_identity()
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
        
        print(f"✅ Task {task_id} status updated to '{new_status}'")
        
        return jsonify({'success': True, 'message': f'Task status updated to {new_status}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
# @jwt_required()  # Temporarily disabled for testing
def delete_task(task_id):
    """Delete a task - temporarily disabled JWT for testing"""
    try:
        # Get Authorization header to extract user info for testing
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing authorization token'}), 401
        
        # For now, accept any valid format Bearer token (fix JWT later)
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        print(f"🗑️ Deleting task {task_id}")
        
        task = db.session.get(HomeworkSchedule, task_id)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        # Authorization: users can only delete their own tasks or teachers can delete tasks they assigned
        # if task.user_id != current_user_id and task.assigned_by_teacher != current_user_id:
        #     return jsonify({'success': False, 'error': 'Unauthorized: Can only delete your own tasks or tasks you assigned'}), 403

        db.session.delete(task)
        db.session.commit()
        
        print(f"✅ Task {task_id} deleted successfully")
        
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
        print(f"🔍 get_teacher_students called for teacher_id: {teacher_id}")
        
        # Simple authorization check using Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'Missing authorization token'}), 401
        
        # For now, accept any valid format Bearer token (fix JWT later)
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'success': False, 'error': 'Invalid token format'}), 401
        
        print(f"✅ Authorization header present for teacher {teacher_id}")
        
        # Get students through ParentChild table where parent_id is the teacher
        student_relationships = ParentChild.query.filter_by(parent_id=teacher_id).all()
        students_data = []
        
        print(f"🔍 Found {len(student_relationships)} student relationships")
        
        for relationship in student_relationships:
            student = User.query.get(relationship.child_id)
            if student:
                print(f"🔍 Found student: {student.username} (ID: {student.id})")
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
        current_user_id = get_jwt_identity()
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
        
        print(f"🔍 Getting homework assigned by teacher: {teacher_id}")
        
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
        current_time = datetime.utcnow()
        
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
        current_user_id = get_jwt_identity()
        data = request.get_json()
        print("📥 Received data:", data)

        # Ensure user can only start sessions for themselves
        if data.get('user_id') != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only start sessions for yourself'}), 403

        # Debug print to confirm presence of required keys
        if 'user_id' not in data:
            print("❌ Missing 'user_id' in request")
        if 'homework_id' not in data:
            print("❌ Missing 'homework_id' in request")
        session = PomodoroSession(
            user_id=data['user_id'],
            homework_id=data['homework_id'],
            start_time=datetime.utcnow()
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
        current_user_id = get_jwt_identity()
        data = request.get_json()
        duration = data.get('duration') # in minutes

        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Authorization: users can only complete their own sessions
        if session.user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized: Can only complete your own sessions'}), 403

        # Get work and break duration from request
        work_duration = data.get('work_duration', 0)
        break_duration = data.get('break_duration', 0)
        
        # Add any remaining active time
        if session.start_time:
            remaining_work = int((datetime.utcnow() - session.start_time).total_seconds())
            work_duration += remaining_work

        session.work_duration = work_duration
        session.break_duration = break_duration
        session.completed = True
        session.end_time = datetime.utcnow()

        db.session.commit()
        return jsonify({'success': True, 'message': 'Pomodoro session completed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/pause/<int:session_id>', methods=['PUT'])
def pause_pomodoro(session_id):
    """Pause a pomodoro session"""
    try:
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Calculate work duration so far
        if session.start_time:
            work_duration = int((datetime.utcnow() - session.start_time).total_seconds())
            session.work_duration += work_duration

        session.start_time = None  # Reset start time for next resume

        # Session is now paused

        db.session.commit()
        return jsonify({'success': True, 'message': 'Session paused'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/resume/<int:session_id>', methods=['PUT'])
def resume_pomodoro(session_id):
    """Resume a paused pomodoro session"""
    try:
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        session.start_time = datetime.utcnow()

        # Session resumed - break time will be calculated when session ends

        db.session.commit()
        return jsonify({'success': True, 'message': 'Session resumed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/abandon/<int:session_id>', methods=['PUT'])
def abandon_pomodoro(session_id):
    """Abandon a pomodoro session"""
    try:
        data = request.get_json()
        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        # Get work and break duration from request
        work_duration = data.get('work_duration', 0) if data else 0
        break_duration = data.get('break_duration', 0) if data else 0
        
        # Add any remaining active time
        if session.start_time:
            remaining_work = int((datetime.utcnow() - session.start_time).total_seconds())
            work_duration += remaining_work

        session.work_duration = work_duration
        session.break_duration = break_duration
        session.end_time = datetime.utcnow()

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
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Unauthorized access'}), 403
        module_type = data.get('module_type', 'Unknown Module')
        progress_percentage = data.get('progress_percentage', 0)
        is_completed = data.get('is_completed', False)
        progress_data = data.get('progress_data', {})
        submodule_name = data.get('submodule_name', '')
        
        print(f"📝 Saving progress for User {user_id}, Module '{module_type}', Progress: {progress_percentage}%")
        print(f"🔍 Full request data: {data}")  # Log full request data
        
        # Validation
        if not user_id:
            print("❌ Missing user_id")
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get module and submodule IDs
        module_id = get_module_id(module_type)
        
        # Handle submodules based on module type
        if module_has_submodules(module_type):
            # Module has submodules, so submodule_name is required
            if not submodule_name:
                print(f"❌ Submodule name required for module '{module_type}'")
                return jsonify({'success': False, 'error': f'Submodule name required for module: {module_type}'}), 400
            submodule_id = get_submodule_id(module_type, submodule_name)
            if not submodule_id:
                print(f"❌ Invalid submodule '{submodule_name}' for module '{module_type}'")
                return jsonify({'success': False, 'error': f'Invalid submodule: {submodule_name}'}), 400
        else:
            # Module doesn't have submodules, so clear submodule fields
            submodule_name = None
            submodule_id = None
        
        print(f"🔍 Module ID: {module_id}, Submodule ID: {submodule_id} for '{module_type}'/'{submodule_name}'")
        
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
            print(f"✅ Updated existing progress record for {module_type}")
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
            print(f"✅ Created new progress record for {module_type}")
        
        # Commit changes
        db.session.commit()
        
        print(f"✅ Progress saved successfully for {module_type}")
        return jsonify({
            'success': True, 
            'message': 'Progress saved successfully',
            'progress_percentage': progress_percentage,
            'is_completed': is_completed
        }), 200
        
    except Exception as e:
        print(f"💥 Error in save_module_progress: {e}")
        import traceback
        traceback.print_exc()  # Print full traceback
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
        
        print(f"🔍 Getting module progress for user {user_id}, module: '{decoded_module_type}'")
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            print(f"❌ User {user_id} not found")
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Check if module exists
        module_info = MODULE_MAPPING.get(decoded_module_type)
        if not module_info:
            print(f"❌ Module '{decoded_module_type}' not found")
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
                
                print(f"✅ Retrieved module progress for user {user_id}, module {decoded_module_type}: {progress_data}")
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
                
                print(f"✅ Retrieved module progress for user {user_id}, module {decoded_module_type}: {progress_data}")
                return jsonify({
                    'success': True,
                    'progress': progress_data
                }), 200
        
        print(f"📝 No progress found for user {user_id}, module {decoded_module_type}")
        # Return success with null progress instead of 404 for better UX
        return jsonify({
            'success': True, 
            'progress': None,
            'message': f'No progress found for module: {decoded_module_type}'
        }), 200
        
    except Exception as e:
        print(f"💥 Error retrieving module progress: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/module/progress/<int:user_id>', methods=['GET'])
@jwt_required()
def get_all_module_progress(user_id):
    """Get all module progress for a user"""
    try:
        print(f"🔍 Getting all module progress for user {user_id}")
        
        # Check if user exists
        user = db.session.get(User, user_id)
        if not user:
            print(f"❌ User {user_id} not found")
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
        
        print(f"✅ Retrieved {len(progress_list)} module progress records for user {user_id}")
        return jsonify({
            'success': True,
            'progress_list': progress_list,
            'total_modules': len(progress_list),
            'completed_modules': sum(1 for p in progress_list if p['overall_completed']),
            'modules_with_submodules': [p['module_name'] for p in progress_list if p['has_submodules']],
            'modules_without_submodules': [p['module_name'] for p in progress_list if not p['has_submodules']]
        }), 200
        
    except Exception as e:
        print(f"💥 Error retrieving all module progress: {e}")
        import traceback
        traceback.print_exc()
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

@app.route('/api/child/quest-stats/<int:user_id>', methods=['GET'])
@jwt_required()
def get_quest_statistics(user_id):
    """Get detailed quest statistics"""
    try:
        print(f"🔍 Getting detailed quest statistics for user {user_id}")
        
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
        
        print(f"📊 Detailed quest stats for user {user_id}: {stats}")
        
        return jsonify({
            'success': True,
            'quest_statistics': stats
        }), 200
        
    except Exception as e:
        print(f"💥 Error getting quest statistics: {e}")
        import traceback
        traceback.print_exc()
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
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Allow users to access their own notifications or parents to access their children's
        if user_id != current_user_id and current_user.role != 'parent':
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
        current_user_id = get_jwt_identity()
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
        print(f"Error generating notifications: {e}")
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
        user_id = data.get('user_id', 1)
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
                timestamp=datetime.utcnow(),
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
@jwt_required()
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
            start_time=datetime.utcnow(),
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
                print(f"Deleted file: {drawing.save_image_path}")
            except Exception as e:
                print(f"Error deleting file: {str(e)}")
        
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
# Error Handlers
# ---------------------------
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
            print("🔄 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create default admin user
            create_default_admin()
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
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
        
        print(f"Activity completed: {activity_name} by user {user_id}, earned {stars_earned} stars")
        
        return jsonify({
            'success': True,
            'message': f'{activity_name} completed successfully!',
            'stars_earned': stars_earned,
            'achievement_id': achievement.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error tracking activity completion: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Achievement Management Routes
@app.route('/api/achievements/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_achievements(user_id):
    """Get all achievements for a user"""
    try:
        print(f"🔄 Loading achievements for user {user_id}")
        
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
                'badge_name': achievement.badge_name,
                'description': achievement.description,
                'date_awarded': achievement.date_awarded.isoformat() if achievement.date_awarded else None,
                'badge_type': getattr(achievement, 'badge_type', 'general'),
                'icon': getattr(achievement, 'icon', '🏆')
            }
                
            achievement_list.append(achievement_data)
        
        print(f"✅ Found {len(achievement_list)} achievements for user {user_id}")
        
        return jsonify({
            'success': True,
            'achievements': achievement_list
        }), 200
        
    except Exception as e:
        print(f"💥 Error loading achievements for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
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
        
        print(f"🔄 Creating achievement: {badge_name} for user {user_id}")
        
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
            date_awarded=datetime.utcnow()
        )
        
        # Add additional fields if the Achievement model supports them
        if hasattr(Achievement, 'badge_type'):
            achievement.badge_type = badge_type
        if hasattr(Achievement, 'icon'):
            achievement.icon = icon
        
        db.session.add(achievement)
        db.session.commit()
        
        print(f"✅ Created achievement: {badge_name} for user {user_id}")
        
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
        print(f"💥 Error creating achievement: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# Add this function near other notification-related routes

# Add this method near other notification-related routes
def clear_user_notifications(user_id):
    """Clear all notifications for a specific user"""
    try:
        # Delete all existing notifications for the user
        Notification.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        print(f"🗑️ Cleared all notifications for user {user_id}")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error clearing notifications for user {user_id}: {e}")
        return False

# Modify the logout route to clear notifications
@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint that clears user notifications"""
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

        # Get screen time entries only for today
        today_screen_data = ScreenTime.query.filter_by(date=today).all()

        # Sum screen time per child user
        user_hours = defaultdict(float)
        for entry in today_screen_data:
            # Ensure the user is a child (optional if you're confident only child users are in screen_time)
            user = User.query.get(entry.user_id)
            if user and user.role == 'child':
                user_hours[entry.user_id] += entry.hours

        # Total number of child users who logged screen time today
        total_children_with_data = len(user_hours)

        # Average screen time (in hours), then convert to MM:SS
        avg_screen_time = (sum(user_hours.values()) / total_children_with_data) if total_children_with_data > 0 else 0
        # Convert to total seconds, not minutes
        total_seconds = round(avg_screen_time * 3600)
        mm, ss = divmod(total_seconds, 60)
        formatted_avg = f"{mm:02d}:{ss:02d}"


        stats = {
            "totalUsers": User.query.filter_by(role='child').count(),  # only child users
            "chatSessions": ChatSession.query.count(),
            "achievements": Achievement.query.count(),
            "avg_screen_time_per_user": formatted_avg
        }

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Test/Development Routes
@app.route('/api/test/clear-user-data/<int:user_id>', methods=['DELETE'])
@jwt_required()
def clear_user_data_for_testing(user_id):
    """Clear all user data for testing - DEVELOPMENT ONLY"""
    try:
        # Security check: ensure user can only clear their own data
        current_user_id = get_jwt_identity()
        if user_id != current_user_id:
            return jsonify({'success': False, 'error': 'Can only clear your own data'}), 403
        
        print(f"🗑️ Clearing all data for user {user_id} (TESTING)")
        
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

if __name__ == '__main__':
    # Initialize database when running directly
    initialize_database()
    app.run(debug=True, port=5000)