# 🔧 Backend API Guide for Vue.js Frontend

## 🚀 Server Configuration

Your Flask backend is now configured to work with Vue.js frontend running on:
- **Frontend URL**: http://localhost:5173 (Vue.js default)
- **Backend URL**: http://localhost:5000 (Flask API)

## 📡 Available API Endpoints

### 🔐 Authentication Routes

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "string", 
  "password": "string",
  "role": "user" // optional, defaults to "user"
}

Response:
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

#### Login User
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response:
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "testuser", 
    "email": "test@example.com",
    "role": "user"
  }
}
```

### 💬 Chat Routes

#### Send Chat Message
```
POST /api/chat
Content-Type: application/json

{
  "message": "Hello, I need help with time management",
  "user_id": 1 // optional, defaults to 1
}

Response:
{
  "success": true,
  "response": "I'd be happy to help you with time management! What specific challenges are you facing?",
  "timestamp": "2025-01-28T10:30:00.000Z"
}
```

#### Get Chat History
```
GET /api/chat/history/{user_id}

Response:
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "message": "Hello",
      "sender": "user",
      "timestamp": "2025-01-28T10:30:00.000Z"
    },
    {
      "id": 2,
      "message": "Hi there! How can I help you today?",
      "sender": "assistant", 
      "timestamp": "2025-01-28T10:30:05.000Z"
    }
  ]
}
```

### 👤 User Routes

#### Get User Profile
```
GET /api/user/profile/{user_id}

Response:
{
  "success": true,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com", 
    "role": "user"
  }
}
```

### 🔍 Health Check
```
GET /api/health

Response:
{
  "success": true,
  "message": "API is running",
  "status": "healthy"
}
```

## 🛠️ Vue.js Axios Configuration

Add this to your Vue.js main.js or a separate API service file:

```javascript
import axios from 'axios'

// Configure axios base URL
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Request interceptor
axios.interceptors.request.use(
  (config) => {
    console.log('Making request:', config)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor  
axios.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    if (error.response?.status === 401) {
      // Handle unauthorized access
      // Redirect to login or clear user session
    }
    return Promise.reject(error)
  }
)

export default axios
```

## 📋 Example Usage in Vue.js

```javascript
// Login example
async function login(username, password) {
  try {
    const response = await axios.post('/api/auth/login', {
      username,
      password
    })
    
    if (response.data.success) {
      // Store user data in Pinia store or localStorage
      localStorage.setItem('user', JSON.stringify(response.data.user))
      return response.data.user
    }
  } catch (error) {
    console.error('Login failed:', error.response?.data?.error)
    throw error
  }
}

// Chat example
async function sendMessage(message, userId = 1) {
  try {
    const response = await axios.post('/api/chat', {
      message,
      user_id: userId
    })
    
    if (response.data.success) {
      return response.data.response
    }
  } catch (error) {
    console.error('Message failed:', error.response?.data?.error)
    throw error
  }
}
```

## 🔧 Installation & Setup

1. **Install Flask-CORS** (already added to requirements.txt):
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Flask Backend**:
   ```bash
   python app.py
   ```
   Backend will run on: http://localhost:5000

3. **Start Vue.js Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on: http://localhost:5173

## 🧪 Testing Default Admin Account

You can test with the default admin account:
- **Username**: admin
- **Password**: admin123
- **Email**: admin123@gmail.com

## 🎯 Next Steps for Vue.js Development

1. Create authentication components (Login/Register)
2. Set up Pinia stores for user state management
3. Create chat interface components
4. Add skill learning area components
5. Implement routing with Vue Router
6. Style with Bootstrap or your preferred CSS framework

Your backend is now ready to support your Vue.js frontend! 🚀 