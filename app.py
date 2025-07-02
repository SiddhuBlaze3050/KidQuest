from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ChatSession,ChildProfile, ParentChild, SavingGoal, Transaction, HomeworkSchedule, PomodoroSession, ScreenTime, Notification
import re
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

@app.route('/chat-history/<int:user_id>', methods=['GET'])
def get_chat_history(user_id):
    try:
        chats = ChatSession.query.filter_by(user_id=user_id)\
                                 .order_by(ChatSession.timestamp.asc()).all()
        
        chat_history = []
        for chat in chats:
            chat_history.append({
                'id': chat.id,
                'message': chat.message,
                'sender': chat.sender,
                'timestamp': chat.timestamp.isoformat()
            })
        
        return jsonify({'chat_history': chat_history}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-chat/<int:user_id>', methods=['DELETE'])
def clear_chat_history(user_id):
    try:
        ChatSession.query.filter_by(user_id=user_id).delete()
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
    """API endpoint for chat interface"""
    try:
        data = request.get_json()
        message = data.get('message')
        user_id = data.get('user_id', 1)  # Default to user_id 1 for now
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Use existing chatbot logic
        response_data = chatbot_logic(user_id, message)
        return jsonify({
            'success': True,
            'response': response_data['response'],
            'timestamp': response_data['timestamp']
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/history/<int:user_id>', methods=['GET'])
def api_chat_history(user_id):
    """API endpoint to get chat history"""
    try:
        chats = ChatSession.query.filter_by(user_id=user_id)\
                                 .order_by(ChatSession.timestamp.asc())\
                                 .limit(50).all()
        
        messages = []
        for chat in chats:
            messages.append({
                'id': chat.id,
                'message': chat.message,
                'sender': chat.sender,
                'timestamp': chat.timestamp.isoformat()
            })
        
        return jsonify({
            'success': True,
            'messages': messages
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

def chatbot_logic(user_id, user_message):
    """Extracted chatbot logic for reuse"""
    # Save user message to database
    user_chat = ChatSession(
        user_id=user_id,
        message=user_message,
        sender='user'
    )
    db.session.add(user_chat)
    
    # Get recent chat history (last 10 messages)
    recent_chats = ChatSession.query.filter_by(user_id=user_id)\
                                   .order_by(ChatSession.timestamp.desc())\
                                   .limit(10).all()
    
    # Build conversation context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add recent chat history in chronological order
    for chat in reversed(recent_chats):
        role = "user" if chat.sender == "user" else "assistant"
        messages.append({"role": role, "content": chat.message})
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Get response from OpenAI/Groq
    response = client.chat.completions.create(
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        messages=messages,
        max_tokens=200,
        temperature=0.7
    )
    
    bot_reply = response.choices[0].message.content.strip()
    
    # Save bot response to database
    bot_chat = ChatSession(
        user_id=user_id,
        message=bot_reply,
        sender='assistant',
    )
    db.session.add(bot_chat)
    db.session.commit()
    
    return {
        'response': bot_reply,
        'timestamp': bot_chat.timestamp.isoformat()
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