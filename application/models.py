from datetime import datetime
from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.sqlite import JSON
from .database import db

class UsersRoles(db.Model):
    tablename = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))

class Role(db.Model, RoleMixin):
    tablename = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin): 
    tablename = 'user'
    d = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    # Relationships
    roles = db.relationship(
        'Role', secondary='users_roles', backref=db.backref('users', lazy='dynamic')
    )
    progress_logs = db.relationship(
        'ProgressLog', backref='user', cascade='all,delete', lazy=True
    )
    reminders = db.relationship(
        'Reminder', backref='user', cascade='all,delete', lazy=True
    )
     
    class LifeSkill(db.Model):
        tablename = 'life_skill'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        description = db.Column(db.Text(), nullable=False)
        age_min = db.Column(db.Integer(), nullable=False)
        age_max = db.Column(db.Integer(), nullable=False)
        display_order = db.Column(db.Integer(), default=0)

        activities = db.relationship(
            'Activity', backref='life_skill', cascade='all,delete', lazy=True
        )

    class Activity(db.Model):
        tablename = 'activity'
        id = db.Column(db.Integer(), primary_key=True)
        life_skill_id = db.Column(
            db.Integer(), db.ForeignKey('life_skill.id'), nullable=False
        )
        name = db.Column(db.String(150), nullable=False)
        instructions = db.Column(db.Text(), nullable=False)
        content = db.Column(JSON, nullable=True)
        sequence = db.Column(db.Integer(), default=0)

        progress_logs = db.relationship(
            'ProgressLog', backref='activity', cascade='all,delete', lazy=True
        )

    class ProgressLog(db.Model):
        tablename = 'progress_log'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
        activity_id = db.Column(
            db.Integer(), db.ForeignKey('activity.id'), nullable=False
        )
        timestamp = db.Column(
            db.DateTime(), default=datetime.utcnow, nullable=False
        )
        score = db.Column(db.Float(), nullable=True)
        completed = db.Column(db.Boolean(), default=False, nullable=False)
        details = db.Column(db.Text(), nullable=True)

    class Reminder(db.Model):
        tablename = 'reminder'
        