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

  // Health Tracker

  async getHealthTasks(userId) {
    try {
      const res = await api.get(`/api/health/tasks/${userId}`)
      return res.data.tasks
    } catch (error) {
      throw error
    }
  },

  async toggleHealthTask(taskId) {
    try {
      const res = await api.post(`/api/health/tasks/${taskId}/toggle`)
      return res.data.completed
    } catch (error) {
      throw error
    }
  },

  async getHealthStreak(userId) {
    try {
      const res = await api.get(`/api/health/streak/${userId}`)
      return res.data.streak
    } catch (error) {
      throw error
    }
  },

  async getWaterCount(userId) {
    try {
      const res = await api.get(`/api/health/water/${userId}`)
      return res.data.count
    } catch (error) {
      throw error
    }
  },

  async incrementWaterCount(userId) {
    try {
      const res = await api.post(`/api/health/water/${userId}`)
      return res.data.count
    } catch (error) {
      throw error
    }
  },

  async getWaterLog(userId) {
    try {
      const res = await api.get(`/api/health/water/log/${userId}`)
      return res.data.log
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
        session_id: sessionId,
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
        summary,
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
      console.log('✅ Sending to API from api.js :', {
        user_id: userId,
        homework_id: homeworkId,
      })
      const response = await api.post('/api/pomodoro/start', {
        user_id: userId,
        homework_id: homeworkId,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async pausePomodoro(sessionId) {
    try {
      const response = await api.put(`/api/pomodoro/pause/${sessionId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async resumePomodoro(sessionId) {
    try {
      const response = await api.put(`/api/pomodoro/resume/${sessionId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  async completePomodoro(sessionId, workDuration = 0, breakDuration = 0) {
    try {
      const response = await api.put(`/api/pomodoro/complete/${sessionId}`, {
        work_duration: workDuration,
        break_duration: breakDuration,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async abandonPomodoro(sessionId, workDuration = 0, breakDuration = 0) {
    try {
      const response = await api.put(`/api/pomodoro/abandon/${sessionId}`, {
        work_duration: workDuration,
        break_duration: breakDuration,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  async getTaskTimeAnalytics(userId, homeworkId = null) {
    try {
      const params = homeworkId ? { homework_id: homeworkId } : {}
      const response = await api.get(`/api/task-time/analytics/${userId}`, { params })
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

  // Module Progress
  async saveModuleProgress(userId, moduleType, progressData) {
    try {
      console.log(`🔄 Saving module progress: User ${userId}, Module ${moduleType}`, progressData)
      const response = await api.post('/api/module/progress', {
        user_id: userId,
        module_type: moduleType,
        progress_data: progressData,
      })
      console.log('✅ Module progress save response:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Module progress save failed:', error.response?.data || error.message)
      throw error
    }
  },

  async getModuleProgress(userId, moduleType) {
    try {
      console.log(`🔄 Loading module progress: User ${userId}, Module ${moduleType}`)
      // Properly encode the module type to handle spaces and special characters
      const encodedModuleType = encodeURIComponent(moduleType)
      const response = await api.get(`/api/module/progress/${userId}/${encodedModuleType}`)
      console.log('✅ Module progress load response:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Module progress load failed:', error.response?.data || error.message)
      // If no progress found, return empty progress instead of throwing error
      if (error.response?.status === 404) {
        console.log(`📝 No existing progress found for ${moduleType}, returning empty progress`)
        return {
          success: true,
          progress: null,
        }
      }
      throw error
    }
  },

  // Achievements
  async getUserAchievements(userId) {
    try {
      console.log(`🔄 Loading achievements for user ${userId}`)
      const response = await api.get(`/api/achievements/${userId}`)
      console.log('✅ Achievements loaded:', response.data)
      return response.data.achievements || []
    } catch (error) {
      console.error('❌ Failed to load achievements:', error.response?.data || error.message)
      return [] // Return empty array if no achievements found
    }
  },

  async createAchievement(achievementData) {
    try {
      console.log('🔄 Creating achievement:', achievementData)
      const response = await api.post('/api/achievement', achievementData)
      console.log('✅ Achievement created:', response.data)
      return response.data
    } catch (error) {
      console.error('❌ Failed to create achievement:', error.response?.data || error.message)
      throw error
    }
  },

  async updateModuleProgress(progressData) {
    try {
      console.log('📝 SIMPLE: Updating module progress:', progressData)

      // Add fallback values to prevent errors
      const safeProgressData = {
        user_id: progressData.user_id,
        module_type: progressData.module_type || 'Unknown Module',
        progress_percentage: progressData.progress_percentage || 0,
        is_completed: progressData.is_completed || false,
        progress_data: progressData.progress_data || {},
      }

      const response = await api.post('/api/module/progress', safeProgressData)
      console.log('✅ SIMPLE: Module progress updated:', response.data)
      return response.data
    } catch (error) {
      console.error(
        '⚠️ SIMPLE: Module progress update failed, but continuing:',
        error.response?.data || error.message,
      )

      // Be very forgiving - return success even on API errors
      // The progress is still saved locally anyway
      return {
        success: true,
        message: 'Progress saved locally (API issue)',
        progress_percentage: progressData.progress_percentage || 0,
      }
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

  // Test endpoint for debugging task completion notifications
  async testTaskCompletionNotification(userId, taskName = 'Test Task: Math Homework') {
    try {
      const response = await api.post('/api/test/task-completion-notification', {
        user_id: userId,
        task_name: taskName,
      })
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Debug user stats
  async debugUserStats(userId) {
    try {
      const response = await api.get(`/api/debug/user-stats/${userId}`)
      return response.data
    } catch (error) {
      throw error
    }
  },

  // Clear notifications for testing
  async clearNotifications(userId) {
    try {
      const response = await api.delete(`/api/notifications/clear/${userId}`)
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
