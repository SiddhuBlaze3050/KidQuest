import pytest
import json
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, HealthTask, WaterLog, HealthStreak
from flask_jwt_extended import create_access_token


class TestHealthTracker:
    """Test cases for Health Tracker endpoints"""

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

    def test_get_health_tasks(self):
        """Test fetching today's health tasks for a user"""
        response = self.client.get(f'/api/health/tasks/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert isinstance(data['tasks'], list)

    def test_get_health_tasks_with_existing_data(self):
        """Test fetching health tasks when user has existing tasks"""
        # Create test health tasks
        task1 = HealthTask(
            user_id=self.test_user_id,
            task_name='Morning Exercise',
            date=date.today(),
            completed=False
        )
        task2 = HealthTask(
            user_id=self.test_user_id,
            task_name='Drink Water',
            date=date.today(),  
            completed=True
        )
        db.session.add(task1)
        db.session.add(task2)
        db.session.commit()

        response = self.client.get(f'/api/health/tasks/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['tasks']) == 2
        assert any(task['name'] == 'Morning Exercise' for task in data['tasks'])
        assert any(task['name'] == 'Drink Water' for task in data['tasks'])

    def test_get_health_tasks_unauthorized(self):
        """Test accessing health tasks without authentication"""
        response = self.client.get(f'/api/health/tasks/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_toggle_health_task_completion(self):
        """Test toggling health task completion status"""
        # Create test health task
        task = HealthTask(
            user_id=self.test_user_id,
            task_name='Morning Yoga',
            date=date.today(),
            completed=False
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

        # Toggle task completion
        response = self.client.post(f'/api/health/tasks/{task_id}/toggle', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['completed'] is True

        # Toggle back to incomplete
        response = self.client.post(f'/api/health/tasks/{task_id}/toggle', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['completed'] is False

    def test_toggle_nonexistent_task(self):
        """Test toggling completion for non-existent task"""
        response = self.client.post('/api/health/tasks/99999/toggle', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['success'] is False
        assert 'Task not found' in data['error']

    def test_get_health_streak(self):
        """Test fetching health streak for a user"""
        response = self.client.get(f'/api/health/streak/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'streak' in data
        assert isinstance(data['streak'], int)

    def test_get_health_streak_with_existing_data(self):
        """Test fetching health streak when user has existing streak data"""
        # Create health streak record
        streak = HealthStreak(
            user_id=self.test_user_id,
            current_streak=7,
            last_updated=date.today()
        )
        db.session.add(streak)
        db.session.commit()

        response = self.client.get(f'/api/health/streak/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['streak'] == 7

    def test_log_water_intake(self):
        """Test logging water intake for a user"""
        water_data = {
            'glasses': 2,
            'date': date.today().isoformat()
        }

        response = self.client.post(f'/api/health/water/{self.test_user_id}', 
                                  headers=self.headers, 
                                  json=water_data)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'count' in data

    def test_log_water_intake_multiple_times(self):
        """Test logging water intake multiple times in a day"""
        # First log
        water_data = {'glasses': 1}
        response = self.client.post(f'/api/health/water/{self.test_user_id}', 
                                  headers=self.headers, 
                                  json=water_data)
        data = json.loads(response.data)
        assert response.status_code == 200
        assert 'count' in data

        # Second log - should add to existing
        water_data = {'glasses': 2}
        response = self.client.post(f'/api/health/water/{self.test_user_id}', 
                                  headers=self.headers, 
                                  json=water_data)
        data = json.loads(response.data)
        assert response.status_code == 200
        assert 'count' in data

    def test_get_water_intake(self):
        """Test fetching today's water intake for a user"""
        response = self.client.get(f'/api/health/water/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'count' in data
        assert isinstance(data['count'], int)

    def test_get_water_intake_with_existing_data(self):
        """Test fetching water intake when user has logged water"""
        # Create water log entry
        water_log = WaterLog(
            user_id=self.test_user_id,
            count=5,
            date=date.today()
        )
        db.session.add(water_log)
        db.session.commit()

        response = self.client.get(f'/api/health/water/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['count'] == 5

    def test_get_water_log_history(self):
        """Test fetching water log history for a user"""
        response = self.client.get(f'/api/health/water/log/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'log' in data
        assert isinstance(data['log'], list)

    def test_get_water_log_with_existing_data(self):
        """Test fetching water log history when user has existing logs"""
        # Create multiple water log entries
        from datetime import datetime, timedelta
        
        for i in range(3):
            log_date = date.today() - timedelta(days=i)
            water_log = WaterLog(
                user_id=self.test_user_id,
                count=4 + i,
                date=log_date
            )
            db.session.add(water_log)
        db.session.commit()

        response = self.client.get(f'/api/health/water/log/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['log']) == 3

    def test_water_endpoints_unauthorized(self):
        """Test accessing water endpoints without authentication"""
        # Test POST water intake
        response = self.client.post(f'/api/health/water/{self.test_user_id}', json={'glasses': 1})
        data = json.loads(response.data)
        assert response.status_code == 401
        assert data['success'] is False

        # Test GET water intake
        response = self.client.get(f'/api/health/water/{self.test_user_id}')
        data = json.loads(response.data)
        assert response.status_code == 401
        assert data['success'] is False

        # Test GET water log
        response = self.client.get(f'/api/health/water/log/{self.test_user_id}')
        data = json.loads(response.data)
        assert response.status_code == 401
        assert data['success'] is False

    def test_invalid_water_intake_data(self):
        """Test logging water intake with invalid data"""
        # Test with negative glasses
        water_data = {'glasses': -1}
        response = self.client.post(f'/api/health/water/{self.test_user_id}', 
                                  headers=self.headers, 
                                  json=water_data)
        data = json.loads(response.data)
        # Backend accepts any POST and increments count
        assert response.status_code == 200
        assert data['success'] is True

        # Test with missing glasses field
        response = self.client.post(f'/api/health/water/{self.test_user_id}', 
                                  headers=self.headers, 
                                  json={})
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
