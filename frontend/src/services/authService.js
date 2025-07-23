import axios from 'axios'
import Swal from 'sweetalert2'

// JWT Authentication Service
class AuthService {
  constructor() {
    this.token = this.getToken()
    this.user = this.getUser()
    this.setupAxiosInterceptors()
  }

  // Token Management
  setToken(token) {
    this.token = token
    localStorage.setItem('jwt_token', token)
  }

  getToken() {
    return localStorage.getItem('jwt_token')
  }

  removeToken() {
    this.token = null
    localStorage.removeItem('jwt_token')
  }

  // User Management
  setUser(user) {
    console.log('🔧 AuthService: Setting user data:', user)
    this.user = user
    localStorage.setItem('user', JSON.stringify(user))
    console.log('✅ AuthService: User data stored in localStorage')
  }

  getUser() {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }

  removeUser() {
    this.user = null
    localStorage.removeItem('user')
  }

  // Authentication Status
  isAuthenticated() {
    return !!this.token && !!this.user
  }

  // Login
  async login(username, password) {
    try {
      const response = await axios.post('http://localhost:5000/api/auth/login', {
        username,
        password,
      })

      if (response.data.success) {
        // Store JWT token and user data
        this.setToken(response.data.access_token)
        this.setUser(response.data.user)

        console.log('✅ Login successful, token stored')
        return response.data
      }

      return response.data
    } catch (error) {
      console.error('❌ Login failed:', error)
      throw error
    }
  }

  // Logout
  async logout() {
    try {
      // Call backend logout endpoint to clear notifications
      await axios.post(
        'http://localhost:5000/api/auth/logout',
        {},
        {
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        },
      )

      // Clear local data
      this.removeToken()
      this.removeUser()
      this.clearAllModuleProgress()

      console.log('✅ Logout successful, tokens, module progress, and notifications cleared')

      // Redirect to home page
      window.location.href = '/'
    } catch (error) {
      console.error('❌ Logout failed:', error)

      // Fallback: even if backend call fails, still clear local data
      this.removeToken()
      this.removeUser()
      this.clearAllModuleProgress()
      window.location.href = '/'
    }
  }

  // Clear all module progress data from localStorage
  clearAllModuleProgress() {
    try {
      const keys = Object.keys(localStorage)

      // Find and remove all module progress related keys
      const moduleProgressKeys = keys.filter(
        (key) =>
          key.includes('Progress') ||
          key.includes('progress') ||
          key.includes('Module') ||
          key.includes('module') ||
          key.includes('wordWizard') ||
          key.includes('mathMagic') ||
          key.includes('safety') ||
          key.includes('science') ||
          key.includes('good_touch') ||
          key.includes('safetyMeasures') ||
          key.includes('safetyModule') ||
          key.includes('scienceExplorer'),
      )

      if (moduleProgressKeys.length > 0) {
        console.log('🧹 Clearing module progress keys:', moduleProgressKeys)

        moduleProgressKeys.forEach((key) => {
          localStorage.removeItem(key)
          console.log(`✅ Removed module progress: ${key}`)
        })

        console.log('🎉 All module progress cleared from localStorage')
      } else {
        console.log('✅ No module progress found to clear')
      }
    } catch (error) {
      console.error('❌ Error clearing module progress:', error)
    }
  }

  // Get current user
  getCurrentUser() {
    return this.user
  }

  // Check if user has specific role
  hasRole(role) {
    console.log(`🔍 AuthService: Checking role '${role}'`)
    console.log('👤 Current user:', this.user)
    console.log('🎭 User role:', this.user?.role)
    const hasRole = this.user && this.user.role === role
    console.log(`✅ Has role '${role}':`, hasRole)
    return hasRole
  }

  // Setup axios interceptors for automatic token handling
  setupAxiosInterceptors() {
    // Request interceptor - add JWT token to all requests
    axios.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      },
    )

    // Response interceptor - handle token expiration
    axios.interceptors.response.use(
      (response) => {
        return response
      },
      async (error) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized errors
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          // Clear tokens and module progress, then redirect to login
          this.removeToken()
          this.removeUser()
          this.clearAllModuleProgress()

          // Show user-friendly message
          Swal.fire({
            icon: 'warning',
            title: 'Session Expired',
            text: 'Your session has expired. Please log in again.',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ff6b6b, #ffa726)',
            color: 'white',
          })

          // Redirect to home page
          window.location.href = '/'

          return Promise.reject(error)
        }

        return Promise.reject(error)
      },
    )
  }

  // Refresh token (for future implementation)
  async refreshToken() {
    // This can be implemented when you add refresh tokens
    console.log('🔄 Token refresh not implemented yet')
  }

  // Check if token is expired
  isTokenExpired() {
    if (!this.token) return true

    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]))
      const currentTime = Date.now() / 1000
      const isExpired = payload.exp < currentTime

      // If token is expired, clear all data
      if (isExpired) {
        console.log('⚠️ Token expired, clearing all data')
        this.removeToken()
        this.removeUser()
        this.clearAllModuleProgress()
      }

      return isExpired
    } catch (error) {
      console.error('Error parsing token:', error)
      // If we can't parse the token, it's invalid, so clear everything
      this.removeToken()
      this.removeUser()
      this.clearAllModuleProgress()
      return true
    }
  }
}

// Create and export singleton instance
const authService = new AuthService()
export default authService
