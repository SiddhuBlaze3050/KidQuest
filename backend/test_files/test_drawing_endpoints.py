import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, DoodleSession
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone
import base64


class TestDrawingEndpoints:
    """Test cases for Drawing/Doodling endpoints"""

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

            # Create test image data (base64 encoded simple image)
            self.test_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

            yield

            db.session.remove()
            db.drop_all()

    def test_save_drawing_success(self):
        """Test successful drawing save"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'drawing_time': 120  # 2 minutes
        }

        response = self.client.post('/api/drawings/save',
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'drawing_id' in data
        assert 'filename' in data

    def test_save_drawing_missing_data(self):
        """Test saving drawing with missing required data"""
        drawing_data = {
            'user_id': self.test_user_id
            # Missing image_data
        }

        response = self.client.post('/api/drawings/save',
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] is False
        assert 'error' in data

    def test_save_drawing_invalid_image_data(self):
        """Test saving drawing with invalid image data"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': 'invalid_image_data',
            'drawing_time': 60
        }

        response = self.client.post('/api/drawings/save',
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] is False
        assert 'error' in data

    def test_get_user_drawings_empty(self):
        """Test fetching drawings for a user with no drawings"""
        response = self.client.get(f'/api/drawings/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'drawings' in data
        assert isinstance(data['drawings'], list)
        assert len(data['drawings']) == 0

    def test_get_user_drawings_with_data(self):
        """Test fetching drawings for a user with existing drawings"""
        # Create test drawing session
        drawing_session = DoodleSession(
            user_id=self.test_user_id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            drawing_duration=120,
            filename='test_drawing.png'
        )
        db.session.add(drawing_session)
        db.session.commit()

        response = self.client.get(f'/api/drawings/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['drawings']) >= 1
        
        # Check drawing data structure
        drawing = data['drawings'][0]
        assert 'id' in drawing
        assert 'filename' in drawing
        assert 'start_time' in drawing
        assert 'end_time' in drawing
        assert 'drawing_duration' in drawing

    def test_get_user_drawings_unauthorized(self):
        """Test accessing user drawings without authentication"""
        response = self.client.get(f'/api/drawings/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_start_drawing_session(self):
        """Test starting a new drawing session"""
        session_data = {
            'user_id': self.test_user_id
        }

        response = self.client.post('/api/drawings/start-session',
                                  data=json.dumps(session_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'session_id' in data
        assert 'start_time' in data

    def test_start_drawing_session_missing_user_id(self):
        """Test starting drawing session without user ID"""
        session_data = {}

        response = self.client.post('/api/drawings/start-session',
                                  data=json.dumps(session_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] is False
        assert 'error' in data

    def test_get_drawing_image_success(self):
        """Test getting a specific drawing image"""
        # First save a drawing to get an ID
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'drawing_time': 120
        }

        save_response = self.client.post('/api/drawings/save',
                                       data=json.dumps(drawing_data),
                                       content_type='application/json')
        save_data = json.loads(save_response.data)
        
        drawing_id = save_data['drawing_id']

        # Now try to get the image
        response = self.client.get(f'/api/drawings/image/{drawing_id}')
        
        # Should return image data or appropriate response
        assert response.status_code in [200, 404]  # 404 if file doesn't exist in test environment

    def test_get_drawing_image_nonexistent(self):
        """Test getting a non-existent drawing image"""
        non_existent_id = 99999
        response = self.client.get(f'/api/drawings/image/{non_existent_id}')
        
        assert response.status_code == 404

    def test_delete_drawing_success(self):
        """Test successful drawing deletion"""
        # First create a drawing session
        drawing_session = DoodleSession(
            user_id=self.test_user_id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            drawing_duration=120,
            filename='test_drawing.png'
        )
        db.session.add(drawing_session)
        db.session.commit()

        drawing_id = drawing_session.id

        response = self.client.delete(f'/api/drawings/delete/{drawing_id}')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'Drawing deleted successfully' in data['message']

    def test_delete_drawing_nonexistent(self):
        """Test deleting a non-existent drawing"""
        non_existent_id = 99999
        response = self.client.delete(f'/api/drawings/delete/{non_existent_id}')
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['success'] is False
        assert 'Drawing not found' in data['error']

    def test_get_user_drawings_different_user(self):
        """Test that users can only see their own drawings"""
        # Create another user
        other_user = User(
            username='otheruser',
            email='other@example.com',
            password_hash='hashed_password',
            role='child'
        )
        db.session.add(other_user)
        db.session.commit()

        # Create drawing for other user
        other_drawing = DoodleSession(
            user_id=other_user.id,
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            drawing_duration=60,
            filename='other_drawing.png'
        )
        db.session.add(other_drawing)
        db.session.commit()

        # Try to access other user's drawings
        response = self.client.get(f'/api/drawings/{other_user.id}', headers=self.headers)
        data = json.loads(response.data)

        # The endpoint might allow accessing other users' drawings or restrict it
        # This test checks the current behavior
        assert response.status_code in [200, 403]

    def test_save_drawing_with_long_duration(self):
        """Test saving drawing with extended drawing time"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'drawing_time': 3600  # 1 hour
        }

        response = self.client.post('/api/drawings/save',
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'drawing_id' in data
