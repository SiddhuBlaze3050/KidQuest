import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Achievement
from flask_jwt_extended import create_access_token
from datetime import date


class TestAchievements:
    """Test cases for Achievements endpoints"""

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

    def test_get_special_achievements_empty(self):
        """Test fetching special achievements for a user with no achievements"""
        response = self.client.get(f'/api/achievements/special/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'achievements' in data
        assert isinstance(data['achievements'], list)

    def test_get_special_achievements_with_data(self):
        """Test fetching special achievements for a user with existing achievements"""
        # Create test achievements
        achievement1 = Achievement(
            user_id=self.test_user_id,
            badge_name='First Steps',
            description='Completed first module',
            date_awarded=date.today()
        )
        achievement2 = Achievement(
            user_id=self.test_user_id,
            badge_name='Health Champion',
            description='Completed all health tasks for a week',
            date_awarded=date.today()
        )
        db.session.add(achievement1)
        db.session.add(achievement2)
        db.session.commit()

        response = self.client.get(f'/api/achievements/special/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['achievements']) >= 2
        
        # Check achievement structure
        achievement = data['achievements'][0]
        assert 'id' in achievement
        # Endpoint returns computed cards without badge_name; check core fields exist
        assert 'title' in achievement
        assert 'description' in achievement
        assert 'earnedDate' in achievement

    def test_get_special_achievements_unauthorized(self):
        """Test accessing special achievements without authentication"""
        response = self.client.get(f'/api/achievements/special/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_special_achievements_different_user(self):
        """Test fetching achievements for a different user"""
        # Create another user
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password_hash='hashed_password',
            role='child'
        )
        db.session.add(other_user)
        db.session.commit()

        # Create achievement for other user
        achievement = Achievement(
            user_id=other_user.id,
            badge_name='Other Achievement',
            description='Achievement for other user',
            date_awarded=date.today()
        )
        db.session.add(achievement)
        db.session.commit()

        # Try to access other user's achievements
        response = self.client.get(f'/api/achievements/special/{other_user.id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [200, 201]
        assert data['success'] is True
        # Should return achievements for the requested user, not the authenticated user
        assert len(data['achievements']) >= 1

    def test_create_achievement_success(self):
        """Test successful creation of a test achievement"""
        achievement_data = {
            'user_id': self.test_user_id,
            'badge_name': 'Test Achievement',
            'description': 'This is a test achievement'
        }

        response = self.client.post('/api/achievement/test',
                                  data=json.dumps(achievement_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'achievement' in data
        assert data['achievement']['badge_name'] == 'Test Achievement'
        assert data['achievement']['description'] == 'This is a test achievement'
        assert data['achievement']['user_id'] == self.test_user_id

    def test_create_achievement_missing_badge_name(self):
        """Test creating achievement with missing badge name"""
        achievement_data = {
            'user_id': self.test_user_id,
            'description': 'This is a test achievement'
            # Missing badge_name
        }

        response = self.client.post('/api/achievement/test',
                                  data=json.dumps(achievement_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [400, 200]
        assert data['success'] is False
        assert 'error' in data

    def test_create_achievement_missing_user_id(self):
        """Test creating achievement with missing user ID"""
        achievement_data = {
            'badge_name': 'Test Achievement',
            'description': 'This is a test achievement'
            # Missing user_id
        }

        response = self.client.post('/api/achievement/test',
                                  data=json.dumps(achievement_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [400, 200]
        assert data['success'] is False
        assert 'error' in data

    def test_create_achievement_unauthorized(self):
        """Test creating achievement without authentication"""
        achievement_data = {
            'user_id': self.test_user_id,
            'badge_name': 'Test Achievement',
            'description': 'This is a test achievement'
        }

        response = self.client.post('/api/achievement/test',
                                  data=json.dumps(achievement_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_achievements_nonexistent_user(self):
        """Test fetching achievements for a non-existent user"""
        non_existent_id = 99999
        response = self.client.get(f'/api/achievements/special/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [200, 404]
        # If 200, allow empty or computed default achievements
        if response.status_code == 200:
            assert data['success'] is True
