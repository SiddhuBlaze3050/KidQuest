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

### 📚 Module Progress Routes

**Module Types:**
- **Modules WITHOUT submodules**: `math_magic`, `word_wizard`, `good_touch_bad_touch`, `psychometric_assessment`
- **Modules WITH submodules**: `science_explorer`, `safety_measures`

#### Save Module Progress

**For modules WITHOUT submodules (e.g., Math Magic):**
```
POST /api/module/progress
Content-Type: application/json

{
  "user_id": 1,
  "module_type": "math_magic",
  "progress_percentage": 75,
  "is_completed": false,
  "progress_data": {
    "current_lesson": 3,
    "score": 85
  }
}
```

**For modules WITH submodules (e.g., Safety Measures):**
```
POST /api/module/progress
Content-Type: application/json

{
  "user_id": 1,
  "module_type": "safety_measures",
  "submodule_name": "home_safety",
  "progress_percentage": 100,
  "is_completed": true,
  "progress_data": {
    "completed_tips": 4,
    "score": 95
  }
}
```

**Response:**
```
{
  "success": true,
  "message": "Progress saved successfully",
  "progress_percentage": 75,
  "is_completed": false
}
```

#### Get Module Progress

**For modules WITHOUT submodules:**
```
GET /api/module/progress/{user_id}/math_magic

Response:
{
  "success": true,
  "progress": {
    "module_name": "math_magic",
    "submodule_name": null,
    "progress_percentage": 75,
    "is_completed": false,
    "module_id": 1,
    "submodule_id": null
  }
}
```

**For modules WITH submodules:**
```
GET /api/module/progress/{user_id}/safety_measures

Response:
{
  "success": true,
  "progress": {
    "module_name": "safety_measures",
    "progress_percentage": 75.0,
    "is_completed": false,
    "module_id": 4,
    "submodule_progress": [
      {
        "submodule_name": "home_safety",
        "progress_percentage": 100,
        "is_completed": true,
        "submodule_id": 1
      },
      {
        "submodule_name": "road_safety",
        "progress_percentage": 50,
        "is_completed": false,
        "submodule_id": 2
      }
    ],
    "total_submodules": 2,
    "completed_submodules": 1
  }
}
```

#### Get All Module Progress
```
GET /api/module/progress/{user_id}

Response:
{
  "success": true,
  "progress_list": [
    {
      "module_name": "math_magic",
      "module_id": 1,
      "has_submodules": false,
      "submodules": [],
      "overall_progress": 75,
      "overall_completed": false
    },
    {
      "module_name": "safety_measures",
      "module_id": 4,
      "has_submodules": true,
      "submodules": [
        {
          "submodule_name": "home_safety",
          "progress_percentage": 100,
          "is_completed": true,
          "submodule_id": 1
        }
      ],
      "overall_progress": 100.0,
      "overall_completed": true,
      "total_submodules": 1,
      "completed_submodules": 1
    }
  ],
  "total_modules": 2,
  "completed_modules": 1,
  "modules_with_submodules": ["science_explorer", "safety_measures"],
  "modules_without_submodules": ["math_magic", "word_wizard", "good_touch_bad_touch", "psychometric_assessment"]
}
```

#### Get Quest Statistics
```
GET /api/child/quest-stats/{user_id}

Response:
{
  "success": true,
  "quest_statistics": {
    "total_quests": {
      "modules": 5,
      "tasks": 3,
      "achievements": 8,
      "total": 16
    },
    "todays_goals": {
      "modules": 1,
      "tasks": 2,
      "achievements": 1,
      "health_tasks": 3,
      "water_goal": 1,
      "login_streak": 1,
      "total": 9
    },
    "detailed_breakdown": {
      "module_progress": [
        {
          "module_name": "math_magic",
          "submodule_name": "addition",
          "progress": 75,
          "completed": false,
          "updated_at": "2025-01-28T10:30:00.000Z"
        }
      ],
      "tasks": [
        {
          "subject": "Math",
          "task": "Complete homework",
          "status": "completed",
          "updated_at": "2025-01-28T10:30:00.000Z"
        }
      ],
      "achievements": [
        {
          "badge_name": "Memory Game Master",
          "description": "Completed memory game",
          "date_awarded": "2025-01-28T10:30:00.000Z"
        }
      ]
    }
  }
}
```

#### Get Modules Information
```
GET /api/modules/info

Response:
{
  "success": true,
  "modules": {
    "math_magic": {
      "id": 1,
      "name": "Math Magic",
      "has_submodules": false,
      "submodules": {}
    },
    "safety_measures": {
      "id": 4,
      "name": "Safety Measures",
      "has_submodules": true,
      "submodules": {
        "home_safety": {"id": 1, "name": "Home Safety"},
        "road_safety": {"id": 2, "name": "Road Safety"},
        "internet_safety": {"id": 3, "name": "Internet Safety"},
        "fire_safety": {"id": 4, "name": "Fire Safety"}
      }
    }
  },
  "modules_with_submodules": ["science_explorer", "safety_measures"],
  "modules_without_submodules": ["math_magic", "word_wizard", "good_touch_bad_touch", "psychometric_assessment"]
}
```

### 🔧 Admin Routes (Development Only)

#### Recreate Database
```
POST /api/admin/recreate-database

Response:
{
  "success": true,
  "message": "Database recreated successfully"
}
```

**⚠️ Warning:** This will delete all existing data and recreate all tables. Use only in development.

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