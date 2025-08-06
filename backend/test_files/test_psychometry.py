# KidQuest Application - Psychometric Test Testing
# Team 25 - SE Project May 2025
# File Info: This is testing file for psychometric test endpoints.

# --------------------  Imports  --------------------

import pytest
import json
import sys
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, PsychometricTestResult
from flask_jwt_extended import create_access_token

# --------------------  Setup  --------------------

@pytest.fixture
def test_client():
    """Create test client and setup test database"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'  # Set JWT secret for testing
    app.config['SECRET_KEY'] = 'test-secret-key'  # Set secret key for session
    
    with app.app_context():
        db.create_all()
        
        # Create test user
        test_user = User(
            username='testchild',
            email='child@example.com',
            password_hash='hashed_password',
            role='child'
        )
        db.session.add(test_user)
        db.session.commit()
        global test_user_id
        test_user_id = str(test_user.id)
        client = app.test_client()
        
        # Create JWT token for authentication
        with app.app_context():
            access_token = create_access_token(identity=test_user_id)
        
        yield client, test_user_id, access_token
        
        db.session.remove()
        db.drop_all()

# --------------------  Mock Data  --------------------

def get_mock_assessment_results():
    """Return mock assessment results for testing"""
    return {
        'learning_style': 'Visual',
        'personality_type': 'Extroverted',
        'top_interest': 'Science',
        'concentration_level': 85.5,
        'memory_strength': 78.2,
        'detailed_scores': {
            'visual': 85,
            'auditory': 65,
            'kinesthetic': 70
        },
        'personality_breakdown': {
            'extroversion': 80,
            'introversion': 20,
            'analytical': 75,
            'creative': 85
        },
        'feedback': 'Strong visual learner with excellent creative abilities.'
    }
def get_mock_test_questions():
    """Return mock test questions for testing"""
    return [
        {
            'question': 'What is your preferred way of learning?',
            'options': ['Visual diagrams', 'Audio lectures', 'Hands-on practice', 'Reading text'],
            'correct_answer': 'Visual diagrams',
            'category': 'learning_style'
        },
        {
            'question': 'How do you solve problems?',
            'options': ['Think step by step', 'Discuss with others', 'Try different approaches', 'Research thoroughly'],
            'correct_answer': 'Think step by step',
            'category': 'personality'
        },
        {
            'question': 'What subjects interest you most?',
            'options': ['Mathematics', 'Science', 'Arts', 'Sports'],
            'correct_answer': 'Science',
            'category': 'interests'
        }
    ]

def get_mock_responses():
    """Return mock user responses for testing"""
    return [
        {'question_id': 1, 'answer': 'A', 'is_correct': True},
        {'question_id': 2, 'answer': 'B', 'is_correct': False},
        {'question_id': 3, 'answer': 'C', 'is_correct': True}
    ]
# --------------------  START Route Tests  --------------------

def test_start_psychometry_test_success_with_fixture_post_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/start' page is requested (POST) with valid user_id
    THEN check that the response is 200 and returns first question
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    mock_questions = get_mock_test_questions()
    
    # Mock the psychometry service
    with patch('app.psychometry_service') as mock_service:
        mock_service.initialize_assessment.return_value = mock_questions
        
        response = client.post(
            '/api/psychometry/start',
            headers=headers,
            json={'user_id': test_user_id}
        )
        response_data = response.get_json()
        
        assert response.status_code == 200
        assert 'question' in response_data
        assert 'options' in response_data
        assert 'question_number' in response_data
        assert 'total_questions' in response_data
        assert response_data['question_number'] == 1
        assert response_data['total_questions'] == 3
        assert response_data['progress'] == 0.0
        
        # Verify session was set up correctly
        with client.session_transaction() as sess:
            assert sess['psychometry_user_id'] == test_user_id
            assert sess['psychometry_current_index'] == 0
            assert len(sess['psychometry_questions']) == 3
            assert sess['psychometry_responses'] == []
            assert 'psychometry_start_time' in sess


def test_start_psychometry_test_missing_user_id_with_fixture_post_400(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/start' page is requested (POST) without user_id
    THEN check that the response is 400 and returns user_id required error
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.post(
        '/api/psychometry/start',
        headers=headers,
        json={}  # No user_id provided
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['error'] == 'user_id is required'


def test_start_psychometry_test_service_error_with_fixture_post_500(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/start' page is requested (POST) and service fails
    THEN check that the response is 500 and returns error message
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Mock the psychometry service to raise an exception
    with patch('app.psychometry_service') as mock_service:
        mock_service.initialize_assessment.side_effect = Exception("Service initialization failed")
        
        response = client.post(
            '/api/psychometry/start',
            headers=headers,
            json={'user_id': test_user_id}
        )
        response_data = response.get_json()
        
        assert response.status_code == 500
        assert response_data['error'] == 'Failed to start psychometry test'
        assert 'Service initialization failed' in response_data['message']


def test_start_psychometry_test_with_null_user_id_with_fixture_post_400(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/start' page is requested (POST) with null user_id
    THEN check that the response is 400 and returns user_id required error
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.post(
        '/api/psychometry/start',
        headers=headers,
        json={'user_id': None}  # Null user_id
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['error'] == 'user_id is required'


def test_start_psychometry_test_with_empty_string_user_id_with_fixture_post_400(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/start' page is requested (POST) with empty string user_id
    THEN check that the response is 400 and returns user_id required error
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.post(
        '/api/psychometry/start',
        headers=headers,
        json={'user_id': ''}  # Empty string user_id
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['error'] == 'user_id is required'


# --------------------  GET Route Tests  --------------------

def test_get_psychometry_results_empty_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/results/{child_id}' page is requested (GET) with no existing results
    THEN check that the response is 404 and returns no result found error
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.get(
        f'/api/psychometry/results/{test_user_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 404
    assert response_data['success'] == False
    assert response_data['error'] == 'No result found'


def test_get_psychometry_results_with_data_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/results/{child_id}' page is requested (GET) with existing results
    THEN check that the response is 200 and returns the latest result
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Create test psychometric results with explicit timestamps
    import time
    
    # Create first result (older)
    result1 = PsychometricTestResult(
        child_id=test_user_id,
        learning_style='Visual',
        personality_type='Introverted',
        top_interest='Math',
        concentration_level=75.0,
        memory_strength=80.0,
        detailed_scores={'visual': 80, 'auditory': 60},
        personality_breakdown={'introversion': 70, 'extroversion': 30},
        duration_seconds=120.5,
        feedback='Good analytical skills'
    )
    db.session.add(result1)
    db.session.commit()
    
    # Small delay to ensure different timestamps
    time.sleep(0.01)
    
    # Create second result (newer)
    result2 = PsychometricTestResult(
        child_id=test_user_id,
        learning_style='Auditory',
        personality_type='Extroverted',
        top_interest='Science',
        concentration_level=85.0,
        memory_strength=78.0,
        detailed_scores={'visual': 70, 'auditory': 85},
        personality_breakdown={'introversion': 30, 'extroversion': 70},
        duration_seconds=150.2,
        feedback='Strong auditory learner'
    )
    db.session.add(result2)
    db.session.commit()
    
    response = client.get(
        f'/api/psychometry/results/{test_user_id}',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 200
    assert response_data['success'] == True
    # Should return the latest result (result2)
    assert response_data['result']['learning_style'] == 'Auditory'
    assert response_data['result']['personality_type'] == 'Extroverted'
    assert response_data['result']['top_interest'] == 'Science'
    assert response_data['result']['concentration_level'] == 85.0
    assert response_data['result']['memory_strength'] == 78.0
    assert response_data['result']['duration_seconds'] == 150.2


def test_get_psychometry_results_invalid_child_id_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/results/{invalid_child_id}' page is requested (GET) with invalid child ID
    THEN check that the response is 404
    """
    client, _, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.get(
        '/api/psychometry/results/invalid_id',
        headers=headers,
    )
    
    assert response.status_code == 404


def test_get_psychometry_results_nonexistent_child_id_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/results/{nonexistent_child_id}' page is requested (GET) with valid but nonexistent child ID
    THEN check that the response is 404 and returns no result found error
    """
    client, _, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = client.get(
        '/api/psychometry/results/999',
        headers=headers,
    )
    response_data = response.get_json()
    
    assert response.status_code == 404
    assert response_data['success'] == False
    assert response_data['error'] == 'No result found'


def test_get_psychometry_results_not_found(test_client):
    """
    GIVEN a child with NO psychometric test result
    WHEN the parent dashboard requests the latest result
    THEN the API returns 404 with error message
    """
    client, test_user_id, access_token = test_client

    response = client.get(f'/api/psychometry/results/{test_user_id}')
    data = response.get_json()

    assert response.status_code == 404
    assert data['success'] is False
    assert data['error'] == 'No result found'

def test_get_psychometry_results_returns_latest_result(test_client):
    """
    GIVEN a child with multiple psychometric test results
    WHEN the endpoint is called
    THEN the API returns the most recent result (by taken_at)
    """
    client, test_user_id, access_token = test_client
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    from datetime import datetime, timedelta

    # Add two results with different timestamps
    result_old = PsychometricTestResult(
        child_id=test_user_id,
        taken_at=datetime.utcnow() - timedelta(days=1),
        learning_style="Kinesthetic",
        personality_type="Balanced",
        top_interest="Art",
        concentration_level=60.0,
        memory_strength=70.0,
        detailed_scores={"art": 9},
        personality_breakdown={"Balanced": 100},
        duration_seconds=100,
        feedback="Old result"
    )
    result_new = PsychometricTestResult(
        child_id=test_user_id,
        taken_at=datetime.utcnow(),
        learning_style="Visual",
        personality_type="Introvert",
        top_interest="Math",
        concentration_level=90.0,
        memory_strength=95.0,
        detailed_scores={"math": 10},
        personality_breakdown={"Introvert": 100},
        duration_seconds=120,
        feedback="New result"
    )
    db.session.add(result_old)
    db.session.add(result_new)
    db.session.commit()

    response = client.get(
        f'/api/psychometry/results/{test_user_id}',
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['result']['feedback'] == "New result"
    assert data['result']['learning_style'] == "Visual"

def test_get_psychometry_results_partial_data(test_client):
    """
    GIVEN a child with a psychometric test result missing optional fields
    WHEN the endpoint is called
    THEN the API returns the result with None for missing fields
    """
    client, test_user_id, access_token = test_client
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Only required fields, omit optional ones
    result = PsychometricTestResult(
        child_id=test_user_id,
        learning_style="Visual",
        personality_type="Introvert",
        top_interest="Math",
        concentration_level=90.0,
        memory_strength=95.0,
        # No detailed_scores, personality_breakdown, duration_seconds, feedback
    )
    db.session.add(result)
    db.session.commit()

    response = client.get(
        f'/api/psychometry/results/{test_user_id}',
        headers=headers,
    )
    data = response.get_json()
    assert response.status_code == 200
    assert data['result']['learning_style'] == "Visual"
    assert data['result']['detailed_scores'] is None or data['result']['detailed_scores'] == {}

# --------------------  POST Route Tests  --------------------



def test_complete_psychometry_assessment_no_session_data_with_fixture_post_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/submit' page is requested (POST) with no session data
    THEN check that the response is 400 because session is required
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # No session data set up - should fail
    response = client.post(
        '/api/psychometry/submit',
        headers=headers,
        json={
            'user_id': test_user_id,
            'answer': 'A'
        }
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert 'error' in response_data


def test_complete_psychometry_assessment_empty_responses_with_fixture_post_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/submit' page is requested (POST) with invalid question index
    THEN check that the response is 400 for invalid question index
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Set up session data with no questions (empty array)
    with client.session_transaction() as sess:
        sess['psychometry_user_id'] = test_user_id
        sess['psychometry_current_index'] = 0
        sess['psychometry_responses'] = []
        sess['psychometry_questions'] = []  # No questions available
    
    response = client.post(
        '/api/psychometry/submit',
        headers=headers,
        json={
            'user_id': test_user_id,
            'answer': 'A'
        }
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['error'] == 'Invalid question index'


def test_complete_psychometry_assessment_service_error_with_fixture_post_500(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/submit' page is requested (POST) and psychometry service throws an error
    THEN check that the response is 500 and returns error message
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Set up session data but mock service to fail
    with client.session_transaction() as sess:
        sess['psychometry_user_id'] = test_user_id
        sess['psychometry_current_index'] = 0
        sess['psychometry_responses'] = []
        sess['psychometry_questions'] = [
            {
                'question': 'Test question?',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 'A',
                'category': 'visual'
            }
        ]
    
    # Mock the psychometry service to raise an exception
    with patch('app.psychometry_service') as mock_service:
        mock_service.process_answer.side_effect = Exception("Service unavailable")
        
        response = client.post(
            '/api/psychometry/submit',
            headers=headers,
            json={
                'user_id': test_user_id,
                'answer': 'A'
            }
        )
        response_data = response.get_json()
        
        assert response.status_code == 500
        assert response_data['error'] == 'Failed to submit answer'
        assert 'Service unavailable' in response_data['message']


def test_complete_psychometry_assessment_database_error_with_fixture_post_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/submit' page is requested (POST) with missing answer
    THEN check that the response is 400 for missing answer
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Set up valid session data
    with client.session_transaction() as sess:
        sess['psychometry_user_id'] = test_user_id
        sess['psychometry_current_index'] = 0
        sess['psychometry_responses'] = []
        sess['psychometry_questions'] = [
            {
                'question': 'Test question?',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 'A',
                'category': 'visual'
            }
        ]
    
    # Submit without answer
    response = client.post(
        '/api/psychometry/submit',
        headers=headers,
        json={
            'user_id': test_user_id
            # Missing 'answer' field
        }
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['error'] == 'No answer provided'


def test_complete_psychometry_assessment_all_correct_with_fixture_post_200(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/psychometry/submit' page is requested (POST) with user ID mismatch
    THEN check that the response is 400 for user ID mismatch
    """
    client, test_user_id, access_token = test_client
    
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Set up session data with different user_id
    with client.session_transaction() as sess:
        sess['psychometry_user_id'] = '999'  # Different from test_user_id
        sess['psychometry_current_index'] = 0
        sess['psychometry_responses'] = []
        sess['psychometry_questions'] = [
            {
                'question': 'Test question?',
                'options': ['A', 'B', 'C', 'D'],
                'correct_answer': 'A',
                'category': 'visual'
            }
        ]
    
    response = client.post(
        '/api/psychometry/submit',
        headers=headers,
        json={
            'user_id': test_user_id,  # Different from session user_id
            'answer': 'A'
        }
    )
    response_data = response.get_json()
    
    assert response.status_code == 400
    assert response_data['error'] == 'User ID mismatch or missing'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])