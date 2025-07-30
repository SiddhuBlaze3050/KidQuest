# Notifications Test Cases Documentation

## Test Suite Overview
**Module**: Notification System  
**Test File**: `test_notifications.py`  
**APIs Tested**: `/api/notifications/{user_id}`, `/api/notifications/mark-read`, `/api/auth/login`  
**Authentication**: JWT Bearer Token Required  

---

## 1. Authentication Test Cases

### Test Case 1.1: User Login for Notification Testing
**API being tested**: `/api/auth/login`

**Inputs**:
- HTTP Method: POST
- JSON Body:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "access_token": "jwt_token_string",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

**Actual Output**: HTTP Status Code: 200, JWT token and user data returned

**Result**: Success ✅

---

### Test Case 1.2: Authentication Failure
**API being tested**: `/api/auth/login`

**Inputs**:
- HTTP Method: POST
- JSON Body:
```json
{
  "username": "admin",
  "password": "wrongpassword"
}
```

**Expected output**:
- HTTP Status Code: 401
- JSON Response:
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

**Actual Output**: HTTP Status Code: 401, Authentication failed

**Result**: Success ✅

---

## 2. Get Notifications Test Cases

### Test Case 2.1: Get Notifications - Initial State
**API being tested**: `/api/notifications/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/notifications/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (authenticated admin user)

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 1,
      "content": "Welcome back! You have new updates.",
      "notification_type": "info",
      "is_read": false,
      "created_at": "2025-07-30T12:00:00"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Notifications array returned

**Result**: Success ✅

---

### Test Case 2.2: Get Notifications - Verify Persistence
**API being tested**: `/api/notifications/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/notifications/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Subsequent request to verify data persistence

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Same notifications with consistent data

**Actual Output**: HTTP Status Code: 200, Consistent notification data returned

**Result**: Success ✅

---

### Test Case 2.3: Get Notifications - Unauthorized Access
**API being tested**: `/api/notifications/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/notifications/999`
- Headers: `Authorization: Bearer {jwt_token}`
- Attempting to access different user's notifications

**Expected output**:
- HTTP Status Code: 403
- JSON Response:
```json
{
  "error": "Unauthorized access"
}
```

**Actual Output**: HTTP Status Code: 403, Properly rejected unauthorized access

**Result**: Success ✅

---

## 3. Mark Notifications as Read Test Cases

### Test Case 3.1: Mark Notifications as Read - Success
**API being tested**: `/api/notifications/mark-read`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "notification_ids": [1, 2]
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "message": "Notifications marked as read",
  "marked_count": 2
}
```

**Actual Output**: HTTP Status Code: 200, Notifications successfully marked as read

**Result**: Success ✅

---

### Test Case 3.2: Mark Notifications as Read - Empty Array
**API being tested**: `/api/notifications/mark-read`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "notification_ids": []
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Handling of empty notification array

**Actual Output**: HTTP Status Code: 200, Empty array handled gracefully

**Result**: Success ✅

---

### Test Case 3.3: Verify Read Status Update
**API being tested**: `/api/notifications/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/notifications/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Verification after marking notifications as read

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Notifications with updated `is_read: true` status

**Actual Output**: HTTP Status Code: 200, Read status properly updated

**Result**: Success ✅

---

## 4. Automatic Notification Generation Test Cases

### Test Case 4.1: Auto-Generation on Login
**API being tested**: `/api/auth/login` (triggers notification generation)

**Inputs**:
- HTTP Method: POST
- JSON Body:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Expected output**:
- HTTP Status Code: 200
- Side Effect: Automatic notifications generated for user

**Actual Output**: HTTP Status Code: 200, Login successful with auto-notifications

**Result**: Success ✅

---

### Test Case 4.2: Verify Auto-Generated Notifications
**API being tested**: `/api/notifications/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/notifications/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Check for auto-generated welcome/activity notifications

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Contains auto-generated notifications with "Welcome back" or activity-related content

**Actual Output**: HTTP Status Code: 200, Auto-generated notifications present

**Result**: Success ✅

---

## 5. Backend Connectivity Test Cases

### Test Case 5.1: Backend Health Check
**API being tested**: Backend connectivity verification

**Inputs**:
- HTTP Method: GET
- URL: `/api/auth/login`
- Timeout: 5 seconds

**Expected output**:
- HTTP Status Code: Any response (indicates backend is running)
- Connection established within timeout

**Actual Output**: Connection successful, backend responding

**Result**: Success ✅

---

### Test Case 5.2: Backend Connection Failure Handling
**API being tested**: Backend connectivity with unavailable server

**Inputs**:
- HTTP Method: GET
- URL: `/api/auth/login`
- Scenario: Backend server not running

**Expected output**:
- Connection Error: `requests.exceptions.ConnectionError`
- Graceful error handling and user notification

**Actual Output**: Connection error properly handled with user-friendly message

**Result**: Success ✅
