"""
Test script for JWT RBAC authentication in KidQuest application.
This script tests token generation, validation, and role-based access control.
"""
import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "parent": {"username": "parent", "password": "parentparent", "role": "parent"},
    "child": {"username": "child", "password": "childchild", "role": "child"},
    "teacher": {"username": "teacher", "password": "teacherteacher", "role": "teacher"}
}
ENDPOINTS = {
    "login": "/api/auth/login",  # This is the correct endpoint from app_jwt.py
    "refresh": "/api/auth/refresh",
    "logout": "/api/auth/logout",  # This is the correct endpoint from app_jwt.py
    "protected": "/api/auth/protected",
    "admin_only": "/api/auth/admin",
    "parent_only": "/api/auth/parent",
    "child_only": "/api/auth/child",
    "teacher_only": "/api/auth/teacher"
}

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "total": 0
}

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def print_result(test_name, success, message=""):
    """Print test result with formatting."""
    test_results["total"] += 1
    if success:
        test_results["passed"] += 1
        status = "✅ PASSED"
    else:
        test_results["failed"] += 1
        status = "❌ FAILED"
    
    print(f"{status} - {test_name}")
    if message:
        print(f"       {message}")

def login_user(username, password):
    """Login a user and return the tokens."""
    print(f"Logging in as {username}...")
    response = requests.post(
        f"{BASE_URL}{ENDPOINTS['login']}", 
        json={"username": username, "password": password}
    )
    return response

def test_token_generation():
    """Test JWT token generation for different user roles."""
    print_header("Testing JWT Token Generation")
    
    for user_type, user_data in USERS.items():
        response = login_user(user_data["username"], user_data["password"])
        
        # Check if login was successful
        if response.status_code == 200:
            data = response.json()
            has_access_token = "access_token" in data
            has_refresh_token = "refresh_token" in data
            
            print_result(
                f"Token generation for {user_type}",
                has_access_token and has_refresh_token,
                f"Access token: {'Present' if has_access_token else 'Missing'}, "
                f"Refresh token: {'Present' if has_refresh_token else 'Missing'}"
            )
            
            # Store tokens for later tests if available
            if has_access_token and has_refresh_token:
                USERS[user_type]["access_token"] = data["access_token"]
                USERS[user_type]["refresh_token"] = data["refresh_token"]
        else:
            print_result(
                f"Token generation for {user_type}",
                False,
                f"Login failed with status code {response.status_code}: {response.text}"
            )

def test_protected_endpoints():
    """Test access to protected endpoints with different user roles."""
    print_header("Testing Role-Based Access Control")
    
    # Test cases: (user_type, endpoint, should_succeed)
    test_cases = [
        ("admin", "protected", True),
        ("admin", "admin_only", True),
        ("admin", "parent_only", True),
        ("admin", "child_only", True),
        ("admin", "teacher_only", True),
        
        ("parent", "protected", True),
        ("parent", "admin_only", False),
        ("parent", "parent_only", True),
        ("parent", "child_only", False),
        ("parent", "teacher_only", False),
        
        ("child", "protected", True),
        ("child", "admin_only", False),
        ("child", "parent_only", False),
        ("child", "child_only", True),
        ("child", "teacher_only", False),
    ]
    
    for user_type, endpoint, should_succeed in test_cases:
        # Skip if we don't have a token for this user
        if "access_token" not in USERS[user_type]:
            print_result(
                f"{user_type} accessing {endpoint}",
                False,
                "No access token available for this user"
            )
            continue
        
        # Make the request
        response = requests.get(
            f"{BASE_URL}{ENDPOINTS[endpoint]}",
            headers={"Authorization": f"Bearer {USERS[user_type]['access_token']}"}
        )
        
        # Check if the result matches expectations
        success = (response.status_code == 200) == should_succeed
        expected_status = 200 if should_succeed else 403
        
        print_result(
            f"{user_type} accessing {endpoint}",
            success,
            f"Expected status: {expected_status}, Actual status: {response.status_code}"
        )

def test_token_refresh():
    """Test token refresh functionality."""
    print_header("Testing Token Refresh")
    
    for user_type, user_data in USERS.items():
        # Skip if we don't have a refresh token for this user
        if "refresh_token" not in user_data:
            print_result(
                f"Token refresh for {user_type}",
                False,
                "No refresh token available for this user"
            )
            continue
        
        # Try to refresh the token
        response = requests.post(
            f"{BASE_URL}{ENDPOINTS['refresh']}",
            json={"refresh_token": user_data["refresh_token"]}
        )
        
        # Check if refresh was successful
        if response.status_code == 200:
            data = response.json()
            has_new_access_token = "access_token" in data
            has_new_refresh_token = "refresh_token" in data
            
            print_result(
                f"Token refresh for {user_type}",
                has_new_access_token and has_new_refresh_token,
                f"New access token: {'Present' if has_new_access_token else 'Missing'}, "
                f"New refresh token: {'Present' if has_new_refresh_token else 'Missing'}"
            )
            
            # Update tokens for later tests
            if has_new_access_token and has_new_refresh_token:
                USERS[user_type]["access_token"] = data["access_token"]
                USERS[user_type]["refresh_token"] = data["refresh_token"]
        else:
            print_result(
                f"Token refresh for {user_type}",
                False,
                f"Refresh failed with status code {response.status_code}: {response.text}"
            )

def test_token_invalidation():
    """Test token invalidation on logout."""
    print_header("Testing Token Invalidation")
    
    for user_type, user_data in USERS.items():
        # Skip if we don't have an access token for this user
        if "access_token" not in user_data:
            print_result(
                f"Token invalidation for {user_type}",
                False,
                "No access token available for this user"
            )
            continue
        
        # Logout the user
        logout_response = requests.post(
            f"{BASE_URL}{ENDPOINTS['logout']}",
            headers={
                "Authorization": f"Bearer {user_data['access_token']}",
                "Content-Type": "application/json"
            },
            json={}
        )
        
        # Check if logout was successful
        logout_success = logout_response.status_code == 200
        
        if logout_success:
            # Try to access a protected endpoint with the invalidated token
            protected_response = requests.get(
                f"{BASE_URL}{ENDPOINTS['protected']}",
                headers={"Authorization": f"Bearer {user_data['access_token']}"}
            )
            
            # Token should be invalidated, so access should be denied
            token_invalidated = protected_response.status_code == 401
            
            print_result(
                f"Token invalidation for {user_type}",
                token_invalidated,
                f"Logout status: {logout_response.status_code}, "
                f"Protected access after logout: {protected_response.status_code}"
            )
        else:
            print_result(
                f"Token invalidation for {user_type}",
                False,
                f"Logout failed with status code {logout_response.status_code}: {logout_response.text}"
            )

def print_summary():
    """Print test summary."""
    print_header("Test Summary")
    print(f"Total tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Success rate: {(test_results['passed'] / test_results['total'] * 100):.2f}%")

def main():
    """Main test function."""
    print_header("JWT RBAC Authentication Test")
    
    try:
        # Run tests
        test_token_generation()
        test_protected_endpoints()
        test_token_refresh()
        test_token_invalidation()
        
        # Print summary
        print_summary()
        
        # Return exit code based on test results
        return 0 if test_results["failed"] == 0 else 1
    
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server. Make sure the Flask app is running.")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: An unexpected error occurred: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())