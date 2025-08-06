# KidQuest Application - Task Tracker Testing
# Team 25 - SE Project May 2025
# File Info: This is testing file for task tracker endpoints.

# --------------------  Imports  --------------------

import pytest
import json
import sys
import os
from datetime import date, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, HomeworkSchedule
from flask_jwt_extended import create_access_token

# --------------------  Setup  --------------------

@pytest.fixture
def test_client():
    """Create test client and setup test database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'  # Set JWT secret for testing
    
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
        
        # Make test_user_id accessible globally in this module
        global test_user_id
        test_user_id = test_user.id
        client = app.test_client()
        
        # Create JWT token for authentication
        with app.app_context():
            access_token = create_access_token(identity=test_user_id)
        
        yield client, test_user_id, access_token
        
        db.session.remove()
        db.drop_all()

# --------------------  Tests  --------------------

def test_get_tasks_empty_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks/{user_id}' page is requested (GET) with no existing tasks
    THEN check that the response is 200 and returns empty tasks list
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.get(
        f'/api/tasks/{test_user_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert response_data['tasks'] == []


def test_get_tasks_with_data_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks/{user_id}' page is requested (GET) with existing tasks
    THEN check that the response is 200 and returns user's tasks
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create test tasks
    task1 = HomeworkSchedule(
        user_id=test_user_id,
        subject='Math',
        task='Complete algebra homework',
        due_date=date.today() + timedelta(days=1),
        status='pending'
    )
    task2 = HomeworkSchedule(
        user_id=test_user_id,
        subject='Science',
        task='Lab report',
        due_date=date.today() + timedelta(days=2),
        status='in-progress'
    )
    db.session.add_all([task1, task2])
    db.session.commit()
    
    response = client.get(
        f'/api/tasks/{test_user_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert len(response_data['tasks']) == 2
    assert response_data['tasks'][0]['subject'] == 'Math'
    assert response_data['tasks'][1]['subject'] == 'Science'


def test_get_tasks_invalid_user_id_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks/{invalid_user_id}' page is requested (GET) with invalid user ID
    THEN check that the response is 404
    """
    client, _, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.get(
        '/api/tasks/invalid_id',
        headers=headers,
    )
    
    assert response.status_code == 404


def test_create_task_success_with_fixture_post_201(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks' page is requested (POST) with valid task data
    THEN check that the response is 201 and task is created successfully
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    task_data = {
        'user_id': test_user_id,
        'subject': 'English',
        'task': 'Write an essay',
        'due_date': '2024-12-25'
    }
    
    response = client.post(
        '/api/tasks',
        json=task_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 201
    assert response_data['success'] == True
    assert response_data['message'] == 'Task created successfully'
    assert response_data['task']['subject'] == 'English'
    assert response_data['task']['task'] == 'Write an essay'
    assert response_data['task']['status'] == 'pending'


def test_create_task_invalid_date_with_fixture_post_400(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks' page is requested (POST) with invalid date format
    THEN check that the response is 400 and returns error message
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    task_data = {
        'user_id': test_user_id,
        'subject': 'English',
        'task': 'Write an essay',
        'due_date': 'invalid-date'
    }
    
    response = client.post(
        '/api/tasks',
        json=task_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['success'] == False
    assert 'Invalid date format' in response_data['error']


def test_create_task_empty_date_with_fixture_post_201(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks' page is requested (POST) with empty date
    THEN check that the response is 201 and task is created with null date
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    task_data = {
        'user_id': test_user_id,
        'subject': 'English',
        'task': 'Write an essay',
        'due_date': ''
    }
    
    response = client.post(
        '/api/tasks',
        json=task_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 201
    assert response_data['success'] == True
    assert response_data['task']['due_date'] is None


def test_create_task_missing_fields_with_fixture_post_500(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks' page is requested (POST) with missing required fields
    THEN check that the response is 500 and returns error
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    task_data = {
        'user_id': test_user_id
        # Missing 'task' field
    }
    
    response = client.post(
        '/api/tasks',
        json=task_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 500
    assert response_data['success'] == False


def test_update_task_status_success_with_fixture_put_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks/{task_id}/status' page is requested (PUT) with valid status data
    THEN check that the response is 200 and task status is updated successfully
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create a test task
    task = HomeworkSchedule(
        user_id=test_user_id,
        subject='Math',
        task='Complete homework',
        status='pending'
    )
    db.session.add(task)
    db.session.commit()
    
    update_data = {'status': 'completed'}
    
    response = client.put(
        f'/api/tasks/{task.id}/status',
        json=update_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert 'Task status updated to completed' in response_data['message']
    
    # Verify the task was actually updated
    updated_task = HomeworkSchedule.query.get(task.id)
    assert updated_task.status == 'completed'


def test_update_task_status_not_found_with_fixture_put_404(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/tasks/{task_id}/status' page is requested (PUT) with non-existent task ID
    THEN check that the response is 404 and returns task not found error
    """
    client, _, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    update_data = {'status': 'completed'}
    
    response = client.put(
        '/api/tasks/999/status',
        json=update_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 404
    assert response_data['success'] == False
    assert response_data['error'] == 'Task not found'

def test_get_tasks_for_parents_success(test_client):
    """
    GIVEN a parent user with a parent-child relationship
    WHEN the parent requests tasks for their child
    THEN the API returns the child's tasks with status 200
    """
    client, test_user_id, access_token = test_client

    # Create parent user and parent-child link
    from models import User, ParentChild, HomeworkSchedule, db
    parent = User(
        username='parentuser',
        email='parent@example.com',
        password_hash='hashed_password',
        role='parent'
    )
    db.session.add(parent)
    db.session.commit()

    parent_child = ParentChild(parent_id=parent.id, child_id=test_user_id)
    db.session.add(parent_child)
    db.session.commit()

    # Create a task for the child
    task = HomeworkSchedule(
        user_id=test_user_id,
        subject='Science',
        task='Read chapter 5',
        status='pending'
    )
    db.session.add(task)
    db.session.commit()

    # Generate JWT for parent
    from flask_jwt_extended import create_access_token
    parent_token = create_access_token(identity=parent.id)
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {parent_token}"
    }

    response = client.get(
        f'/api/tasks-for-parent/{test_user_id}',
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['success'] is True
    assert len(data['tasks']) == 1
    assert data['tasks'][0]['subject'] == 'Science'
    assert data['tasks'][0]['user_id'] == test_user_id

def test_get_tasks_for_parents_unauthorized_role(test_client):
    """
    GIVEN a non-parent user
    WHEN they request tasks for another user
    THEN the API returns 403 unauthorized access
    """
    client, test_user_id, access_token = test_client

    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    response = client.get(
        f'/api/tasks-for-parent/{test_user_id}',
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 403
    assert data['success'] is False
    assert 'parent role required' in data['error']

def test_get_tasks_for_parents_no_relationship(test_client):
    """
    GIVEN a parent user with no parent-child relationship
    WHEN the parent requests tasks for a child
    THEN the API returns 403 unauthorized access
    """
    client, test_user_id, access_token = test_client

    from models import User, db
    parent = User(
        username='parentuser2',
        email='parent2@example.com',
        password_hash='hashed_password',
        role='parent'
    )
    db.session.add(parent)
    db.session.commit()

    from flask_jwt_extended import create_access_token
    parent_token = create_access_token(identity=parent.id)
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {parent_token}"
    }

    response = client.get(
        f'/api/tasks-for-parent/{test_user_id}',
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 403
    assert data['success'] is False
    assert 'no parent-child relationship' in data['error']


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 