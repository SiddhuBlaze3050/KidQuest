import pytest
import json
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, LoginStreak
from flask_jwt_extended import create_access_token


class TestLoginStreak:
    """Test cases for Login Streak endpoints"""

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

    def test_get_login_streak_new_user(self):
        """Test fetching login streak for a new user with no streak record"""
        response = self.client.get(f'/api/login-streak/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['current_streak'] == 0
        assert data['total_logins'] == 0
        assert data['longest_streak'] == 0
        assert data['last_login_date'] is None

    def test_get_login_streak_existing_user(self):
        """Test fetching login streak for a user with existing streak record"""
        # Create login streak record
        login_streak = LoginStreak(
            user_id=self.test_user_id,
            current_streak=5,
            last_login_date=date.today(),
            total_logins=10,
            longest_streak=7
        )
        db.session.add(login_streak)
        db.session.commit()

        response = self.client.get(f'/api/login-streak/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['current_streak'] == 5
        assert data['total_logins'] == 10
        assert data['longest_streak'] == 7
        assert data['last_login_date'] == date.today().isoformat()

    def test_get_login_streak_unauthorized(self):
        """Test accessing login streak without authentication"""
        response = self.client.get(f'/api/login-streak/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_login_streak_nonexistent_user(self):
        """Test fetching login streak for a non-existent user"""
        non_existent_id = 99999
        response = self.client.get(f'/api/login-streak/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        # Should still return success with default values
        assert response.status_code == 200
        assert data['success'] is True
        assert data['current_streak'] == 0
        assert data['total_logins'] == 0
        assert data['longest_streak'] == 0
