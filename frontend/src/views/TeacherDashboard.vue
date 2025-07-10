<template>
  <div class="teacher-dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="container">
        <div class="header-content">
          <div class="teacher-logo">
            <span class="logo-icon">👩‍🏫</span>
            <div class="logo-text">
              <h1>Teacher Dashboard</h1>
              <span class="subtitle">{{ className }} - Class Management</span>
            </div>
          </div>
          <div class="header-actions">
            <div class="date-selector">
              <select v-model="selectedPeriod" @change="updatePeriod">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <button @click="openChatbot" class="chatbot-btn">
              <i class="fas fa-comments"></i>
              Parent Chat
            </button>
            <button @click="exportData" class="export-btn">
              <i class="fas fa-download"></i>
              Export
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
        <!-- Overview Cards Row -->
        <div class="overview-grid">
          <div class="overview-card students-card" @click="showStudentsModal">
            <div class="card-icon">👥</div>
            <div class="card-content">
              <h3>Total Students</h3>
              <div class="students-count">{{ classStats.totalStudents }}</div>
              <p>{{ classStats.activeStudents }} active today</p>
            </div>
          </div>

          <div class="overview-card assignments-card" @click="showAssignmentsModal">
            <div class="card-icon">📝</div>
            <div class="card-content">
              <h3>Current Assignments</h3>
              <div class="assignments-count">{{ assignmentStats.current }}</div>
              <p>{{ assignmentStats.pending }} pending submissions</p>
            </div>
          </div>

          <div class="overview-card completion-card" @click="showAnalyticsModal">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <h3>Completion Rate</h3>
              <div class="completion-circle" :style="{ '--progress': completionRate }">
                <span class="completion-text">{{ completionRate }}%</span>
              </div>
              <p>Class average this week</p>
            </div>
          </div>

          <div class="overview-card engagement-card" @click="showEngagementModal">
            <div class="card-icon">⚡</div>
            <div class="card-content">
              <h3>Engagement Score</h3>
              <div class="engagement-value">{{ engagementScore }}/10</div>
              <p>{{ engagementTrend }}</p>
            </div>
          </div>
        </div>

        <!-- Main Features Grid -->
        <div class="main-features-grid">
          <!-- Class Task Tracker -->
          <div class="feature-card task-tracker-card" @click="showTaskTrackerModal">
            <div class="card-header">
              <div class="card-icon">🎯</div>
              <h3>Class Task Tracker</h3>
            </div>
            <div class="card-content">
              <div class="student-list">
                <div v-for="student in classStats.students.slice(0, 6)" :key="student.id" class="student-row">
                  <div class="student-info">
                    <div class="student-avatar">{{ student.avatar }}</div>
                    <div class="student-details">
                      <div class="student-name">{{ student.name }}</div>
                      <div class="student-status" :class="student.status">{{ student.statusText }}</div>
                    </div>
                  </div>
                  <div class="student-progress">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: student.progress + '%' }"></div>
                    </div>
                    <span class="progress-text">{{ student.progress }}%</span>
                  </div>
                </div>
              </div>
              <div class="view-all-btn" @click.stop="showAllStudents">
                View All Students ({{ classStats.totalStudents }})
              </div>
            </div>
          </div>

          <!-- Assignment Manager -->
          <div class="feature-card assignment-card" @click="showAssignmentManagerModal">
            <div class="card-header">
              <div class="card-icon">📋</div>
              <h3>Assignment Manager</h3>
            </div>
            <div class="card-content">
              <div class="assignment-list">
                <div v-for="assignment in currentAssignments.slice(0, 4)" :key="assignment.id" class="assignment-item">
                  <div class="assignment-info">
                    <div class="assignment-title">{{ assignment.title }}</div>
                    <div class="assignment-subject">{{ assignment.subject }}</div>
                    <div class="assignment-due">Due: {{ assignment.dueDate }}</div>
                  </div>
                  <div class="assignment-stats">
                    <div class="submitted-count">{{ assignment.submitted }}/{{ classStats.totalStudents }}</div>
                    <div class="submission-rate" :class="getSubmissionRateClass(assignment.submissionRate)">
                      {{ assignment.submissionRate }}%
                    </div>
                  </div>
                </div>
              </div>
              <button @click.stop="createNewAssignment" class="create-assignment-btn">
                <i class="fas fa-plus"></i>
                Create New Assignment
              </button>
            </div>
          </div>

          <!-- Analytics Dashboard -->
          <div class="feature-card analytics-card" @click="showAnalyticsModal">
            <div class="card-header">
              <div class="card-icon">📈</div>
              <h3>Class Analytics</h3>
            </div>
            <div class="card-content">
              <div class="analytics-grid">
                <div class="analytics-item">
                  <div class="analytics-icon">📊</div>
                  <div class="analytics-label">Avg. Score</div>
                  <div class="analytics-value">{{ analyticsData.avgScore }}%</div>
                </div>
                <div class="analytics-item">
                  <div class="analytics-icon">⏱️</div>
                  <div class="analytics-label">Avg. Time</div>
                  <div class="analytics-value">{{ analyticsData.avgTime }}min</div>
                </div>
                <div class="analytics-item">
                  <div class="analytics-icon">🎯</div>
                  <div class="analytics-label">On Time</div>
                  <div class="analytics-value">{{ analyticsData.onTimeRate }}%</div>
                </div>
                <div class="analytics-item">
                  <div class="analytics-icon">📈</div>
                  <div class="analytics-label">Improvement</div>
                  <div class="analytics-value">+{{ analyticsData.improvement }}%</div>
                </div>
              </div>
              <div class="performance-chart">
                <div class="chart-header">Weekly Performance</div>
                <div class="chart-bars">
                  <div v-for="day in performanceData" :key="day.day" class="chart-bar">
                    <div class="bar-fill" :style="{ height: day.percentage + '%' }"></div>
                    <div class="bar-label">{{ day.day }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Parent Communication Hub -->
          <div class="feature-card communication-card" @click="showCommunicationModal">
            <div class="card-header">
              <div class="card-icon">💬</div>
              <h3>Parent Communication</h3>
            </div>
            <div class="card-content">
              <div class="communication-stats">
                <div class="comm-stat">
                  <div class="stat-icon">📧</div>
                  <div class="stat-info">
                    <div class="stat-value">{{ communicationStats.messages }}</div>
                    <div class="stat-label">Messages Today</div>
                  </div>
                </div>
                <div class="comm-stat">
                  <div class="stat-icon">🤖</div>
                  <div class="stat-info">
                    <div class="stat-value">{{ communicationStats.chatbotSessions }}</div>
                    <div class="stat-label">AI Conversations</div>
                  </div>
                </div>
              </div>
              <div class="recent-conversations">
                <div class="conversation-header">Recent Conversations</div>
                <div v-for="conv in recentConversations.slice(0, 3)" :key="conv.id" class="conversation-item">
                  <div class="conv-avatar">{{ conv.parentAvatar }}</div>
                  <div class="conv-details">
                    <div class="conv-parent">{{ conv.parentName }}</div>
                    <div class="conv-preview">{{ conv.lastMessage }}</div>
                    <div class="conv-time">{{ conv.time }}</div>
                  </div>
                  <div class="conv-status" :class="conv.status">{{ conv.statusIcon }}</div>
                </div>
              </div>
              <button @click.stop="openParentChatbot" class="chatbot-access-btn">
                <i class="fas fa-robot"></i>
                Open Parent AI Assistant
              </button>
            </div>
          </div>

          <!-- Student Mood Tracker -->
          <div class="feature-card mood-card" @click="showMoodModal">
            <div class="card-header">
              <div class="card-icon">😊</div>
              <h3>Class Mood Tracker</h3>
            </div>
            <div class="card-content">
              <div class="mood-overview">
                <div class="mood-summary">
                  <div class="mood-emoji-large">{{ classMood.overall.emoji }}</div>
                  <div class="mood-text">{{ classMood.overall.text }}</div>
                </div>
                <div class="mood-breakdown">
                  <div v-for="mood in classMood.breakdown" :key="mood.type" class="mood-item">
                    <div class="mood-emoji">{{ mood.emoji }}</div>
                    <div class="mood-count">{{ mood.count }}</div>
                  </div>
                </div>
              </div>
              <div class="mood-alerts">
                <div v-for="alert in moodAlerts.slice(0, 2)" :key="alert.id" class="mood-alert" :class="alert.priority">
                  <div class="alert-icon">{{ alert.icon }}</div>
                  <div class="alert-text">{{ alert.message }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="feature-card actions-card">
            <div class="card-header">
              <div class="card-icon">⚡</div>
              <h3>Quick Actions</h3>
            </div>
            <div class="card-content">
              <div class="action-buttons">
                <button @click="sendClassAnnouncement" class="action-btn announcement-btn">
                  <i class="fas fa-bullhorn"></i>
                  Send Announcement
                </button>
                <button @click="scheduleParentMeeting" class="action-btn meeting-btn">
                  <i class="fas fa-calendar-plus"></i>
                  Schedule Meeting
                </button>
                <button @click="generateProgressReport" class="action-btn report-btn">
                  <i class="fas fa-file-alt"></i>
                  Progress Report
                </button>
                <button @click="exportClassData" class="action-btn export-btn">
                  <i class="fas fa-download"></i>
                  Export Data
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Magic -->
        <div class="floating-magic">
          <div class="magic-element" style="--delay: 0s; --x: 10%; --y: 20%;">📚</div>
          <div class="magic-element" style="--delay: 2s; --x: 90%; --y: 30%;">✏️</div>
          <div class="magic-element" style="--delay: 4s; --x: 15%; --y: 70%;">🎓</div>
          <div class="magic-element" style="--delay: 6s; --x: 85%; --y: 80%;">📝</div>
        </div>
      </div>
    </main>

    <!-- Modals -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <component :is="modalComponent" :data="modalData" />
        </div>
      </div>
    </div>

    <!-- Parent Chatbot Modal -->
    <div v-if="showChatbotModal" class="chatbot-modal-overlay" @click="closeChatbot">
      <div class="chatbot-modal" @click.stop>
        <div class="chatbot-header">
          <h3>Parent AI Assistant</h3>
          <button @click="closeChatbot" class="close-btn">×</button>
        </div>
        <div class="chatbot-body">
          <div class="chat-messages" ref="chatMessages">
            <div v-for="message in chatMessages" :key="message.id" class="chat-message" :class="message.sender">
              <div class="message-content">{{ message.content }}</div>
              <div class="message-time">{{ message.time }}</div>
            </div>
          </div>
          <div class="chat-input">
            <input 
              v-model="newMessage" 
              @keyup.enter="sendMessage" 
              placeholder="Type your message to parents..."
              class="message-input"
            />
            <button @click="sendMessage" class="send-btn">
              <i class="fas fa-paper-plane"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Reactive State
const className = ref('Grade 5A')
const selectedPeriod = ref('daily')
const showModal = ref(false)
const showChatbotModal = ref(false)
const modalTitle = ref('')
const modalComponent = ref('')
const modalData = ref({})
const newMessage = ref('')
const chatMessages = ref([
  {
    id: 1,
    sender: 'assistant',
    content: 'Hello! I am here to help you communicate with parents. How can I assist you today?',
    time: '10:30 AM'
  }
])

// Class Statistics
const classStats = ref({
  totalStudents: 24,
  activeStudents: 22,
  students: [
    { id: 1, name: 'Emma Johnson', avatar: '👧', status: 'completed', statusText: 'All tasks done', progress: 100 },
    { id: 2, name: 'Liam Smith', avatar: '👦', status: 'in-progress', statusText: '2 tasks pending', progress: 75 },
    { id: 3, name: 'Sophia Davis', avatar: '👧', status: 'completed', statusText: 'All tasks done', progress: 100 },
    { id: 4, name: 'Noah Wilson', avatar: '👦', status: 'pending', statusText: '3 tasks pending', progress: 40 },
    { id: 5, name: 'Olivia Brown', avatar: '👧', status: 'in-progress', statusText: '1 task pending', progress: 90 },
    { id: 6, name: 'William Jones', avatar: '👦', status: 'completed', statusText: 'All tasks done', progress: 100 }
  ]
})

const assignmentStats = ref({
  current: 5,
  pending: 12
})

const completionRate = ref(85)
const engagementScore = ref(8.5)
const engagementTrend = ref('Trending up this week')

// Current Assignments
const currentAssignments = ref([
  {
    id: 1,
    title: 'Math Practice - Fractions',
    subject: 'Mathematics',
    dueDate: 'July 12, 2025',
    submitted: 18,
    submissionRate: 75
  },
  {
    id: 2,
    title: 'Science Project - Solar System',
    subject: 'Science',
    dueDate: 'July 15, 2025',
    submitted: 12,
    submissionRate: 50
  },
  {
    id: 3,
    title: 'English Essay - My Summer',
    subject: 'English',
    dueDate: 'July 10, 2025',
    submitted: 22,
    submissionRate: 92
  },
  {
    id: 4,
    title: 'History Timeline',
    subject: 'History',
    dueDate: 'July 18, 2025',
    submitted: 8,
    submissionRate: 33
  }
])

// Analytics Data
const analyticsData = ref({
  avgScore: 87,
  avgTime: 45,
  onTimeRate: 78,
  improvement: 12
})

const performanceData = ref([
  { day: 'Mon', percentage: 85 },
  { day: 'Tue', percentage: 92 },
  { day: 'Wed', percentage: 78 },
  { day: 'Thu', percentage: 88 },
  { day: 'Fri', percentage: 95 },
  { day: 'Sat', percentage: 70 },
  { day: 'Sun', percentage: 65 }
])

// Communication Stats
const communicationStats = ref({
  messages: 15,
  chatbotSessions: 8
})

const recentConversations = ref([
  {
    id: 1,
    parentName: 'Sarah Johnson',
    parentAvatar: '👩',
    lastMessage: 'How is Emma doing with math?',
    time: '2 hours ago',
    status: 'unread',
    statusIcon: '🔴'
  },
  {
    id: 2,
    parentName: 'Mike Smith',
    parentAvatar: '👨',
    lastMessage: 'Thank you for the update!',
    time: '4 hours ago',
    status: 'read',
    statusIcon: '✅'
  },
  {
    id: 3,
    parentName: 'Lisa Davis',
    parentAvatar: '👩',
    lastMessage: 'Can we schedule a meeting?',
    time: '1 day ago',
    status: 'replied',
    statusIcon: '💬'
  }
])

// Class Mood Data
const classMood = ref({
  overall: {
    emoji: '😊',
    text: 'Generally Happy'
  },
  breakdown: [
    { type: 'happy', emoji: '😊', count: 15 },
    { type: 'neutral', emoji: '😐', count: 6 },
    { type: 'sad', emoji: '😢', count: 2 },
    { type: 'excited', emoji: '🤩', count: 1 }
  ]
})

const moodAlerts = ref([
  {
    id: 1,
    icon: '⚠️',
    message: '2 students showing signs of stress',
    priority: 'medium'
  },
  {
    id: 2,
    icon: '💡',
    message: 'Class engagement up 15% this week',
    priority: 'positive'
  }
])

// Methods
const openModal = (title, component, data) => {
  modalTitle.value = title
  modalComponent.value = component
  modalData.value = data
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const openChatbot = () => {
  showChatbotModal.value = true
}

const closeChatbot = () => {
  showChatbotModal.value = false
}

const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  
  // Add user message
  chatMessages.value.push({
    id: Date.now(),
    sender: 'user',
    content: newMessage.value,
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  })
  
  const userMessage = newMessage.value
  newMessage.value = ''
  
  // Simulate AI response (replace with actual API call)
  setTimeout(() => {
    chatMessages.value.push({
      id: Date.now() + 1,
      sender: 'assistant',
      content: generateParentResponse(userMessage),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    })
  }, 1000)
}

const generateParentResponse = (message) => {
  // Simple response generator - replace with actual AI integration
  const responses = [
    "I understand your concern. Let me help you draft a message to parents about this.",
    "That's a great point. Here's how you can communicate this effectively to parents:",
    "Based on the class data, I recommend mentioning the following to parents:",
    "I can help you create a personalized message for each parent about their child's progress."
  ]
  return responses[Math.floor(Math.random() * responses.length)]
}

const getSubmissionRateClass = (rate) => {
  if (rate >= 80) return 'high'
  if (rate >= 60) return 'medium'
  return 'low'
}

// Modal Methods
const showStudentsModal = () => openModal('Class Overview', 'students-modal', classStats.value)
const showAssignmentsModal = () => openModal('Assignments', 'assignments-modal', currentAssignments.value)
const showAnalyticsModal = () => openModal('Analytics', 'analytics-modal', analyticsData.value)
const showEngagementModal = () => openModal('Engagement', 'engagement-modal', { score: engagementScore.value })
const showTaskTrackerModal = () => openModal('Task Tracker', 'task-tracker-modal', classStats.value)
const showAssignmentManagerModal = () => openModal('Assignment Manager', 'assignment-manager-modal', currentAssignments.value)
const showCommunicationModal = () => openModal('Communication', 'communication-modal', communicationStats.value)
const showMoodModal = () => openModal('Class Mood', 'mood-modal', classMood.value)

// Action Methods
const createNewAssignment = () => {
  console.log('Creating new assignment...')
  // Implement assignment creation logic
}

const sendClassAnnouncement = () => {
  console.log('Sending class announcement...')
  // Implement announcement logic
}

const scheduleParentMeeting = () => {
  console.log('Scheduling parent meeting...')
  // Implement meeting scheduling logic
}

const generateProgressReport = () => {
  console.log('Generating progress report...')
  // Implement report generation logic
}

const exportClassData = () => {
  console.log('Exporting class data...')
  // Implement data export logic
}

const showAllStudents = () => {
  showStudentsModal()
}

const openParentChatbot = () => {
  openChatbot()
}

const updatePeriod = () => {
  console.log('Period changed:', selectedPeriod.value)
  // Implement period update logic
}

const exportData = () => {
  console.log('Exporting data...')
  // Implement data export logic
}

const logout = () => {
  console.log('Logging out...')
  // Implement logout logic
}

onMounted(() => {
  // Initialize dashboard data
  console.log('Teacher Dashboard mounted')
})
</script>

<style scoped>
/* Import the same base styles as Parent Dashboard */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.teacher-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  font-family: 'Merriweather', serif;
}

/* Header Styles */
.dashboard-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.teacher-logo {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 2.5rem;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d);
  border-radius: 50%;
  padding: 10px;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.logo-text h1 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
}

.subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.date-selector select,
.export-btn,
.logout-btn,
.chatbot-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.chatbot-btn {
  background: rgba(76, 175, 80, 0.2);
  border-color: rgba(76, 175, 80, 0.3);
}

.chatbot-btn:hover {
  background: rgba(76, 175, 80, 0.3);
  transform: translateY(-2px);
}

.export-btn:hover,
.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.logout-btn {
  background: rgba(255, 107, 107, 0.2);
  border-color: rgba(255, 107, 107, 0.3);
}

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.3);
}

/* Main Dashboard */
.dashboard-main {
  padding: 30px 0;
}

/* Overview Grid */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.overview-card {
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.overview-card:nth-child(1) {
  background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
}

.overview-card:nth-child(2) {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.overview-card:nth-child(3) {
  background: linear-gradient(135deg, #FFD93D 0%, #FFA726 100%);
}

.overview-card:nth-child(4) {
  background: linear-gradient(135deg, #A8E6CF 0%, #7FCDCD 100%);
}

.overview-card .card-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
  display: block;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.overview-card h3 {
  color: white;
  font-size: 1.2rem;
  margin-bottom: 15px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.overview-card p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  margin-top: 10px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.students-count,
.assignments-count,
.engagement-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.completion-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(white 0deg, white calc(var(--progress) * 3.6deg), rgba(255, 255, 255, 0.3) calc(var(--progress) * 3.6deg));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 15px 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.completion-text {
  color: #333;
  font-weight: 700;
  font-size: 1.1rem;
}

/* Main Features Grid */
.main-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.feature-card {
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 300px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.feature-card:nth-child(1) {
  background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
}

.feature-card:nth-child(2) {
  background: linear-gradient(135deg, #A8EDEA 0%, #FED6E3 100%);
}

.feature-card:nth-child(3) {
  background: linear-gradient(135deg, #FFECD2 0%, #FCB69F 100%);
}

.feature-card:nth-child(4) {
  background: linear-gradient(135deg, #C3ECE0 0%, #E6F3FF 100%);
}

.feature-card:nth-child(5) {
  background: linear-gradient(135deg, #FFB7B7 0%, #FFDFDF 100%);
}

.feature-card:nth-child(6) {
  background: linear-gradient(135deg, #B8E6B8 0%, #DCEDC8 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.card-header .card-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #333 0%, #555 100%);
  border-radius: 50%;
  padding: 10px;
  min-width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.card-header h3 {
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.card-content {
  flex: 1;
}

/* Student List Styles */
.student-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
}

.student-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 12px;
  transition: all 0.3s ease;
}

.student-row:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: translateX(5px);
}

.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-avatar {
  font-size: 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  padding: 8px;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.student-name {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.student-status {
  font-size: 0.8rem;
  color: #666;
  margin-top: 2px;
}

.student-status.completed {
  color: #4CAF50;
}

.student-status.in-progress {
  color: #FF9800;
}

.student-status.pending {
  color: #F44336;
}

.student-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 60px;
  height: 6px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: #333;
  min-width: 35px;
}

.view-all-btn {
  text-align: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  color: #333;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Assignment List Styles */
.assignment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 15px;
}

.assignment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 15px;
  transition: all 0.3s ease;
}

.assignment-item:hover {
  background: rgba(255, 255, 255, 0.6);
}

.assignment-title {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.assignment-subject {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
}

.assignment-due {
  font-size: 0.8rem;
  color: #888;
}

.assignment-stats {
  text-align: right;
}

.submitted-count {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.submission-rate {
  font-size: 0.8rem;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.submission-rate.high {
  background: rgba(76, 175, 80, 0.8);
  color: white;
}

.submission-rate.medium {
  background: rgba(255, 152, 0, 0.8);
  color: white;
}

.submission-rate.low {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.create-assignment-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.create-assignment-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

/* Analytics Styles */
.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.analytics-item {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  transition: all 0.3s ease;
}

.analytics-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.analytics-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.analytics-label {
  font-size: 0.8rem;
  color: #666;
  margin-bottom: 4px;
}

.analytics-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
}

.performance-chart {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 15px;
}

.chart-header {
  text-align: center;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.chart-bars {
  display: flex;
  justify-content: space-between;
  align-items: end;
  height: 80px;
  gap: 8px;
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(to top, #4CAF50, #8BC34A);
  border-radius: 4px 4px 0 0;
  min-height: 10px;
  transition: height 0.3s ease;
}

.bar-label {
  font-size: 0.7rem;
  color: #666;
  font-weight: 600;
}

/* Communication Styles */
.communication-stats {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.comm-stat {
  flex: 1;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  font-size: 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  padding: 8px;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
}

.recent-conversations {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
}

.conversation-header {
  font-weight: 600;
  color: #333;
  margin-bottom: 12px;
  font-size: 0.9rem;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.conversation-item:last-child {
  border-bottom: none;
}

.conv-avatar {
  font-size: 1.2rem;
  background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
  border-radius: 50%;
  padding: 6px;
  min-width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.conv-details {
  flex: 1;
}

.conv-parent {
  font-weight: 600;
  color: #333;
  font-size: 0.8rem;
}

.conv-preview {
  font-size: 0.7rem;
  color: #666;
  margin-top: 2px;
}

.conv-time {
  font-size: 0.7rem;
  color: #888;
  margin-top: 2px;
}

.conv-status {
  font-size: 0.8rem;
}

.chatbot-access-btn {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.chatbot-access-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* Mood Tracker Styles */
.mood-overview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mood-summary {
  text-align: center;
}

.mood-emoji-large {
  font-size: 3rem;
  margin-bottom: 8px;
}

.mood-text {
  font-weight: 600;
  color: #333;
  font-size: 1rem;
}

.mood-breakdown {
  display: flex;
  gap: 15px;
}

.mood-item {
  text-align: center;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 12px;
  min-width: 60px;
}

.mood-emoji {
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.mood-count {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.mood-alerts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mood-alert {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.8rem;
}

.mood-alert.medium {
  background: rgba(255, 152, 0, 0.2);
  border-left: 4px solid #FF9800;
}

.mood-alert.positive {
  background: rgba(76, 175, 80, 0.2);
  border-left: 4px solid #4CAF50;
}

.alert-icon {
  font-size: 1rem;
}

.alert-text {
  color: #333;
  font-weight: 500;
}

/* Quick Actions Styles */
.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-btn {
  padding: 12px;
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 0.8rem;
}

.announcement-btn {
  background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
}

.meeting-btn {
  background: linear-gradient(135deg, #4ECDC4, #44A08D);
}

.report-btn {
  background: linear-gradient(135deg, #FFD93D, #FFA726);
}

.export-btn {
  background: linear-gradient(135deg, #A8E6CF, #7FCDCD);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* Floating Magic Animation */
.floating-magic {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.magic-element {
  position: absolute;
  font-size: 1.5rem;
  opacity: 0.6;
  animation: float 8s ease-in-out infinite;
  animation-delay: var(--delay);
  left: var(--x);
  top: var(--y);
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(90deg); }
  50% { transform: translateY(-10px) rotate(180deg); }
  75% { transform: translateY(-15px) rotate(270deg); }
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
}

/* Chatbot Modal Styles */
.chatbot-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.chatbot-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  height: 70vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.chatbot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
  border-radius: 20px 20px 0 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.chatbot-header h3 {
  font-size: 1.3rem;
  font-weight: 600;
}

.chatbot-header .close-btn {
  color: white;
}

.chatbot-header .close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.chatbot-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.chat-message {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
}

.chat-message.user {
  align-self: flex-end;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.chat-message.assistant {
  align-self: flex-start;
  background: #f5f5f5;
  color: #333;
}

.message-content {
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 5px;
}

.message-time {
  font-size: 0.7rem;
  opacity: 0.7;
}

.chat-input {
  display: flex;
  gap: 10px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #eee;
  border-radius: 25px;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.message-input:focus {
  border-color: #667eea;
}

.send-btn {
  padding: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* Responsive Design */
@media (max-width: 1200px) {
  .main-features-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .main-features-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    grid-template-columns: 1fr;
  }
  
  .communication-stats {
    flex-direction: column;
  }
  
  .mood-overview {
    flex-direction: column;
    gap: 20px;
  }
  
  .mood-breakdown {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 15px;
  }
  
  .feature-card {
    min-height: auto;
    padding: 20px;
  }
  
  .logo-text h1 {
    font-size: 1.5rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .chatbot-modal {
    width: 95%;
    height: 80vh;
  }
}
</style>