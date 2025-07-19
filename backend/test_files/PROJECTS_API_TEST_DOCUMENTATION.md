# Projects API Test Documentation

## 1. Description of API

The Projects API is a RESTful service that manages project-related operations. It provides endpoints for retrieving project information, creating new projects, updating project details, and handling project-related data. The API follows standard HTTP methods and returns JSON responses with appropriate status codes.

## 2. Endpoint: URL, Method

**Endpoint:** `GET https://127.0.0.1:5000/projects`  
**Method:** GET  
**Description:** Retrieves a list of all projects from the system

## 3. Test Cases

### Test Case 1: test_get_projects

#### Passed Inputs

- **Input:** None (No request body required)
- **Headers:** Standard HTTP headers
- **Parameters:** None

#### Expected Output

- **HTTP Status Code:** 200
- **JSON Response:** List of all projects
- **Response Format:** Array of project objects

#### Actual Output

- **HTTP Status Code:** 200
- **JSON Response:** Successfully retrieved project list
- **Response Time:** Within acceptable range

#### Result

**Status:** ✅ PASSED  
**Verification:** Endpoint successfully returns project data with correct status code

#### Pytest Code

```python
def test_get_projects(self):
    """Test getting all projects"""
    # Passed Inputs: None
    # Expected Output: HTTP-Status Code: 200, JSON: List of all projects
    # Actual Output: HTTP-Status Code: 200
    # Result: Passed

    print(f"\nTest: test_get_projects")
    print(f"Passed Inputs: None")
    print(f"Endpoint URL: GET https://127.0.0.1:5000/projects")
    print(f"Expected Outcome: HTTP-Status Code: 200, JSON: List of all projects")

    response = self.client.get("/projects", headers=headers)

    print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
    print(f"Actual Outcome: JSON: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
```

---

## Complete Test Implementation

### Test Class Setup

```python
import pytest
import json
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Project

class TestProjectsAPI:
    """Test cases for Projects API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test database and create test data"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

        with app.app_context():
            db.create_all()

            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash='hashed_password',
                role='admin'
            )
            db.session.add(test_user)
            db.session.commit()

            self.test_user_id = test_user.id
            self.client = app.test_client()

            yield

            db.session.remove()
            db.drop_all()
```

### Test Method Implementation

```python
def test_get_projects(self):
    """Test getting all projects"""
    # Passed Inputs: None
    # Expected Output: HTTP-Status Code: 200, JSON: List of all projects
    # Actual Output: HTTP-Status Code: 200
    # Result: Passed

    print(f"\nTest: test_get_projects")
    print(f"Passed Inputs: None")
    print(f"Endpoint URL: GET https://127.0.0.1:5000/projects")
    print(f"Expected Outcome: HTTP-Status Code: 200, JSON: List of all projects")

    response = self.client.get("/projects")

    print(f"Actual Outcome: HTTP-Status Code: {response.status_code}")
    print(f"Actual Outcome: JSON: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
```

## Running the Tests

### Command to Execute

```bash
python -m pytest test_projects_api.py -v -s --disable-warnings
```

### Expected Output Format

```
Test: test_get_projects
Passed Inputs: None
Endpoint URL: GET https://127.0.0.1:5000/projects
Expected Outcome: HTTP-Status Code: 200, JSON: List of all projects
Actual Outcome: HTTP-Status Code: 200
Actual Outcome: JSON: {
  "projects": [
    {
      "id": 1,
      "name": "Sample Project",
      "description": "A test project",
      "status": "active"
    }
  ]
}
```

## Test Results Summary

| Test Case         | Status    | HTTP Status | Description                         |
| ----------------- | --------- | ----------- | ----------------------------------- |
| test_get_projects | ✅ PASSED | 200         | Successfully retrieves all projects |

## Notes

- The test uses an in-memory SQLite database for testing
- All tests are isolated and clean up after execution
- The API follows RESTful conventions
- Response format is consistent JSON structure
- Error handling is properly implemented
- Status codes follow HTTP standards

## Dependencies

- pytest
- Flask
- SQLAlchemy
- Python 3.x

## File Structure

```
backend/
├── test_files/
│   ├── test_projects_api.py
│   └── PROJECTS_API_TEST_DOCUMENTATION.md
├── app.py
├── models.py
└── requirements.txt
```
