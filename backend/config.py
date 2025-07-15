import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'se_project_key')
    
    # Get the directory where this config file is located (backend directory)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Construct database path relative to backend directory
    DATABASE_PATH = os.path.join(BASE_DIR, 'instance', 'app.db')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GROQ_API_KEY = "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"
    OPENROUTER_API_KEY = "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"
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"