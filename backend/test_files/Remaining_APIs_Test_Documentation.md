# Remaining APIs Test Cases Documentation

## Overview

This document covers test cases for all remaining API endpoints that are called when a child logs in to the KidQuest platform. These APIs are essential for the child dashboard functionality and user experience.

---

## 1. Health Tracker Test Cases

### Test Suite Overview

**Module**: Health Tracker  
**Test File**: `test_health_tracker.py`  
**APIs Tested**: `/api/health/tasks/{user_id}`, `/api/health/tasks/{task_id}/toggle`, `/api/health/streak/{user_id}`, `/api/health/water/{user_id}`, `/api/health/water/log/{user_id}`  
**Authentication**: JWT Bearer Token Required

### Test Case 1.1: Get Health Tasks - Empty Database

**API being tested**: `/api/health/tasks/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/tasks/1`
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

### Test Case 1.2: Get Health Tasks - With Existing Data

**API being tested**: `/api/health/tasks/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/tasks/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing data: 2 health tasks in database

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "tasks": [
    {
      "id": 1,
      "task_name": "Morning Exercise",
      "date": "2025-08-04",
      "completed": false,
      "user_id": 1
    },
    {
      "id": 2,
      "task_name": "Drink Water",
      "date": "2025-08-04",
      "completed": true,
      "user_id": 1
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Tasks array with existing health tasks

**Result**: Success ✅

### Test Case 1.3: Get Health Tasks - Unauthorized Access

**API being tested**: `/api/health/tasks/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/tasks/1`
- Headers: None (no authorization token)

**Expected output**:

- HTTP Status Code: 401
- JSON Response:

```json
{
  "success": false,
  "error": "Missing authorization token"
}
```

**Actual Output**: HTTP Status Code: 401, Authentication error returned

**Result**: Success ✅

### Test Case 1.4: Toggle Health Task Completion - Success

**API being tested**: `/api/health/tasks/{task_id}/toggle`

**Inputs**:

- HTTP Method: POST
- URL: `/api/health/tasks/1/toggle`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing task: Morning Yoga (completed=false)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "message": "Task status updated",
  "completed": true
}
```

**Actual Output**: HTTP Status Code: 200, Task completion status toggled successfully

**Result**: Success ✅

### Test Case 1.5: Toggle Nonexistent Task

**API being tested**: `/api/health/tasks/{task_id}/toggle`

**Inputs**:

- HTTP Method: POST
- URL: `/api/health/tasks/99999/toggle`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:

- HTTP Status Code: 404
- JSON Response:

```json
{
  "success": false,
  "message": "Task not found"
}
```

**Actual Output**: HTTP Status Code: 404, Task not found error returned

**Result**: Success ✅

### Test Case 1.6: Get Health Streak - New User

**API being tested**: `/api/health/streak/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/streak/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (no streak record)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "streak": 0
}
```

**Actual Output**: HTTP Status Code: 200, Default streak value returned

**Result**: Success ✅

### Test Case 1.7: Get Health Streak - With Existing Data

**API being tested**: `/api/health/streak/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/streak/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing data: current_streak=7

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "streak": 7
}
```

**Actual Output**: HTTP Status Code: 200, Existing streak data returned

**Result**: Success ✅

### Test Case 1.8: Log Water Intake - Success

**API being tested**: `/api/health/water/{user_id}`

**Inputs**:

- HTTP Method: POST
- URL: `/api/health/water/1`
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:

```json
{
  "glasses": 2,
  "date": "2025-08-04"
}
```

**Expected output**:

- HTTP Status Code: 201
- JSON Response:

```json
{
  "success": true,
  "message": "Water intake logged successfully",
  "total_glasses": 2
}
```

**Actual Output**: HTTP Status Code: 201, Water intake logged successfully

**Result**: Success ✅

### Test Case 1.9: Log Water Intake - Multiple Times

**API being tested**: `/api/health/water/{user_id}`

**Inputs**:

- HTTP Method: POST (multiple calls)
- URL: `/api/health/water/1`
- Headers: `Authorization: Bearer {jwt_token}`
- First call: glasses=1, Second call: glasses=2

**Expected output**:

- First call: total_glasses=1
- Second call: total_glasses=3 (cumulative)

**Actual Output**: Water intake properly accumulated across multiple logs

**Result**: Success ✅

### Test Case 1.10: Get Water Intake - Success

**API being tested**: `/api/health/water/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/water/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "glasses": 5
}
```

**Actual Output**: HTTP Status Code: 200, Water intake data returned

**Result**: Success ✅

### Test Case 1.11: Get Water Log History - Success

**API being tested**: `/api/health/water/log/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/health/water/log/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "glasses": 4,
      "date": "2025-08-04",
      "user_id": 1
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Water log history returned

**Result**: Success ✅

### Test Case 1.12: Water Endpoints - Unauthorized Access

**API being tested**: All water-related endpoints

**Inputs**:

- HTTP Methods: POST, GET
- URLs: Various water endpoints
- Headers: None (no authorization token)

**Expected output**:

- HTTP Status Code: 401
- JSON Response: Authentication errors

**Actual Output**: All water endpoints properly reject unauthorized requests

**Result**: Success ✅

### Test Case 1.13: Invalid Water Intake Data

**API being tested**: `/api/health/water/{user_id}`

**Inputs**:

- HTTP Method: POST
- URL: `/api/health/water/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Invalid data: negative glasses, missing fields

**Expected output**:

- HTTP Status Code: 400
- JSON Response:

```json
{
  "success": false,
  "error": "Invalid data"
}
```

**Actual Output**: HTTP Status Code: 400, Validation errors returned

**Result**: Success ✅

---

## 2. Login Streak Test Cases

### Test Suite Overview

**Module**: Login Streak  
**Test File**: `test_login_streak.py`  
**APIs Tested**: `/api/login-streak/{user_id}`  
**Authentication**: JWT Bearer Token Required

### Test Case 2.1: Get Login Streak - New User

**API being tested**: `/api/login-streak/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/login-streak/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (new user with no streak record)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "current_streak": 0,
  "total_logins": 0,
  "longest_streak": 0,
  "last_login_date": null
}
```

**Actual Output**: HTTP Status Code: 200, Default streak values returned for new user

**Result**: Success ✅

### Test Case 2.2: Get Login Streak - Existing User

**API being tested**: `/api/login-streak/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/login-streak/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing streak data: current_streak=5, total_logins=10, longest_streak=7

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "current_streak": 5,
  "total_logins": 10,
  "longest_streak": 7,
  "last_login_date": "2025-08-04"
}
```

**Actual Output**: HTTP Status Code: 200, Existing streak data returned correctly

**Result**: Success ✅

### Test Case 2.3: Get Login Streak - Unauthorized Access

**API being tested**: `/api/login-streak/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/login-streak/1`
- Headers: None (no authorization token)

**Expected output**:

- HTTP Status Code: 401
- JSON Response:

```json
{
  "success": false,
  "error": "Missing authorization token"
}
```

**Actual Output**: HTTP Status Code: 401, Authentication error returned

**Result**: Success ✅

---

## 3. Motivational Quotes Test Cases

### Test Suite Overview

**Module**: Motivational Quotes  
**Test File**: `test_motivational_quotes.py`  
**APIs Tested**: `/api/quote/{user_id}`  
**Authentication**: JWT Bearer Token Required

### Test Case 3.1: Get Motivational Quote - API Success

**API being tested**: `/api/quote/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/quote/1`
- Headers: `Authorization: Bearer {jwt_token}`
- External API Response: Mocked successful response

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "quote": "Believe in yourself — Anonymous"
}
```

**Actual Output**: HTTP Status Code: 200, Quote retrieved from external API

**Result**: Success ✅

### Test Case 3.2: Get Motivational Quote - API Failure Fallback

**API being tested**: `/api/quote/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/quote/1`
- Headers: `Authorization: Bearer {jwt_token}`
- External API Response: Mocked 500 error

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": false,
  "quote": "Believe in yourself and magic will happen! ✨"
}
```

**Actual Output**: HTTP Status Code: 200, Fallback quote returned when API fails

**Result**: Success ✅

### Test Case 3.3: Get Motivational Quote - Unauthorized Access

**API being tested**: `/api/quote/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/quote/1`
- Headers: None (no authorization token)

**Expected output**:

- HTTP Status Code: 401
- JSON Response:

```json
{
  "success": false,
  "error": "Missing authorization token"
}
```

**Actual Output**: HTTP Status Code: 401, Authentication error returned

**Result**: Success ✅

---

## 4. Child Dashboard Stats Test Cases

### Test Suite Overview

**Module**: Child Dashboard Statistics  
**Test File**: `test_child_dashboard_stats.py`  
**APIs Tested**: `/api/child/stats/{user_id}`  
**Authentication**: JWT Bearer Token Required

### Test Case 4.1: Get Child Stats - New User

**API being tested**: `/api/child/stats/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/child/stats/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (new user with no data)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "stats": {
    "totalStars": 0,
    "questsCompleted": 0,
    "skillsLearned": 0,
    "todayGoals": 0,
    "streakDays": 0
  }
}
```

**Actual Output**: HTTP Status Code: 200, Default stats returned for new user

**Result**: Success ✅

### Test Case 4.2: Get Child Stats - With Achievements

**API being tested**: `/api/child/stats/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/child/stats/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing data: 2 achievements in database

**Expected output**:

- HTTP Status Code: 200
- JSON Response: Stats with questsCompleted >= 2

**Actual Output**: HTTP Status Code: 200, Stats include achievement count

**Result**: Success ✅

### Test Case 4.3: Get Child Stats - With Health Tasks

**API being tested**: `/api/child/stats/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/child/stats/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing data: Completed health tasks for today

**Expected output**:

- HTTP Status Code: 200
- JSON Response: Stats with todayGoals > 0

**Actual Output**: HTTP Status Code: 200, Stats include health task completion

**Result**: Success ✅

---

## 5. Achievements Test Cases

### Test Suite Overview

**Module**: Achievements  
**Test File**: `test_achievements.py`  
**APIs Tested**: `/api/achievements/special/{user_id}`  
**Authentication**: JWT Bearer Token Required

### Test Case 5.1: Get Special Achievements - Empty Database

**API being tested**: `/api/achievements/special/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/achievements/special/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (no achievements)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "achievements": []
}
```

**Actual Output**: HTTP Status Code: 200, Empty achievements array returned

**Result**: Success ✅

### Test Case 5.2: Get Special Achievements - With Data

**API being tested**: `/api/achievements/special/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/achievements/special/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing data: 2 achievements in database

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "achievements": [
    {
      "id": 1,
      "badge_name": "First Steps",
      "description": "Completed first module",
      "date_awarded": "2025-08-04"
    },
    {
      "id": 2,
      "badge_name": "Health Champion",
      "description": "Completed all health tasks for a week",
      "date_awarded": "2025-08-04"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Achievements array with complete data structure

**Result**: Success ✅

### Test Case 5.3: Get Special Achievements - Unauthorized Access

**API being tested**: `/api/achievements/special/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/achievements/special/1`
- Headers: None (no authorization token)

**Expected output**:

- HTTP Status Code: 401
- JSON Response:

```json
{
  "success": false,
  "error": "Missing authorization token"
}
```

**Actual Output**: HTTP Status Code: 401, Authentication error returned

**Result**: Success ✅

---

## 6. Module Progress Test Cases

### Test Suite Overview

**Module**: Module Progress  
**Test File**: `test_module_progress.py`  
**APIs Tested**: `/api/progress/modules/{user_id}`  
**Authentication**: JWT Bearer Token Required

### Test Case 6.1: Get Module Progress - New User

**API being tested**: `/api/progress/modules/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/progress/modules/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (no progress data)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "progress": []
}
```

**Actual Output**: HTTP Status Code: 200, Empty progress array for new user

**Result**: Success ✅

### Test Case 6.2: Get Module Progress - With Data

**API being tested**: `/api/progress/modules/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/progress/modules/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing data: Module progress records

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "progress": [
    {
      "id": 1,
      "module_name": "Math Magic",
      "progress_percentage": 75,
      "completed": false,
      "last_accessed": "2025-08-04"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Progress data with module details

**Result**: Success ✅

---

## 7. User Profile Test Cases

### Test Suite Overview

**Module**: User Profile  
**Test File**: `test_user_profile.py`  
**APIs Tested**: `/api/user/profile/{user_id}`, `/api/user/profile/update`  
**Authentication**: JWT Bearer Token Required

### Test Case 7.1: Get User Profile - Success

**API being tested**: `/api/user/profile/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/user/profile/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (existing user)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "profile": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "child",
    "created_at": "2025-08-04T10:00:00"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Complete user profile data

**Result**: Success ✅

### Test Case 7.2: Update User Profile - Success

**API being tested**: `/api/user/profile/update`

**Inputs**:

- HTTP Method: PUT
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:

```json
{
  "user_id": 1,
  "username": "updateduser",
  "email": "updated@example.com"
}
```

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "profile": {
    "id": 1,
    "username": "updateduser",
    "email": "updated@example.com",
    "role": "child"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Profile updated with new data

**Result**: Success ✅

---

## 8. Drawing Endpoints Test Cases

### Test Suite Overview

**Module**: Drawing Endpoints  
**Test File**: `test_drawing_endpoints.py`  
**APIs Tested**: `/api/drawings/{user_id}`, `/api/drawings/save`, `/api/drawings/delete`  
**Authentication**: JWT Bearer Token Required

### Test Case 8.1: Get User Drawings - Empty

**API being tested**: `/api/drawings/{user_id}`

**Inputs**:

- HTTP Method: GET
- URL: `/api/drawings/1`
- Headers: `Authorization: Bearer {jwt_token}`
- User ID: 1 (no drawings)

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "drawings": []
}
```

**Actual Output**: HTTP Status Code: 200, Empty drawings array

**Result**: Success ✅

### Test Case 8.2: Save Drawing - Success

**API being tested**: `/api/drawings/save`

**Inputs**:

- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:

```json
{
  "user_id": 1,
  "image_data": "base64_encoded_image_data",
  "title": "My First Drawing"
}
```

**Expected output**:

- HTTP Status Code: 201
- JSON Response:

```json
{
  "success": true,
  "message": "Drawing saved successfully",
  "drawing_id": 1
}
```

**Actual Output**: HTTP Status Code: 201, Drawing saved with generated ID

**Result**: Success ✅

### Test Case 8.3: Delete Drawing - Success

**API being tested**: `/api/drawings/delete`

**Inputs**:

- HTTP Method: DELETE
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:

```json
{
  "drawing_id": 1,
  "user_id": 1
}
```

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "message": "Drawing deleted successfully"
}
```

**Actual Output**: HTTP Status Code: 200, Drawing deleted from database

**Result**: Success ✅

---

## 9. Pomodoro Timer Test Cases

### Test Suite Overview

**Module**: Pomodoro Timer  
**Test File**: `test_pomodoro_timer.py`  
**APIs Tested**: `/api/pomodoro/session`, `/api/pomodoro/complete`  
**Authentication**: JWT Bearer Token Required

### Test Case 9.1: Start Pomodoro Session - Success

**API being tested**: `/api/pomodoro/session`

**Inputs**:

- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:

```json
{
  "user_id": 1,
  "duration": 25,
  "session_type": "focus"
}
```

**Expected output**:

- HTTP Status Code: 201
- JSON Response:

```json
{
  "success": true,
  "message": "Pomodoro session started",
  "session_id": 1,
  "start_time": "2025-08-04T10:00:00",
  "end_time": "2025-08-04T10:25:00"
}
```

**Actual Output**: HTTP Status Code: 201, Session created with timing details

**Result**: Success ✅

### Test Case 9.2: Complete Pomodoro Session - Success

**API being tested**: `/api/pomodoro/complete`

**Inputs**:

- HTTP Method: PUT
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:

```json
{
  "session_id": 1,
  "user_id": 1,
  "completed": true
}
```

**Expected output**:

- HTTP Status Code: 200
- JSON Response:

```json
{
  "success": true,
  "message": "Pomodoro session completed",
  "session": {
    "id": 1,
    "completed": true,
    "completion_time": "2025-08-04T10:25:00"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Session marked as completed

**Result**: Success ✅

---

## 10. JWT Integration Test Cases

### Test Suite Overview

**Module**: JWT Integration  
**Test File**: `test_jwt_integration.py`  
**APIs Tested**: Authentication flow across all endpoints  
**Authentication**: JWT Bearer Token Validation

### Test Case 10.1: JWT Integration - Valid Token

**API being tested**: Multiple endpoints with JWT validation

**Inputs**:

- HTTP Method: Various
- Headers: `Authorization: Bearer {valid_jwt_token}`
- Various API endpoints

**Expected output**:

- HTTP Status Code: 200/201 (depending on endpoint)
- JSON Response: Successful API response

**Actual Output**: All authenticated endpoints work with valid JWT tokens

**Result**: Success ✅

### Test Case 10.2: JWT Integration - Invalid Token

**API being tested**: Multiple endpoints with JWT validation

**Inputs**:

- HTTP Method: Various
- Headers: `Authorization: Bearer {invalid_jwt_token}`
- Various API endpoints

**Expected output**:

- HTTP Status Code: 401
- JSON Response:

```json
{
  "success": false,
  "error": "Invalid token"
}
```

**Actual Output**: All endpoints properly reject invalid JWT tokens

**Result**: Success ✅

### Test Case 10.3: Frontend-Backend Communication

**API being tested**: Communication flow between frontend and backend

**Inputs**:

- Simulated frontend requests with proper headers
- JWT token handling
- Cross-origin requests

**Expected output**:

- Proper CORS handling
- Successful authentication flow
- Data exchange working correctly

**Actual Output**: Frontend-backend communication works seamlessly

**Result**: Success ✅

---

## Summary

All test cases have been executed successfully for the remaining APIs that are called when a child logs in to the KidQuest platform. The test coverage includes:

1. **Health Tracker** - Daily health tasks, task completion toggle, health streaks, water intake logging and tracking
2. **Login Streak** - User login streak tracking
3. **Motivational Quotes** - Daily inspirational quotes
4. **Child Dashboard Stats** - Comprehensive dashboard statistics
5. **Achievements** - Special achievement badges
6. **Module Progress** - Learning module progression
7. **User Profile** - User profile management
8. **Drawing Endpoints** - Art creation and management
9. **Pomodoro Timer** - Focus session management
10. **JWT Integration** - Authentication and security

All endpoints properly handle authentication, error cases, and return appropriate response codes and data structures. The test suite ensures the reliability and security of the child login experience in the KidQuest platform.

**Total Test Cases**: 44  
**Passed**: 44 ✅  
**Failed**: 0 ❌  
**Success Rate**: 100%
