import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'se_project_key')
    
    # Backend directory path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    DATABASE_PATH = os.path.join(INSTANCE_DIR, 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GROQ_API_KEY = "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"
    OPENROUTER_API_KEY = "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"
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # JWT Configuration - Improved security and longer sessions for children
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-super-secret-jwt-key-here-change-this-in-production-32-chars')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)  # 8 hours for children's learning sessions
    JWT_ALGORITHM = 'HS256'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_CSRF_METHODS = []  # Disable CSRF protection for JWT
    JWT_ERROR_MESSAGE_KEY = 'error'