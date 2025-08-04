import os
from datetime import timedelta

class TestConfig:
    """Configuration specifically for testing to avoid database pollution"""
    SECRET_KEY = 'test-secret-key'
    
    # Backend directory path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Use separate test database directory
    TEST_INSTANCE_DIR = os.path.join(BASE_DIR, 'test_instance')
    TEST_DATABASE_PATH = os.path.join(TEST_INSTANCE_DIR, 'test.db')
    
    # Completely isolated test database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Enable testing mode
    TESTING = True
    
    # JWT Configuration for testing
    JWT_SECRET_KEY = 'test-jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_ALGORITHM = 'HS256'
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Test API keys (can be dummy values)
    GROQ_API_KEY = "test-groq-key"
    OPENROUTER_API_KEY = "test-openrouter-key"
    OPENROUTER_API_URL = "https://test-openrouter.ai/api/v1/chat/completions"
