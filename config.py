import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'se_project_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GROQ_API_KEY = "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"