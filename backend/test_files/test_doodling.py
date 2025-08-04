import pytest
import json
import base64
import os
from io import BytesIO
from PIL import Image
import sys

# Add the parent directory to the Python path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

# Test configuration
BASE_URL = "http://localhost:5000"

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # Create a test user
            test_user = User(
                username="test_artist",
                email="artist@test.com",
                password_hash=generate_password_hash("testpass123"),
                role="child"
            )
            db.session.add(test_user)
            db.session.commit()
            
            yield client
            
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Get JWT authentication headers for test requests"""
    login_response = client.post('/api/auth/login', 
                                json={
                                    'username': 'test_artist', 
                                    'password': 'testpass123'
                                })
    
    assert login_response.status_code == 200
    login_data = json.loads(login_response.data)
    access_token = login_data['access_token']
    
    return {'Authorization': f'Bearer {access_token}'}

@pytest.fixture
def sample_image_data():
    """Create a sample PNG image as base64 data for testing"""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convert to base64
    image_bytes = buffer.getvalue()
    base64_data = base64.b64encode(image_bytes).decode('utf-8')
    
    return f"data:image/png;base64,{base64_data}"

class TestDoodlingAPI:
    """Test suite for doodling/drawing API endpoints"""
    
    def test_start_drawing_session(self, client):
        """Test starting a new drawing session"""
        response = client.post('/api/drawings/start-session', 
                             json={
                                 'user_id': 1,
                                 'ref_image_path': '/static/reference_images/dog.png',
                                 'ref_image_title': 'Draw a Dog'
                             })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'session_id' in data
        assert 'start_time' in data
        assert data['ref_image_title'] == 'Draw a Dog'
    
    def test_save_drawing(self, client, auth_headers, sample_image_data):
        """Test saving a drawing with image data"""
        response = client.post('/api/drawings/save', 
                             headers=auth_headers,
                             json={
                                 'image_data': sample_image_data,
                                 'description': 'My test drawing',
                                 'ref_image_path': '/static/reference_images/dog.png',
                                 'ref_image_title': 'Test Dog Drawing',
                                 'time_taken': 120
                             })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['message'] == 'Drawing saved successfully!'
        assert 'drawing_id' in data
        assert 'file_path' in data
        assert data['time_taken'] == 120
        assert data['ref_image_title'] == 'Test Dog Drawing'
    
    def test_save_drawing_error_scenarios(self, client, auth_headers):
        """Test various error scenarios when saving drawings"""
        
        # Test missing image data
        response1 = client.post('/api/drawings/save', 
                               headers=auth_headers,
                               json={
                                   'user_id': 1,
                                   'description': 'My test drawing'
                               })
        
        assert response1.status_code == 400
        data1 = json.loads(response1.data)
        assert data1['success'] is False
        assert 'image' in data1['error'].lower()
        
        # Test saving without authentication
        response2 = client.post('/api/drawings/save', 
                               json={
                                   'image_data': 'data:image/png;base64,test',
                                   'description': 'No auth test'
                               })
        
        assert response2.status_code == 401
    
    def test_drawing_retrieval_scenarios(self, client, auth_headers, sample_image_data):
        """Test various drawing retrieval scenarios"""
        
        # First, save a drawing
        save_response = client.post('/api/drawings/save', 
                                  headers=auth_headers,
                                  json={
                                      'image_data': sample_image_data,
                                      'description': 'Test drawing for retrieval',
                                      'ref_image_title': 'Test Reference'
                                  })
        
        assert save_response.status_code == 200
        save_data = json.loads(save_response.data)
        drawing_id = save_data['drawing_id']
        
        # Test getting user drawings
        response1 = client.get('/api/drawings/1', headers=auth_headers)
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['success'] is True
        assert 'drawings' in data1
        assert len(data1['drawings']) >= 1
        
        drawing = data1['drawings'][0]
        assert 'id' in drawing
        assert 'description' in drawing
        assert 'timestamp' in drawing
        assert 'file_path' in drawing
        assert drawing['description'] == 'Test drawing for retrieval'
        
        # Test getting specific drawing image
        response2 = client.get(f'/api/drawings/image/{drawing_id}')
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['success'] is True
        assert 'image_data' in data2
        assert data2['image_data'].startswith('data:image/png;base64,')
        assert data2['description'] == 'Test drawing for retrieval'
        
        # Test getting non-existent drawing image
        response3 = client.get('/api/drawings/image/999')
        assert response3.status_code == 404
        data3 = json.loads(response3.data)
        assert data3['success'] is False
        assert 'not found' in data3['error'].lower()
        
        # Test empty user drawings
        response4 = client.get('/api/drawings/999', headers=auth_headers)
        assert response4.status_code == 200
        data4 = json.loads(response4.data)
        assert data4['success'] is True
        assert data4['drawings'] == []
    
    def test_drawing_deletion_scenarios(self, client, auth_headers, sample_image_data):
        """Test various drawing deletion scenarios"""
        # First, save a drawing to delete
        save_response = client.post('/api/drawings/save', 
                                  headers=auth_headers,
                                  json={
                                      'image_data': sample_image_data,
                                      'description': 'Drawing to be deleted'
                                  })
        
        assert save_response.status_code == 200
        save_data = json.loads(save_response.data)
        drawing_id = save_data['drawing_id']
        
        # Test successful deletion
        response1 = client.delete(f'/api/drawings/delete/{drawing_id}', 
                                headers=auth_headers)
        
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['success'] is True
        assert 'deleted successfully' in data1['message'].lower()
        
        # Test deleting non-existent drawing
        response2 = client.delete('/api/drawings/delete/999', 
                                headers=auth_headers)
        
        assert response2.status_code == 404
        data2 = json.loads(response2.data)
        assert data2['success'] is False
        assert 'not found' in data2['error'].lower()
        
        # Test deletion without authentication
        response3 = client.delete('/api/drawings/delete/123')
        assert response3.status_code == 401
    
    def test_reference_image_functionality(self, client):
        """Test reference image related functionality"""
        # Test getting all reference images
        response1 = client.get('/api/drawings/reference-images')
        
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        assert data1['success'] is True
        assert 'images' in data1
        assert isinstance(data1['images'], list)
        
        # Test getting random reference image
        response2 = client.get('/api/drawings/random-reference')
        
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert data2['success'] is True
        # Could have reference data or fallback message depending on if files exist
    
    def test_drawing_session_workflow(self, client, auth_headers, sample_image_data):
        """Test complete drawing session workflow"""
        # 1. Start drawing session
        start_response = client.post('/api/drawings/start-session', 
                                   json={
                                       'user_id': 1,
                                       'ref_image_path': '/static/reference_images/dog.png',
                                       'ref_image_title': 'Complete Workflow Dog'
                                   })
        
        assert start_response.status_code == 201
        start_data = json.loads(start_response.data)
        session_id = start_data['session_id']
        
        # 2. Save the drawing
        save_response = client.post('/api/drawings/save', 
                                  headers=auth_headers,
                                  json={
                                      'image_data': sample_image_data,
                                      'description': 'Complete workflow drawing',
                                      'ref_image_title': 'Complete Workflow Dog',
                                      'time_taken': 300
                                  })
        
        assert save_response.status_code == 200
        save_data = json.loads(save_response.data)
        drawing_id = save_data['drawing_id']
        
        # 3. Retrieve user's drawings
        get_response = client.get('/api/drawings/1', headers=auth_headers)
        assert get_response.status_code == 200
        get_data = json.loads(get_response.data)
        
        # Verify the drawing is in the list
        found_drawing = None
        for drawing in get_data['drawings']:
            if drawing['id'] == drawing_id:
                found_drawing = drawing
                break
        
        assert found_drawing is not None
        assert found_drawing['description'] == 'Complete workflow drawing'
        assert found_drawing['time_taken'] == 300
        
        # 4. Get the specific image
        image_response = client.get(f'/api/drawings/image/{drawing_id}')
        assert image_response.status_code == 200
        
        # 5. Delete the drawing
        delete_response = client.delete(f'/api/drawings/delete/{drawing_id}', 
                                      headers=auth_headers)
        assert delete_response.status_code == 200

if __name__ == '__main__':
    pytest.main(['-v', __file__])
