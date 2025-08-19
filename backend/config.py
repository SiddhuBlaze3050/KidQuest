import os
from datetime import timedelta

class Config:
    # Secret keys from environment (set in Render Dashboard)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kidquest-secret-key')

    # Backend directory path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Ensure instance directory exists (important for Render)
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    os.makedirs(INSTANCE_DIR, exist_ok=True)

    # Database configuration - FREE TIER SETUP
    # SQLite on ephemeral storage (resets on each deployment)
    DATABASE_PATH = os.path.join(INSTANCE_DIR, 'app.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{DATABASE_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLite Configuration optimized for free tier
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': 300,  # Recycle connections every 5 minutes
        'pool_pre_ping': True,
        'connect_args': {'timeout': 20}  # SQLite connection timeout
    }
    
    # FREE TIER NOTES:
    # - Database resets on each deployment (good for testing)
    # - Service spins down after 15 minutes of inactivity
    # - Perfect for development and demonstration

    # API Keys (better stored in Render environment variables)
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Production settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'team-kidquest-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)  # 8 hours for children's learning sessions
    JWT_ALGORITHM = 'HS256'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_CSRF_METHODS = []  # Disable CSRF protection for JWT
    JWT_ERROR_MESSAGE_KEY = 'error'
