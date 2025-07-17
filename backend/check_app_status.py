"""
Script to check the status of the Flask application and JWT authentication endpoints.
"""
import requests
import sys

BASE_URL = "http://localhost:5000"

def check_server_status():
    """Check if the server is running."""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Server status: {'Running' if response.status_code == 200 else 'Error'}")
        print(f"Status code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("Server is not running.")
        return False

def check_jwt_endpoints():
    """Check if JWT authentication endpoints are registered."""
    endpoints = [
        "/api/auth/jwt/login",
        "/api/auth/refresh",
        "/api/auth/jwt/logout",
        "/api/auth/protected",
        "/api/auth/admin",
        "/api/auth/parent",
        "/api/auth/child",
        "/api/auth/teacher"
    ]
    
    print("\nChecking JWT endpoints:")
    for endpoint in endpoints:
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {'Available' if response.status_code != 404 else 'Not found'} (Status: {response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"{endpoint}: Connection error")

def main():
    """Main function."""
    if check_server_status():
        check_jwt_endpoints()
    else:
        print("Cannot check JWT endpoints because the server is not running.")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())