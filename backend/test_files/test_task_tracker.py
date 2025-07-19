import pytest
import json
import sys
import os
from datetime import datetime, date, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, HomeworkSchedule


class TestTaskTracker:
    """Test cases for Task Tracker endpoints"""
    
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

    """
    Endpoint: GET /api/tasks/{user_id}
    Method: GET
    Test Cases:
    1. test_get_tasks_empty
    2. test_get_tasks_with_data
    """
    
    def test_get_tasks_empty(self):
        """Test getting tasks when user has no tasks"""
        # Passed Inputs: user_id (from setup)
        # Expected Output: HTTP-Status Code: 200, JSON: Empty tasks list
        # Actual Output: HTTP-Status Code: 200
        # Result: Passed
        
        print(f"\nTest: test_get_tasks_empty")
        print(f"Passed Inputs: user_id = {self.test_user_id}")
        print(f"Endpoint URL: GET https://127.0.0.1:5000/api/tasks/{self.test_user_id}")
        print(f"Expected Outcome: HTTP-Status Code: 200, JSON: Empty tasks list")
        
        response = self.client.get(f'/api/tasks/{self.test_user_id}')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['success'] == True
        assert data['tasks'] == []
    
    def test_get_tasks_with_data(self):
        """Test getting tasks when user has tasks"""
        # Passed Inputs: user_id (from setup)
        # Expected Output: HTTP-Status Code: 200, JSON: List of user's tasks
        # Actual Output: HTTP-Status Code: 200
        # Result: Passed
        
        print(f"\nTest: test_get_tasks_with_data")
        print(f"Passed Inputs: user_id = {self.test_user_id}")
        print(f"Endpoint URL: GET https://127.0.0.1:5000/api/tasks/{self.test_user_id}")
        print(f"Expected Outcome: HTTP-Status Code: 200, JSON: List of user's tasks")
        
        # Create test tasks
        task1 = HomeworkSchedule(
            user_id=self.test_user_id,
            subject='Math',
            task='Complete algebra homework',
            due_date=date.today() + timedelta(days=1),
            status='pending'
        )
        task2 = HomeworkSchedule(
            user_id=self.test_user_id,
            subject='Science',
            task='Lab report',
            due_date=date.today() + timedelta(days=2),
            status='in-progress'
        )
        db.session.add_all([task1, task2])
        db.session.commit()
        
        print(f"Created test tasks for user {self.test_user_id}")
        
        response = self.client.get(f'/api/tasks/{self.test_user_id}')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['success'] == True
        assert len(data['tasks']) == 2
        assert data['tasks'][0]['subject'] == 'Math'
        assert data['tasks'][1]['subject'] == 'Science'

    """
    Endpoint: POST /api/tasks
    Method: POST
    Test Cases:
    1. test_create_task_success
    2. test_create_task_invalid_date
    3. test_create_task_empty_date
    4. test_create_task_missing_fields
    """
    
    def test_create_task_success(self):
        """Test creating a new task successfully"""
        # Passed Inputs: JSON with user_id, subject, task, due_date
        # Expected Output: HTTP-Status Code: 201, JSON: Task created successfully
        # Actual Output: HTTP-Status Code: 201
        # Result: Passed
        
        task_data = {
            'user_id': self.test_user_id,
            'subject': 'English',
            'task': 'Write an essay',
            'due_date': '2024-12-25'
        }
        
        print(f"\nTest: test_create_task_success")
        print(f"Passed Inputs: {json.dumps(task_data, indent=2)}")
        print(f"Endpoint URL: POST https://127.0.0.1:5000/api/tasks")
        print(f"Expected Outcome: HTTP-Status Code: 201, JSON: Task created successfully")
        
        response = self.client.post('/api/tasks',
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 201
        assert data['success'] == True
        assert data['message'] == 'Task created successfully'
        assert data['task']['subject'] == 'English'
        assert data['task']['task'] == 'Write an essay'
        assert data['task']['status'] == 'pending'
    
    def test_create_task_invalid_date(self):
        """Test creating a task with invalid date format"""
        # Passed Inputs: JSON with invalid due_date format
        # Expected Output: HTTP-Status Code: 400, JSON: Error message
        # Actual Output: HTTP-Status Code: 400
        # Result: Passed
        
        task_data = {
            'user_id': self.test_user_id,
            'subject': 'English',
            'task': 'Write an essay',
            'due_date': 'invalid-date'
        }
        
        print(f"\nTest: test_create_task_invalid_date")
        print(f"Passed Inputs: {json.dumps(task_data, indent=2)}")
        print(f"Endpoint URL: POST https://127.0.0.1:5000/api/tasks")
        print(f"Expected Outcome: HTTP-Status Code: 400, JSON: Error message")
        
        response = self.client.post('/api/tasks',
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 400
        assert data['success'] == False
        assert 'Invalid date format' in data['error']
    
    def test_create_task_empty_date(self):
        """Test creating a task with empty date"""
        # Passed Inputs: JSON with empty due_date
        # Expected Output: HTTP-Status Code: 201, JSON: Task created with null date
        # Actual Output: HTTP-Status Code: 201
        # Result: Passed
        
        task_data = {
            'user_id': self.test_user_id,
            'subject': 'English',
            'task': 'Write an essay',
            'due_date': ''
        }
        
        print(f"\nTest: test_create_task_empty_date")
        print(f"Passed Inputs: {json.dumps(task_data, indent=2)}")
        print(f"Endpoint URL: POST https://127.0.0.1:5000/api/tasks")
        print(f"Expected Outcome: HTTP-Status Code: 201, JSON: Task created with null date")
        
        response = self.client.post('/api/tasks',
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 201
        assert data['success'] == True
        assert data['task']['due_date'] is None

    def test_create_task_missing_fields(self):
        """Test creating a task with missing required fields"""
        # Passed Inputs: JSON with missing required fields
        # Expected Output: HTTP-Status Code: 500, JSON: Error message
        # Actual Output: HTTP-Status Code: 500
        # Result: Passed
        
        task_data = {
            'user_id': self.test_user_id
            # Missing 'task' field
        }
        
        print(f"\nTest: test_create_task_missing_fields")
        print(f"Passed Inputs: {json.dumps(task_data, indent=2)}")
        print(f"Endpoint URL: POST https://127.0.0.1:5000/api/tasks")
        print(f"Expected Outcome: HTTP-Status Code: 500, JSON: Error message")
        
        response = self.client.post('/api/tasks',
                                  data=json.dumps(task_data),
                                  content_type='application/json')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 500
        assert data['success'] == False

    """
    Endpoint: PUT /api/tasks/{task_id}/status
    Method: PUT
    Test Cases:
    1. test_update_task_status_success
    2. test_update_task_status_not_found
    """
    
    def test_update_task_status_success(self):
        """Test updating task status successfully"""
        # Passed Inputs: task_id, JSON with new status
        # Expected Output: HTTP-Status Code: 200, JSON: Status updated successfully
        # Actual Output: HTTP-Status Code: 200
        # Result: Passed
        
        # Create a test task
        task = HomeworkSchedule(
            user_id=self.test_user_id,
            subject='Math',
            task='Complete homework',
            status='pending'
        )
        db.session.add(task)
        db.session.commit()
        
        update_data = {'status': 'completed'}
        
        print(f"\nTest: test_update_task_status_success")
        print(f"Passed Inputs: task_id = {task.id}, update_data = {json.dumps(update_data, indent=2)}")
        print(f"Endpoint URL: PUT https://127.0.0.1:5000/api/tasks/{task.id}/status")
        print(f"Expected Outcome: HTTP-Status Code: 200, JSON: Status updated successfully")
        
        response = self.client.put(f'/api/tasks/{task.id}/status',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 200
        assert data['success'] == True
        assert 'Task status updated to completed' in data['message']
        
        # Verify the task was actually updated
        updated_task = HomeworkSchedule.query.get(task.id)
        assert updated_task.status == 'completed'
    
    def test_update_task_status_not_found(self):
        """Test updating status of non-existent task"""
        # Passed Inputs: non-existent task_id, JSON with new status
        # Expected Output: HTTP-Status Code: 404, JSON: Task not found error
        # Actual Output: HTTP-Status Code: 404
        # Result: Passed
        
        update_data = {'status': 'completed'}
        
        print(f"\nTest: test_update_task_status_not_found")
        print(f"Passed Inputs: task_id = 999, update_data = {json.dumps(update_data, indent=2)}")
        print(f"Endpoint URL: PUT https://127.0.0.1:5000/api/tasks/999/status")
        print(f"Expected Outcome: HTTP-Status Code: 404, JSON: Task not found error")
        
        response = self.client.put('/api/tasks/999/status',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        data = json.loads(response.data)
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        print(f"Actual Outcome: JSON: {json.dumps(data, indent=2)}")
        
        assert response.status_code == 404
        assert data['success'] == False
        assert data['error'] == 'Task not found'

    """
    Endpoint: GET /api/tasks/{invalid_user_id}
    Method: GET
    Test Cases:
    1. test_get_tasks_invalid_user_id
    """
    
    def test_get_tasks_invalid_user_id(self):
        """Test getting tasks with invalid user ID"""
        # Passed Inputs: invalid user_id
        # Expected Output: HTTP-Status Code: 404, JSON: Error message
        # Actual Output: HTTP-Status Code: 404
        # Result: Passed
        
        print(f"\nTest: test_get_tasks_invalid_user_id")
        print(f"Passed Inputs: user_id = 'invalid_id'")
        print(f"Endpoint URL: GET https://127.0.0.1:5000/api/tasks/invalid_id")
        print(f"Expected Outcome: HTTP-Status Code: 404, JSON: Error message")
        
        response = self.client.get('/api/tasks/invalid_id')
        
        print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
        
        assert response.status_code == 404  # Flask will return 404 for invalid route


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 