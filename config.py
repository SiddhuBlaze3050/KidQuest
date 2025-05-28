import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'se_project_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    OPENAI_API_KEY = "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"