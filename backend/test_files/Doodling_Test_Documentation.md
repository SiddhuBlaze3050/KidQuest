# Doodling API Test Cases Documentation
---

## 1. Drawing Session Management Test Cases

### Test Case 1.1: Start Drawing Session
**API being tested**: `/api/drawings/start-session`

**Inputs**:
- HTTP Method: POST
- JSON Body:
```json
{
  "user_id": 1,
  "ref_image_path": "/static/reference_images/dog.png",
  "ref_image_title": "Draw a Dog"
}
```

**Expected output**:
- HTTP Status Code: 200 or 201
- JSON Response:
```json
{
  "success": true,
  "session_id": 1,
  "start_time": "2025-08-06T12:00:00Z",
  "ref_image_title": "Draw a Dog"
}
```

**Actual Output**: HTTP Status Code: 200/201, Drawing session created successfully

**Result**: Success ✅

**Note**: This endpoint does NOT require JWT authentication

---

## 2. Drawing Save Operations Test Cases

### Test Case 2.1: Save Drawing Successfully
**API being tested**: `/api/drawings/save`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "user_id": 1,
  "image_data": "data:image/png;base64,{base64_encoded_image}",
  "description": "My beautiful test drawing",
  "ref_image_title": "Test Dog Drawing",
  "time_taken": 120
}
```

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "drawing_id": 1,
  "filename": "drawing_1_20250806_120000.png",
  "message": "Drawing saved successfully"
}
```

**Actual Output**: HTTP Status Code: 200, Drawing saved with metadata

**Result**: Success ✅

**Note**: The drawing is saved with automatic filename generation and proper metadata storage

---

### Test Case 2.2: Save Drawing Missing Data Validation
**API being tested**: `/api/drawings/save`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "user_id": 1
  // Missing image_data field
}
```

**Expected output**:
- HTTP Status Code: 400
- JSON Response:
```json
{
  "success": false,
  "error": "Missing required image data"
}
```

**Actual Output**: HTTP Status Code: 400, Proper validation error returned

**Result**: Success ✅

---

### Test Case 2.3: Save Drawing with Long Duration
**API being tested**: `/api/drawings/save`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "user_id": 1,
  "image_data": "data:image/png;base64,{base64_data}",
  "description": "Long duration drawing",
  "drawing_time": 3600
}
```

**Expected output**:
- HTTP Status Code: 200
- Proper handling of extended session times

**Result**: Success ✅

---

## 3. Drawing Retrieval Test Cases

### Test Case 3.1: Get User Drawings (Empty)
**API being tested**: `/api/drawings/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/drawings/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "drawings": []
}
```

**Actual Output**: HTTP Status Code: 200, Empty drawings array returned

**Result**: Success ✅

---

### Test Case 3.2: Get User Drawings with Existing Data
**API being tested**: `/api/drawings/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/drawings/1`
- Headers: `Authorization: Bearer {jwt_token}`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "drawings": [
    {
      "id": 1,
      "description": "Test drawing description",
      "save_image_path": "test_drawing.png",
      "ref_image_title": "Test Reference Image",
      "is_completed": true,
      "time_taken": 120,
      "timestamp": "2025-08-06T12:00:00Z"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Drawings list with complete metadata

**Result**: Success ✅

**Note**: Returns all drawings for the authenticated user with full metadata

---

### Test Case 3.3: Get Drawing Image Success
**API being tested**: `/api/drawings/image/{drawing_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/drawings/image/1`

**Expected output**:
- HTTP Status Code: 200 or 404
- JSON Response (if found):
```json
{
  "success": true,
  "image_data": "data:image/png;base64,{base64_data}",
  "description": "Test drawing for retrieval"
}
```

**Actual Output**: HTTP Status Code: 200/404, Image data returned or not found error

**Result**: Success ✅

**Note**: This endpoint does NOT require JWT authentication

---

## 4. Drawing Deletion Test Cases

### Test Case 4.1: Delete Drawing Successfully
**API being tested**: `/api/drawings/delete/{drawing_id}`

**Inputs**:
- HTTP Method: DELETE
- URL: `/api/drawings/delete/1`

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "message": "Drawing deleted successfully"
}
```

**Actual Output**: HTTP Status Code: 200, Drawing removed from database

**Result**: Success ✅

---

### Test Case 4.2: Delete Non-existent Drawing
**API being tested**: `/api/drawings/delete/{drawing_id}`

**Inputs**:
- HTTP Method: DELETE
- URL: `/api/drawings/delete/99999`

**Expected output**:
- HTTP Status Code: 404
- JSON Response:
```json
{
  "success": false,
  "error": "Drawing not found"
}
```

**Actual Output**: HTTP Status Code: 404, Proper error handling for missing drawing

**Result**: Success ✅

---

## 5. Reference Images Test Cases

### Test Case 5.1: Get Reference Images
**API being tested**: `/api/drawings/reference-images`

**Inputs**:
- HTTP Method: GET

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "images": [
    {
      "path": "static/reference_images/dog.png",
      "filename": "dog.png",
      "title": "Dog",
      "url": "/static/reference_images/dog.png"
    }
  ]
}
```

**Actual Output**: HTTP Status Code: 200, Reference images list returned

**Result**: Success ✅

**Note**: This endpoint does NOT require JWT authentication

---

### Test Case 5.2: Get Random Reference Image
**API being tested**: `/api/drawings/random-reference`

**Inputs**:
- HTTP Method: GET

**Expected output**:
- HTTP Status Code: 200
- JSON Response:
```json
{
  "success": true,
  "reference": {
    "path": "static/reference_images/random.png",
    "filename": "random.png",
    "title": "Random Image"
  }
}
```

**Actual Output**: HTTP Status Code: 200, Random reference image provided

**Result**: Success ✅

**Note**: This endpoint does NOT require JWT authentication

---

## 6. Authentication & Security Test Cases

### Test Case 6.1: Unauthorized Access Protection
**API being tested**: `/api/drawings/{user_id}`

**Inputs**:
- HTTP Method: GET
- URL: `/api/drawings/1`
- Headers: No authorization token

**Expected output**:
- HTTP Status Code: 401
- JSON Response:
```json
{
  "success": false,
  "error": "Missing authorization token"
}
```

**Actual Output**: HTTP Status Code: 200 (Authentication bypass)

**Result**: FAILED ❌

---

## 7. Data Validation Test Cases

### Test Case 7.1: Malformed Base64 Data Handling
**API being tested**: `/api/drawings/save`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "user_id": 1,
  "image_data": "data:image/png;base64,INVALID_BASE64_DATA!!!",
  "description": "Malformed data test",
  "drawing_time": 60
}
```

**Expected output**:
- HTTP Status Code: 400 (Bad Request)
- JSON Response:
```json
{
  "success": false,
  "error": "Invalid image data format"
}
```

**Actual Output**: HTTP Status Code: 500 (Internal Server Error)

**Result**: FAILED ❌

---

### Test Case 7.2: Unicode Description Handling
**API being tested**: `/api/drawings/save`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- JSON Body:
```json
{
  "user_id": 1,
  "image_data": "data:image/png;base64,{valid_base64_data}",
  "description": "My Drawing 🎨 with émojis & spëciàl çhars!",
  "drawing_time": 120
}
```

**Expected output**:
- HTTP Status Code: 200
- Proper handling of unicode characters in description

**Actual Output**: HTTP Status Code: 200, Unicode characters saved successfully

**Result**: Success ✅

**Note**: Application properly handles international characters and emojis in descriptions

---

## 8. Performance & Scale Test Cases

### Test Case 8.1: Large Image Data Handling
**API being tested**: `/api/drawings/save`

**Inputs**:
- HTTP Method: POST
- Headers: `Authorization: Bearer {jwt_token}`
- Large image data (2000x2000 pixels, ~12MB base64)

**Expected output**:
- HTTP Status Code: 200 or 413 (Request Entity Too Large)
- Proper handling of large file sizes

**Actual Output**: HTTP Status Code: 200, Large images processed successfully

**Result**: Success ✅

**Note**: System can handle large image files without issues

---

### Test Case 8.2: Concurrent Drawing Sessions
**API being tested**: `/api/drawings/start-session`

**Inputs**:
- Multiple simultaneous session creation requests (5 concurrent)
- Different reference images for each session

**Expected output**:
- All sessions created successfully
- No race conditions or data corruption

**Actual Output**: All sessions created with unique IDs

**Result**: Success ✅

**Note**: System handles concurrent session creation properly

---

### Test Case 8.3: API Rate Limiting Enforcement
**API being tested**: `/api/drawings/save`

**Inputs**:
- Rapid sequential requests (20 calls in succession)
- Same user making multiple save requests

**Expected output**:
- At least one HTTP Status Code: 429 (Too Many Requests)
- Rate limiting protection active

**Actual Output**: All requests return 200, no rate limiting enforced

**Result**: FAILED ❌

---

## 9. Complete Workflow Test Cases

### Test Case 9.1: End-to-End Drawing Workflow
**APIs being tested**: Complete drawing session workflow

**Inputs**:
1. Start session: `/api/drawings/start-session`
2. Save drawing: `/api/drawings/save`
3. Retrieve drawings: `/api/drawings/{user_id}`

**Expected output**:
- All operations complete successfully
- Data consistency maintained throughout workflow

**Actual Output**: Complete workflow executed successfully with data integrity

**Result**: Success ✅

**Note**: Full drawing workflow from session creation to data retrieval works seamlessly

---