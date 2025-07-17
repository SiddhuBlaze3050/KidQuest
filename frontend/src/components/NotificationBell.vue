<template>
    <div class="notification-bell" ref="bellContainer">
        <div class="bell-icon" @click="toggleDropdown" :class="{ 'has-notifications': unreadCount > 0 }">
            <span class="bell">🔔</span>
            <div v-if="unreadCount > 0" class="notification-badge">
                {{ unreadCount > 9 ? '9+' : unreadCount }}
            </div>
        </div>

        <!-- Notification Dropdown -->
        <div v-if="showDropdown" class="notification-dropdown">
            <div class="dropdown-header">
                <h3>Notifications</h3>
                <div class="header-actions">
                    <div class="notification-filters">
                        <button @click="filterType = 'all'" :class="{ active: filterType === 'all' }"
                            class="filter-btn">All</button>
                        <button @click="filterType = 'achievement'" :class="{ active: filterType === 'achievement' }"
                            class="filter-btn">🏆</button>
                        <button @click="filterType = 'health'" :class="{ active: filterType === 'health' }"
                            class="filter-btn">💪</button>
                        <button @click="filterType = 'learning'" :class="{ active: filterType === 'learning' }"
                            class="filter-btn">📚</button>
                        <button @click="filterType = 'financial'" :class="{ active: filterType === 'financial' }"
                            class="filter-btn">💰</button>
                    </div>
                    <button @click="fetchNotifications" class="refresh-notifications-btn" title="Refresh notifications">
                        🔄
                    </button>
                    <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-read-btn">
                        Mark all read
                    </button>
                </div>
            </div>

            <div class="notification-list">
                <div v-if="notifications.length === 0" class="empty-notifications">
                    <p>No notifications yet!</p>
                    <p class="empty-subtitle">Complete activities to earn notifications</p>
                </div>

                <div v-else>
                    <div v-for="notification in filteredNotifications" :key="notification.id" class="notification-item"
                        :class="{
                            'unread': !notification.is_read,
                            'high-priority': notification.priority === 'high',
                            'urgent-priority': notification.priority === 'urgent',
                            [notification.notification_type]: true
                        }" @click="handleNotificationClick(notification)">

                        <div class="notification-icon">
                            {{ getNotificationIcon(notification.notification_type, notification.extra_data) }}
                        </div>
                        <div class="notification-content">
                            <div class="notification-text">{{ notification.content }}</div>
                            <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
                        </div>
                        <div v-if="!notification.is_read" class="unread-dot"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { apiService } from '@/services/api'

export default {
    name: 'NotificationBell',
    props: {
        userId: {
            type: Number,
            required: true
        }
    },
    setup(props) {
        const notifications = ref([])
        const showDropdown = ref(false)
        const bellContainer = ref(null)
        const filterType = ref('all')

        const unreadCount = computed(() => {
            return notifications.value.filter(n => !n.is_read).length
        })

        const hasHighPriority = computed(() => {
            return notifications.value.some(n => !n.is_read && (n.priority === 'high' || n.priority === 'urgent'))
        })

        const priorityClass = computed(() => {
            if (hasHighPriority.value) return 'high-priority'
            return 'normal-priority'
        })

        const filteredNotifications = computed(() => {
            let filtered = notifications.value

            if (filterType.value !== 'all') {
                filtered = filtered.filter(n => n.notification_type === filterType.value)
            }

            // Sort by priority and timestamp
            return filtered.sort((a, b) => {
                const priorityOrder = { 'urgent': 0, 'high': 1, 'normal': 2, 'low': 3 }
                if (a.priority !== b.priority) {
                    return priorityOrder[a.priority] - priorityOrder[b.priority]
                }
                return new Date(b.timestamp) - new Date(a.timestamp)
            })
        })

        const fetchNotifications = async () => {
            try {
                const response = await apiService.getNotifications(props.userId)
                if (response.success) {
                    notifications.value = response.notifications
                }
            } catch (error) {
                console.error('Error fetching notifications:', error)
            }
        }

        const markAsRead = async (notification) => {
            if (!notification.is_read) {
                try {
                    await apiService.markNotificationsRead([notification.id])
                    notification.is_read = true
                } catch (error) {
                    console.error('Error marking notification as read:', error)
                }
            }
        }

        const markAllAsRead = async () => {
            const unreadIds = notifications.value
                .filter(n => !n.is_read)
                .map(n => n.id)

            if (unreadIds.length > 0) {
                try {
                    await apiService.markNotificationsRead(unreadIds)
                    notifications.value.forEach(n => {
                        if (unreadIds.includes(n.id)) {
                            n.is_read = true
                        }
                    })
                } catch (error) {
                    console.error('Error marking all notifications as read:', error)
                }
            }
        }



        const handleNotificationClick = async (notification) => {
            // Mark as read if unread
            if (!notification.is_read) {
                await markAsRead(notification)
            }

            // Handle action URL if present
            if (notification.action_url) {
                // Navigate to the URL (you can use router here)
                console.log('Navigate to:', notification.action_url)
                // router.push(notification.action_url) // Uncomment when router is available
            }
        }

        const getNotificationIcon = (type, extra_data) => {
            // Use extra_data icon if available, fallback to type-based icons
            if (extra_data && extra_data.icon) {
                return extra_data.icon
            }

            const icons = {
                'achievement': '🏆',
                'health': '💪',
                'learning': '📚',
                'financial': '💰',
                'system': '✨',
                'general': '📢'
            }
            return icons[type] || '📢'
        }



        const toggleDropdown = () => {
            showDropdown.value = !showDropdown.value
        }

        const closeDropdown = (event) => {
            if (bellContainer.value && !bellContainer.value.contains(event.target)) {
                showDropdown.value = false
            }
        }

        const formatTime = (timestamp) => {
            const date = new Date(timestamp)
            const now = new Date()
            const diffInMilliseconds = now - date
            const diffInSeconds = Math.floor(diffInMilliseconds / 1000)
            const diffInMinutes = Math.floor(diffInSeconds / 60)
            const diffInHours = Math.floor(diffInMinutes / 60)
            const diffInDays = Math.floor(diffInHours / 24)

            // Debug: Log the first few notifications
            if (Math.random() < 0.1) { // Only log 10% of the time to avoid spam
                console.log(`🕐 Timestamp debug:`, {
                    original: timestamp,
                    parsed: date.toISOString(),
                    now: now.toISOString(),
                    diffHours: diffInHours,
                    diffMinutes: diffInMinutes,
                    diffSeconds: diffInSeconds
                })
            }

            // More precise time formatting
            if (diffInSeconds < 30) {
                return 'Just now'
            } else if (diffInSeconds < 60) {
                return `${diffInSeconds}s ago`
            } else if (diffInMinutes < 60) {
                return `${diffInMinutes}m ago`
            } else if (diffInHours < 24) {
                return `${diffInHours}h ago`
            } else if (diffInDays < 7) {
                return `${diffInDays}d ago`
            } else {
                return date.toLocaleDateString()
            }
        }

        onMounted(() => {
            fetchNotifications()
            document.addEventListener('click', closeDropdown)

            // Set up automatic refresh every 10 seconds to catch new notifications
            const refreshInterval = setInterval(() => {
                if (!showDropdown.value) {  // Only refresh when dropdown is closed
                    fetchNotifications()
                }
            }, 10000)

            // Store interval ID for cleanup
            window.notificationRefreshInterval = refreshInterval
        })

        onBeforeUnmount(() => {
            document.removeEventListener('click', closeDropdown)

            // Clear the notification refresh interval
            if (window.notificationRefreshInterval) {
                clearInterval(window.notificationRefreshInterval)
                window.notificationRefreshInterval = null
            }
        })

        return {
            notifications,
            showDropdown,
            unreadCount,
            bellContainer,
            filterType,
            hasHighPriority,
            priorityClass,
            filteredNotifications,
            fetchNotifications,
            markAsRead,
            markAllAsRead,
            handleNotificationClick,
            getNotificationIcon,
            toggleDropdown,
            formatTime
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.notification-bell {
    position: relative;
    font-family: 'Merriweather', serif;
}

.bell-icon {
    position: relative;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 50%;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.bell-icon:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: scale(1.1);
}

.bell-icon.has-notifications {
    animation: ring 2s ease-in-out infinite;
}

.bell-icon.has-notifications.high-priority {
    animation: urgentRing 1s ease-in-out infinite;
}

.bell {
    font-size: 1.5rem;
    color: #333;
}

.notification-badge {
    position: absolute;
    top: -2px;
    right: -2px;
    background: #ff4757;
    color: white;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: bold;
    animation: pulse 1.5s ease-in-out infinite;
    box-shadow: 0 2px 6px rgba(255, 71, 87, 0.4);
}

.notification-badge.high-priority {
    background: #ff6b6b;
    animation: urgentPulse 1s ease-in-out infinite;
}

.notification-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    width: 350px;
    max-height: 400px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(0, 0, 0, 0.1);
    z-index: 1000;
    overflow: hidden;
    margin-top: 0.5rem;
}

.dropdown-header {
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.dropdown-header h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
}

.header-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
}

.notification-filters {
    display: flex;
    gap: 0.25rem;
}

.filter-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.3s;
    min-width: 30px;
}

.filter-btn:hover,
.filter-btn.active {
    background: rgba(255, 255, 255, 0.4);
    transform: translateY(-1px);
}

.mark-all-read-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: background 0.3s;
}

.mark-all-read-btn:hover {
    background: rgba(255, 255, 255, 0.3);
}

.refresh-notifications-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.4rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.3s;
    margin-right: 0.5rem;
}

.refresh-notifications-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: rotate(180deg);
}

.notification-list {
    max-height: 300px;
    overflow-y: auto;
}

.empty-notifications {
    padding: 2rem;
    text-align: center;
    color: #666;
}

.empty-subtitle {
    font-size: 0.9rem;
    color: #999;
    margin-top: 0.5rem;
}

.notification-item {
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}

.notification-item:hover {
    background: rgba(102, 126, 234, 0.05);
    transform: translateX(2px);
}

.notification-item.unread {
    background: rgba(102, 126, 234, 0.1);
    border-left: 3px solid #667eea;
}

.notification-item.high-priority {
    border-left-color: #ff6b6b;
    background: rgba(255, 107, 107, 0.1);
}

.notification-item.urgent-priority {
    border-left-color: #ff4757;
    background: rgba(255, 71, 87, 0.15);
    animation: pulse 2s ease-in-out infinite;
}

.notification-icon {
    font-size: 1.5rem;
    min-width: 24px;
    text-align: center;
    margin-top: 0.1rem;
}

.notification-content {
    flex: 1;
}

.notification-text {
    font-size: 0.9rem;
    line-height: 1.4;
    margin-bottom: 0.5rem;
    color: #333;
    font-weight: 500;
}

.notification-time {
    font-size: 0.75rem;
    color: #666;
    opacity: 0.8;
}

.unread-dot {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 8px;
    height: 8px;
    background: #667eea;
    border-radius: 50%;
}

/* Custom scrollbar */
.notification-list::-webkit-scrollbar {
    width: 6px;
}

.notification-list::-webkit-scrollbar-track {
    background: #f1f1f1;
}

.notification-list::-webkit-scrollbar-thumb {
    background: #667eea;
    border-radius: 3px;
}

.notification-list::-webkit-scrollbar-thumb:hover {
    background: #5a6fd8;
}

/* Animations */
@keyframes ring {

    0%,
    100% {
        transform: rotate(0);
    }

    10%,
    30% {
        transform: rotate(-10deg);
    }

    20%,
    40% {
        transform: rotate(10deg);
    }
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }
}

@keyframes urgentRing {

    0%,
    100% {
        transform: rotate(0);
    }

    25% {
        transform: rotate(-15deg);
    }

    75% {
        transform: rotate(15deg);
    }
}

@keyframes urgentPulse {

    0%,
    100% {
        transform: scale(1);
        opacity: 1;
    }

    50% {
        transform: scale(1.2);
        opacity: 0.8;
    }
}
</style>