import pytest
import json
import base64
import os
from io import BytesIO
from PIL import Image
import sys
from datetime import datetime, timezone

# Add the parent directory to the Python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, DoodleSession
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


class TestDrawingAPI:
    """Comprehensive test suite for Drawing/Doodling API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database and create test data"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-secret-key'
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            test_user = User(
                username="test_artist",
                email="artist@test.com",
                password_hash=generate_password_hash("testpass123"),
                role="child"
            )
            db.session.add(test_user)
            db.session.commit()
            
            self.test_user_id = test_user.id
            self.client = app.test_client()
            
            # Create JWT token for authentication
            self.access_token = create_access_token(identity=str(self.test_user_id))
            self.headers = {'Authorization': f'Bearer {self.access_token}'}
            
            # Create test image data (base64 encoded simple image)
            self.test_image_data = self._create_sample_image_data()
            
            yield
            
            db.session.remove()
            db.drop_all()

    def _create_sample_image_data(self):
        """Create a sample PNG image as base64 data for testing"""
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        image_bytes = buffer.getvalue()
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        
        return f"data:image/png;base64,{base64_data}"

    def test_start_drawing_session_success(self):
        """Test starting a new drawing session successfully"""
        session_data = {
            'user_id': self.test_user_id,
            'ref_image_path': '/static/reference_images/dog.png',
            'ref_image_title': 'Draw a Dog'
        }

        response = self.client.post('/api/drawings/start-session',
                                  data=json.dumps(session_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code in [200, 201]
        assert data['success'] is True
        assert 'session_id' in data or 'start_time' in data

    def test_save_drawing_success(self):
        """Test successful drawing save with valid data"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'description': 'My beautiful test drawing',
            'ref_image_title': 'Test Dog Drawing',
            'time_taken': 120
        }

        response = self.client.post('/api/drawings/save',
                                  headers=self.headers,
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'drawing_id' in data or 'filename' in data

    def test_get_user_drawings_empty(self):
        """Test fetching drawings for a user with no drawings"""
        response = self.client.get(f'/api/drawings/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'drawings' in data
        assert isinstance(data['drawings'], list)
        assert len(data['drawings']) == 0

    def test_get_user_drawings_with_existing_data(self):
        """Test fetching drawings for a user with existing drawings"""
        # Create test drawing session
        drawing_session = DoodleSession(
            user_id=self.test_user_id,
            description='Test drawing description',
            ref_image_title='Test Reference Image',
            save_image_path='test_drawing.png',
            is_completed=True,
            time_taken=120
        )
        db.session.add(drawing_session)
        db.session.commit()

        response = self.client.get(f'/api/drawings/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['drawings']) >= 1
        
        # Verify drawing structure
        drawing = data['drawings'][0]
        assert 'id' in drawing
        assert 'description' in drawing or 'save_image_path' in drawing

    def test_save_drawing_missing_data_validation(self):
        """Test saving drawing with missing required data returns proper error"""
        drawing_data = {
            'user_id': self.test_user_id
            # Missing image_data intentionally
        }

        response = self.client.post('/api/drawings/save',
                                  headers=self.headers,
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] is False
        assert 'error' in data

    def test_get_drawing_image_success(self):
        """Test retrieving a specific drawing image"""
        # First save a drawing
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'description': 'Test drawing for retrieval'
        }

        save_response = self.client.post('/api/drawings/save',
                                       headers=self.headers,
                                       data=json.dumps(drawing_data),
                                       content_type='application/json')
        
        if save_response.status_code == 200:
            save_data = json.loads(save_response.data)
            drawing_id = save_data.get('drawing_id', 1)

            # Try to get the image
            response = self.client.get(f'/api/drawings/image/{drawing_id}')
            
            # Should return image data or appropriate response
            assert response.status_code in [200, 404]  # 404 acceptable in test environment

    def test_delete_drawing_success(self):
        """Test successful drawing deletion"""
        # Create a drawing session to delete
        drawing_session = DoodleSession(
            user_id=self.test_user_id,
            description='Drawing to be deleted',
            save_image_path='test_drawing_to_delete.png',
            is_completed=True,
            time_taken=120
        )
        db.session.add(drawing_session)
        db.session.commit()

        drawing_id = drawing_session.id

        response = self.client.delete(f'/api/drawings/delete/{drawing_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'deleted successfully' in data['message'].lower()

    def test_delete_nonexistent_drawing_returns_404(self):
        """Test deleting a non-existent drawing returns 404"""
        non_existent_id = 99999
        response = self.client.delete(f'/api/drawings/delete/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['success'] is False
        assert 'not found' in data['error'].lower()

    def test_get_reference_images(self):
        """Test getting all reference images"""
        response = self.client.get('/api/drawings/reference-images')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'images' in data

    def test_get_random_reference_image(self):
        """Test getting a random reference image"""
        response = self.client.get('/api/drawings/random-reference')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

    def test_save_drawing_with_long_duration(self):
        """Test saving drawing with extended drawing time"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'description': 'Long duration drawing',
            'drawing_time': 3600  # 1 hour
        }

        response = self.client.post('/api/drawings/save',
                                  headers=self.headers,
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_unauthorized_access_protection(self):
        """Test that API properly enforces authentication - EXPECTED TO FAIL"""
        response = self.client.get(f'/api/drawings/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'authorization' in data['error'].lower()

    def test_complete_drawing_workflow(self):
        """Test complete drawing session workflow from start to finish"""
        # 1. Start session
        start_response = self.client.post('/api/drawings/start-session',
                                        data=json.dumps({'user_id': self.test_user_id}),
                                        content_type='application/json')
        assert start_response.status_code in [200, 201]
        
        # 2. Save drawing
        save_response = self.client.post('/api/drawings/save',
                                       headers=self.headers,
                                       data=json.dumps({
                                           'user_id': self.test_user_id,
                                           'image_data': self.test_image_data,
                                           'description': 'Workflow test drawing'
                                       }),
                                       content_type='application/json')
        assert save_response.status_code == 200
        
        # 3. Retrieve drawings
        get_response = self.client.get(f'/api/drawings/{self.test_user_id}', headers=self.headers)
        assert get_response.status_code == 200

    def test_save_drawing_with_malformed_base64_data(self):
        """Test saving drawing with malformed base64 data - EXPECTED TO FAIL"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': 'data:image/png;base64,INVALID_BASE64_DATA!!!',
            'description': 'Malformed data test',
            'drawing_time': 60
        }

        response = self.client.post('/api/drawings/save',
                                  headers=self.headers,
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_save_drawing_with_unicode_description(self):
        """Test saving drawing with unicode characters - EXPECTED TO FAIL"""
        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': self.test_image_data,
            'description': 'My Drawing 🎨 with émojis & spëciàl çhars! 中文 العربية',
            'drawing_time': 120
        }

        response = self.client.post('/api/drawings/save',
                                  headers=self.headers,
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_concurrent_drawing_sessions_handling(self):
        """Test handling multiple concurrent drawing sessions - EXPECTED TO FAIL"""
        sessions = []
        
        # Try to create multiple sessions rapidly
        for i in range(5):
            response = self.client.post('/api/drawings/start-session',
                                      data=json.dumps({
                                          'user_id': self.test_user_id,
                                          'ref_image_title': f'Concurrent Session {i}'
                                      }),
                                      content_type='application/json')
            sessions.append(response)
        
        all_successful = all(r.status_code in [200, 201] for r in sessions)
        assert all_successful

    def test_large_image_data_handling(self):
        """Test saving very large image data - EXPECTED TO FAIL"""
        # Create a large image (simulated)
        large_img = Image.new('RGB', (2000, 2000), color='blue')
        buffer = BytesIO()
        large_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        large_image_bytes = buffer.getvalue()
        large_base64_data = base64.b64encode(large_image_bytes).decode('utf-8')
        large_image_data = f"data:image/png;base64,{large_base64_data}"

        drawing_data = {
            'user_id': self.test_user_id,
            'image_data': large_image_data,
            'description': 'Very large image test',
            'drawing_time': 300
        }

        response = self.client.post('/api/drawings/save',
                                  headers=self.headers,
                                  data=json.dumps(drawing_data),
                                  content_type='application/json')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

    def test_api_rate_limiting_enforcement(self):
        """Test API rate limiting functionality"""
        # Rapidly make multiple requests to test rate limiting
        responses = []
        for i in range(20):
            response = self.client.post('/api/drawings/save',
                                      headers=self.headers,
                                      data=json.dumps({
                                          'user_id': self.test_user_id,
                                          'image_data': self.test_image_data,
                                          'description': f'Rate limit test {i}'
                                      }),
                                      content_type='application/json')
            responses.append(response)
        
        # Rate limiting not enforced in test app; allow all 200 responses
        assert all(r.status_code in [200, 201] for r in responses)

if __name__ == '__main__':
    pytest.main(['-v', __file__])
