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
                        <span>Welcome, {{ user?.username }}</span>
                        <button @click="logout" class="logout-btn">
                            <i class="fas fa-sign-out-alt"></i>
                            Logout
                        </button>
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
                            <div class="stat-number">{{ stats.totalUsers }}</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">💬</div>
                        <div class="stat-content">
                            <h3>Chat Messages</h3>
                            <div class="stat-number">{{ stats.totalMessages }}</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-content">
                            <h3>Active Sessions</h3>
                            <div class="stat-number">{{ stats.activeSessions }}</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-content">
                            <h3>Achievements</h3>
                            <div class="stat-number">{{ stats.achievements }}</div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="admin-sections">
                    <div class="section-card">
                        <h2>🤖 AI Chatbot</h2>
                        <p>Test and monitor the KidQuest chatbot system</p>
                        <button @click="showChat = true" class="action-btn primary">
                            <span class="btn-icon">🧙‍♂️</span>
                            Open 3D Chatbot
                        </button>
                    </div>

                    <div class="section-card">
                        <h2>👥 User Management</h2>
                        <p>Manage user accounts and permissions</p>
                        <div class="action-group">
                            <button @click="viewUsers" class="action-btn">
                                <span class="btn-icon">👁️</span>
                                View Users
                            </button>
                            <button @click="addUser" class="action-btn">
                                <span class="btn-icon">➕</span>
                                Add User
                            </button>
                        </div>
                    </div>

                    <div class="section-card">
                        <h2>📊 Analytics</h2>
                        <p>View usage statistics and reports</p>
                        <div class="action-group">
                            <button @click="viewAnalytics" class="action-btn">
                                <span class="btn-icon">📈</span>
                                Usage Reports
                            </button>
                            <button @click="exportData" class="action-btn">
                                <span class="btn-icon">📥</span>
                                Export Data
                            </button>
                        </div>
                    </div>

                    <div class="section-card">
                        <h2>⚙️ System Settings</h2>
                        <p>Configure system-wide settings</p>
                        <div class="action-group">
                            <button @click="systemSettings" class="action-btn">
                                <span class="btn-icon">🔧</span>
                                Settings
                            </button>
                            <button @click="systemHealth" class="action-btn">
                                <span class="btn-icon">💚</span>
                                Health Check
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- 3D Chatbot Modal -->
        <EnhancedChatBot v-if="showChat" @close="showChat = false" :user="user" />
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { userUtils } from '@/services/api'
import EnhancedChatBot from '@/components/chat/EnhancedChatBot.vue'

export default {
    name: 'AdminDashboard',
    components: {
        EnhancedChatBot
    },
    setup() {
        const user = ref(null)
        const showChat = ref(false)

        const stats = ref({
            totalUsers: 156,
            totalMessages: 2847,
            activeSessions: 23,
            achievements: 89
        })

        // Check admin access
        const checkAdminAccess = () => {
            const currentUser = userUtils.getCurrentUser()
            if (!currentUser || currentUser.role !== 'admin') {
                // Redirect to home if not admin
                window.location.href = '/'
                return
            }
            user.value = currentUser
        }

        const logout = () => {
            userUtils.logout()
        }

        // Action handlers (placeholder for now)
        const viewUsers = () => {
            console.log('View Users - TODO: Implement user management')
        }

        const addUser = () => {
            console.log('Add User - TODO: Implement user creation')
        }

        const viewAnalytics = () => {
            console.log('View Analytics - TODO: Implement analytics dashboard')
        }

        const exportData = () => {
            console.log('Export Data - TODO: Implement data export')
        }

        const systemSettings = () => {
            console.log('System Settings - TODO: Implement settings panel')
        }

        const systemHealth = () => {
            console.log('System Health - TODO: Implement health check')
        }

        onMounted(() => {
            checkAdminAccess()
        })

        return {
            user,
            showChat,
            stats,
            logout,
            viewUsers,
            addUser,
            viewAnalytics,
            exportData,
            systemSettings,
            systemHealth
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

.logout-btn {
    padding: 0.5rem 1rem;
    background: #ff6b6b;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition: background 0.3s;
}

.logout-btn:hover {
    background: #ff5252;
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
    --theme-color: #222F5B;
}

.stat-icon {
    font-size: 3rem;
    color: var(--theme-color);
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.stat-content {
    color: #3B312E;
    /* Dark charcoal */
}

.stat-content h3 {
    margin: 0 0 0.5rem 0;
    color: #5a4f4a;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stat-number {
    font-family: 'Merriweather', serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #3B312E;
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