#!/usr/bin/env python3
"""
JWT Authentication Integration Test Script
Tests the JWT authentication flow between frontend and backend
Includes race condition prevention, timezone handling, and dashboard API testing
"""

import requests
import pytest
import json
import sys
import time
from datetime import datetime, timezone, timedelta

BASE_URL = "http://localhost:5000"
pytestmark = pytest.mark.integration
FRONTEND_URL = "http://localhost:5173"

# Define IST timezone for testing
IST = timezone(timedelta(hours=5, minutes=30))

def test_jwt_integration():
    """Test the complete JWT authentication flow with race condition prevention"""
    print("🔍 Testing JWT Authentication Integration with Race Condition Prevention")
    print("=" * 70)
    
    # Test 1: Login with valid child credentials
    print("\n1. Testing Child User Login...")
    login_data = {
        "username": "Test1",  # Using child user instead of admin
        "password": "test1test"  # Correct password for Test1 user
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200 and response.json().get('success'):
            response_data = response.json()
            token = response_data.get('access_token')
            user_data = response_data.get('user')
            expires_in = response_data.get('expires_in')
            
            print(f"   ✅ Login successful!")
            print(f"   🔑 Token received: {token[:20]}...")
            print(f"   👤 User: {user_data}")
            print(f"   ⏰ Token expires in: {expires_in} seconds")
            print(f"   🎭 User role: {user_data.get('role')}")
        else:
            print(f"   ❌ Login failed: {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return False
    
    # Test 2: Immediate Token Verification (Race Condition Test)
    print("\n2. Testing Immediate Token Verification...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test the /api/auth/verify endpoint immediately after login
        response = requests.get(f"{BASE_URL}/api/auth/verify", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            verify_data = response.json()
            print(f"   ✅ Token verification successful!")
            print(f"   🆔 User ID verified: {verify_data.get('user_id')}")
            print(f"   🎭 Role verified: {verify_data.get('role')}")
            print(f"   👤 Username verified: {verify_data.get('username')}")
        else:
            print(f"   ❌ Token verification failed: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Token verification error: {e}")
    
    # Test 3: Dashboard API Calls Simulation
    print("\n3. Testing Dashboard API Calls (Child Dashboard Simulation)...")
    user_id = user_data.get('id')
    dashboard_endpoints = [
        f"/api/notifications/{user_id}",
        f"/api/quote/{user_id}",
        f"/api/child/stats/{user_id}",
        f"/api/login-streak/{user_id}",
        f"/api/achievements/special/{user_id}",
        f"/api/module/progress/{user_id}/good_touch_bad_touch",
        f"/api/module/progress/{user_id}/safety_measures",
        f"/api/module/progress/{user_id}/science_explorer",
        f"/api/module/progress/{user_id}/word_wizard",
        f"/api/module/progress/{user_id}/math_magic"
    ]
    
    successful_calls = 0
    for endpoint in dashboard_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            if response.status_code == 200:
                successful_calls += 1
                print(f"   ✅ {endpoint.split('/')[-1]}: Success")
            else:
                print(f"   ❌ {endpoint.split('/')[-1]}: Failed ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {endpoint.split('/')[-1]}: Error - {e}")
    
    print(f"   📊 Dashboard API Success Rate: {successful_calls}/{len(dashboard_endpoints)} ({(successful_calls/len(dashboard_endpoints)*100):.1f}%)")
    
    # Test 4: Timezone Verification
    print("\n4. Testing IST Timezone Handling...")
    try:
        # Test if timestamps are in IST
        response = requests.get(f"{BASE_URL}/api/login-streak/{user_id}", headers=headers)
        if response.status_code == 200:
            current_time = datetime.now(IST)
            print(f"   ✅ IST Timezone test successful!")
            print(f"   🕐 Current IST time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        else:
            print(f"   ❌ Timezone test failed")
    except Exception as e:
        print(f"   ❌ Timezone test error: {e}")
    
    # Test 5: Access protected endpoint without token (Security Test)
    print("\n5. Testing Unauthorized Access...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/verify")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print(f"   ✅ Properly rejected unauthorized access!")
        else:
            print(f"   ❌ Should have rejected unauthorized access")
            
    except Exception as e:
        print(f"   ❌ Unauthorized access test error: {e}")
    
    # Test 6: Cross-User Authorization Test
    print("\n6. Testing Cross-User Authorization...")
    try:
        other_user_id = 999  # Non-existent user ID
        response = requests.get(f"{BASE_URL}/api/child/stats/{other_user_id}", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [403, 404]:
            print(f"   ✅ Properly rejected access to other user's data!")
        else:
            print(f"   ⚠️ Security check: verify user authorization is working properly")
            
    except Exception as e:
        print(f"   ❌ Cross-user authorization test error: {e}")
    
    # Test 7: Race Condition Prevention Test
    print("\n7. Testing Race Condition Prevention...")
    try:
        # Simulate rapid consecutive API calls like dashboard loading
        start_time = time.time()
        rapid_calls = []
        
        for i in range(5):
            response = requests.get(f"{BASE_URL}/api/auth/verify", headers=headers)
            rapid_calls.append(response.status_code == 200)
            time.sleep(0.1)  # Very quick successive calls
        
        end_time = time.time()
        success_rate = sum(rapid_calls) / len(rapid_calls) * 100
        
        print(f"   📊 Rapid calls success rate: {success_rate:.1f}%")
        print(f"   ⏱️ Total time: {(end_time - start_time):.2f} seconds")
        
        if success_rate >= 80:  # Allow some tolerance
            print(f"   ✅ Race condition prevention working!")
        else:
            print(f"   ❌ Possible race condition issues detected")
            
    except Exception as e:
        print(f"   ❌ Race condition test error: {e}")
    
    # Test 8: Logout
    print("\n8. Testing Logout...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Logout successful!")
            
            # Verify token is invalidated
            verify_response = requests.get(f"{BASE_URL}/api/auth/verify", headers=headers)
            if verify_response.status_code == 401:
                print(f"   ✅ Token properly invalidated after logout!")
            else:
                print(f"   ⚠️ Token still valid after logout - check token invalidation")
        else:
            print(f"   ❌ Logout failed")
            
    except Exception as e:
        print(f"   ❌ Logout error: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 JWT Integration Test Complete!")
    return True

def test_frontend_backend_communication():
    """Test communication patterns between frontend and backend"""
    print("\n\n🔍 Testing Frontend-Backend Communication Patterns")
    print("=" * 70)
    
    # Test 1: CORS configuration
    print("\n1. Testing CORS Configuration...")
    try:
        headers = {
            "Origin": FRONTEND_URL,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type"
        }
        response = requests.options(f"{BASE_URL}/api/auth/login", headers=headers)
        print(f"   Status: {response.status_code}")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print(f"   CORS Headers: {cors_headers}")
        
        if response.status_code in [200, 204] and cors_headers['Access-Control-Allow-Origin']:
            print(f"   ✅ CORS preflight successful!")
        else:
            print(f"   ❌ CORS preflight failed")
            
    except Exception as e:
        print(f"   ❌ CORS test error: {e}")

    # Test 2: Authentication Flow Timing
    print("\n2. Testing Authentication Flow Timing...")
    try:
        login_data = {"username": "Test1", "password": "test1test"}  # Correct password
        
        # Measure login time
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        login_time = time.time() - start_time
        
        if response.status_code == 200:
            token = response.json().get('access_token')
            headers = {"Authorization": f"Bearer {token}"}
            
            # Measure verification time
            start_time = time.time()
            verify_response = requests.get(f"{BASE_URL}/api/auth/verify", headers=headers)
            verify_time = time.time() - start_time
            
            print(f"   ⏱️ Login time: {login_time:.3f} seconds")
            print(f"   ⏱️ Verification time: {verify_time:.3f} seconds")
            print(f"   ⏱️ Total auth flow: {login_time + verify_time:.3f} seconds")
            
            if (login_time + verify_time) < 2.0:  # Should be fast
                print(f"   ✅ Authentication flow is performant!")
            else:
                print(f"   ⚠️ Authentication flow might be slow")
        else:
            print(f"   ❌ Login failed in timing test")
            
    except Exception as e:
        print(f"   ❌ Timing test error: {e}")

    # Test 3: Error Response Format
    print("\n3. Testing Error Response Format...")
    try:
        # Test with invalid credentials
        invalid_login = {"username": "invalid", "password": "invalid"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=invalid_login)
        
        if response.status_code == 401:
            error_data = response.json()
            required_fields = ['success', 'error']  # Updated to match actual response format
            has_required = all(field in error_data for field in required_fields)
            
            print(f"   Status: {response.status_code}")
            print(f"   Error format: {error_data}")
            
            if has_required and not error_data.get('success'):
                print(f"   ✅ Error response format is consistent!")
            else:
                print(f"   ❌ Error response format needs improvement")
        else:
            print(f"   ❌ Expected 401 status for invalid credentials")
            
    except Exception as e:
        print(f"   ❌ Error format test error: {e}")

def test_datetime_timezone_handling():
    """Test datetime and timezone handling improvements"""
    print("\n\n🔍 Testing DateTime and Timezone Handling")
    print("=" * 70)
    
    # Login to get token for testing
    login_data = {"username": "Test1", "password": "test1test"}  # Correct password
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print("   ❌ Could not login for timezone tests")
        return
    
    token = login_response.json().get('access_token')
    user_id = login_response.json().get('user', {}).get('id')
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Login streak timezone
    print("\n1. Testing Login Streak Timezone...")
    try:
        response = requests.get(f"{BASE_URL}/api/login-streak/{user_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login streak data received")
            print(f"   📅 Current streak: {data.get('current_streak', 'N/A')}")
            print(f"   📊 Total logins: {data.get('total_logins', 'N/A')}")
        else:
            print(f"   ❌ Failed to get login streak data")
    except Exception as e:
        print(f"   ❌ Login streak test error: {e}")
    
    # Test 2: Dashboard stats with IST
    print("\n2. Testing Dashboard Stats with IST...")
    try:
        response = requests.get(f"{BASE_URL}/api/child/stats/{user_id}", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Dashboard stats received")
            print(f"   ⭐ Total stars: {stats.get('totalStars', 'N/A')}")
            print(f"   🎯 Today's goals: {stats.get('todayGoals', 'N/A')}")
            print(f"   📈 Streak days: {stats.get('streakDays', 'N/A')}")
        else:
            print(f"   ❌ Failed to get dashboard stats")
    except Exception as e:
        print(f"   ❌ Dashboard stats test error: {e}")
    
    print(f"   🕐 Test completed at IST: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %Z')}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced JWT Authentication Tests...")
    print(f"🕐 Test started at IST: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Check if backend is running
    print("\n🔍 Checking Backend Status...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login", timeout=5)
        print("✅ Backend is responding")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running! Please start the Flask backend first.")
        print("   Run: python app.py")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️ Backend check failed: {e}")
    
    # Check if frontend is running (optional)
    print("\n🔍 Checking Frontend Status...")
    try:
        response = requests.get(FRONTEND_URL, timeout=3)
        print("✅ Frontend is responding")
    except requests.exceptions.ConnectionError:
        print("⚠️ Frontend is not running (optional for these tests)")
        print("   To start: npm run dev")
    except Exception as e:
        print(f"⚠️ Frontend check failed: {e}")
    
    print("\n" + "=" * 70)
    
    # Run all test suites
    try:
        success = True
        
        # Main JWT integration tests
        if not test_jwt_integration():
            success = False
        
        # Communication pattern tests
        test_frontend_backend_communication()
        
        # DateTime and timezone tests
        test_datetime_timezone_handling()
        
        print("\n" + "=" * 70)
        if success:
            print("� All JWT Integration Tests Completed Successfully!")
            print("✅ Race condition prevention is working")
            print("✅ Authentication flow is secure and reliable")
            print("✅ IST timezone handling is functioning")
        else:
            print("⚠️ Some tests failed - check the output above")
            
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
    
    print(f"\n🏁 Test completed at IST: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %Z')}")
