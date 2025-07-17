"""
Script to manually test login for each user.
"""
import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
USERS = {
    "admin": {"username": "admin", "password": "admin123", "role": "admin"},
    "parent": {"username": "parent", "password": "parentparent", "role": "parent"},
    "child": {"username": "child", "password": "childchild", "role": "child"},
    "teacher": {"username": "teacher", "password": "teacherteacher", "role": "teacher"}
}

def test_login(username, password):
    """Test login for a user."""
    print(f"Testing login for {username}...")
    
    # Make the login request
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    
    # Print the response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # If login was successful, print the tokens
    if response.status_code == 200:
        data = response.json()
        print(f"Access token: {data.get('access_token')[:20]}...")
        print(f"Refresh token: {data.get('refresh_token')[:20]}...")
    
    print()

def main():
    """Main function."""
    for user_type, user_data in USERS.items():
        test_login(user_data["username"], user_data["password"])

if __name__ == "__main__":
    main()