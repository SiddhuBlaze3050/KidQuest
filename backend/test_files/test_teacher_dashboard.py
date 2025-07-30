# KidQuest Application - Teacher Dashboard Testing
# Team 25 - SE Project May 2025
# File Info: This is testing file for teacher dashboard related endpoints.

# --------------------  Imports  --------------------

import pytest
import json
import sys
import os
from datetime import date, timedelta, datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, HomeworkSchedule, ParentChild, PomodoroSession
from flask_jwt_extended import create_access_token

# --------------------  Setup  --------------------

@pytest.fixture
def test_client():
    """Create test client and setup test database"""
    # Import app fresh for each test to avoid Flask app reuse issues
    from app import app, db
    
    # Configure the app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'  # Set JWT secret for testing
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Disable token expiration for testing
    
    with app.app_context():
        db.create_all()
        
        # Create test teacher
        test_teacher = User(
            username='testteacher',
            email='teacher@example.com',
            password_hash='hashed_password',
            role='teacher'
        )
        db.session.add(test_teacher)
        db.session.flush()  # Flush to get ID without committing
        
        # Create test students
        test_student1 = User(
            username='teststudent1',
            email='student1@example.com',
            password_hash='hashed_password',
            role='child'
        )
        test_student2 = User(
            username='teststudent2',
            email='student2@example.com',
            password_hash='hashed_password',
            role='child'
        )
        db.session.add_all([test_student1, test_student2])
        db.session.flush()  # Flush to get IDs without committing
        
        # Create teacher-student relationships
        relationship1 = ParentChild(
            parent_id=test_teacher.id,
            child_id=test_student1.id,
            relationship_type='teacher'
        )
        relationship2 = ParentChild(
            parent_id=test_teacher.id,
            child_id=test_student2.id,
            relationship_type='teacher'
        )
        db.session.add_all([relationship1, relationship2])
        db.session.commit()  # Now commit all changes
        
        test_teacher_id = test_teacher.id
        test_student1_id = test_student1.id
        test_student2_id = test_student2.id
        client = app.test_client()
        
        # Create JWT tokens for authentication
        teacher_access_token = create_access_token(identity=test_teacher_id)
        student_access_token = create_access_token(identity=test_student1_id)
        
        # Store app and db for use in tests
        app._test_app = app
        app._test_db = db
        
        yield client, test_teacher_id, test_student1_id, test_student2_id, teacher_access_token, student_access_token
        
        db.session.remove()
        db.drop_all()

# --------------------  Teacher Students Management Tests  --------------------

def test_get_teacher_students_success(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/students/{teacher_id}' page is requested (GET) with valid teacher ID
    THEN check that the response is 200 and returns teacher's students
    """
    client, teacher_id, student1_id, student2_id, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/students/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert len(response_data['students']) == 2
    assert any(student['id'] == student1_id for student in response_data['students'])
    assert any(student['id'] == student2_id for student in response_data['students'])


def test_get_teacher_students_no_authorization(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/students/{teacher_id}' page is requested (GET) without authorization
    THEN check that the response is 401 and returns authorization error
    """
    client, teacher_id, _, _, _, _ = test_client
    
    response = client.get(f'/api/teacher/students/{teacher_id}')
    response_data = response.get_json()
    
    assert response.status_code == 401
    assert response_data['success'] == False
    assert 'Missing authorization token' in response_data['error']


def test_get_teacher_students_invalid_token(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/students/{teacher_id}' page is requested (GET) with invalid token
    THEN check that the response is 401 and returns token error
    """
    client, teacher_id, _, _, _, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": "Bearer invalid_token"
    }
    
    response = client.get(
        f'/api/teacher/students/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 401
    assert response_data['success'] == False
    assert 'Invalid token format' in response_data['error']


def test_get_teacher_students_empty_relationships(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/students/{teacher_id}' page is requested (GET) for teacher with no students
    THEN check that the response is 200 and returns empty students list
    """
    client, _, _, _, _, _ = test_client
    
    # Get the app and db from the client for this test
    from app import app, db
    
    # Create a new teacher with no student relationships within the app context
    with app.app_context():
        new_teacher = User(
            username='newteacher',
            email='newteacher@example.com',
            password_hash='hashed_password',
            role='teacher'
        )
        db.session.add(new_teacher)
        db.session.commit()
        
        teacher_token = create_access_token(identity=new_teacher.id)
        teacher_id = new_teacher.id
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/students/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert response_data['students'] == []


# --------------------  Teacher Homework Management Tests  --------------------

def test_get_teacher_homework_success(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/homework/{teacher_id}' page is requested (GET) with existing homework
    THEN check that the response is 200 and returns teacher's assigned homework
    """
    client, teacher_id, student1_id, _, teacher_token, _ = test_client
    
    # Create test homework assigned by teacher within app context
    with app.app_context():
        homework1 = HomeworkSchedule(
            user_id=student1_id,
            subject='Math',
            task='Complete algebra homework',
            due_date=date.today() + timedelta(days=1),
            status='pending',
            assigned_by_teacher=teacher_id,
            created_at=datetime.utcnow()
        )
        homework2 = HomeworkSchedule(
            user_id=student1_id,
            subject='Science',
            task='Lab report',
            due_date=date.today() + timedelta(days=2),
            status='in-progress',
            assigned_by_teacher=teacher_id,
            created_at=datetime.utcnow()
        )
        db.session.add_all([homework1, homework2])
        db.session.commit()
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/homework/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert len(response_data['homework']) == 2
    assert response_data['homework'][0]['subject'] == 'Math'
    assert response_data['homework'][1]['subject'] == 'Science'


def test_get_teacher_homework_empty(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/homework/{teacher_id}' page is requested (GET) with no assigned homework
    THEN check that the response is 200 and returns empty homework list
    """
    client, teacher_id, _, _, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/homework/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert response_data['homework'] == []


def test_get_teacher_homework_no_authorization(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/homework/{teacher_id}' page is requested (GET) without authorization
    THEN check that the response is 401 and returns authorization error
    """
    client, teacher_id, _, _, _, _ = test_client
    
    response = client.get(f'/api/teacher/homework/{teacher_id}')
    response_data = response.get_json()
    
    assert response.status_code == 401
    assert response_data['success'] == False
    assert 'Missing authorization token' in response_data['error']


# --------------------  Homework Assignment Tests  --------------------

def test_assign_homework_success(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/assign-homework' page is requested (POST) with valid homework data
    THEN check that the response is 201 and homework is assigned successfully
    """
    client, teacher_id, student1_id, student2_id, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    homework_data = {
        'subject': 'English',
        'task': 'Write an essay about friendship',
        'due_date': '2024-12-25',
        'assigned_to': [student1_id, student2_id]
    }
    
    response = client.post(
        '/api/teacher/assign-homework',
        json=homework_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 201
    assert response_data['success'] == True
    assert 'Homework assigned successfully' in response_data['message']
    assert len(response_data['created_tasks']) == 2


def test_assign_homework_missing_fields(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/assign-homework' page is requested (POST) with missing required fields
    THEN check that the response is 400 and returns field error
    """
    client, teacher_id, student1_id, _, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    homework_data = {
        'subject': 'English',
        'task': 'Write an essay',
        # Missing 'due_date' and 'assigned_to'
    }
    
    response = client.post(
        '/api/teacher/assign-homework',
        json=homework_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['success'] == False
    assert 'Missing required field' in response_data['error']


def test_assign_homework_invalid_date(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/assign-homework' page is requested (POST) with invalid date format
    THEN check that the response is 400 and returns date format error
    """
    client, teacher_id, student1_id, _, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    homework_data = {
        'subject': 'English',
        'task': 'Write an essay',
        'due_date': 'invalid-date-format',
        'assigned_to': [student1_id]
    }
    
    response = client.post(
        '/api/teacher/assign-homework',
        json=homework_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['success'] == False
    assert 'Invalid date format' in response_data['error']


def test_assign_homework_unauthorized_student(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/assign-homework' page is requested (POST) with student not under teacher
    THEN check that the response is 403 and returns unauthorized error
    """
    client, teacher_id, _, _, teacher_token, _ = test_client
    
    # Create a student not under this teacher within app context
    with app.app_context():
        unauthorized_student = User(
            username='unauthorizedstudent',
            email='unauthorized@example.com',
            password_hash='hashed_password',
            role='child'
        )
        db.session.add(unauthorized_student)
        db.session.commit()
        unauthorized_student_id = unauthorized_student.id
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    homework_data = {
        'subject': 'English',
        'task': 'Write an essay',
        'due_date': '2024-12-25',
        'assigned_to': [unauthorized_student_id]
    }
    
    response = client.post(
        '/api/teacher/assign-homework',
        json=homework_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 403
    assert response_data['success'] == False
    assert 'Unauthorized to assign homework to students' in response_data['error']


def test_assign_homework_non_teacher_role(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/assign-homework' page is requested (POST) by non-teacher user
    THEN check that the response is 403 and returns role error
    """
    client, _, student1_id, _, _, student_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {student_token}"
    }
    
    homework_data = {
        'subject': 'English',
        'task': 'Write an essay',
        'due_date': '2024-12-25',
        'assigned_to': [student1_id]
    }
    
    response = client.post(
        '/api/teacher/assign-homework',
        json=homework_data,
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 403
    assert response_data['success'] == False
    assert 'Only teachers can assign homework' in response_data['error']


# --------------------  Student Tasks for Teacher Tests  --------------------

def test_get_student_tasks_for_teacher_success(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/student-tasks/{teacher_id}' page is requested (GET) with existing student tasks
    THEN check that the response is 200 and returns student tasks
    """
    client, teacher_id, student1_id, student2_id, teacher_token, _ = test_client
    
    # Create test tasks for students within app context
    with app.app_context():
        task1 = HomeworkSchedule(
            user_id=student1_id,
            subject='Math',
            task='Student created task 1',
            due_date=date.today() + timedelta(days=1),
            status='pending'
        )
        task2 = HomeworkSchedule(
            user_id=student2_id,
            subject='Science',
            task='Student created task 2',
            due_date=date.today() + timedelta(days=2),
            status='completed'
        )
        db.session.add_all([task1, task2])
        db.session.commit()
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/student-tasks/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert len(response_data['tasks']) == 2
    assert any(task['task'] == 'Student created task 1' for task in response_data['tasks'])
    assert any(task['task'] == 'Student created task 2' for task in response_data['tasks'])


def test_get_student_tasks_for_teacher_unauthorized(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/student-tasks/{teacher_id}' page is requested (GET) by unauthorized user
    THEN check that the response is 403 and returns unauthorized error
    """
    client, teacher_id, _, _, _, student_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {student_token}"
    }
    
    response = client.get(
        f'/api/teacher/student-tasks/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 403
    assert response_data['success'] == False
    assert 'Unauthorized access' in response_data['error']


def test_get_student_tasks_for_teacher_with_pomodoro_stats(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/student-tasks/{teacher_id}' page is requested (GET) with tasks having pomodoro sessions
    THEN check that the response is 200 and includes time spent statistics
    """
    client, teacher_id, student1_id, _, teacher_token, _ = test_client
    
    # Create test task and pomodoro sessions within app context
    with app.app_context():
        task = HomeworkSchedule(
            user_id=student1_id,
            subject='Math',
            task='Task with pomodoro sessions',
            due_date=date.today() + timedelta(days=1),
            status='in-progress'
        )
        db.session.add(task)
        db.session.flush()  # Flush to get task ID
        
        # Create pomodoro sessions for the task
        session1 = PomodoroSession(
            user_id=student1_id,
            homework_id=task.id,
            work_duration=1500,  # 25 minutes in seconds
            break_duration=300,   # 5 minutes in seconds
            completed=True
        )
        session2 = PomodoroSession(
            user_id=student1_id,
            homework_id=task.id,
            work_duration=1200,  # 20 minutes in seconds
            break_duration=300,   # 5 minutes in seconds
            completed=True
        )
        db.session.add_all([session1, session2])
        db.session.commit()
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/student-tasks/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert len(response_data['tasks']) == 1
    # Should have time_spent calculated from pomodoro sessions (45 minutes total)
    assert response_data['tasks'][0]['time_spent'] == 45


def test_get_student_tasks_for_teacher_empty(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/teacher/student-tasks/{teacher_id}' page is requested (GET) with no student tasks
    THEN check that the response is 200 and returns empty tasks list
    """
    client, teacher_id, _, _, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    response = client.get(
        f'/api/teacher/student-tasks/{teacher_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    assert response_data['tasks'] == []


# --------------------  Integration Tests  --------------------

def test_teacher_workflow_assign_and_retrieve_homework(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN a teacher assigns homework and then retrieves it
    THEN check that the complete workflow works correctly
    """
    client, teacher_id, student1_id, student2_id, teacher_token, _ = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {teacher_token}"
    }
    
    # Step 1: Assign homework
    homework_data = {
        'subject': 'History',
        'task': 'Research about ancient civilizations',
        'due_date': '2024-12-30',
        'assigned_to': [student1_id, student2_id]
    }
    
    assign_response = client.post(
        '/api/teacher/assign-homework',
        json=homework_data,
        headers=headers,
    )
    assign_data = assign_response.get_json()
    
    assert assign_response.status_code == 201
    assert assign_data['success'] == True
    
    # Step 2: Retrieve assigned homework
    homework_response = client.get(
        f'/api/teacher/homework/{teacher_id}',
        headers=headers,
    )
    homework_data = homework_response.get_json()
    
    assert homework_response.status_code == 200
    assert homework_data['success'] == True
    assert len(homework_data['homework']) == 2  # One for each student
    assert all(hw['subject'] == 'History' for hw in homework_data['homework'])
    
    # Step 3: Retrieve student tasks
    tasks_response = client.get(
        f'/api/teacher/student-tasks/{teacher_id}',
        headers=headers,
    )
    tasks_data = tasks_response.get_json()
    
    assert tasks_response.status_code == 200
    assert tasks_data['success'] == True
    assert len(tasks_data['tasks']) == 2  # Same tasks should appear in student tasks


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
