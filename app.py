from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ChatSession,ChildProfile, ParentChild, SavingGoal, Transaction
import re
from config import Config
from openai import OpenAI

app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS for Vue.js frontend
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

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