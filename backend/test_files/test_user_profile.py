import pytest
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
from flask_jwt_extended import create_access_token


class TestUserProfile:
    """Test cases for User Profile endpoints"""

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

    def test_get_user_profile_by_id(self):
        """Test fetching user profile by user ID"""
        response = self.client.get(f'/api/user/profile/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['id'] == self.test_user_id
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['role'] == 'child'

    def test_get_current_user_profile(self):
        """Test fetching current user's profile using JWT token"""
        response = self.client.get('/api/user/profile', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'user' in data
        assert data['user']['id'] == self.test_user_id
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
        assert data['user']['role'] == 'child'

    def test_get_user_profile_unauthorized(self):
        """Test accessing user profile without authentication"""
        response = self.client.get(f'/api/user/profile/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_current_user_profile_unauthorized(self):
        """Test accessing current user profile without authentication"""
        response = self.client.get('/api/user/profile')
        data = json.loads(response.data)

        assert response.status_code == 401
        assert data['success'] is False
        assert 'Missing authorization token' in data['error']

    def test_get_user_profile_nonexistent_user(self):
        """Test fetching profile for a non-existent user"""
        non_existent_id = 99999
        response = self.client.get(f'/api/user/profile/{non_existent_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data['success'] is False
        assert 'User not found' in data['error']

    def test_get_user_profile_different_roles(self):
        """Test fetching profiles for users with different roles"""
        # Create users with different roles
        parent_user = User(
            username='parentuser',
            email='parent@example.com',
            password_hash='hashed_password',
            role='parent'
        )
        teacher_user = User(
            username='teacheruser',
            email='teacher@example.com',
            password_hash='hashed_password',
            role='teacher'
        )
        admin_user = User(
            username='adminuser',
            email='admin@example.com',
            password_hash='hashed_password',
            role='admin'
        )
        
        db.session.add(parent_user)
        db.session.add(teacher_user)
        db.session.add(admin_user)
        db.session.commit()

        # Test fetching parent profile
        response = self.client.get(f'/api/user/profile/{parent_user.id}', headers=self.headers)
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['user']['role'] == 'parent'

        # Test fetching teacher profile
        response = self.client.get(f'/api/user/profile/{teacher_user.id}', headers=self.headers)
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['user']['role'] == 'teacher'

        # Test fetching admin profile
        response = self.client.get(f'/api/user/profile/{admin_user.id}', headers=self.headers)
        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['user']['role'] == 'admin'

    def test_user_profile_data_integrity(self):
        """Test that user profile data doesn't include sensitive information"""
        response = self.client.get(f'/api/user/profile/{self.test_user_id}', headers=self.headers)
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        
        # Ensure sensitive data is not included
        user_data = data['user']
        assert 'password_hash' not in user_data
        assert 'password' not in user_data
        
        # Ensure required fields are present
        required_fields = ['id', 'username', 'email', 'role']
        for field in required_fields:
            assert field in user_data

    def test_get_available_students(self):
        """Test fetching available students for teacher registration"""
        # Create additional child users
        child1 = User(
            username='child1',
            email='child1@example.com',
            password_hash='hashed_password',
            role='child'
        )
        child2 = User(
            username='child2',
            email='child2@example.com',
            password_hash='hashed_password',
            role='child'
        )
        
        db.session.add(child1)
        db.session.add(child2)
        db.session.commit()

        response = self.client.get('/api/students/available')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'data' in data
        assert len(data['data']) >= 3  # Should include all child users
        
        # Check student data structure
        student = data['data'][0]
        assert 'id' in student
        assert 'username' in student
        assert 'email' in student
        assert 'avatar' in student

    def test_get_available_students_only_children(self):
        """Test that available students endpoint only returns users with 'child' role"""
        # Create users with different roles
        parent_user = User(
            username='parentuser',
            email='parent@example.com',
            password_hash='hashed_password',
            role='parent'
        )
        teacher_user = User(
            username='teacheruser',
            email='teacher@example.com',
            password_hash='hashed_password',
            role='teacher'
        )
        
        db.session.add(parent_user)
        db.session.add(teacher_user)
        db.session.commit()

        response = self.client.get('/api/students/available')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        
        # All returned users should have 'child' role (we can't verify this directly from the endpoint
        # but we can ensure the original child user is included)
        usernames = [student['username'] for student in data['data']]
        assert 'testuser' in usernames  # Our original child user
        
        # Ensure parent and teacher users are not included
        assert 'parentuser' not in usernames
        assert 'teacheruser' not in usernames
