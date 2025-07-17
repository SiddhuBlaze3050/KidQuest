# JWT RBAC Testing and Troubleshooting Guide

This guide will help you test and troubleshoot the JWT-based Role-Based Access Control (RBAC) implementation in the KidQuest application.

## Issues Identified

1. **Database Configuration**: The application was using an in-memory SQLite database, which means data was lost when the application was restarted or when different scripts were run.
2. **Database Locking**: When using a file-based SQLite database, multiple processes trying to access the same database file can cause locking issues.
3. **User Authentication**: Only the admin user can log in successfully; parent, child, and teacher logins fail.

## Solutions

### 1. Fix Database Configuration

Update the config.py file to use a file-based SQLite database instead of an in-memory database:

```python
# Use a file-based SQLite database
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DATABASE_PATH}')
```

### 2. Initialize the Database

Run the init_db.py script to create the database tables and set up the test users:

```bash
python3 init_db.py
```

### 3. Start the Flask Application

Start the Flask application:

```bash
python3 app.py
```

### 4. Test User Authentication

Test login for each user:

```bash
python3 manual_login_test.py
```

### 5. Test JWT RBAC Implementation

Run the test_jwt_rbac.py script to verify that the JWT RBAC implementation is working correctly:

```bash
python3 test_jwt_rbac.py
```

## Troubleshooting

### Database Locking Issues

If you encounter database locking issues, try:

1. Stop all processes that might be accessing the database
2. Delete the database file and recreate it
3. Use a different database file for each process

### User Authentication Issues

If users can't log in, check:

1. The users exist in the database
2. The password hashes are correct
3. The login endpoint is correctly defined
4. The password checking logic is working correctly

### JWT RBAC Issues

If the JWT RBAC implementation isn't working correctly, check:

1. The JWT authentication is properly initialized in app.py
2. The JWT service module is correctly implemented
3. The RBAC service module is correctly implemented
4. The authentication middleware is correctly implemented

## Manual Testing

You can manually test the JWT RBAC implementation using curl:

```bash
# Login as Admin
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}'

# Access Protected Endpoint
curl -X GET http://localhost:5000/api/auth/protected -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Refresh Token
curl -X POST http://localhost:5000/api/auth/refresh -H "Content-Type: application/json" -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'

# Logout
curl -X POST http://localhost:5000/api/auth/logout -H "Authorization: Bearer YOUR_ACCESS_TOKEN" -H "Content-Type: application/json" -d '{}'
```

## Next Steps

1. Fix the database configuration to use a persistent database
2. Ensure all users can log in successfully
3. Verify that the JWT RBAC implementation is working correctly
4. Update the frontend to use the JWT authentication