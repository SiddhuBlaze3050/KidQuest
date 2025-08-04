# KidQuest Application - Finance Module Testing
# Team 25 - SE Project May 2025
# File Info: This is the testing file for finance tracker endpoints.

import pytest
import json
import os
import sys
from werkzeug.security import generate_password_hash

# Adjust path for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Transaction, SavingGoal

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            user = User(username="test_user", email="test@user.com",
                        password_hash=generate_password_hash("pass123"), role="child")
            db.session.add(user)
            db.session.commit()
            user_id = user.id  # Dynamically fetch user ID

            yield client, user_id
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    client, _ = client
    login_res = client.post('/api/auth/login', json={
        'username': 'test_user',
        'password': 'pass123'
    })
    assert login_res.status_code == 200
    token = json.loads(login_res.data)['access_token']
    return {'Authorization': f'Bearer {token}'}

class TestFinanceModule:
    def test_get_transactions_empty(self, client, auth_headers):
        """Should return empty transaction list for new user"""
        client, user_id = client
        res = client.get(f'/api/finance/transactions/{user_id}', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['transactions'] == []

    def test_add_transaction_and_retrieve(self, client, auth_headers):
        """Add and fetch a transaction for the same user"""
        client, user_id = client
        txn = {
            'user_id': user_id,
            'amount': 20.0,
            'type': 'income',
            'description': 'Allowance'
        }
        post_res = client.post('/api/finance/transaction', headers=auth_headers, json=txn)
        assert post_res.status_code == 201
        post_data = post_res.get_json()
        assert post_data['success'] is True
        assert post_data['transaction']['amount'] == 20.0

        get_res = client.get(f'/api/finance/transactions/{user_id}', headers=auth_headers)
        assert get_res.status_code == 200
        txns = get_res.get_json()['transactions']
        assert len(txns) == 1
        assert txns[0]['description'] == 'Allowance'

    def test_unauthorized_transaction_add(self, client, auth_headers):
        """Try to add a transaction for another user"""
        client, _ = client
        txn = {
            'user_id': 999,
            'amount': 50,
            'type': 'expense',
            'description': 'Fake try'
        }
        res = client.post('/api/finance/transaction', headers=auth_headers, json=txn)
        assert res.status_code == 403
        assert 'Unauthorized' in res.get_json()['error']

    def test_get_savings_goals_empty(self, client, auth_headers):
        """Should return empty goal list for new user"""
        client, user_id = client
        res = client.get(f'/api/finance/goals/{user_id}', headers=auth_headers)
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['goals'] == []

    def test_add_goal_and_retrieve(self, client, auth_headers):
        """Add and fetch a goal for the same user"""
        client, user_id = client
        goal = {
            'user_id': user_id,
            'label': 'Buy a bike',
            'target_amount': 100.0
        }
        post_res = client.post('/api/finance/goal', headers=auth_headers, json=goal)
        assert post_res.status_code == 201
        data = post_res.get_json()
        assert data['success'] is True
        assert data['goal']['label'] == 'Buy a bike'
        assert data['goal']['current_amount'] == 0

        get_res = client.get(f'/api/finance/goals/{user_id}', headers=auth_headers)
        assert get_res.status_code == 200
        goals = get_res.get_json()['goals']
        assert len(goals) == 1
        assert goals[0]['target_amount'] == 100.0

    def test_unauthorized_goal_add(self, client, auth_headers):
        """Try to add a goal for another user"""
        client, _ = client
        goal = {
            'user_id': 999,
            'label': 'Illegal save',
            'target_amount': 9999.0
        }
        res = client.post('/api/finance/goal', headers=auth_headers, json=goal)
        assert res.status_code == 403
        assert 'Unauthorized' in res.get_json()['error']

if __name__ == '__main__':
    pytest.main(['-v', __file__])
