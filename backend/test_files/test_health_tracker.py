import pytest
import json
import sys
import os
from datetime import date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, HealthTask


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

            yield

            db.session.remove()
            db.drop_all()

    def test_get_health_tasks(self):
        """Test fetching today's health tasks for a user"""
        response = self.client.get(f'/api/health/tasks/{self.test_user_id}')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert isinstance(data['tasks'], list)
