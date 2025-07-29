#!/usr/bin/env python3
"""
JWT Authentication Integration Test Script
Tests the JWT authentication flow between frontend and backend
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_jwt_integration():
    """Test the complete JWT authentication flow"""
    print("🔍 Testing JWT Authentication Integration")
    print("=" * 50)
    
    # Test 1: Login with valid credentials
    print("\n1. Testing Login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200 and response.json().get('success'):
            token = response.json().get('access_token')
            user_data = response.json().get('user')
            print(f"   ✅ Login successful!")
            print(f"   🔑 Token received: {token[:20]}...")
            print(f"   👤 User: {user_data}")
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 2: Access protected endpoint with token
    print("\n2. Testing Protected Endpoint Access...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/user/profile", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print(f"   ✅ Protected endpoint access successful!")
        else:
            print(f"   ❌ Protected endpoint access failed")
            
    except Exception as e:
        print(f"   ❌ Protected endpoint error: {e}")
    
    # Test 3: Access protected endpoint without token
    print("\n3. Testing Unauthorized Access...")
    try:
        response = requests.get(f"{BASE_URL}/api/user/profile")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 401:
            print(f"   ✅ Properly rejected unauthorized access!")
        else:
            print(f"   ❌ Should have rejected unauthorized access")
            
    except Exception as e:
        print(f"   ❌ Unauthorized access test error: {e}")
    
    # Test 4: Access user-specific endpoint with wrong user
    print("\n4. Testing User Authorization...")
    try:
        wrong_user_id = 999  # Assuming this doesn't match the logged-in user
        response = requests.get(f"{BASE_URL}/api/child/stats/{wrong_user_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 403:
            print(f"   ✅ Properly rejected access to other user's data!")
        else:
            print(f"   ⚠️ Security check: verify user authorization is working")
            
    except Exception as e:
        print(f"   ❌ User authorization test error: {e}")
    
    # Test 5: Logout
    print("\n5. Testing Logout...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print(f"   ✅ Logout successful!")
        else:
            print(f"   ❌ Logout failed")
            
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 JWT Integration Test Complete!")
    return True

def test_frontend_backend_communication():
    """Test communication patterns between frontend and backend"""
    print("\n\n🔍 Testing Frontend-Backend Communication Patterns")
    print("=" * 50)
    
    # Test CORS configuration
    print("\n1. Testing CORS Configuration...")
    try:
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type"
        }
        response = requests.options(f"{BASE_URL}/api/auth/login", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 204]:
            print(f"   ✅ CORS preflight successful!")
        else:
            print(f"   ❌ CORS preflight failed")
            
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")

if __name__ == "__main__":
    print("🚀 Starting JWT Authentication Tests...")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login", timeout=5)
        print("✅ Backend is responding")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running! Please start the Flask backend first.")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Backend check failed: {e}")
    
    # Run tests
    test_jwt_integration()
    test_frontend_backend_communication()
    
    print("\n🏁 All tests completed!")
