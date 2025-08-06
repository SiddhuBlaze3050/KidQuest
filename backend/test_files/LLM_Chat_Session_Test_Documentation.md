# LLM Chat Session Test Cases Documentation

## Test Suite Overview
**Module**: LLM Chat Session System  
**Test File**: `test_llm_chat_sessions.py`  
**APIs Tested**: `/api/chat` (POST), `/api/chat/sessions/{user_id}` (GET), `/api/chat/session/{session_id}` (GET), `/api/chat/session/{session_id}/summary` (PUT), `/api/chat/history/{user_id}` (GET), `/chat-history/{user_id}` (GET - legacy), `/clear-chat/{user_id}` (DELETE)  
**Authentication**: JWT Bearer Token Required (all endpoints)  

---

## 1. Chat Messaging Test Cases

### Test Case 1.1: Send Message - New Session
**API being tested**: `/api/chat`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "message": "Hello, how are you today?",
  "user_id": 1
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "response": "Hello! I'm here to help you. How are you feeling today?",
  "timestamp": "2025-07-30T12:00:00Z",
  "session_id": 1
}
```

**Actual Output**: HTTP Status Code: 200, New session created with mood detection

**Result**: Success ✅

**Note**: Mood tags are automatically detected from LLM response and stored but not shown to user

---

### Test Case 1.2: Send Message - Existing Session
**API being tested**: `/api/chat`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "message": "How are you doing?",
  "user_id": 1,
  "session_id": 1
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Message sent to existing session successfully

**Actual Output**: HTTP Status Code: 200, Message added to existing session with context preservation

**Result**: Success ✅

**Note**: Session context is maintained across messages for coherent conversations

---

### Test Case 1.3: Chat Error Scenarios
**API being tested**: `/api/chat`

**Inputs**:
- Missing message field
- No authentication token

**Expected output**:
- HTTP Status Codes: 400 (missing message), 401 (no auth)
- Appropriate error messages

**Result**: Success ✅

---

## 2. Session Retrieval Test Cases

### Test Case 2.1: Get All User Sessions
**API being tested**: `/api/chat/sessions/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/sessions/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "sessions": [
    {
      "id": 1,
      "created_at": "2025-07-30T12:00:00Z",
      "updated_at": "2025-07-30T12:05:00Z",
      "mood_tag": "happy",
      "interaction_count": 2,
      "last_message_preview": "Hello there!",
      "summary": null
    }
  ]
}
```

**Result**: Success ✅

---

### Test Case 2.2: Get Specific Session Details
**API being tested**: `/api/chat/session/{session_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/session/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "session": {
    "id": 1,
    "created_at": "2025-07-30T12:00:00Z",
    "updated_at": "2025-07-30T12:05:00Z",
    "mood_tag": "happy",
    "summary": null,
    "messages": [
      {
        "id": "user_1",
        "sender": "user",
        "message": "Hello there!",
        "timestamp": "2025-07-30T12:00:00Z",
        "mood_tag": "happy"
      },
      {
        "id": "bot_1",
        "sender": "assistant",
        "message": "Hi! How can I help?",
        "timestamp": "2025-07-30T12:00:01Z"
      }
    ]
  }
}
```

**Actual Output**: HTTP Status Code: 200, Complete session with all interactions

**Result**: Success ✅

**Note**: Messages are returned in chronological order with unique IDs for each interaction

---

### Test Case 2.3: Get Non-existent Session
**API being tested**: `/api/chat/session/{session_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/session/999`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 404
- JSON Response:
```json
{
  "success": false,
  "error": "Session not found"
}
```

**Actual Output**: HTTP Status Code: 404, Proper error handling

**Result**: Success ✅

---

## 3. Authorization Test Cases

### Test Case 3.1: Unauthorized Session Access
**API being tested**: `/api/chat/session/{session_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/session/2` (different user's session)
- Headers: `Authorization: Bearer {jwt_token}` (user 1's token)

**Expected output**:
- HTTP Status Code: 403
- JSON Response:
```json
{
  "success": false,
  "error": "Unauthorized access"
}
```

**Actual Output**: HTTP Status Code: 403, Proper authorization enforcement

**Result**: Success ✅

**Note**: Users can only access their own chat sessions

---

### Test Case 3.3: Chat Rate Limiting
**API being tested**: `/api/chat`

**Inputs**:
- HTTP Method: POST (multiple rapid requests)
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body: 10 rapid consecutive messages
```json
{
  "message": "Rapid message #1",
  "user_id": 1
}
```

**Expected output**:
- HTTP Status Code: 429 (Too Many Requests) for some requests
- JSON Response:
```json
{
  "success": false,
  "error": "Rate limit exceeded. Please try again later."
}
```

**Actual Output**: HTTP Status Code: 200 for all requests, No rate limiting implemented

**Result**: FAILURE ❌
---

### Test Case 3.4: Unauthorized Summary Update
**API being tested**: `/api/chat/session/{session_id}/summary`

**Inputs**:
- HTTP Method: PUT
- URL: `/api/chat/session/2/summary` (different user's session)
- Headers: `Authorization: Bearer {jwt_token}` (user 1's token)

**Expected output**:
- HTTP Status Code: 403
- JSON Response: Unauthorized access error

**Actual Output**: HTTP Status Code: 403, Authorization properly enforced

**Result**: Success ✅

---

## 4. Session Management Test Cases

### Test Case 4.1: Update Session Summary
**API being tested**: `/api/chat/session/{session_id}/summary`

**Inputs**:
- HTTP Method: PUT
- URL: `/api/chat/session/1/summary`
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "summary": "User discussed homework help and feeling excited about learning."
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "message": "Session summary updated"
}
```

**Actual Output**: HTTP Status Code: 200, Summary updated successfully

**Result**: Success ✅

**Note**: Session `updated_at` timestamp is automatically updated

---

### Test Case 4.2: Get Legacy Chat History
**API being tested**: `/chat-history/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/chat-history/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "chat_history": [
    {
      "id": "user_1",
      "message": "Legacy test message",
      "sender": "user",
      "timestamp": "2025-07-30T12:00:00Z"
    },
    {
      "id": "bot_1",
      "message": "Legacy test response",
      "sender": "assistant",
      "timestamp": "2025-07-30T12:00:01Z"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Legacy format chat history returned

**Result**: Success ✅

**Note**: Legacy endpoint for backward compatibility - returns last 50 messages across all sessions

---

## 5. Data Management Test Cases

### Test Case 5.1: Clear All Chat History
**API being tested**: `/clear-chat/{user_id}`

**Inputs**:
- HTTP Method: DELETE
- URL: `/clear-chat/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "message": "Chat history cleared successfully"
}
```

**Actual Output**: HTTP Status Code: 200, All sessions and interactions deleted

**Result**: Success ✅

**Note**: Deletes all ChatSession and LLMInteractions records for the user

---

### Test Case 5.2: Verify Data Deletion
**API being tested**: `/api/chat/sessions/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/chat/sessions/1` (after clearing)
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response: Empty sessions array

**Result**: Success ✅

---

## 6. Advanced Functionality Test Cases

### Test Case 6.1: Mood Detection
**API being tested**: `/api/chat` (with mood analysis)

**Inputs**:
- HTTP Method: POST
- JSON Body:
```json
{
  "message": "I am feeling really sad today",
  "user_id": 1
}
```

**Expected output**:
- HTTP Status Code: 200
- Response contains mood analysis
- Mood tag stored in database as "sad"

**Actual Output**: HTTP Status Code: 200, Mood "sad" detected and stored without showing tag to user

**Result**: Success ✅

**Note**: Mood tags in format `[MOOD: emotion]` are extracted and stored but removed from user-visible response

---

### Test Case 6.2: API Error Handling
**API being tested**: `/api/chat` (with simulated API failure)

**Inputs**:
- Mock LLM API connection failure
- Normal chat message request

**Expected output**:
- HTTP Status Code: 200
- Fallback response: "I'm having trouble connecting to my services right now"

**Actual Output**: HTTP Status Code: 200, Graceful fallback response provided

**Result**: Success ✅

**Note**: Uses default fallback message when LLM API fails, ensures user always gets a response

---

### Test Case 6.3: Context Preservation
**API being tested**: `/api/chat` (multiple messages in session)

**Inputs**:
- First message: "My name is Alice"
- Second message: "What is my name?" (same session)

**Expected output**:
- HTTP Status Code: 200
- Both interactions stored in same session
- Context maintained across messages

**Actual Output**: HTTP Status Code: 200, Conversation context preserved with last 10 interactions

**Result**: Success ✅

**Note**: System maintains conversation context by including recent interactions in LLM prompts

---
