# Parent Dashboard Test Cases Documentation

## Test Suite Overview
**Module**: Parent Dashboard System  
**Test File**: `test_parent_dashboard.py`  
**APIs Tested**: `/api/tasks-for-parent/{child_id}`, `/api/chat/mood-summary/{child_id}`  
**Authentication**: JWT Bearer Token Required  
**Authorization**: Parent role and parent-child relationship required

---

## 1. Get Tasks for Parent Test Cases (`/api/tasks-for-parent/{child_id}`)

### Test Case 1.1: Get Tasks - Success with Valid Parent-Child Relationship
**API being tested**: `/api/tasks-for-parent/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/tasks-for-parent/1`
- Headers: `Authorization: Bearer {parent_jwt_token}`
- Database Setup:
  - Parent user with role 'parent'
  - Child user (test_user_id)
  - ParentChild relationship record
  - HomeworkSchedule task for child

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "tasks": [
    {
      "subject": "Science",
      "task": "Read chapter 5",
      "status": "pending",
      "user_id": "1"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Child's tasks returned successfully

**Result**: Success ✅

---

### Test Case 1.2: Get Tasks - Unauthorized Role (Non-Parent User)
**API being tested**: `/api/tasks-for-parent/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/tasks-for-parent/1`
- Headers: `Authorization: Bearer {child_jwt_token}` (non-parent user)
- User Role: 'child' (not 'parent')

**Expected output**:
- HTTP Status Code: 403
- JSON Response:
```json
{
  "success": false,
  "error": "parent role required"
}
```

**Actual Output**: HTTP Status Code: 403, Unauthorized access error returned

**Result**: Success ✅

---

### Test Case 1.3: Get Tasks - No Parent-Child Relationship
**API being tested**: `/api/tasks-for-parent/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/tasks-for-parent/1`
- Headers: `Authorization: Bearer {parent_jwt_token}`
- Database Setup:
  - Parent user with role 'parent'
  - Child user exists
  - No ParentChild relationship record

**Expected output**:
- HTTP Status Code: 403
- JSON Response:
```json
{
  "success": false,
  "error": "no parent-child relationship"
}
```

**Actual Output**: HTTP Status Code: 403, No relationship error returned

**Result**: Success ✅

---

## 2. Mood Summary Test Cases (`/api/chat/mood-summary/{child_id}`)

### Test Case 2.1: Get Mood Summary - Success with Chat Data
**API being tested**: `/api/chat/mood-summary/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/mood-summary/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Database Setup:
  - ChatSession records for child
  - LLMInteractions with mood tags ('happy')
  - User messages like "I love drawing!"
- LLM Service: Mock successful response

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "overall_mood": "happy because child enjoyed activities",
  "latest_mood": "happy",
  "mood_tags": ["happy"]
}
```

**Actual Output**: HTTP Status Code: 200, Mood summary generated successfully

**Result**: Success ✅

---

### Test Case 2.2: Get Mood Summary - No Chat Sessions
**API being tested**: `/api/chat/mood-summary/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/mood-summary/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Database Setup: No ChatSession records for child

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "overall_mood": null,
  "latest_mood": null,
  "mood_tags": []
}
```

**Actual Output**: HTTP Status Code: 200, Empty mood data returned gracefully

**Result**: Success ✅

---

### Test Case 2.3: Get Mood Summary - LLM Service Failure (Fallback)
**API being tested**: `/api/chat/mood-summary/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/mood-summary/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Database Setup:
  - ChatSession with interactions
  - Latest interaction with mood_tag 'sad'
- LLM Service: Mock exception "LLM error"

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "overall_mood": "Unable to summarize mood at this time.",
  "latest_mood": "sad",
  "mood_tags": ["sad"]
}
```

**Actual Output**: HTTP Status Code: 200, Fallback mood summary provided

**Result**: Success ✅

---
