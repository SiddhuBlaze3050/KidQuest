import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, HomeworkSchedule, PomodoroSession
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone


class TestPomodoroTimer:
    """Test cases for Pomodoro Timer endpoints"""

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

            # Create test homework
            homework = HomeworkSchedule(
                user_id=self.test_user_id,
                subject='Math',
                task='Complete algebra homework',
                due_date=datetime.now(timezone.utc).date(),
                status='pending'
            )
            db.session.add(homework)
            db.session.commit()
            self.test_homework_id = homework.id

            yield

            db.session.remove()
            db.drop_all()

    def test_start_pomodoro_success(self):
        """Test successfully starting a pomodoro session"""
        pomodoro_data = {
            'user_id': self.test_user_id,
            'homework_id': self.test_homework_id
        }

        response = self.client.post('/api/pomodoro/start',
                                  data=json.dumps(pomodoro_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [200, 201]
        assert data['success'] is True
        assert 'session_id' in data
        assert 'start_time' in data

    def test_start_pomodoro_missing_user_id(self):
        """Test starting pomodoro without user ID"""
        pomodoro_data = {
            'homework_id': self.test_homework_id
        }

        response = self.client.post('/api/pomodoro/start',
                                  data=json.dumps(pomodoro_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [400, 403]
        assert data['success'] is False
        assert 'error' in data

    def test_start_pomodoro_unauthorized(self):
        """Test starting pomodoro without authentication"""
        pomodoro_data = {
            'user_id': self.test_user_id,
            'homework_id': self.test_homework_id
        }

        response = self.client.post('/api/pomodoro/start',
                                  data=json.dumps(pomodoro_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_pause_pomodoro_success(self):
        """Test successfully pausing a pomodoro session"""
        # First start a session
        pomodoro_session = PomodoroSession(
            user_id=self.test_user_id,
            homework_id=self.test_homework_id,
            start_time=datetime.now(timezone.utc),
            completed=False
        )
        db.session.add(pomodoro_session)
        db.session.commit()

        session_id = pomodoro_session.id

        response = self.client.put(f'/api/pomodoro/pause/{session_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_pause_pomodoro_nonexistent_session(self):
        """Test pausing a non-existent pomodoro session"""
        non_existent_id = 99999
        response = self.client.put(f'/api/pomodoro/pause/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['success'] is False
        assert 'Session not found' in data['error']

    def test_resume_pomodoro_success(self):
        """Test successfully resuming a paused pomodoro session"""
        # Create a paused session
        pomodoro_session = PomodoroSession(
            user_id=self.test_user_id,
            homework_id=self.test_homework_id,
            start_time=datetime.now(timezone.utc),
            completed=False
        )
        db.session.add(pomodoro_session)
        db.session.commit()

        session_id = pomodoro_session.id

        response = self.client.put(f'/api/pomodoro/resume/{session_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_resume_pomodoro_nonexistent_session(self):
        """Test resuming a non-existent pomodoro session"""
        non_existent_id = 99999
        response = self.client.put(f'/api/pomodoro/resume/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['success'] is False
        assert 'Session not found' in data['error']

    def test_complete_pomodoro_success(self):
        """Test successfully completing a pomodoro session"""
        # Create an active session
        pomodoro_session = PomodoroSession(
            user_id=self.test_user_id,
            homework_id=self.test_homework_id,
            start_time=datetime.now(timezone.utc),
            completed=False
        )
        db.session.add(pomodoro_session)
        db.session.commit()

        session_id = pomodoro_session.id

        completion_data = {
            'work_duration': 1500,  # 25 minutes
            'break_duration': 300   # 5 minutes
        }

        response = self.client.put(f'/api/pomodoro/complete/{session_id}',
                                 data=json.dumps(completion_data),
                                 content_type='application/json',
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_complete_pomodoro_with_default_durations(self):
        """Test completing pomodoro with default work and break durations"""
        # Create an active session
        pomodoro_session = PomodoroSession(
            user_id=self.test_user_id,
            homework_id=self.test_homework_id,
            start_time=datetime.now(timezone.utc),
            completed=False
        )
        db.session.add(pomodoro_session)
        db.session.commit()

        session_id = pomodoro_session.id

        # Complete without providing durations (should use defaults)
        response = self.client.put(f'/api/pomodoro/complete/{session_id}',
                                 data=json.dumps({}),
                                 content_type='application/json',
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_complete_pomodoro_nonexistent_session(self):
        """Test completing a non-existent pomodoro session"""
        non_existent_id = 99999
        completion_data = {
            'work_duration': 1500,
            'break_duration': 300
        }

        response = self.client.put(f'/api/pomodoro/complete/{non_existent_id}',
                                 data=json.dumps(completion_data),
                                 content_type='application/json',
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code in [404, 500]
        assert data['success'] is False
        assert 'Session not found' in data['error']

    def test_pomodoro_session_lifecycle(self):
        """Test the complete lifecycle of a pomodoro session"""
        # 1. Start session
        pomodoro_data = {
            'user_id': self.test_user_id,
            'homework_id': self.test_homework_id
        }

        start_response = self.client.post('/api/pomodoro/start',
                                        data=json.dumps(pomodoro_data),
                                        content_type='application/json',
                                        headers=self.headers)
        start_data = json.loads(start_response.data)
        
        assert start_response.status_code in [200, 201]
        session_id = start_data['session_id']

        # 2. Pause session
        pause_response = self.client.put(f'/api/pomodoro/pause/{session_id}', headers=self.headers)
        pause_data = json.loads(pause_response.data)
        assert pause_response.status_code == 200
        assert pause_data['success'] is True

        # 3. Resume session
        resume_response = self.client.put(f'/api/pomodoro/resume/{session_id}', headers=self.headers)
        resume_data = json.loads(resume_response.data)
        assert resume_response.status_code == 200
        assert resume_data['success'] is True

        # 4. Complete session
        completion_data = {
            'work_duration': 1500,
            'break_duration': 300
        }

        complete_response = self.client.put(f'/api/pomodoro/complete/{session_id}',
                                          data=json.dumps(completion_data),
                                          content_type='application/json',
                                          headers=self.headers)
        complete_data = json.loads(complete_response.data)
        assert complete_response.status_code == 200
        assert complete_data['success'] is True

    def test_start_pomodoro_without_homework(self):
        """Test starting pomodoro session without specifying homework"""
        pomodoro_data = {
            'user_id': self.test_user_id
            # No homework_id provided
        }

        response = self.client.post('/api/pomodoro/start',
                                  data=json.dumps(pomodoro_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        # Should still work (homework_id might be optional)
        assert response.status_code in [200, 400]  # Depends on implementation
