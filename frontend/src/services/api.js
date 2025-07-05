import axios from 'axios'
import Swal from 'sweetalert2'

// Configure axios base URL
const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('Making API request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  },
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('API response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    if (error.response?.status === 401) {
      // Handle unauthorized access - clear user data
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

// API Service Functions
export const apiService = {
  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/api/health')
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Authentication
  async login(username, password) {
    try {
      const response = await api.post('/api/auth/login', {
        username,
        password,
      })

      if (response.data.success) {
        // Store user data in localStorage
        localStorage.setItem('user', JSON.stringify(response.data.user))
        return response.data
      }
      throw new Error(response.data.error || 'Login failed')
    } catch (error) {
      throw error
    }
  },

  async register(payload) {
    try {
      const response = await api.post('/api/auth/register', payload)
      if (response.data.success) {
        return response.data
      }
      throw new Error(response.data.error || 'Registration failed')
    } catch (error) {
      throw error
    }
  },

  // User Profile
  async getUserProfile(userId) {
    try {
      const response = await api.get(`/api/user/profile/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Finance Tracker
  async getTransactions(userId) {
    try {
      const response = await api.get(`/api/finance/transactions/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async addTransaction(transactionData) {
    try {
      const response = await api.post('/api/finance/transaction', transactionData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getSavingsGoals(userId) {
    try {
      const response = await api.get(`/api/finance/goals/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async addSavingsGoal(goalData) {
    try {
      const response = await api.post('/api/finance/goal', goalData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async updateSavingsGoal(payload) {
    try {
      const response = await api.put(`/api/finance/goal/${payload.id}`, payload)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Chat - Enhanced with session support
  async sendMessage(message, userId = 1, sessionId = null) {
    try {
      const response = await api.post('/api/chat', {
        message,
        user_id: userId,
        session_id: sessionId
      })

      if (response.data.success) {
        return response.data
      }
      throw new Error(response.data.error || 'Message failed')
    } catch (error) {
      throw error
    }
  },

  async getChatHistory(userId) {
    try {
      const response = await api.get(`/api/chat/history/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getChatSessions(userId) {
    try {
      const response = await api.get(`/api/chat/sessions/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getSession(sessionId) {
    try {
      const response = await api.get(`/api/chat/session/${sessionId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async updateSessionSummary(sessionId, summary) {
    try {
      const response = await api.put(`/api/chat/session/${sessionId}/summary`, {
        summary
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async clearChatHistory(userId) {
    try {
      const response = await api.delete(`/clear-chat/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Child Dashboard
  async getChildStats(userId) {
    try {
      const response = await api.get(`/api/child/stats/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getChildQuests(userId) {
    try {
      const response = await api.get(`/api/child/quests/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async toggleQuest(questId) {
    try {
      const response = await api.post(`/api/child/quest/${questId}/toggle`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Task Tracker
  async getTasks(userId) {
    try {
      const response = await api.get(`/api/tasks/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async createTask(taskData) {
    try {
      const response = await api.post('/api/tasks', taskData)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async updateTaskStatus(taskId, status) {
    try {
      const response = await api.put(`/api/tasks/${taskId}/status`, { status })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Pomodoro
  async startPomodoro(userId, homeworkId) {
    try {
      const response = await api.post('/api/pomodoro/start', {
        user_id: userId,
        homework_id: homeworkId,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async completePomodoro(sessionId, duration) {
    try {
      const response = await api.put(`/api/pomodoro/complete/${sessionId}`, {
        duration,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Screen Time
  async logScreenTime(userId, durationSeconds) {
    try {
      const response = await api.post('/api/screen-time/log', {
        user_id: userId,
        duration_seconds: durationSeconds,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Notifications
  async getNotifications(userId) {
    try {
      const response = await api.get(`/api/notifications/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async markNotificationsRead(notificationIds) {
    try {
      const response = await api.post('/api/notifications/mark-read', {
        notification_ids: notificationIds,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async createSampleNotifications(userId) {
    try {
      const response = await api.post('/api/notifications/create-sample', {
        user_id: userId,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Generic fetch methods
  async get(endpoint) {
    const response = await api.get(endpoint)
    return response.data
  },

  async post(endpoint, data) {
    const response = await api.post(endpoint, data)
    return response.data
  },

  async put(endpoint, data) {
    const response = await api.put(endpoint, data)
    return response.data
  },

  async delete(endpoint) {
    const response = await api.delete(endpoint)
    return response.data
  },
}

// User utility functions
export const userUtils = {
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    } catch (error) {
      console.error('Error parsing user data:', error)
      return null
    }
  },

  isLoggedIn() {
    return this.getCurrentUser() !== null
  },

  logout() {
    localStorage.removeItem('user')
    window.location.href = '/'
  },
}

export default api
