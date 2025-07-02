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
                <button v-if="unreadCount > 0" @click="markAllAsRead" class="mark-all-read-btn">
                    Mark all read
                </button>
            </div>

            <div class="notification-list">
                <div v-if="notifications.length === 0" class="empty-notifications">
                    <p>No notifications yet!</p>
                    <button @click="createSampleNotifications" class="sample-btn">
                        Create Sample Notifications
                    </button>
                </div>

                <div v-else>
                    <div v-for="notification in notifications" :key="notification.id" class="notification-item"
                        :class="{ 'unread': !notification.is_read }" @click="markAsRead(notification)">
                        <div class="notification-content">
                            {{ notification.content }}
                        </div>
                        <div class="notification-time">
                            {{ formatTime(notification.timestamp) }}
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

        const unreadCount = computed(() => {
            return notifications.value.filter(n => !n.is_read).length
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

        const createSampleNotifications = async () => {
            try {
                await apiService.createSampleNotifications(props.userId)
                await fetchNotifications() // Refresh the list
            } catch (error) {
                console.error('Error creating sample notifications:', error)
            }
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
            const diffInHours = (now - date) / (1000 * 60 * 60)

            if (diffInHours < 1) {
                const diffInMinutes = Math.floor((now - date) / (1000 * 60))
                return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes}m ago`
            } else if (diffInHours < 24) {
                return `${Math.floor(diffInHours)}h ago`
            } else {
                return date.toLocaleDateString()
            }
        }

        onMounted(() => {
            fetchNotifications()
            document.addEventListener('click', closeDropdown)
        })

        onBeforeUnmount(() => {
            document.removeEventListener('click', closeDropdown)
        })

        return {
            notifications,
            showDropdown,
            unreadCount,
            bellContainer,
            fetchNotifications,
            markAsRead,
            markAllAsRead,
            createSampleNotifications,
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
}

.dropdown-header h3 {
    margin: 0;
    font-size: 1.1rem;
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

.notification-list {
    max-height: 300px;
    overflow-y: auto;
}

.empty-notifications {
    padding: 2rem;
    text-align: center;
    color: #666;
}

.sample-btn {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 1rem;
    transition: transform 0.3s;
}

.sample-btn:hover {
    transform: translateY(-2px);
}

.notification-item {
    padding: 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    cursor: pointer;
    transition: background 0.3s;
    position: relative;
}

.notification-item:hover {
    background: rgba(102, 126, 234, 0.05);
}

.notification-item.unread {
    background: rgba(102, 126, 234, 0.1);
    border-left: 3px solid #667eea;
}

.notification-content {
    font-size: 0.9rem;
    line-height: 1.4;
    margin-bottom: 0.5rem;
    color: #333;
}

.notification-time {
    font-size: 0.75rem;
    color: #666;
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
</style>