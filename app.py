from flask import Flask, request, jsonify, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ChatSession
import re
from config import Config
from openai import OpenAI

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+") 

# Initialize OpenAI client
client = OpenAI(base_url="https://api.groq.com/openai/v1",api_key=app.config['GROQ_API_KEY'])

# ---------------------------
# Authentication Routes
# ---------------------------

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    if not EMAIL_REGEX.match(email):
        return jsonify({'error': 'Invalid email address'}), 400
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'error': 'Username or email already exists'}), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return jsonify({
            'message': 'Login successful', 
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

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
# Chatbot Routes
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
# Frontend Routes
# ---------------------------

@app.route('/')
def index():
    """Serve the main homepage"""
    # Provide default user progress data for the template
    userProgress = {
        'time': 0,
        'creative': 0,
        'financial': 0,
        'health': 0,
        'safety': 0,
        'english': 0,
        'communication': 0,
        'quiz': 0,
        'overall': 0
    }
    
    # Default user data for template
    user = {
        'streak': 0,
        'achievements': []
    }
    
    # Default badges data
    userBadges = [
        {'id': 1, 'name': 'First Steps', 'icon': 'fas fa-baby', 'earned': False},
        {'id': 2, 'name': 'Time Master', 'icon': 'fas fa-clock', 'earned': False},
        {'id': 3, 'name': 'Creative Genius', 'icon': 'fas fa-palette', 'earned': False},
        {'id': 4, 'name': 'Money Smart', 'icon': 'fas fa-coins', 'earned': False},
        {'id': 5, 'name': 'Health Hero', 'icon': 'fas fa-heart', 'earned': False},
        {'id': 6, 'name': 'Safety Scout', 'icon': 'fas fa-shield-alt', 'earned': False},
    ]
    
    # Default streak
    userStreak = 0
    
    return render_template('index.html', 
                         userProgress=userProgress, 
                         user=user, 
                         userBadges=userBadges, 
                         userStreak=userStreak)

@app.route('/home')
def home():
    """Alternative route for homepage"""
    # Provide default user progress data for the template
    userProgress = {
        'time': 0,
        'creative': 0,
        'financial': 0,
        'health': 0,
        'safety': 0,
        'english': 0,
        'communication': 0,
        'quiz': 0,
        'overall': 0
    }
    
    # Default user data for template
    user = {
        'streak': 0,
        'achievements': []
    }
    
    # Default badges data
    userBadges = [
        {'id': 1, 'name': 'First Steps', 'icon': 'fas fa-baby', 'earned': False},
        {'id': 2, 'name': 'Time Master', 'icon': 'fas fa-clock', 'earned': False},
        {'id': 3, 'name': 'Creative Genius', 'icon': 'fas fa-palette', 'earned': False},
        {'id': 4, 'name': 'Money Smart', 'icon': 'fas fa-coins', 'earned': False},
        {'id': 5, 'name': 'Health Hero', 'icon': 'fas fa-heart', 'earned': False},
        {'id': 6, 'name': 'Safety Scout', 'icon': 'fas fa-shield-alt', 'earned': False},
    ]
    
    # Default streak
    userStreak = 0
    
    return render_template('index.html', 
                         userProgress=userProgress, 
                         user=user, 
                         userBadges=userBadges, 
                         userStreak=userStreak)

# ---------------------------
# API Routes for Frontend
# ---------------------------

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chat interface"""
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    # For now, use a default user_id (could be from session later)
    user_id = 1
    
    try:
        # Use existing chatbot logic
        response_data = chatbot_logic(user_id, message)
        return jsonify({
            'success': True,
            'response': response_data['response']
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    """API endpoint to get chat history"""
    # For now, use a default user_id (could be from session later)
    user_id = 1
    
    try:
        chats = ChatSession.query.filter_by(user_id=user_id)\
                                 .order_by(ChatSession.timestamp.asc())\
                                 .limit(20).all()
        
        messages = []
        for chat in chats:
            messages.append({
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