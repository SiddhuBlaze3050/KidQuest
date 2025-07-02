<template>
    <div class="parent-dashboard">
        <!-- Header -->
        <header class="dashboard-header">
            <div class="container">
                <div class="header-content">
                    <div class="parent-logo">
                        <span class="logo-icon">👨‍👩‍👧‍👦</span>
                        <div class="logo-text">
                            <h1>Parent Dashboard</h1>
                            <span class="subtitle">{{ childName }}'s Progress Monitor</span>
                        </div>
                    </div>
                    <div class="header-actions">
                        <div class="date-selector">
                            <select v-model="selectedPeriod" @change="updateData">
                                <option value="today">Today</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                                <option value="all">All Time</option>
                            </select>
                        </div>
                        <button @click="exportReport" class="export-btn">
                            <i class="fas fa-download"></i>
                            Export Report
                        </button>
                        <button @click="logout" class="logout-btn">
                            <i class="fas fa-sign-out-alt"></i>
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="dashboard-main">
            <div class="container">
                <!-- Overview Cards -->
                <div class="overview-section">
                    <div class="overview-card highlight-card">
                        <div class="card-icon">📊</div>
                        <div class="card-content">
                            <h3>Overall Progress</h3>
                            <div class="progress-ring">
                                <div class="progress-circle" :style="{ '--progress': overallProgress }">
                                    <span class="progress-text">{{ overallProgress }}%</span>
                                </div>
                            </div>
                            <p>Excellent development this {{ selectedPeriod }}!</p>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-icon">⏱️</div>
                        <div class="card-content">
                            <h3>Screen Time</h3>
                            <div class="metric-value">{{ screenTime.total }}h {{ screenTime.minutes }}m</div>
                            <div class="metric-change" :class="screenTime.trend">
                                {{ screenTime.change }}% vs last {{ selectedPeriod }}
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-icon">✅</div>
                        <div class="card-content">
                            <h3>Tasks Completed</h3>
                            <div class="metric-value">{{ tasksCompleted.count }}/{{ tasksCompleted.total }}</div>
                            <div class="completion-bar">
                                <div class="completion-fill" :style="{ width: (tasksCompleted.count / tasksCompleted.total * 100) + '%' }"></div>
                            </div>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-icon">💰</div>
                        <div class="card-content">
                            <h3>Money Saved</h3>
                            <div class="metric-value">${{ moneySaved.amount }}</div>
                            <div class="savings-goal">
                                Goal: ${{ moneySaved.goal }}
                                <div class="goal-progress">{{ (moneySaved.amount / moneySaved.goal * 100).toFixed(0) }}%</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Detailed Analytics -->
                <div class="analytics-grid">
                    <!-- Psychometric Test Results -->
                    <div class="analytics-card">
                        <div class="card-header">
                            <h3>🧠 Psychometric Assessment</h3>
                            <span class="last-updated">Last updated: {{ formatDate(psychometricData.lastTest) }}</span>
                        </div>
                        <div class="psychometric-results">
                            <div class="personality-traits">
                                <h4>Personality Traits</h4>
                                <div class="trait-list">
                                    <div v-for="trait in psychometricData.traits" :key="trait.name" class="trait-item">
                                        <span class="trait-name">{{ trait.name }}</span>
                                        <div class="trait-bar">
                                            <div class="trait-fill" :style="{ width: trait.score + '%', backgroundColor: trait.color }"></div>
                                        </div>
                                        <span class="trait-score">{{ trait.score }}%</span>
                                    </div>
                                </div>
                            </div>
                            <div class="learning-style">
                                <h4>Learning Style</h4>
                                <div class="learning-chart">
                                    <div v-for="style in psychometricData.learningStyles" :key="style.type" class="learning-item">
                                        <div class="learning-icon">{{ style.icon }}</div>
                                        <div class="learning-info">
                                            <span class="learning-type">{{ style.type }}</span>
                                            <span class="learning-percentage">{{ style.percentage }}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Screen Time Analytics -->
                    <div class="analytics-card">
                        <div class="card-header">
                            <h3>📱 Screen Time Analysis</h3>
                            <div class="time-controls">
                                <button v-for="period in timePeriods" :key="period" 
                                        @click="selectedTimePeriod = period"
                                        :class="{ active: selectedTimePeriod === period }"
                                        class="time-btn">
                                    {{ period }}
                                </button>
                            </div>
                        </div>
                        <div class="screen-time-chart">
                            <div class="chart-container">
                                <canvas ref="screenTimeChart" width="400" height="200"></canvas>
                            </div>
                            <div class="app-breakdown">
                                <h4>App Usage Breakdown</h4>
                                <div class="app-list">
                                    <div v-for="app in appUsage" :key="app.name" class="app-item">
                                        <div class="app-info">
                                            <span class="app-icon">{{ app.icon }}</span>
                                            <span class="app-name">{{ app.name }}</span>
                                        </div>
                                        <div class="app-time">{{ app.time }}</div>
                                        <div class="app-bar">
                                            <div class="app-fill" :style="{ width: app.percentage + '%' }"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Homework & Tasks -->
                    <div class="analytics-card">
                        <div class="card-header">
                            <h3>📚 Homework & Tasks</h3>
                            <span class="completion-rate">{{ homeworkStats.completionRate }}% completion rate</span>
                        </div>
                        <div class="homework-content">
                            <div class="homework-calendar">
                                <h4>This Week's Schedule</h4>
                                <div class="calendar-grid">
                                    <div v-for="day in weeklySchedule" :key="day.date" class="calendar-day" :class="day.status">
                                        <div class="day-name">{{ day.name }}</div>
                                        <div class="day-date">{{ day.date }}</div>
                                        <div class="day-tasks">
                                            <span class="task-count">{{ day.completed }}/{{ day.total }}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="homework-details">
                                <h4>Recent Activities</h4>
                                <div class="activity-list">
                                    <div v-for="activity in recentHomework" :key="activity.id" class="activity-item">
                                        <div class="activity-icon" :class="activity.status">{{ activity.icon }}</div>
                                        <div class="activity-info">
                                            <span class="activity-title">{{ activity.title }}</span>
                                            <span class="activity-subject">{{ activity.subject }}</span>
                                        </div>
                                        <div class="activity-meta">
                                            <span class="activity-time">{{ activity.timeSpent }}</span>
                                            <span class="activity-score" v-if="activity.score">{{ activity.score }}%</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Child's Emotional Insights -->
                    <div class="analytics-card">
                        <div class="card-header">
                            <h3>💭 Emotional Insights</h3>
                            <span class="insight-period">Based on {{ emotionalInsights.conversationCount }} conversations</span>
                        </div>
                        <div class="emotional-content">
                            <div class="mood-tracker">
                                <h4>Mood Trends</h4>
                                <div class="mood-chart">
                                    <div v-for="mood in emotionalInsights.moodTrends" :key="mood.date" class="mood-day">
                                        <div class="mood-emoji" :title="mood.feeling">{{ mood.emoji }}</div>
                                        <div class="mood-date">{{ mood.date }}</div>
                                    </div>
                                </div>
                            </div>
                            <div class="conversation-summary">
                                <h4>Recent Conversations Summary</h4>
                                <div class="summary-cards">
                                    <div v-for="summary in emotionalInsights.summaries" :key="summary.id" class="summary-card">
                                        <div class="summary-topic">{{ summary.topic }}</div>
                                        <div class="summary-text">{{ summary.text }}</div>
                                        <div class="summary-sentiment" :class="summary.sentiment">
                                            {{ summary.sentiment }} sentiment
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Creative Activities -->
                    <div class="analytics-card">
                        <div class="card-header">
                            <h3>🎨 Creative Activities</h3>
                            <span class="activity-count">{{ creativeActivities.totalSessions }} sessions</span>
                        </div>
                        <div class="creative-content">
                            <div class="doodle-gallery">
                                <h4>Recent Doodles</h4>
                                <div class="doodle-grid">
                                    <div v-for="doodle in creativeActivities.doodles" :key="doodle.id" class="doodle-item">
                                        <div class="doodle-preview" :style="{ backgroundColor: doodle.primaryColor }">
                                            <span class="doodle-title">{{ doodle.title }}</span>
                                        </div>
                                        <div class="doodle-meta">
                                            <span class="doodle-date">{{ formatDate(doodle.date) }}</span>
                                            <span class="doodle-time">{{ doodle.timeSpent }}m</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="creativity-stats">
                                <h4>Creativity Metrics</h4>
                                <div class="creativity-metrics">
                                    <div class="metric-item">
                                        <span class="metric-label">Avg. Session Time</span>
                                        <span class="metric-value">{{ creativeActivities.avgSessionTime }}m</span>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Favorite Colors</span>
                                        <div class="color-palette">
                                            <div v-for="color in creativeActivities.favoriteColors" :key="color" 
                                                 class="color-dot" :style="{ backgroundColor: color }"></div>
                                        </div>
                                    </div>
                                    <div class="metric-item">
                                        <span class="metric-label">Creativity Score</span>
                                        <div class="creativity-score">{{ creativeActivities.creativityScore }}/100</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Pomodoro Session Results -->
                    <div class="analytics-card">
                        <div class="card-header">
                            <h3>🍅 Focus & Productivity</h3>
                            <span class="session-count">{{ pomodoroData.totalSessions }} sessions completed</span>
                        </div>
                        <div class="pomodoro-content">
                            <div class="focus-metrics">
                                <div class="focus-stat">
                                    <div class="stat-value">{{ pomodoroData.totalFocusTime }}</div>
                                    <div class="stat-label">Total Focus Time</div>
                                </div>
                                <div class="focus-stat">
                                    <div class="stat-value">{{ pomodoroData.avgSessionLength }}m</div>
                                    <div class="stat-label">Avg Session</div>
                                </div>
                                <div class="focus-stat">
                                    <div class="stat-value">{{ pomodoroData.focusScore }}/100</div>
                                    <div class="stat-label">Focus Score</div>
                                </div>
                            </div>
                            <div class="session-history">
                                <h4>Recent Sessions</h4>
                                <div class="session-list">
                                    <div v-for="session in pomodoroData.recentSessions" :key="session.id" class="session-item">
                                        <div class="session-time">{{ session.date }}</div>
                                        <div class="session-activity">{{ session.activity }}</div>
                                        <div class="session-duration">{{ session.duration }}m</div>
                                        <div class="session-rating">
                                            <div class="rating-stars">
                                                <span v-for="n in 5" :key="n" 
                                                      :class="{ filled: n <= session.rating }" 
                                                      class="star">⭐</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Recommendations Section -->
                <div class="recommendations-section">
                    <h2>📋 Personalized Recommendations</h2>
                    <div class="recommendations-grid">
                        <div v-for="recommendation in recommendations" :key="recommendation.id" class="recommendation-card">
                            <div class="rec-icon">{{ recommendation.icon }}</div>
                            <div class="rec-content">
                                <h4>{{ recommendation.title }}</h4>
                                <p>{{ recommendation.description }}</p>
                                <div class="rec-priority" :class="recommendation.priority">
                                    {{ recommendation.priority }} priority
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'

import { userUtils } from '@/services/api'


export default {
    name: 'ParentDashboard',
    setup() {
        const childName = ref("Aleena")
        const selectedPeriod = ref("week")
        const selectedTimePeriod = ref("7D")
        const timePeriods = ["1D", "7D", "30D"]
        const overallProgress = ref(78)

        // Screen time data
        const screenTime = ref({
            total: 3,
            minutes: 45,
            change: -12,
            trend: 'positive'
        })

        // Tasks completed
        const tasksCompleted = ref({
            count: 8,
            total: 12
        })

        // Money saved
        const moneySaved = ref({
            amount: 45.50,
            goal: 100
        })

        // Psychometric data
        const psychometricData = ref({
            lastTest: new Date('2025-01-20'),
            traits: [
                { name: 'Creativity', score: 85, color: '#ff6b6b' },
                { name: 'Focus', score: 72, color: '#4ecdc4' },
                { name: 'Social Skills', score: 90, color: '#45b7d1' },
                { name: 'Problem Solving', score: 78, color: '#96ceb4' },
                { name: 'Emotional Intelligence', score: 83, color: '#feca57' }
            ],
            learningStyles: [
                { type: 'Visual', percentage: 45, icon: '👁️' },
                { type: 'Auditory', percentage: 30, icon: '👂' },
                { type: 'Kinesthetic', percentage: 25, icon: '🤚' }
            ]
        })

        // App usage data
        const appUsage = ref([
            { name: 'Learning Games', time: '1h 30m', percentage: 40, icon: '🎮' },
            { name: 'Educational Videos', time: '45m', percentage: 20, icon: '📺' },
            { name: 'Reading App', time: '1h 15m', percentage: 33, icon: '📚' },
            { name: 'Creative Drawing', time: '15m', percentage: 7, icon: '🎨' }
        ])

        // Homework stats
        const homeworkStats = ref({
            completionRate: 85
        })

        // Weekly schedule
        const weeklySchedule = ref([
            { name: 'Mon', date: '20', completed: 3, total: 4, status: 'partial' },
            { name: 'Tue', date: '21', completed: 4, total: 4, status: 'complete' },
            { name: 'Wed', date: '22', completed: 2, total: 3, status: 'partial' },
            { name: 'Thu', date: '23', completed: 3, total: 3, status: 'complete' },
            { name: 'Fri', date: '24', completed: 1, total: 2, status: 'current' },
            { name: 'Sat', date: '25', completed: 0, total: 1, status: 'upcoming' },
            { name: 'Sun', date: '26', completed: 0, total: 1, status: 'upcoming' }
        ])

        // Recent homework
        const recentHomework = ref([
            { id: 1, title: 'Math Practice', subject: 'Mathematics', timeSpent: '25m', score: 92, icon: '🔢', status: 'completed' },
            { id: 2, title: 'Reading Comprehension', subject: 'English', timeSpent: '20m', score: 88, icon: '📖', status: 'completed' },
            { id: 3, title: 'Science Quiz', subject: 'Science', timeSpent: '15m', score: null, icon: '🔬', status: 'in-progress' },
            { id: 4, title: 'History Essay', subject: 'History', timeSpent: '35m', score: 95, icon: '📜', status: 'completed' }
        ])

        // Emotional insights
        const emotionalInsights = ref({
            conversationCount: 15,
            moodTrends: [
                { date: 'Mon', emoji: '😊', feeling: 'Happy' },
                { date: 'Tue', emoji: '🤔', feeling: 'Thoughtful' },
                { date: 'Wed', emoji: '😄', feeling: 'Excited' },
                { date: 'Thu', emoji: '😌', feeling: 'Calm' },
                { date: 'Fri', emoji: '🤗', feeling: 'Affectionate' },
                { date: 'Sat', emoji: '😴', feeling: 'Tired' },
                { date: 'Sun', emoji: '😊', feeling: 'Content' }
            ],
            summaries: [
                {
                    id: 1,
                    topic: 'School Friends',
                    text:  childName.value +' shared excitement about making a new friend in art class and working on a group project together.',
                    sentiment: 'positive'
                },
                {
                    id: 2,
                    topic: 'Learning Challenges',
                    text: 'Expressed some frustration with math homework but showed determination to practice more.',
                    sentiment: 'neutral'
                },
                {
                    id: 3,
                    topic: 'Future Goals',
                    text: 'Talked about wanting to learn guitar and showed interest in joining the school music program.',
                    sentiment: 'positive'
                }
            ]
        })

        // Creative activities
        const creativeActivities = ref({
            totalSessions: 12,
            avgSessionTime: 18,
            creativityScore: 87,
            favoriteColors: ['#ff6b6b', '#4ecdc4', '#45b7d1', '#feca57', '#96ceb4'],
            doodles: [
                { id: 1, title: 'Space Adventure', date: new Date('2025-01-23'), timeSpent: 22, primaryColor: '#4ecdc4' },
                { id: 2, title: 'Family Portrait', date: new Date('2025-01-22'), timeSpent: 35, primaryColor: '#ff6b6b' },
                { id: 3, title: 'Dream House', date: new Date('2025-01-21'), timeSpent: 28, primaryColor: '#feca57' },
                { id: 4, title: 'Pet Dragon', date: new Date('2025-01-20'), timeSpent: 15, primaryColor: '#96ceb4' }
            ]
        })

        // Pomodoro data
        const pomodoroData = ref({
            totalSessions: 24,
            totalFocusTime: '8h 30m',
            avgSessionLength: 22,
            focusScore: 82,
            recentSessions: [
                { id: 1, date: 'Today 3:30 PM', activity: 'Math Homework', duration: 25, rating: 4 },
                { id: 2, date: 'Today 2:00 PM', activity: 'Reading', duration: 20, rating: 5 },
                { id: 3, date: 'Yesterday 4:15 PM', activity: 'Science Project', duration: 30, rating: 3 },
                { id: 4, date: 'Yesterday 2:45 PM', activity: 'Art Practice', duration: 15, rating: 5 }
            ]
        })

        // Recommendations
        const recommendations = ref([
            {
                id: 1,
                icon: '📚',
                title: 'Increase Reading Time',
                description: childName.value+'shows strong comprehension skills. Consider adding 15 more minutes of daily reading to boost vocabulary.',
                priority: 'medium'
            },
            {
                id: 2,
                icon: '🎵',
                title: 'Explore Music Learning',
                description: 'Based on conversations, '+childName.value+' is interested in learning guitar. This could enhance cognitive development.',
                priority: 'high'
            },
            {
                id: 3,
                icon: '⏰',
                title: 'Optimize Screen Time',
                description: 'Screen time is within healthy limits, but consider more educational content during peak learning hours.',
                priority: 'low'
            },
            {
                id: 4,
                icon: '🤝',
                title: 'Social Activities',
                description: childName.value+' enjoys group activities. Consider enrolling in team sports or group learning programs.',
                priority: 'medium'
            }
        ])

        const formatDate = (date) => {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }

        const updateData = () => {
            console.log('Updating data for period:', selectedPeriod.value)
            // Here you would typically fetch new data based on the selected period
        }

        const exportReport = () => {
            alert('Exporting comprehensive report for ' + childName.value + '...')
            // Here you would implement actual report export functionality
        }

        const logout = () => {
            userUtils.logout()
        }

        const drawScreenTimeChart = () => {
            nextTick(() => {
                const canvas = document.querySelector('canvas')
                if (!canvas) return
                
                const ctx = canvas.getContext('2d')
                const width = canvas.width
                const height = canvas.height
                
                // Clear canvas
                ctx.clearRect(0, 0, width, height)
                
                // Sample data for screen time over the week
                const data = [2.5, 3.2, 2.8, 4.1, 3.5, 2.9, 3.7]
                const labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                
                // Draw chart
                const maxValue = Math.max(...data)
                const barWidth = width / data.length
                const barMaxHeight = height - 40
                
                ctx.fillStyle = '#4ecdc4'
                
                data.forEach((value, index) => {
                    const barHeight = (value / maxValue) * barMaxHeight
                    const x = index * barWidth + 10
                    const y = height - barHeight - 20
                    
                    ctx.fillRect(x, y, barWidth - 20, barHeight)
                    
                    // Draw labels
                    ctx.fillStyle = '#666'
                    ctx.font = '12px Arial'
                    ctx.textAlign = 'center'
                    ctx.fillText(labels[index], x + (barWidth - 20) / 2, height - 5)
                    ctx.fillText(value + 'h', x + (barWidth - 20) / 2, y - 5)
                    
                    ctx.fillStyle = '#4ecdc4'
                })
            })
        }

        onMounted(() => {
            drawScreenTimeChart()
        })

        return {
            childName,
            selectedPeriod,
            selectedTimePeriod,
            timePeriods,
            overallProgress,
            screenTime,
            tasksCompleted,
            moneySaved,
            psychometricData,
            appUsage,
            homeworkStats,
            weeklySchedule,
            recentHomework,
            emotionalInsights,
            creativeActivities,
            pomodoroData,
            recommendations,
            formatDate,
            updateData,
            exportReport,
            logout
        }
    }
}
</script>

<style scoped>
.parent-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header */
.dashboard-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.parent-logo {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.logo-icon {
    font-size: 2.5rem;
}

.logo-text h1 {
    margin: 0;
    font-size: 1.5rem;
    color: #333;
    font-weight: 700;
}

.subtitle {
    font-size: 0.9rem;
    color: #666;
    font-weight: 400;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.date-selector select {
    padding: 0.5rem 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    background: white;
    font-size: 0.9rem;
    cursor: pointer;
}

.export-btn, .logout-btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.export-btn {
    background: #4ecdc4;
    color: white;
}

.logout-btn {
    background: #ff6b6b;
    color: white;
}

.export-btn:hover, .logout-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* Main Content */
.dashboard-main {
    padding: 2rem 0;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Overview Section */
.overview-section {
    display: grid;
    grid-template-columns: 2fr repeat(3, 1fr);
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.overview-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.overview-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.highlight-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.card-icon {
    font-size: 2rem;
    margin-bottom: 0.5rem;
}

.card-content h3 {
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
}

.progress-ring {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
}

.progress-circle {
    position: relative;
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: conic-gradient(#4ecdc4 calc(var(--progress) * 1%), rgba(255, 255, 255, 0.3) 0);
    display: flex;
    align-items: center;
    justify-content: center;
}

.progress-circle::before {
    content: '';
    position: absolute;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: inherit;
}

.progress-text {
    position: relative;
    z-index: 1;
    font-size: 1.2rem;
    font-weight: 700;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 0.5rem;
}

.metric-change {
    font-size: 0.9rem;
    font-weight: 500;
}

.metric-change.positive {
    color: #4caf50;
}

.metric-change.negative {
    color: #ff5722;
}

.completion-bar {
    width: 100%;
    height: 8px;
    background: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 0.5rem;
}

.completion-fill {
    height: 100%;
    background: linear-gradient(90deg, #4ecdc4, #45b7d1);
    border-radius: 4px;
    transition: width 0.3s ease;
}

.savings-goal {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    color: #666;
    margin-top: 0.5rem;
}

.goal-progress {
    font-weight: 600;
    color: #4ecdc4;
}

/* Analytics Grid */
.analytics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 2rem;
    margin-bottom: 3rem;
}

.analytics-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e0e0e0;
}

.card-header h3 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #333;
}

.last-updated, .insight-period, .activity-count, .session-count, .completion-rate {
    font-size: 0.8rem;
    color: #666;
    background: #f5f5f5;
    padding: 0.3rem 0.8rem;
    border-radius: 12px;
}

/* Psychometric Results */
.psychometric-results {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}

.personality-traits h4, .learning-style h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
}

.trait-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.trait-item {
    display: grid;
    grid-template-columns: 1fr 2fr auto;
    align-items: center;
    gap: 1rem;
}

.trait-name {
    font-size: 0.9rem;
    font-weight: 500;
    color: #555;
}

.trait-bar {
    height: 8px;
    background: #e0e0e0;
    border-radius: 4px;
    overflow: hidden;
}

.trait-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.trait-score {
    font-size: 0.9rem;
    font-weight: 600;
    color: #333;
    min-width: 40px;
    text-align: right;
}

.learning-chart {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.learning-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.learning-icon {
    font-size: 1.5rem;
}

.learning-info {
    display: flex;
    flex-direction: column;
}

.learning-type {
    font-weight: 500;
    color: #333;
}

.learning-percentage {
    font-size: 0.9rem;
    color: #666;
}

/* Screen Time Analytics */
.time-controls {
    display: flex;
    gap: 0.5rem;
}

.time-btn {
    padding: 0.4rem 0.8rem;
    border: 1px solid #e0e0e0;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.3s;
}

.time-btn.active {
    background: #4ecdc4;
    color: white;
    border-color: #4ecdc4;
}

.screen-time-chart {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.chart-container {
    display: flex;
    justify-content: center;
    align-items: center;
}

.app-breakdown h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
}

.app-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.app-item {
    display: grid;
    grid-template-columns: 1fr auto 2fr;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.app-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.app-icon {
    font-size: 1.2rem;
}

.app-name {
    font-weight: 500;
    color: #333;
}

.app-time {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.app-bar {
    height: 6px;
    background: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
}

.app-fill {
    height: 100%;
    background: linear-gradient(90deg, #4ecdc4, #45b7d1);
    border-radius: 3px;
    transition: width 0.3s ease;
}

/* Homework & Tasks */
.homework-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.homework-calendar h4, .homework-details h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
}

.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.5rem;
}

.calendar-day {
    padding: 0.8rem 0.5rem;
    border-radius: 8px;
    text-align: center;
    border: 2px solid transparent;
    transition: all 0.3s;
}

.calendar-day.complete {
    background: #e8f5e8;
    border-color: #4caf50;
}

.calendar-day.partial {
    background: #fff3e0;
    border-color: #ff9800;
}

.calendar-day.current {
    background: #e3f2fd;
    border-color: #2196f3;
}

.calendar-day.upcoming {
    background: #f5f5f5;
    border-color: #e0e0e0;
}

.day-name {
    font-size: 0.8rem;
    font-weight: 600;
    color: #666;
}

.day-date {
    font-size: 1.1rem;
    font-weight: 700;
    color: #333;
    margin: 0.2rem 0;
}

.task-count {
    font-size: 0.8rem;
    color: #666;
}

.activity-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.activity-item {
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.activity-icon {
    font-size: 1.5rem;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.activity-icon.completed {
    background: #e8f5e8;
}

.activity-icon.in-progress {
    background: #fff3e0;
}

.activity-info {
    display: flex;
    flex-direction: column;
}

.activity-title {
    font-weight: 600;
    color: #333;
}

.activity-subject {
    font-size: 0.9rem;
    color: #666;
}

.activity-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.2rem;
}

.activity-time {
    font-size: 0.8rem;
    color: #666;
}

.activity-score {
    font-size: 0.9rem;
    font-weight: 600;
    color: #4caf50;
}

/* Emotional Insights */
.emotional-content {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
}

.mood-tracker h4, .conversation-summary h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
}

.mood-chart {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}

.mood-day {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.8rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.mood-emoji {
    font-size: 1.5rem;
    cursor: pointer;
}

.mood-date {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.summary-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.summary-card {
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #4ecdc4;
}

.summary-topic {
    font-weight: 600;
    color: #333;
    margin-bottom: 0.5rem;
}

.summary-text {
    font-size: 0.9rem;
    color: #555;
    line-height: 1.5;
    margin-bottom: 0.5rem;
}

.summary-sentiment {
    font-size: 0.8rem;
    font-weight: 500;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    display: inline-block;
}

.summary-sentiment.positive {
    background: #e8f5e8;
    color: #4caf50;
}

.summary-sentiment.neutral {
    background: #fff3e0;
    color: #ff9800;
}

.summary-sentiment.negative {
    background: #ffebee;
    color: #f44336;
}

/* Creative Activities */
.creative-content {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
}

.doodle-gallery h4, .creativity-stats h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
}

.doodle-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
}

.doodle-item {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

.doodle-item:hover {
    transform: translateY(-2px);
}

.doodle-preview {
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 0.9rem;
}

.doodle-meta {
    padding: 0.8rem;
    background: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.doodle-date, .doodle-time {
    font-size: 0.8rem;
    color: #666;
}

.creativity-metrics {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.metric-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.metric-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.metric-value {
    font-size: 1.2rem;
    font-weight: 600;
    color: #333;
}

.color-palette {
    display: flex;
    gap: 0.3rem;
}

.color-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 2px solid white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.creativity-score {
    font-size: 1.2rem;
    font-weight: 600;
    color: #4ecdc4;
}

/* Pomodoro Session Results */
.pomodoro-content {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
}

.focus-metrics {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.focus-stat {
    text-align: center;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.session-history h4 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #333;
}

.session-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.session-item {
    display: grid;
    grid-template-columns: auto 1fr auto auto;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
}

.session-time {
    font-size: 0.8rem;
    color: #666;
    min-width: 120px;
}

.session-activity {
    font-weight: 500;
    color: #333;
}

.session-duration {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

.rating-stars {
    display: flex;
    gap: 0.1rem;
}

.star {
    font-size: 0.8rem;
    opacity: 0.3;
}

.star.filled {
    opacity: 1;
}

/* Recommendations Section */
.recommendations-section {
    margin-top: 3rem;
}

.recommendations-section h2 {
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    font-size: 2rem;
    font-weight: 700;
}

.recommendations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.recommendation-card {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    display: flex;
    gap: 1rem;
    transition: transform 0.3s ease;
}

.recommendation-card:hover {
    transform: translateY(-3px);
}

.rec-icon {
    font-size: 2rem;
    flex-shrink: 0;
}

.rec-content {
    flex: 1;
}

.rec-content h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
}

.rec-content p {
    margin: 0 0 1rem 0;
    font-size: 0.9rem;
    color: #555;
    line-height: 1.5;
}

.rec-priority {
    font-size: 0.8rem;
    font-weight: 500;
    padding: 0.3rem 0.8rem;
    border-radius: 12px;
    display: inline-block;
}

.rec-priority.high {
    background: #ffebee;
    color: #f44336;
}

.rec-priority.medium {
    background: #fff3e0;
    color: #ff9800;
}

.rec-priority.low {
    background: #e8f5e8;
    color: #4caf50;
}

/* Responsive Design */
@media (max-width: 1200px) {
    .overview-section {
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
    }
    
    .analytics-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .header-actions {
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .overview-section {
        grid-template-columns: 1fr;
    }
    
    .psychometric-results,
    .screen-time-chart,
    .homework-content,
    .emotional-content,
    .creative-content,
    .pomodoro-content {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .calendar-grid {
        grid-template-columns: repeat(4, 1fr);
    }
    
    .doodle-grid {
        grid-template-columns: 1fr;
    }
    
    .recommendations-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 0 0.5rem;
    }
    
    .dashboard-main {
        padding: 1rem 0;
    }
    
    .overview-card,
    .analytics-card,
    .recommendation-card {
        padding: 1rem;
    }
    
    .logo-icon {
        font-size: 2rem;
    }
    
    .logo-text h1 {
        font-size: 1.2rem;
    }
    
    .calendar-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}
</style>