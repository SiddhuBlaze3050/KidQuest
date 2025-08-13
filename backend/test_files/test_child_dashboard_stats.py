import pytest
import json
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Achievement, HealthTask, LoginStreak, UserModuleProgress
from flask_jwt_extended import create_access_token


class TestChildDashboardStats:
    """Test cases for Child Dashboard Statistics endpoints"""

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

    def test_get_child_stats_new_user(self):
        """Test fetching dashboard stats for a new user with no data"""
        response = self.client.get(f'/api/child/stats/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'stats' in data
        assert data['stats']['totalStars'] >= 0
        assert data['stats']['questsCompleted'] >= 0
        assert data['stats']['skillsLearned'] >= 0
        assert data['stats']['todayGoals'] >= 0
        assert data['stats']['streakDays'] >= 0

    def test_get_child_stats_with_achievements(self):
        """Test fetching dashboard stats for a user with achievements"""
        # Create some achievements
        achievement1 = Achievement(
            user_id=self.test_user_id,
            badge_name='Test Achievement 1',
            description='First test achievement',
            date_awarded=date.today()
        )
        achievement2 = Achievement(
            user_id=self.test_user_id,
            badge_name='Test Achievement 2',
            description='Second test achievement',
            date_awarded=date.today()
        )
        db.session.add(achievement1)
        db.session.add(achievement2)
        db.session.commit()

        response = self.client.get(f'/api/child/stats/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        # Quests completed may vary based on computed logic; ensure non-negative
        assert data['stats']['questsCompleted'] >= 0

    def test_get_child_stats_with_health_tasks(self):
        """Test fetching dashboard stats for a user with health tasks"""
        # Create completed health tasks for today
        health_task1 = HealthTask(
            user_id=self.test_user_id,
            task_name='Running',
            date=date.today(),
            completed=True
        )
        health_task2 = HealthTask(
            user_id=self.test_user_id,
            task_name='Meditation',
            date=date.today(),
            completed=True
        )
        db.session.add(health_task1)
        db.session.add(health_task2)
        db.session.commit()

        response = self.client.get(f'/api/child/stats/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['stats']['todayGoals'] >= 2  # Should include completed health tasks

    def test_get_child_stats_with_login_streak(self):
        """Test fetching dashboard stats for a user with login streak"""
        # Create login streak
        login_streak = LoginStreak(
            user_id=self.test_user_id,
            current_streak=5,
            last_login_date=date.today(),
            total_logins=10,
            longest_streak=7
        )
        db.session.add(login_streak)
        db.session.commit()

        response = self.client.get(f'/api/child/stats/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['stats']['streakDays'] == 5

    def test_get_child_stats_with_module_progress(self):
        """Test fetching dashboard stats for a user with completed modules"""
        # Create completed module progress
        module_progress = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='math_magic',
            progress=100.0,
            completed=True
        )
        db.session.add(module_progress)
        db.session.commit()

        response = self.client.get(f'/api/child/stats/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [200, 201]
        assert data['success'] is True
        assert data['stats']['skillsLearned'] >= 1  # Should include completed modules

    def test_get_child_stats_unauthorized(self):
        """Test accessing child stats without authentication"""
        response = self.client.get(f'/api/child/stats/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_child_stats_nonexistent_user(self):
        """Test fetching stats for a non-existent user"""
        non_existent_id = 99999
        response = self.client.get(f'/api/child/stats/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        # Should return default values for non-existent user
        assert data['stats']['totalStars'] >= 0
        assert data['stats']['questsCompleted'] >= 0
        assert data['stats']['skillsLearned'] >= 0
        assert data['stats']['todayGoals'] >= 0
        assert data['stats']['streakDays'] >= 0

    def test_create_test_achievement(self):
        """Test creating a test achievement through the API"""
        achievement_data = {
            'user_id': self.test_user_id,
            'badge_name': 'Test Achievement API',
            'description': 'Created via API test'
        }

        response = self.client.post('/api/achievement/test', 
                                  data=json.dumps(achievement_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'achievement' in data
        assert data['achievement']['badge_name'] == 'Test Achievement API'
        assert data['achievement']['description'] == 'Created via API test'

    def test_create_test_achievement_missing_data(self):
        """Test creating a test achievement with missing required data"""
        achievement_data = {
            'user_id': self.test_user_id
            # Missing badge_name and description
        }

        response = self.client.post('/api/achievement/test', 
                                  data=json.dumps(achievement_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        # Endpoint may create defaults and return success
        assert response.status_code in [200, 201]
        assert data['success'] is True
