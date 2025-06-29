import axios from 'axios'

// Configure axios base URL
const api = axios.create({
  baseURL: 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
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

  async addTransaction(payload) {
    try {
        const response = await api.post('/api/finance/transaction', payload)
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

  async addSavingsGoal(payload) {
    try {
        const response = await api.post('/api/finance/goal', payload)
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

  // Chat
  async sendMessage(message, userId = 1) {
    try {
      const response = await api.post('/api/chat', {
        message,
        user_id: userId,
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
