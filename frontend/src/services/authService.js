import axios from 'axios'
import Swal from 'sweetalert2'

// JWT Authentication Service
class AuthService {
  constructor() {
    this.token = this.getToken()
    this.user = this.getUser()
    this.refreshTimer = null

    // Get API base URL from environment
    this.API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

    // Set up axios headers immediately if token exists
    if (this.token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
    }

    this.setupAxiosInterceptors()

    // Check if we have an existing token and set up refresh timer
    this.initializeTokenTimer()
  }

  // Initialize token timer on service startup
  initializeTokenTimer() {
    if (!this.token) return

    const storedExpiration = localStorage.getItem('jwt_token_expires')
    if (storedExpiration) {
      const expirationTime = parseInt(storedExpiration)
      const currentTime = Date.now()
      const timeUntilExpiry = Math.floor((expirationTime - currentTime) / 1000)

      console.log(`🔍 AuthService initialized - token expires in ${timeUntilExpiry} seconds`)

      if (timeUntilExpiry > 300) {
        // More than 5 minutes left
        this.setupTokenRefreshTimer(timeUntilExpiry - 300) // Refresh 5 minutes before expiry
      } else if (timeUntilExpiry > 0) {
        // Less than 5 minutes - verify immediately
        this.verifyAndRefreshToken()
      } else {
        // Already expired
        console.log('⚠️ Token already expired on initialization')
        this.removeToken()
        this.removeUser()
        this.clearAllModuleProgress()
      }
    }
  }

  // Store token with expiration tracking
  setToken(token, expiresIn = null) {
    this.token = token
    localStorage.setItem('jwt_token', token)
    console.log('🔧 AuthService: Token stored in localStorage:', !!token)
    console.log('🔧 AuthService: Token length:', token ? token.length : 0)

    // Store expiration time if provided
    if (expiresIn) {
      const expirationTime = Date.now() + expiresIn * 1000 // Convert seconds to milliseconds
      localStorage.setItem('jwt_token_expires', expirationTime.toString())
      console.log('🔧 AuthService: Token expiration set for:', new Date(expirationTime))

      // Set up token refresh timer (refresh 5 minutes before expiry)
      this.setupTokenRefreshTimer(expiresIn - 300) // 5 minutes before expiry
    }

    // Update axios default headers immediately
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      console.log('✅ AuthService: Axios default Authorization header set')
    } else {
      delete axios.defaults.headers.common['Authorization']
      console.log('🗑️ AuthService: Axios default Authorization header removed')
    }
  }

  getToken() {
    return localStorage.getItem('jwt_token')
  }

  removeToken() {
    this.token = null
    localStorage.removeItem('jwt_token')
    localStorage.removeItem('jwt_token_expires')
    // Remove axios authorization header
    delete axios.defaults.headers.common['Authorization']
    // Clear any pending refresh timers
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer)
      this.refreshTimer = null
    }
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

  // Wait for token to be ready and validated
  async waitForTokenReady(maxAttempts = 10, delayMs = 100) {
    console.log('🔍 AuthService: Waiting for token to be ready...')

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      console.log(`🔍 AuthService: Token readiness check ${attempt}/${maxAttempts}`)

      // Check if token exists and is set in axios headers
      const token = this.getToken()
      const hasAxiosHeader = !!axios.defaults.headers.common['Authorization']
      const isAuthenticated = this.isAuthenticated()

      console.log(`🔍 Token exists: ${!!token}`)
      console.log(`🔍 Axios header set: ${hasAxiosHeader}`)
      console.log(`🔍 Is authenticated: ${isAuthenticated}`)

      if (token && hasAxiosHeader && isAuthenticated) {
        console.log('✅ AuthService: Token is ready!')
        return true
      }

      // If not ready, wait before next attempt
      if (attempt < maxAttempts) {
        console.log(`⏳ AuthService: Token not ready, waiting ${delayMs}ms...`)
        await new Promise((resolve) => setTimeout(resolve, delayMs))
      }
    }

    console.log('❌ AuthService: Token readiness timeout')
    return false
  }

  // Verify token by making a test API call
  async verifyTokenValidity() {
    try {
      console.log('🔍 AuthService: Verifying token validity...')

      const response = await axios.get(`${this.API_BASE_URL}/api/auth/verify`, {
        timeout: 5000, // 5 second timeout
      })

      if (response.data.success) {
        console.log('✅ AuthService: Token is valid')
        return true
      } else {
        console.log('❌ AuthService: Token verification failed')
        return false
      }
    } catch (error) {
      console.log('❌ AuthService: Token verification error:', error.message)
      return false
    }
  }

  // Complete authentication check (token ready + valid)
  async ensureAuthenticated() {
    console.log('🔐 AuthService: Ensuring complete authentication...')

    // Step 1: Wait for token to be ready in localStorage and axios
    const isReady = await this.waitForTokenReady()
    if (!isReady) {
      console.log('❌ AuthService: Token not ready')
      return false
    }

    // Step 2: Verify token is valid with backend
    const isValid = await this.verifyTokenValidity()
    if (!isValid) {
      console.log('❌ AuthService: Token not valid')
      // Clear invalid token
      this.removeToken()
      this.removeUser()
      return false
    }

    console.log('✅ AuthService: Authentication ensured - ready for API calls')
    return true
  }

  // Login
  async login(username, password) {
    try {
      console.log('🔑 AuthService: Attempting login for:', username)
      console.log('🌐 AuthService: Making request to backend...')

      const response = await axios.post(`${this.API_BASE_URL}/api/auth/login`, {
        username,
        password,
      })

      console.log('📊 AuthService: Login response received:', response)
      console.log('📊 AuthService: Response status:', response.status)
      console.log('📊 AuthService: Response data:', response.data)

      if (response.data.success) {
        console.log('🎉 AuthService: Login successful!')
        console.log(
          '🔧 AuthService: Setting token:',
          response.data.access_token.substring(0, 20) + '...',
        )
        console.log('🎯 AuthService: User role from response:', response.data.user?.role)
        console.log('🎯 AuthService: Is child user?', response.data.user?.role === 'child')
        console.log('⏰ AuthService: Token expires in:', response.data.expires_in, 'seconds')

        // Store JWT token and user data with expiration
        this.setToken(response.data.access_token, response.data.expires_in)
        this.setUser(response.data.user)

        // Force update axios default headers for immediate effect
        axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`

        console.log('✅ AuthService: Login successful, token stored and axios headers updated')
        console.log('👤 AuthService: User data stored:', response.data.user)
        console.log('🔧 AuthService: Token in localStorage:', !!localStorage.getItem('jwt_token'))
        console.log(
          '🌐 AuthService: Axios default header set:',
          !!axios.defaults.headers.common['Authorization'],
        )

        // Verify authentication state after setting data
        console.log('🔍 AuthService: Verifying authentication state...')
        console.log('🔍 AuthService: isAuthenticated():', this.isAuthenticated())
        console.log('🔍 AuthService: hasRole("child"):', this.hasRole('child'))
        console.log('🔍 AuthService: getCurrentUser():', this.getCurrentUser())

        // Wait for token to be fully ready and verified before returning success
        console.log('⏳ AuthService: Ensuring token is ready for API calls...')
        try {
          const tokenReady = await this.ensureAuthenticated()
          if (tokenReady) {
            console.log('✅ AuthService: Token verified and ready for dashboard API calls')
            return response.data
          } else {
            console.error('❌ AuthService: Token verification failed after login')
            throw new Error('Token verification failed after successful login')
          }
        } catch (verificationError) {
          console.error('❌ AuthService: Token verification error after login:', verificationError)
          // Still return success since login worked, but warn about verification issue
          return response.data
        }
      } else {
        // Handle unsuccessful login response
        console.log('❌ AuthService: Login failed with response:', response.data)
        console.log('❌ AuthService: Returning failure response to LoginModal')
        return response.data
      }
    } catch (error) {
      console.error('❌ AuthService: Login failed with error:', error)
      console.error('❌ AuthService: Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
      })

      // If it's a 401 error with response data, return the error response
      if (error.response && error.response.status === 401 && error.response.data) {
        console.log(
          '🔍 AuthService: Handling 401 error, returning response data:',
          error.response.data,
        )
        return error.response.data
      }

      // For other types of errors, throw them
      console.log('🔍 AuthService: Re-throwing error for other error types')
      throw error
    }
  }

  // Logout
  async logout() {
    try {
      // Call backend logout endpoint to clear notifications
      await axios.post(
        `${this.API_BASE_URL}/api/auth/logout`,
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
        console.log('🔧 Request interceptor - Token available:', !!token)
        console.log('🌐 Making request to:', config.url)

        if (token) {
          // Ensure headers object exists
          if (!config.headers) {
            config.headers = {}
          }
          config.headers.Authorization = `Bearer ${token}`
          console.log('✅ Authorization header added to request')
          console.log(
            '🔍 Full Authorization header:',
            config.headers.Authorization
              ? config.headers.Authorization.substring(0, 20) + '...'
              : 'NOT SET',
          )
          console.log('🔍 Token from localStorage:', token.substring(0, 20) + '...')
        } else {
          console.log('⚠️ No token available for request')
          console.log(
            '🔍 Token from localStorage check:',
            localStorage.getItem('jwt_token') ? 'EXISTS' : 'MISSING',
          )
        }
        return config
      },
      (error) => {
        console.error('❌ Request interceptor error:', error)
        return Promise.reject(error)
      },
    )

    // Response interceptor - handle token expiration
    axios.interceptors.response.use(
      (response) => {
        console.log('✅ Response received:', response.status, response.config.url)
        return response
      },
      async (error) => {
        console.error('❌ Response error:', error.response?.status, error.config?.url)
        const originalRequest = error.config

        // Check if this is a login request - be very specific about login URLs
        const isLoginRequest =
          originalRequest.url &&
          (originalRequest.url.includes('/api/auth/login') ||
            originalRequest.url.endsWith('/api/auth/login') ||
            originalRequest.url.includes('/api/auth/login') ||
            originalRequest.url === `${this.API_BASE_URL}/api/auth/login`)

        console.log('🔍 Interceptor: Is login request?', isLoginRequest)
        console.log('🔍 Interceptor: Request URL:', originalRequest.url)

        // For login requests with 401, ALWAYS let the login method handle it
        if (error.response?.status === 401 && isLoginRequest) {
          console.log('� Login request failed with 401 - letting login method handle it')
          console.log('� Login error details:', error.response?.data)
          return Promise.reject(error)
        }

        // For non-login requests, handle session expiration properly
        if (error.response?.status === 401 && !isLoginRequest && !originalRequest._retry) {
          const hasToken = this.getToken()
          const hasUser = this.getUser()
          const errorData = error.response?.data || {}

          console.log('🔍 Interceptor: Has token?', !!hasToken)
          console.log('🔍 Interceptor: Has user?', !!hasUser)
          console.log('🔍 Interceptor: Error type:', errorData.error_type)

          // Only treat as session expired if we had both token and user (valid session)
          if (hasToken && hasUser) {
            originalRequest._retry = true

            console.log('🔒 Valid session exists but got 401 - treating as session expired')
            console.log('🧹 Clearing auth data and redirecting to login')

            // Clear tokens and module progress, then redirect to login
            this.removeToken()
            this.removeUser()
            this.clearAllModuleProgress()

            // Show user-friendly message based on error type
            let title = 'Session Expired'
            let text = 'Your session has expired. Please log in again.'

            if (errorData.error_type === 'token_expired') {
              title = 'Session Expired'
              text = 'Your login session has expired. Please log in again to continue.'
            } else if (errorData.error_type === 'token_invalid') {
              title = 'Invalid Session'
              text = 'Your session is invalid. Please log in again.'
            } else if (errorData.error_type === 'token_missing') {
              title = 'Session Required'
              text = 'Please log in to access this feature.'
            }

            Swal.fire({
              icon: 'warning',
              title: title,
              text: text,
              timer: 4000,
              showConfirmButton: true,
              confirmButtonText: 'Go to Login',
              background: 'linear-gradient(135deg, #ff6b6b, #ffa726)',
              color: 'white',
            }).then((result) => {
              if (result.isConfirmed || result.isDismissed) {
                window.location.href = '/'
              }
            })

            // Redirect to home page after a short delay
            setTimeout(() => {
              window.location.href = '/'
            }, 4500)
          } else {
            console.log('🔍 No valid session - passing 401 through without session expired popup')
          }
        }

        return Promise.reject(error)
      },
    )
  }

  // Token refresh timer and verification
  setupTokenRefreshTimer(delaySeconds) {
    // Clear any existing timer
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer)
    }

    console.log(`⏰ Setting up token refresh timer for ${delaySeconds} seconds`)

    this.refreshTimer = setTimeout(async () => {
      console.log('🔄 Token refresh timer triggered - verifying token')
      await this.verifyAndRefreshToken()
    }, delaySeconds * 1000)
  }

  // Verify token and potentially refresh
  async verifyAndRefreshToken() {
    try {
      console.log('🔍 Verifying current token...')

      const response = await axios.get(`${this.API_BASE_URL}/api/auth/verify`)

      if (response.data.success) {
        console.log('✅ Token is still valid')
        const expiresAt = response.data.token_info.expires_at
        const now = Math.floor(Date.now() / 1000)
        const timeUntilExpiry = expiresAt - now

        console.log(`⏰ Token expires in ${timeUntilExpiry} seconds`)

        // If token expires in less than 10 minutes, warn user
        if (timeUntilExpiry < 600) {
          console.log('⚠️ Token expiring soon, should implement refresh or notify user')

          // Show warning to user about upcoming session expiry
          Swal.fire({
            icon: 'info',
            title: 'Session Expiring Soon',
            text: 'Your session will expire in less than 10 minutes. Please save any work.',
            timer: 5000,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white',
          })
        }
      }
    } catch (error) {
      console.error('❌ Token verification failed:', error)

      // If verification fails with 401, the interceptor will handle logout
      if (error.response?.status === 401) {
        console.log('🔒 Token verification failed with 401 - will be handled by interceptor')
      }
    }
  }

  // Refresh token (for future implementation)
  async refreshToken() {
    // This can be implemented when you add refresh tokens
    console.log('🔄 Token refresh not implemented yet')
    // For now, just verify the current token
    await this.verifyAndRefreshToken()
  }

  // Check if token is expired with better validation
  isTokenExpired() {
    if (!this.token) return true

    try {
      // Check stored expiration time first (more reliable)
      const storedExpiration = localStorage.getItem('jwt_token_expires')
      if (storedExpiration) {
        const expirationTime = parseInt(storedExpiration)
        const currentTime = Date.now()
        const isExpired = currentTime >= expirationTime

        console.log(`🔍 Token expiration check:`)
        console.log(`   Current time: ${new Date(currentTime)}`)
        console.log(`   Expires at: ${new Date(expirationTime)}`)
        console.log(`   Is expired: ${isExpired}`)

        if (isExpired) {
          console.log('⚠️ Token expired based on stored expiration time, clearing all data')
          this.removeToken()
          this.removeUser()
          this.clearAllModuleProgress()
          return true
        }

        return false
      }

      // Fallback to JWT payload parsing
      const payload = JSON.parse(atob(this.token.split('.')[1]))
      const currentTime = Date.now() / 1000
      const isExpired = payload.exp < currentTime

      console.log(`🔍 JWT payload expiration check:`)
      console.log(`   Current time: ${currentTime}`)
      console.log(`   Token expires: ${payload.exp}`)
      console.log(`   Is expired: ${isExpired}`)

      // If token is expired, clear all data
      if (isExpired) {
        console.log('⚠️ Token expired based on JWT payload, clearing all data')
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
