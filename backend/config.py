import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'se_project_key')
    
    # Backend directory path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    DATABASE_PATH = os.path.join(INSTANCE_DIR, 'app.db')
    # Use a file-based SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 1800))  # 30 minutes
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 days
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    LOGIN_RATE_LIMIT = os.environ.get('LOGIN_RATE_LIMIT', '5 per 5 minutes')
    REGISTER_RATE_LIMIT = os.environ.get('REGISTER_RATE_LIMIT', '3 per hour')
    
    GROQ_API_KEY = "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"
    OPENROUTER_API_KEY = "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"
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"