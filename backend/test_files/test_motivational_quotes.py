import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
from flask_jwt_extended import create_access_token
requests_mock = pytest.importorskip("requests_mock")


class TestMotivationalQuotes:
    """Test cases for Motivational Quotes endpoint"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database and create test data"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()

            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hashed_password',
                role='child'
            )
            db.session.add(test_user)
            db.session.commit()

            self.test_user_id = test_user.id
            self.client = app.test_client()
            
            # Create JWT token for authentication
            self.access_token = create_access_token(identity=str(self.test_user_id))
            self.headers = {'Authorization': f'Bearer {self.access_token}'}

            yield

            db.session.remove()
            db.drop_all()

    @requests_mock.Mocker()
    def test_get_motivational_quote_success(self, m):
        """Test successful retrieval of motivational quote from external API"""
        # Mock the external API response
        mock_response = [{"q": "Believe in yourself", "a": "Anonymous"}]
        m.get('https://zenquotes.io/api/today', json=mock_response)

        response = self.client.get(f'/api/quote/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['quote'] == "Believe in yourself — Anonymous"

    @requests_mock.Mocker()
    def test_get_motivational_quote_api_failure(self, m):
        """Test handling of external API failure with fallback quote"""
        # Mock API failure
        m.get('https://zenquotes.io/api/today', status_code=500)

        response = self.client.get(f'/api/quote/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200  # Still returns 200 with fallback
        assert data['success'] is False
        assert data['quote'] == "Believe in yourself and magic will happen! ✨"

    def test_get_motivational_quote_unauthorized(self):
        """Test accessing quotes without authentication"""
        response = self.client.get(f'/api/quote/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    @requests_mock.Mocker()
    def test_get_motivational_quote_invalid_response(self, m):
        """Test handling of invalid API response format"""
        # Mock invalid response format
        m.get('https://zenquotes.io/api/today', json={"invalid": "format"})

        response = self.client.get(f'/api/quote/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200  # Still returns 200 with fallback
        assert data['success'] is False
        assert data['quote'] == "Believe in yourself and magic will happen! ✨"
