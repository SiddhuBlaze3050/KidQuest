# Psychometry Test Cases Documentation

## Test Suite Overview
**Module**: Psychometric Assessment System  
**Test File**: `test_psychometry.py`  
**APIs Tested**: `/api/psychometry/start`, `/api/psychometry/results`, `/api/psychometry/submit`  
**Authentication**: JWT Bearer Token Required  

---

## 1. Start Psychometry Test Cases (`/api/psychometry/start`)

### Test Case 1.1: Start Test - Success with Valid User ID
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{"user_id": "1"}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "question": "What is your preferred way of learning?",
  "options": ["Visual diagrams", "Audio lectures", "Hands-on practice", "Reading text"],
  "question_number": 1,
  "total_questions": 3,
  "progress": 0.0
}
```
- Session Setup: User ID, questions array, responses array, start time

**Actual Output**: HTTP Status Code: 200, First question returned with session initialized

**Result**: Success ✅

---

### Test Case 1.2: Start Test - Missing User ID
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{}` (empty body)

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "user_id is required"
}
```

**Actual Output**: HTTP Status Code: 400, User ID required error returned

**Result**: Success ✅

---

### Test Case 1.3: Start Test - Service Error
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{"user_id": "1"}`
- Service: Mocked to throw exception

**Expected output**:
- HTTP Status Code: 500
- JSON Response:
```json
{
  "error": "Failed to start psychometry test",
  "message": "Service initialization failed"
}
```

**Actual Output**: HTTP Status Code: 500, Service error handled gracefully

**Result**: Success ✅

---

### Test Case 1.4: Start Test - Null User ID
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{"user_id": null}`

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "user_id is required"
}
```

**Actual Output**: HTTP Status Code: 400, User ID required error returned

**Result**: Success ✅

---

### Test Case 1.5: Start Test - Empty String User ID
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{"user_id": ""}`

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "error": "user_id is required"
}
```

**Actual Output**: HTTP Status Code: 400, User ID required error returned

**Result**: Success ✅

---

## 2. Get Psychometry Results Test Cases (`/api/psychometry/results/{child_id}`)

### Test Case 2.1: Get Results - Empty Database
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Child ID: 1 (valid test user with no results)

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

### Test Case 2.2: Get Results - With Multiple Results (Returns Latest)
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/1`
- Headers: `Authorization: Bearer {jwt_token}`
- Database: Two results with different timestamps

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Returns the most recent result
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

### Test Case 2.3: Get Results - Invalid Child ID Format
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

### Test Case 2.4: Get Results - Nonexistent Child ID
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

### Test Case 2.5: Get Results - Partial Data (Missing Optional Fields)
**API being tested**: `/api/psychometry/results/{child_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/psychometry/results/1`
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

---

## 3. Submit Psychometry Answer Test Cases (`/api/psychometry/submit`)

### Test Case 3.1: Submit Answer - No Session Data
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: None (no session initialized)
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

### Test Case 3.2: Submit Answer - Invalid Question Index
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

### Test Case 3.3: Submit Answer - Service Error
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

### Test Case 3.4: Submit Answer - Missing Answer Field
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

### Test Case 3.5: Submit Answer - User ID Mismatch
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

---

### Test Case 3.6: Submit Answer - Success Flow (Next Question)
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: Valid session with multiple questions remaining
- JSON Body:
```json
{
  "user_id": "1",
  "answer": "Visual diagrams"
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Next question with updated progress
```json
{
  "question": "How do you solve problems?",
  "options": ["Think step by step", "Discuss with others", "Try different approaches", "Research thoroughly"],
  "question_number": 2,
  "total_questions": 3,
  "progress": 33.3
}
```

**Actual Output**: HTTP Status Code: 200, Next question returned with correct progress

**Result**: Success ✅

---

### Test Case 3.7: Submit Answer - Complete Assessment (Stores Result)
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: On last question with previous responses
- JSON Body: Answer to final question

**Expected output**:
- HTTP Status Code: 200
- Database: PsychometricTestResult record created
- JSON Response: Completion confirmation with results

**Actual Output**: HTTP Status Code: 200, Result stored in database successfully

**Result**: Success ✅

---

### Test Case 3.8: Submit Answer - Accuracy Calculation
**API being tested**: `/api/psychometry/submit`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Session Data: Mixed correct/incorrect responses
- JSON Body: Final answer

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Accurate calculation of total_correct, total_questions, accuracy percentage

**Actual Output**: HTTP Status Code: 200, Accuracy calculated correctly (66.7% for 2/3 correct)

**Result**: Success ✅

---

## 4. LLM Integration Test Cases

### Test Case 4.1: LLM Fallback on Incomplete Response
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{"user_id": "1"}`
- LLM Response: Incomplete/insufficient data

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Fallback questions used instead of LLM response

**Actual Output**: HTTP Status Code: 200, Fallback questions provided when LLM fails

**Result**: Success ✅

---

### Test Case 4.2: LLM Exception Handling
**API being tested**: `/api/psychometry/start`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: `{"user_id": "1"}`
- LLM Service: Throws exception (OpenRouter down)

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Fallback questions used

**Actual Output**: HTTP Status Code: 200, Graceful fallback to predefined questions

**Result**: Success ✅

---

### Test Case 4.3: Feedback Fallback on LLM Failure
**API being tested**: Internal service method (get_results)

**Inputs**:
- Service State: Completed responses
- LLM Service: Fails during feedback generation

**Expected output**:
- Fallback feedback provided based on assessment results

**Actual Output**: Fallback feedback mechanism works correctly

**Result**: Success ✅

---

### Test Case 4.4: Personality Response Handling
**API being tested**: Internal service method (get_results)

**Inputs**:
- Service State: Personality-type responses with mixed correct/incorrect answers

**Expected output**:
- Valid personality_type string in results

**Actual Output**: Personality analysis completed successfully with fallback

**Result**: Success ✅

---
