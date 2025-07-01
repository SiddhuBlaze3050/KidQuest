import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'se_project_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GROQ_API_KEY = "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"
    OPENROUTER_API_KEY = "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"
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"