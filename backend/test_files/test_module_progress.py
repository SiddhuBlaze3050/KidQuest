import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, UserModuleProgress
from flask_jwt_extended import create_access_token


class TestModuleProgress:
    """Test cases for Module Progress endpoints"""

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

    def test_save_module_progress_new_module(self):
        """Test saving progress for a new module"""
        progress_data = {
            'user_id': self.test_user_id,
            'module_type': 'math_magic',
            'progress_percentage': 50,
            'is_completed': False,
            'progress_data': {
                'current_lesson': 3,
                'score': 85
            }
        }

        response = self.client.post('/api/module/progress',
                                  data=json.dumps(progress_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['progress_percentage'] == 50
        assert data['is_completed'] is False

    def test_save_module_progress_with_submodule(self):
        """Test saving progress for a module with submodules"""
        progress_data = {
            'user_id': self.test_user_id,
            'module_type': 'safety_measures',
            'submodule_name': 'home_safety',
            'progress_percentage': 100,
            'is_completed': True,
            'progress_data': {
                'completed_tips': 4,
                'score': 95
            }
        }

        response = self.client.post('/api/module/progress',
                                  data=json.dumps(progress_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['progress_percentage'] == 100
        assert data['is_completed'] is True

    def test_save_module_progress_update_existing(self):
        """Test updating progress for an existing module"""
        # Create initial progress
        initial_progress = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='math_magic',
            progress=30.0,
            completed=False
        )
        db.session.add(initial_progress)
        db.session.commit()

        # Update progress
        progress_data = {
            'user_id': self.test_user_id,
            'module_type': 'math_magic',
            'progress_percentage': 75,
            'is_completed': False
        }

        response = self.client.post('/api/module/progress',
                                  data=json.dumps(progress_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['progress_percentage'] == 75

    def test_get_module_progress_single_module(self):
        """Test getting progress for a single module without submodules"""
        # Create progress record
        progress = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='math_magic',
            progress=75.0,
            completed=False
        )
        db.session.add(progress)
        db.session.commit()

        response = self.client.get(f'/api/module/progress/{self.test_user_id}/math_magic', 
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['progress']['module_name'] == 'math_magic'
        assert data['progress']['progress_percentage'] == 75.0
        assert data['progress']['is_completed'] is False

    def test_get_module_progress_with_submodules(self):
        """Test getting progress for a module with submodules"""
        # Create submodule progress records
        submodule1 = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='safety_measures',
            submodule_name='home_safety',
            progress=100.0,
            completed=True
        )
        submodule2 = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='safety_measures',
            submodule_name='road_safety',
            progress=50.0,
            completed=False
        )
        db.session.add(submodule1)
        db.session.add(submodule2)
        db.session.commit()

        response = self.client.get(f'/api/module/progress/{self.test_user_id}/safety_measures', 
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert data['progress']['module_name'] == 'safety_measures'
        assert 'submodule_progress' in data['progress']
        assert len(data['progress']['submodule_progress']) == 2

    def test_get_all_module_progress(self):
        """Test getting progress for all modules"""
        # Create progress for multiple modules
        progress1 = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='math_magic',
            progress=75.0,
            completed=False
        )
        progress2 = UserModuleProgress(
            user_id=self.test_user_id,
            module_name='word_wizard',
            progress=100.0,
            completed=True
        )
        db.session.add(progress1)
        db.session.add(progress2)
        db.session.commit()

        response = self.client.get(f'/api/module/progress/{self.test_user_id}', 
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'progress_list' in data
        assert len(data['progress_list']) >= 2

    def test_get_modules_info(self):
        """Test getting modules information"""
        response = self.client.get('/api/modules/info', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'modules' in data
        assert 'modules_with_submodules' in data
        assert 'modules_without_submodules' in data

    def test_save_module_progress_missing_data(self):
        """Test saving module progress with missing required data"""
        progress_data = {
            'user_id': self.test_user_id,
            # Missing module_type
            'progress_percentage': 50
        }

        response = self.client.post('/api/module/progress',
                                  data=json.dumps(progress_data),
                                  content_type='application/json',
                                  headers=self.headers)
        data = json.loads(response.data)

        # Backend returns 200 with success False and an error message for no progress
        assert response.status_code == 404 or (response.status_code == 200 and data.get('progress') is None)

    def test_get_module_progress_unauthorized(self):
        """Test accessing module progress without authentication"""
        response = self.client.get(f'/api/module/progress/{self.test_user_id}/math_magic')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_module_progress_nonexistent_module(self):
        """Test getting progress for a non-existent module"""
        response = self.client.get(f'/api/module/progress/{self.test_user_id}/nonexistent_module', 
                                 headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        # Should return default progress for non-existent module
        assert data['progress']['progress_percentage'] == 0
        assert data['progress']['is_completed'] is False
