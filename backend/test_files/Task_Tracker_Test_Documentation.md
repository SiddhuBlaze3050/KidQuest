# Task Tracker Test Cases Documentation

## Test Suite Overview
**Module**: Task Tracker  
**Test File**: `test_task_tracker.py`  
**APIs Tested**: `/api/homework/tasks`, `/api/homework/create`, `/api/homework/update-status`  
**Authentication**: JWT Bearer Token Required  

---

## 1. Get Tasks Test Cases

### Test Case 1.1: Get Tasks - Empty Database
**API being tested**: `/api/homework/tasks/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/homework/tasks/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (valid test user)

**Expected output**:
- HTTP Status Code: 200
- JSON Response: 
```json
{
  "success": true,
  "tasks": []
}
```

**Actual Output**: HTTP Status Code: 200, Empty tasks array returned

**Result**: Success ✅

---

### Test Case 1.2: Get Tasks - With Existing Data
**API being tested**: `/api/homework/tasks/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/homework/tasks/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing task data in database

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "title": "Math Homework",
      "description": "Complete algebra problems",
      "due_date": "2025-01-01",
      "status": "pending",
      "user_id": 1
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Tasks array with existing homework returned

**Result**: Success ✅

---

### Test Case 1.3: Get Tasks - Invalid User ID
**API being tested**: `/api/homework/tasks/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/homework/tasks/invalid_id`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 404
- JSON Response: Error message for invalid user ID

**Actual Output**: HTTP Status Code: 404, Invalid user ID error returned

**Result**: Success ✅

---

## 2. Create Task Test Cases

### Test Case 2.1: Create Task - Success
**API being tested**: `/api/homework/create`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "title": "Science Project",
  "description": "Research on solar system",
  "due_date": "2025-02-15",
  "user_id": 1
}
```

**Expected output**:
- HTTP Status Code: 201
- JSON Response:
```json
{
  "success": true,
  "message": "Task created successfully",
  "task": {
    "id": 1,
    "title": "Science Project",
    "description": "Research on solar system",
    "due_date": "2025-02-15",
    "status": "pending",
    "user_id": 1
  }
}
```

**Actual Output**: HTTP Status Code: 201, Task created successfully with generated ID

**Result**: Success ✅

---

### Test Case 2.2: Create Task - Invalid Date Format
**API being tested**: `/api/homework/create`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "title": "History Essay",
  "description": "Write about World War II",
  "due_date": "invalid-date-format",
  "user_id": 1
}
```

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "success": false,
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

**Actual Output**: HTTP Status Code: 400, Date format validation error returned

**Result**: Success ✅

---

### Test Case 2.3: Create Task - Empty Date (Uses Tomorrow)
**API being tested**: `/api/homework/create`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "title": "English Reading",
  "description": "Read chapter 5",
  "due_date": "",
  "user_id": 1
}
```

**Expected output**:
- HTTP Status Code: 201
- JSON Response: Task created with tomorrow's date as default

**Actual Output**: HTTP Status Code: 201, Task created with default due date (tomorrow)

**Result**: Success ✅

---

### Test Case 2.4: Create Task - Missing Required Fields
**API being tested**: `/api/homework/create`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "title": "Incomplete Task"
}
```

**Expected output**:
- HTTP Status Code: 500
- JSON Response:
```json
{
  "success": false,
  "error": "Failed to create task",
  "message": "Missing required fields"
}
```

**Actual Output**: HTTP Status Code: 500, Missing fields error returned

**Result**: Success ✅

---

## 3. Update Task Status Test Cases

### Test Case 3.1: Update Task Status - Success
**API being tested**: `/api/homework/update-status/{task_id}`

**Inputs**:
- HTTP Method: PUT
- URL: `/api/homework/update-status/1`
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "status": "completed"
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "message": "Task status updated successfully",
  "task": {
    "id": 1,
    "status": "completed"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Task status updated to completed

**Result**: Success ✅

---

### Test Case 3.2: Update Task Status - Task Not Found
**API being tested**: `/api/homework/update-status/{task_id}`

**Inputs**:
- HTTP Method: PUT
- URL: `/api/homework/update-status/999`
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "status": "completed"
}
```

**Expected output**:
- HTTP Status Code: 404
- JSON Response:
```json
{
  "success": false,
  "error": "Task not found"
}
```

**Actual Output**: HTTP Status Code: 404, Task not found error returned

**Result**: Success ✅
