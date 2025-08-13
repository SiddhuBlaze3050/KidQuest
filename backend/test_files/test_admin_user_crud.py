import json
import pytest
import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
from flask_jwt_extended import create_access_token


@pytest.fixture(autouse=True)
def setup_app():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    with app.app_context():
        db.create_all()
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    with app.test_client() as c:
        yield c


@pytest.fixture
def admin_headers():
    # Generate admin token
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        token = create_access_token(identity=str(admin.id))
    return {'Authorization': f'Bearer {token}'}


def test_admin_dashboard_stats(client):
    resp = client.get('/api/admin/dashboard-stats')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_users' in data
    assert 'admin_count' in data


def test_get_all_users(client, admin_headers):
    resp = client.get('/api/admin/users', headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'users' in data


def test_security_validations(client, admin_headers):
    # Creating admin via API should be blocked (role not allowed)
    resp = client.post('/api/admin/users', headers=admin_headers, json={
        'username': 'test_admin_block',
        'email': 'block@example.com',
            'password': 'AdminPass123!',
            'role': 'admin'
    })
    assert resp.status_code in [400, 403]


def test_duplicate_user_validation(client, admin_headers):
    # Create initial user
    uniq = int(datetime.now().timestamp())
    first = client.post('/api/admin/users', headers=admin_headers, json={
        'username': f'test_parent_{uniq}',
        'email': f'parent{uniq}@example.com',
        'password': 'ParentPass123!',
        'role': 'parent'
    })
    assert first.status_code == 201
    created_user = first.get_json()['user']

    # Duplicate username
    dup_username = client.post('/api/admin/users', headers=admin_headers, json={
        'username': created_user['username'],
        'email': f'different{uniq}@example.com',
            'password': 'Password123!',
            'role': 'child'
    })
    assert dup_username.status_code == 409

    # Duplicate email
    dup_email = client.post('/api/admin/users', headers=admin_headers, json={
        'username': f'different_user_{uniq}',
        'email': created_user['email'],
            'password': 'Password123!',
            'role': 'teacher'
    })
    assert dup_email.status_code == 409


def test_unauthorized_access(client):
    # GET without auth
    r1 = client.get('/api/admin/users')
    assert r1.status_code == 401
    # POST without auth
    r2 = client.post('/api/admin/users', json={
        'username': 'unauth', 'password': 'Password123!', 'role': 'parent'
    })
    assert r2.status_code == 401


def test_create_parent_user(client, admin_headers):
    resp = client.post('/api/admin/users', headers=admin_headers, json={
        'username': 'test_parent',
        'email': 'parent@example.com',
        'password': 'ParentPass123!',
        'role': 'parent'
    })
    assert resp.status_code == 201
    assert resp.get_json()['user']['role'] == 'parent'


def test_create_child_user(client, admin_headers):
    resp = client.post('/api/admin/users', headers=admin_headers, json={
        'username': 'test_child',
        'email': 'child@example.com',
                    'password': 'ChildPass123!',
                    'role': 'child'
    })
    assert resp.status_code == 201
    assert resp.get_json()['user']['role'] == 'child'


def test_create_teacher_user(client, admin_headers):
    resp = client.post('/api/admin/users', headers=admin_headers, json={
        'username': 'test_teacher',
        'email': 'teacher@example.com',
                    'password': 'TeacherPass123!',
                    'role': 'teacher'
    })
    assert resp.status_code == 201
    assert resp.get_json()['user']['role'] == 'teacher'


def test_user_update_operations(client, admin_headers):
    # Create first
    create = client.post('/api/admin/users', headers=admin_headers, json={
        'username': 'update_me',
        'email': 'update@example.com',
        'password': 'Password123!',
        'role': 'parent'
    })
    assert create.status_code == 201
    user_id = create.get_json()['user']['id']

    # Update
    updates = {'username': 'updated_user', 'email': 'updated_email@example.com'}
    upd = client.put(f'/api/admin/users/{user_id}', headers=admin_headers, json=updates)
    assert upd.status_code == 200
    assert upd.get_json()['user']['username'] == 'updated_user'


def test_user_deletion(client, admin_headers):
    # Create user to delete
    create = client.post('/api/admin/users', headers=admin_headers, json={
        'username': 'delete_me',
        'email': 'delete@example.com',
        'password': 'Password123!',
        'role': 'parent'
    })
    assert create.status_code == 201
    user_id = create.get_json()['user']['id']

    # Delete
    resp = client.delete(f'/api/admin/users/{user_id}', headers=admin_headers)
    assert resp.status_code == 200