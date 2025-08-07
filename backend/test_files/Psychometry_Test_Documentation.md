# Psychometry Test Cases Documentation

## Test Suite Overview
**Module**: Psychometric Assessment System  
**Test File**: `test_psychometry.py`  
**APIs Tested**: `/api/psychometry/results`, `/api/psychometry/submit`  
**Authentication**: JWT Bearer Token Required  

---

## 1. Get Psychometry Results Test Cases

### Test Case 1.1: Get Results - Empty Database
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Child ID: 1 (valid test user)

**Expected output**:
- HTTP Status Code: 404
- JSON Response:
```json
{
  "success": false,
  "error": "No result found"
}
```

**Actual Output**: HTTP Status Code: 404, No result found error returned

**Result**: Success ✅

---

### Test Case 1.2: Get Results - With Existing Data
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Pre-existing psychometric test results in database

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "result": {
    "id": 2,
    "child_id": "1",
    "learning_style": "Auditory",
    "personality_type": "Extroverted",
    "top_interest": "Science",
    "concentration_level": 85.0,
    "memory_strength": 78.0,
    "duration_seconds": 150.2,
    "taken_at": "2025-07-30T12:00:00"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Latest psychometric result returned

**Result**: Success ✅

---

### Test Case 1.3: Get Results - Invalid Child ID
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/invalid_id`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 404
- JSON Response: Error for invalid child ID format

**Actual Output**: HTTP Status Code: 404, Invalid ID error returned

**Result**: Success ✅

---

### Test Case 1.4: Get Results - Nonexistent Child ID
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/999`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 404
- JSON Response:
```json
{
  "success": false,
  "error": "No result found"
}
```

**Actual Output**: HTTP Status Code: 404, No result found for nonexistent user

**Result**: Success ✅

---

## 2. Submit Psychometry Answer Test Cases

### Test Case 2.1: Submit Answer - Success with Valid Session
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: Valid psychometry session with questions
- JSON Body:
```json
{
  "user_id": "1",
  "answer": "A"
}
```

**Expected output**:
- HTTP Status Code: 200 or 302
- JSON Response: Next question or completion redirect

**Actual Output**: HTTP Status Code: 200/302, Answer processed successfully

**Result**: Success ✅

---

### Test Case 2.2: Submit Answer - No Session Data
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: None (empty session)
- JSON Body:
```json
{
  "user_id": "1",
  "answer": "A"
}
```

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "User ID mismatch or missing"
}
```

**Actual Output**: HTTP Status Code: 400, Session validation error returned

**Result**: Success ✅

---

### Test Case 2.3: Submit Answer - Invalid Question Index
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: Empty questions array
- JSON Body:
```json
{
  "user_id": "1",
  "answer": "A"
}
```

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "Invalid question index"
}
```

**Actual Output**: HTTP Status Code: 400, Invalid question index error returned

**Result**: Success ✅

---

### Test Case 2.4: Submit Answer - Service Error
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: Valid session with mocked service failure
- JSON Body:
```json
{
  "user_id": "1",
  "answer": "A"
}
```

**Expected output**:
- HTTP Status Code: 500
- JSON Response:
```json
{
  "error": "Failed to submit answer",
  "message": "Service unavailable"
}
```

**Actual Output**: HTTP Status Code: 500, Service error handled gracefully

**Result**: Success ✅

---

### Test Case 2.5: Submit Answer - Missing Answer Field
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: Valid psychometry session
- JSON Body:
```json
{
  "user_id": "1"
}
```

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "No answer provided"
}
```

**Actual Output**: HTTP Status Code: 400, Missing answer validation error returned

**Result**: Success ✅

---

### Test Case 2.6: Submit Answer - User ID Mismatch
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: User ID "999" in session
- JSON Body:
```json
{
  "user_id": "1",
  "answer": "A"
}
```

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "User ID mismatch or missing"
}
```

**Actual Output**: HTTP Status Code: 400, User ID mismatch validation error returned

**Result**: Success ✅



### Test Case 3.1: Get Results - No Results for Child
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/{child_id}` (where child has no results)
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 404
- JSON Response:
```json
{
  "success": false,
  "error": "No result found"
}
```

**Actual Output**: HTTP Status Code: 404, No result found error returned

**Result**: Success ✅

---

### Test Case 3.2: Get Results - Returns Latest Result
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/{child_id}` (child has multiple results)
- Headers: `Authorization: Bearer {jwt_token}`
- Database: Two results for the same child, with different timestamps

**Expected output**:
- HTTP Status Code: 200
- JSON Response contains the most recent result (by `taken_at`), e.g.:
```json
{
  "success": true,
  "result": {
    "learning_style": "Visual",
    "personality_type": "Introvert",
    "top_interest": "Math",
    "concentration_level": 90.0,
    "memory_strength": 95.0,
    "feedback": "New result"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Most recent result returned

**Result**: Success ✅

---

### Test Case 3.3: Get Results - Partial Data (Missing Optional Fields)
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/{child_id}` (child has a result with only required fields)
- Headers: `Authorization: Bearer {jwt_token}`
- Database: Result missing optional fields like `detailed_scores`, `personality_breakdown`, `duration_seconds`, `feedback`

**Expected output**:
- HTTP Status Code: 200
- JSON Response contains the result, with missing fields as `null` or empty:
```json
{
  "success": true,
  "result": {
    "learning_style": "Visual",
    "personality_type": "Introvert",
    "top_interest": "Math",
    "concentration_level": 90.0,
    "memory_strength": 95.0,
    "detailed_scores": null
  }
}
```

**Actual Output**: HTTP Status Code: 200, Result returned with missing fields as `null` or `{}`

**Result**: Success ✅