# KidQuest API Guide with JWT Authentication

This guide explains how to use the KidQuest API with JWT authentication.

## Authentication Endpoints

### Login

**Endpoint:** `/api/auth/login`
**Method:** `POST`
**Description:** Authenticate a user and get JWT tokens
**Rate Limit:** 5 attempts per 5 minutes

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin"
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing username or password
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account temporarily locked
- `429 Too Many Requests`: Rate limit exceeded

### Refresh Token

**Endpoint:** `/api/auth/refresh`
**Method:** `POST`
**Description:** Get a new access token using a refresh token

**Request:**
```json
{
  "refresh_token": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "q7r8s9t0-u1v2-w3x4-y5z6-a7b8c9d0e1f2"
}
```

**Error Responses:**
- `400 Bad Request`: Missing refresh token
- `401 Unauthorized`: Invalid or expired refresh token

### Logout

**Endpoint:** `/api/auth/logout`
**Method:** `POST`
**Description:** Invalidate the current access token and optionally all refresh tokens
**Authentication:** Required

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request (optional):**
```json
{
  "revoke_all": true  // Set to true to logout from all devices
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

## Protected Endpoints

### Test Authentication

**Endpoint:** `/api/auth/protected`
**Method:** `GET`
**Description:** Test if authentication is working
**Authentication:** Required

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "You have access to this protected resource",
  "user_id": 1,
  "role": "admin"
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

### Role-Specific Endpoints

#### Admin Only

**Endpoint:** `/api/auth/admin`
**Method:** `GET`
**Description:** Test if user has admin role
**Authentication:** Required
**Role:** Admin

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "You have admin access",
  "user_id": 1
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions

#### Parent Only

**Endpoint:** `/api/auth/parent`
**Method:** `GET`
**Description:** Test if user has parent role
**Authentication:** Required
**Role:** Parent or Admin

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "You have parent access",
  "user_id": 2
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions

#### Child Only

**Endpoint:** `/api/auth/child`
**Method:** `GET`
**Description:** Test if user has child role
**Authentication:** Required
**Role:** Child, Parent, Teacher, or Admin

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "You have child access",
  "user_id": 3
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions

#### Teacher Only

**Endpoint:** `/api/auth/teacher`
**Method:** `GET`
**Description:** Test if user has teacher role
**Authentication:** Required
**Role:** Teacher or Admin

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "You have teacher access",
  "user_id": 4
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions

## Using JWT Authentication with Existing Endpoints

To use JWT authentication with existing endpoints, include the access token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Handling

All API endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message"
}
```

Common error status codes:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Token Management

- Access tokens expire after 30 minutes
- Refresh tokens expire after 30 days
- Always store tokens securely (httpOnly cookies or encrypted localStorage)
- Implement token refresh when access tokens expire
- Clear tokens on logout