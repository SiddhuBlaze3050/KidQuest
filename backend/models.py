from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time, UTC, timezone, timedelta

# Define India Standard Time (IST) - UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

db = SQLAlchemy()

def get_current_ist_time():
    """Get current time in India Standard Time"""
    return datetime.now(IST)

def get_current_utc_time():
    """Get current time in UTC"""
    return datetime.now(UTC)


# ----------------------------
# User Model
# ----------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'parent', 'child', 'teacher', or 'admin'
    
   

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
    end_time = db.Column(db.DateTime, nullable=True)  # When session actually ended
    work_duration = db.Column(db.Integer, default=0)  # Actual work time in seconds
    break_duration = db.Column(db.Integer, default=0)  # Actual break time in seconds
    completed = db.Column(db.Boolean, default=False)


class HomeworkSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(100))
    task = db.Column(db.String(255))
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending') # pending, in-progress, completed
    assigned_by_teacher = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Teacher who assigned this task
    created_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # When task was created (IST)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time, onupdate=get_current_ist_time)  # For tracking status changes (IST)
    pomodoro_sessions = db.relationship('PomodoroSession', backref='homework', lazy=True,cascade="all, delete-orphan")


# ---------------------------
# Creative & Doodling
# ---------------------------

class DoodleSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text, nullable=True)
    ref_image_path = db.Column(db.String(255), nullable=True)  # Reference image for inspiration
    ref_image_title = db.Column(db.String(255), nullable=True)  # Title of reference image
    save_image_path = db.Column(db.String(255), nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time
    time_taken = db.Column(db.Integer, nullable=True)  # Time in seconds
    start_time = db.Column(db.DateTime, nullable=True)  # When drawing started

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    prompt_used = db.Column(db.Text, nullable=True)  # The prompt that inspired this story
    created_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time
    updated_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time, onupdate=get_current_ist_time)  # IST time 

# ---------------------------
# Emotional Chatbot
# ---------------------------

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mood_tag = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=get_current_ist_time)  # IST time

    interactions = db.relationship('LLMInteractions', backref='session', cascade="all, delete-orphan", lazy=True)
    summary = db.Column(db.Text, nullable=True)

class LLMInteractions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_session.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    user_timestamp = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time
    llm_response = db.Column(db.Text, nullable=True)
    llm_timestamp = db.Column(db.DateTime)
    mood_tag = db.Column(db.String(50), nullable=True)

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
    date_awarded = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time


# ---------------------------
# Quizzes (Psychometric / Self-Discovery)
# ---------------------------

class PsychometricTestResult(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    taken_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time

    learning_style = db.Column(db.String(50))
    personality_type = db.Column(db.String(50))
    top_interest = db.Column(db.String(50))

    concentration_level = db.Column(db.Float)
    memory_strength = db.Column(db.Float)

    detailed_scores = db.Column(db.JSON)
    personality_breakdown = db.Column(db.JSON)
    duration_seconds = db.Column(db.Float)
    feedback = db.Column(db.Text)
    def __repr__(self):
        return f'<TestResult Child:{self.child_id} on {self.taken_at:%Y-%m-%d}>'


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

class LoginStreak(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    current_streak = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.Date, default=date.today)
    total_logins = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)

class LoginHistory(db.Model):
    """Track individual login events for historical analytics"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_date = db.Column(db.Date, default=date.today)
    login_time = db.Column(db.DateTime, default=datetime.now)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Index for efficient date-based queries
    __table_args__ = (
        db.Index('idx_login_history_date', 'login_date'),
        db.Index('idx_login_history_user_date', 'user_id', 'login_date'),
    )

class ScreenTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    hours = db.Column(db.Float)
    date = db.Column(db.Date, default=date.today)

# ---------------------------
# Safety Education
# ---------------------------

class UserModuleProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    module_id = db.Column(db.Integer)  # Can be skipped or just used as a static mapping
    submodule_id = db.Column(db.Integer)
    module_name = db.Column(db.String(100))  # add this if not already
    submodule_name = db.Column(db.String(100))
    progress = db.Column(db.Float, default=0.0)  # for tracking % 
    completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time, onupdate=get_current_ist_time)  # For tracking completion dates (IST)
                          


# ---------------------------
# Notifications & Messaging
# ---------------------------

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time


# ---------------------------
# Admin Dashboard Metrics
# ---------------------------

class DashboardMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active_kids = db.Column(db.Integer)
    average_session_duration = db.Column(db.Float)  
    top_features = db.Column(db.Text) 
    created_at = db.Column(db.DateTime(timezone=True), default=get_current_ist_time)  # IST time



