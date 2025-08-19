import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import axios from 'axios'
import authService from './services/authService'

// Configure axios globally with environment-based URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
axios.defaults.baseURL = API_BASE_URL
axios.defaults.withCredentials = true // Enable cookies/session for cross-origin requests

console.log('🌐 API Base URL:', API_BASE_URL)

// Initialize authentication on app startup
console.log('🚀 Initializing authentication on app startup...')
console.log('🔍 Token exists:', !!authService.getToken())
console.log('🔍 User exists:', !!authService.getUser())
console.log('🔍 Is authenticated:', authService.isAuthenticated())
console.log('🔍 Token expired:', authService.isTokenExpired())

// Set authorization header if valid token exists
if (authService.isAuthenticated() && !authService.isTokenExpired()) {
  const token = authService.getToken()
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
  console.log('✅ Authorization header set on app startup')
} else {
  console.log('⚠️ No valid authentication found on app startup')
  // Clear any invalid tokens
  if (authService.getToken()) {
    console.log('🧹 Clearing invalid/expired token')
    authService.removeToken()
    authService.removeUser()
  }
}

const app = createApp(App)

app.use(router)

app.mount('#app')
