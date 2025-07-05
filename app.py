from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Achievement, ChatSession,ChildProfile, DoodleSession, LLMInteractions, ParentChild, SavingGoal, Transaction, HomeworkSchedule, PomodoroSession, ScreenTime, Notification
import re
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

# Import our psychometry module
from psychometry import PsychometryService

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = secrets.token_hex(16)

# Configure CORS for Vue.js frontend
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)

db.init_app(app)

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

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat interface with session support"""
    try:
        data = request.get_json()
        message = data.get('message')
        user_id = data.get('user_id', 1)
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

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is running',
        'status': 'healthy'
    }), 200

# ---------------------------
# Child Dashboard Routes
# ---------------------------

@app.route('/api/child/stats/<int:user_id>', methods=['GET'])
def api_child_stats(user_id):
    """Get child dashboard statistics"""
    try:
        # Mock data for now - in production, calculate from database
        stats = {
            'totalStars': 0,
            'questsCompleted': 0,
            'skillsLearned': 0,
            'todayGoals': 0,
            'streakDays': 0,
            'userLevel': 1
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

@app.route('/api/child/quests/<int:user_id>', methods=['GET'])
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
def api_toggle_quest(quest_id):
    """Toggle quest completion status"""
    try:
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
@app.route('/api/finance/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    try:
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
def add_transaction():
    try:
        data = request.get_json()
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
def get_savings_goals(user_id):
    try:
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
def add_savings_goal():
    try:
        data = request.get_json()
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


# ---------------------------
# Task Tracker (Homework) Routes
# ---------------------------
@app.route('/api/tasks/<int:user_id>', methods=['GET'])
def get_tasks(user_id):
    """Get all tasks for a specific user"""
    try:
        tasks = HomeworkSchedule.query.filter_by(user_id=user_id).order_by(HomeworkSchedule.due_date.asc()).all()
        
        tasks_data = []
        for task in tasks:
            total_duration = db.session.query(db.func.sum(PomodoroSession.duration)).filter_by(homework_id=task.id, completed=True).scalar() or 0
            
            tasks_data.append({
                'id': task.id,
                'subject': task.subject,
                'task': task.task,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'status': task.status,
                'time_spent': total_duration
            })

        return jsonify({
            'success': True,
            'tasks': tasks_data
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        new_task = HomeworkSchedule(
            user_id=data['user_id'],
            subject=data.get('subject'),
            task=data['task'],
            due_date=date.fromisoformat(data['due_date']) if data.get('due_date') else None
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
                'status': new_task.status
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update a task's status"""
    try:
        data = request.get_json()
        new_status = data.get('status')

        task = db.session.get(HomeworkSchedule, task_id)
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        task.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Task status updated to {new_status}'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------------------------
# Pomodoro Session Routes
# ---------------------------
@app.route('/api/pomodoro/start', methods=['POST'])
def start_pomodoro():
    """Start a new pomodoro session for a task"""
    try:
        data = request.get_json()
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

        db.session.commit()
        return jsonify({'success': True, 'session_id': session.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pomodoro/complete/<int:session_id>', methods=['PUT'])
def complete_pomodoro(session_id):
    """Complete a pomodoro session"""
    try:
        data = request.get_json()
        duration = data.get('duration') # in minutes

        session = db.session.get(PomodoroSession, session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404

        session.duration = duration
        session.completed = True
        db.session.commit()

        return jsonify({'success': True, 'message': 'Pomodoro session completed'}), 200
    except Exception as e:
        db.session.rollback()
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
# Notification Routes
# ---------------------------
@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    """Get all notifications for a user"""
    try:
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
def mark_notifications_read():
    """Mark notifications as read"""
    try:
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])
        
        if not notification_ids:
            return jsonify({'success': False, 'error': 'notification_ids are required'}), 400
        
        # Update notifications
        notifications = Notification.query.filter(Notification.id.in_(notification_ids)).all()
        for notification in notifications:
            notification.is_read = True
        
        db.session.commit()
        return jsonify({'success': True, 'message': f'{len(notifications)} notifications marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/create-sample', methods=['POST'])
def create_sample_notifications():
    """Create sample notifications for testing (development only)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id is required'}), 400
        
        sample_notifications = [
            "🎉 Welcome to your magical adventure world!",
            "⭐ You've earned 50 stars today! Keep up the great work!",
            "📚 New reading quest available: 'The Dragon's Tale'",
            "🏆 Achievement unlocked: Math Master Level 1!",
            "💰 Your savings goal is 80% complete!",
            "🎨 New drawing tools have been added to your art pad!"
        ]
        
        created_notifications = []
        for content in sample_notifications:
            notification = Notification(
                user_id=user_id,
                content=content,
                is_read=False
            )
            db.session.add(notification)
            created_notifications.append(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(created_notifications)} sample notifications created'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

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

with app.app_context():
    db.create_all()
    create_default_admin()

if __name__ == '__main__':
    app.run(debug=True, port=5000)