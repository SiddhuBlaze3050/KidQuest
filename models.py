from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time

db = SQLAlchemy()



# ----------------------------
# User Model
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'parent' or 'child'
    
   

    # Relationships
    child_profile = db.relationship('ChildProfile', backref='user', uselist=False)
    parent_relationships = db.relationship('ParentChild', 
                                           backref='parent', 
                                           foreign_keys='ParentChild.parent_id')
    child_relationships = db.relationship('ParentChild', 
                                          backref='child', 
                                          foreign_keys='ParentChild.child_id')


# ----------------------------
# Child Profile Model
# ----------------------------
class ChildProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grade_level = db.Column(db.Integer)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    interests = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))


# ----------------------------
# Parent-Child Mapping
# ----------------------------
class ParentChild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    child_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    relationship_type = db.Column(db.String(20))  # e.g., 'father', 'guardian'



# ---------------------------
# Time Management
# ---------------------------

class PomodoroSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    homework_id = db.Column(db.Integer, db.ForeignKey('homework_schedule.id'), nullable=True)
    start_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    completed = db.Column(db.Boolean, default=False)

class HomeworkSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(100))
    task = db.Column(db.String(255))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending') # pending, in-progress, completed
    pomodoro_sessions = db.relationship('PomodoroSession', backref='homework', lazy=True)

class PuzzleAlarm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    alarm_time = db.Column(db.Time)
    puzzle_solved = db.Column(db.Boolean, default=False)

# ---------------------------
# Creative & Doodling
# ---------------------------

class DoodleSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mood_tag = db.Column(db.String(50))
    figjam_url = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------
# Emotional Chatbot
# ---------------------------

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    sender = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------
# Financial Literacy
# ---------------------------

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    type = db.Column(db.String(10))
    description = db.Column(db.String(255))
    date = db.Column(db.Date, default=date.today)

class SavingGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    label = db.Column(db.String(100))
    target_amount = db.Column(db.Float)
    current_amount = db.Column(db.Float, default=0)

# ---------------------------
# Personal Motivation & Progress
# ---------------------------

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    badge_name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    date_awarded = db.Column(db.DateTime, default=datetime.utcnow)

class Streak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_active_date = db.Column(db.Date)
    current_streak = db.Column(db.Integer)

# ---------------------------
# Quizzes (Psychometric / Self-Discovery)
# ---------------------------

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    question_text = db.Column(db.Text)
    question_type = db.Column(db.String(20))

class UserAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    answer_text = db.Column(db.Text)

# ---------------------------
# Health and Habits
# ---------------------------

class HealthTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date, default=date.today)

class WaterLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    count = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, default=date.today)

class HealthStreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    current_streak = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.Date, default=date.today)

class ScreenTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hours = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today)

# ---------------------------
# Safety Education
# ---------------------------

class SafetyModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255))
    content_url = db.Column(db.String(255))

class UserModuleProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('safety_module.id'))
    completed = db.Column(db.Boolean, default=False)

# ---------------------------
# English Communication
# ---------------------------

class EnglishPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.String(255))

class UserPromptResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    prompt_id = db.Column(db.Integer, db.ForeignKey('english_prompt.id'))
    response_text = db.Column(db.Text)
    date = db.Column(db.Date, default=date.today)

# ---------------------------
# Notifications & Messaging
# ---------------------------

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)
    pre_approved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------
# Admin Dashboard Metrics
# ---------------------------

class DashboardMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active_kids = db.Column(db.Integer)
    average_session_duration = db.Column(db.Float)  
    top_features = db.Column(db.Text) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
