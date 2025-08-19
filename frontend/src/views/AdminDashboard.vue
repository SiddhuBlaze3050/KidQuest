<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <header class="admin-header">
      <div class="container">
        <div class="header-content">
          <div class="admin-logo">
            <span class="logo-icon">🛡️</span>
            <span class="logo-text">KidQuest Admin</span>
          </div>
          <div class="admin-user">
            <span>Welcome, {{ username }}</span>
            <LogoutButton />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="admin-main">
      <div class="container">
        <!-- Stats Cards -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
              <h3>Total Users</h3>
              <div class="stat-number">{{ totalUsers }}</div>
              <div class="stat-details">
                Parents: {{ parentCount }}  Children: {{ childCount }}  Teachers: {{ teacherCount }}  Admins: {{ adminCount }}
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <h3>Active Today</h3>
              <div class="stat-number">{{ activeToday }}</div>
              <div class="stat-details">
                Last Hour: {{ activeLastHour }}
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">💚</div>
            <div class="stat-content">
              <h3>System Status</h3>
              <div class="stat-number" :class="{ 'status-healthy': systemStatus === 'Healthy', 'status-error': systemStatus !== 'Healthy' }">
                {{ systemStatus }}
              </div>
              <div class="stat-details">
                Last Check: {{ lastStatusCheck }}
              </div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon">⏱️</div>
            <div class="stat-content">
              <h3>Avg. Screen Time(Mins)</h3>
              <div class="stat-number">{{ formatScreenTime(averageScreenTime) }}</div>
              <div class="stat-details">
                Daily average across all users
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="admin-sections">
          <div class="section-card">
            <h2>🤖 AI Chatbot</h2>
            <p>Test and monitor the KidQuest chatbot system</p>
            <button @click="showChatbot = true" class="action-btn primary">
              <span class="btn-icon">🧙‍♂️</span>
              Open 3D Chatbot
            </button>
          </div>

          <div class="section-card">
            <h2>👥 User Management</h2>
            <p>Manage user accounts and permissions</p>
            <div class="action-group">
              <button @click="showUserList = true" class="action-btn">
                <span class="btn-icon">👁️</span>
                View Users
              </button>
              <button @click="showAddUser = true" class="action-btn">
                <span class="btn-icon">➕</span>
                Add User
              </button>
            </div>
          </div>

          <div class="section-card">
            <h2>📊 Analytics</h2>
            <p>View usage statistics and reports</p>
            <div class="action-group">
              <button @click="showReports" class="action-btn">
                <span class="btn-icon">📈</span>
                Usage Reports
              </button>
            </div>
          </div>

        </div>
      </div>
    </main>

    <!-- Modals -->
    <UserList v-model="showUserList" @user-added="onUserAdded" />
    <AddUserForm v-model="showAddUser" @user-added="onUserAdded" />
    <AnalyticsModal v-model="showAnalytics" />
    <EnhancedChatBot v-if="showChatbot" :user="currentUser" @close="showChatbot = false" />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import authService from '@/services/authService'
import LogoutButton from '@/components/LogoutButton.vue'
import UserList from '@/components/admin/UserList.vue'
import AddUserForm from '@/components/admin/AddUserForm.vue'
import AnalyticsModal from '@/components/admin/AnalyticsModal.vue'
import EnhancedChatBot from '@/components/chat/EnhancedChatBot.vue'

export default {
    name: 'AdminDashboard',
    components: {
        LogoutButton,
        UserList,
        AddUserForm,
        AnalyticsModal,
        EnhancedChatBot
    },
    setup() {
        const router = useRouter()
        const showUserList = ref(false)
        const showAddUser = ref(false)
        const showChatbot = ref(false)
        const showAnalytics = ref(false)
        const currentUser = ref(null)

        // Enhanced computed username from authService
        const username = computed(() => {
            const user = authService.getCurrentUser()
            return user?.username || 'Admin'
        })

        // Advanced Stats
        const totalUsers = ref(0)
        const parentCount = ref(0)
        const childCount = ref(0)
        const adminCount = ref(0)
        const teacherCount = ref(0)
        const activeToday = ref(0)
        const activeLastHour = ref(0)
        const systemStatus = ref('Healthy')
        const lastStatusCheck = ref(new Date().toLocaleTimeString())
        const averageScreenTime = ref(0) // in minutes

        // Enhanced admin access check with authService
        const checkAdminAccess = () => {
            if (!authService.isAuthenticated()) {
                console.warn('🚫 AdminDashboard: User not authenticated')
                window.location.href = '/'
                return
            }

            const user = authService.getCurrentUser()
            if (!user || user.role !== 'admin') {
                console.warn('🚫 AdminDashboard: User is not admin:', user?.role)
                window.location.href = '/'
                return
            }
            
            console.log('✅ AdminDashboard: Admin access granted for:', user.username)
            currentUser.value = user
        }

        // Define API_BASE_URL at component level for all functions to use
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

        const fetchStats = async () => {
            try {
                const response = await axios.get(`${API_BASE_URL}/api/admin/dashboard-stats`)
                const stats = response.data
                totalUsers.value = stats.total_users || 0
                parentCount.value = stats.parent_count || 0
                childCount.value = stats.child_count || 0
                adminCount.value = stats.admin_count || 0
                teacherCount.value = stats.teacher_count || 0
                activeToday.value = stats.active_today || 0
                activeLastHour.value = stats.active_last_hour || 0
                averageScreenTime.value = stats.average_screen_time || 0
            } catch (error) {
                console.error('Error fetching stats:', error)
            }
        }

        const formatScreenTime = (minutes) => {
            if (minutes === 0) return '00:00'
            const hours = Math.floor(minutes / 60)
            const mins = minutes % 60
            return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`
        }

        const checkSystemStatus = async () => {
            try {
                await axios.get(`${API_BASE_URL}/api/health`)
                systemStatus.value = 'Healthy'
            } catch (error) {
                systemStatus.value = 'Error'
                console.error('System health check failed:', error)
            }
            lastStatusCheck.value = new Date().toLocaleTimeString()
        }

        const showReports = () => {
            showAnalytics.value = true
        }

        const exportData = () => {
            showAnalytics.value = true
        }

        const openSettings = () => {
            // TODO: Implement settings view
            console.log('Opening settings...')
        }

        const onUserAdded = (user) => {
            fetchStats()
        }

        onMounted(async () => {
            // Check admin access first
            checkAdminAccess()

            // Initialize dashboard
            fetchStats()
            checkSystemStatus()

            // Set up periodic updates
            setInterval(fetchStats, 60000) // Update stats every minute
            setInterval(checkSystemStatus, 30000) // Check system status every 30 seconds
        })

        return {
            username,
            showUserList,
            showAddUser,
            showChatbot,
            showAnalytics,
            currentUser,
            totalUsers,
            parentCount,
            childCount,
            adminCount,
            teacherCount,
            activeToday,
            activeLastHour,
            systemStatus,
            lastStatusCheck,
            averageScreenTime,
            formatScreenTime,
            showReports,
            exportData,
            openSettings,
            onUserAdded
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.admin-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #31417A 0%, #667eea 100%);
    font-family: 'Merriweather', serif;
}

.admin-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
}

.admin-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    font-weight: bold;
    color: #6366f1;
}

.logo-icon {
    font-size: 2rem;
}

.admin-user {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: #666;
}

.admin-main {
    padding: 2rem 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: #F0E6D2;
    /* Parchment */
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 1.5rem;
    transition: all 0.4s ease;
    border-top: 4px solid var(--theme-color);
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), 0 0 20px var(--theme-color);
}

.stat-card:nth-child(1) {
    --theme-color: #FFD700;
}

.stat-card:nth-child(2) {
    --theme-color: #C9A270;
}

.stat-card:nth-child(3) {
    --theme-color: #2A623D;
}

.stat-card:nth-child(4) {
    --theme-color: #8B5A2B;
}

.stat-icon {
    font-size: 3rem;
    color: var(--theme-color);
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
    flex-shrink: 0;
}

.stat-content {
    color: #3B312E;
    /* Dark charcoal */
    flex: 1;
    text-align: center;
}

.stat-content h3 {
    margin: 0 0 0.5rem 0;
    color: #5a4f4a;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    text-align: center;
}

.stat-number {
    font-family: 'Merriweather', serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #3B312E;
    text-align: center;
    margin: 0.5rem 0;
}

.stat-details {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #5a4f4a;
    text-align: center;
}

.status-healthy {
    color: #2A623D;
}

.status-error {
    color: #B91C1C;
}

.admin-sections {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.section-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
}

.section-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.section-card h2 {
    margin: 0 0 1rem 0;
    color: white;
    font-size: 1.3rem;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.section-card p {
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 1.5rem;
    line-height: 1.6;
}

.action-btn {
    padding: 0.75rem 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

.action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.2);
}

.action-btn.primary {
    background: linear-gradient(135deg, #ff6b6b, #ffa726);
    color: white;
    border: none;
}

.action-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.btn-icon {
    font-size: 1.1rem;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 15px;
    width: 90%;
    max-width: 1000px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    margin: 0;
    color: #333;
    font-size: 1.5rem;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #666;
    cursor: pointer;
    padding: 0.5rem;
    transition: color 0.3s;
}

.close-btn:hover {
    color: #333;
}

.modal-body {
    padding: 1.5rem;
}

@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }

    .admin-sections {
        grid-template-columns: 1fr;
    }

    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
}
</style>