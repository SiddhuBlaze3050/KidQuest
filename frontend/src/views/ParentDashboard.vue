<template>
  <div class="parent-dashboard">
    <!-- Transactions Modal (add here, at the top, so it overlays everything) -->
    <div v-if="modalComponent === 'transactions-modal'" class="transactions-modal modal-overlay" @click="closeModal">
      <div class="transactions-popup" @click.stop>
        <div class="popup-header">
          <span>Recent Transactions</span>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="popup-body">
          <div class="transaction-list">
            <div v-if="financeStats.recent.length === 0" class="no-transactions">No transactions yet.</div>
            <div v-for="t in financeStats.recent" :key="t.id" class="transaction-item" :class="t.type">
              <div class="transaction-date">{{ t.date }}</div>
              <div class="transaction-desc">{{ t.description }}</div>
              <div class="transaction-amount">
                {{ t.type === 'income' ? '+' : '-' }}₹{{ t.amount }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Transactions Modal -->

<!-- Psychometric Modal Component -->
<div v-if="modalComponent === 'psychometric-modal'" class="psychometric-modal modal-overlay" @click="closeModal">
  <div class="transactions-popup" @click.stop>
    <div class="popup-header">
      <span>Psychometric Test Results</span>
      <button class="close-btn" @click="closeModal">×</button>
    </div>
    <div class="psychometric-detailed popup-body">
      <div class="psycho-stats-grid">
        <div class="psycho-stat-card">
          <div class="stat-icon">👤</div>
          <div class="stat-info">
            <h4>Personality Type</h4>
            <div class="stat-value">{{ modalData.personality }}</div>
            <div class="personality-traits">
              <div v-for="trait in modalData.traits" :key="trait" class="trait-tag">
                {{ trait }}
              </div>
            </div>
          </div>
        </div>
        <div class="psycho-stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <h4>Primary Interests</h4>
          </div>
        </div>
        <div class="psycho-stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info"> 
            <h4>Concentration Level</h4>
            <div class="stat-value">{{ modalData.concentration }}/100</div>
          </div>
        </div>
        <div class="psycho-stat-card">
          <div class="stat-icon">🧠</div>
          <div class="stat-info">
            <h4>Memory Strength</h4>
            <div class="stat-value">{{ modalData.memory }}/100</div>
            <div class="memory-types">
              <div v-for="type in modalData.memoryTypes" :key="type.name" class="memory-type">
                <span class="memory-emoji">{{ type.emoji }}</span>
                <span class="memory-name">{{ type.name }}</span>
                <span class="memory-score">{{ type.score }}/100</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="psycho-extra-info" style="margin-top:2rem;">
        <div><strong>Taken At:</strong> {{ modalData.taken_at }}</div>
        <div><strong>Duration:</strong> {{ modalData.duration_seconds }} seconds</div>
        <div v-if="modalData.feedback"><strong>Feedback:</strong> {{ modalData.feedback }}</div>
      </div>
    </div>
  </div>
</div>


<!-- Recent Tasks Modal Component -->
<div v-if="modalComponent === 'recent-tasks-modal'" class="recent-tasks-modal modal-overlay" @click="closeModal">
  <div class="transactions-popup" @click.stop>
    <div class="popup-header">
      <span>Recent Tasks</span>
      <button class="close-btn" @click="closeModal">×</button>
    </div>
    <div class="popup-body">
      <div v-if="!modalData.allTasks || modalData.allTasks.length === 0" class="no-transactions">
        No recent tasks.
      </div>
      <div v-for="task in modalData.allTasks" :key="task.id" class="transaction-item">
        <div class="transaction-date">{{ task.due_date }}</div>
        <div class="transaction-desc">{{ task.title }} ({{ task.subject }})</div>
        <div class="transaction-amount">{{ task.status }}</div>
      </div>
    </div>
  </div>
</div>



    <!-- Header -->
    <header class="dashboard-header">
      <div class="container">
        <div class="header-content">
          <div class="parent-logo">
            <span class="logo-icon">👨‍👩‍👧‍👦</span>
            <div class="logo-text">
              <h1>Parent Dashboard</h1>
              <span class="subtitle">Progress Monitor</span>
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
          <div class="overview-card progress-card" @click="showProgressModal">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <h3>Overall Progress</h3>
              <div class="progress-circle" :style="{ '--progress': overallProgress }">
                <span class="progress-text">{{ overallProgress }}%</span>
              </div>
              <p>{{ overallProgress }}% tasks completed</p>
            </div>
          </div>

          <div class="overview-card screentime-card" @click="showScreenTimeModal">
            <div class="card-icon">📱</div>
            <div class="card-content">
              <h3>Screen Time</h3>
              <div class="screentime-value">{{ screenTimeData.total }}</div>
              <p>{{ screenTimeData.status }}</p>
            </div>
          </div>

          <div class="overview-card achievement-card" @click="showAchievementModal">
            <div class="card-icon">🏆</div>
            <div class="card-content">
              <h3>Today's Achievement</h3>
              <div class="achievement-text">{{ todayAchievement.text }}</div>
              <div class="achievement-amount">{{ todayAchievement.amount }}</div>
            </div>
          </div>

          <div class="overview-card money-card" @click="showFinanceModal">
            <div class="card-icon">💰</div>
            <div class="card-content">
              <h3>Money Saved</h3>
              <div class="money-value">₹{{ financeStats.savings }}</div>
              <p>{{ financeStats.recent.length }} recent transactions</p>
            </div>
          </div>
        </div>

        <!-- Main Features Grid -->
        <div class="main-features-grid">
          <!-- Health Tracker -->
          <div class="feature-card health-card" @click="showHealthModal">
            <div class="card-header">
              <div class="card-icon">❤️</div>
              <h3>Health Tracker</h3>
            </div>
            <div class="card-content">
              <div class="health-grid">
                <div class="health-item">
                  <div class="health-emoji">✅</div>
                  <div class="health-label">Tasks Done</div>
                  <div class="health-value">{{ healthStats.tasks_completed }}/5</div>
                </div>
                <div class="health-item">
                  <div class="health-emoji">💪</div>
                  <div class="health-label">Completed Tasks</div>
                  <div class="health-value stacked-tasks">
                    <span
                      v-for="(task, idx) in healthStats.completedTaskNames"
                      :key="idx"
                      class="completed-task-name"
                    >
                      {{ task }}
                    </span>
                  </div>
                </div>
                <div class="health-item">
                  <div class="health-emoji">💧</div>
                  <div class="health-label">Water</div>
                  <div class="health-value">{{ healthStats.water_today }}/8</div>
                </div>
                <div class="health-item streak-item">
                  <div class="health-emoji">🔥</div>
                  <div class="health-label">Streak</div>
                  <div class="health-value streak-number">{{ healthStats.streak }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Psychometric Test -->
          <div class="feature-card psychometric-card" @click="showPsychometricModal">
            <div class="card-header">
              <div class="card-icon">🧠</div>
              <h3>Psychometric Test</h3>
            </div>
            <div class="card-content">
              <div class="psychometric-grid">
                <div class="psycho-item">
                  <div class="psycho-emoji">👤</div>
                  <div class="psycho-label">Personality</div>
                  <div class="psycho-value">{{ psychometricData.personality }}</div>
                </div>
                <div class="psycho-item">
                  <div class="psycho-emoji">🎯</div>
                  <div class="psycho-label">Interests</div>
                  <div class="psycho-value">{{ psychometricData.interests }}</div>
                </div>
                <div class="psycho-item">
                  <div class="psycho-emoji">🎯</div>
                  <div class="psycho-label">Concentration</div>
                  <div class="psycho-value">{{ psychometricData.concentration }}/100</div>
                </div>
                <div class="psycho-item">
                  <div class="psycho-emoji">🧠</div>
                  <div class="psycho-label">Memory</div>
                  <div class="psycho-value">{{ psychometricData.memory }}/100</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Doodling Sessions -->
          <div class="feature-card doodling-card" @click="showDoodlingModal">
            <div class="card-header">
              <div class="card-icon">🎨</div>
              <h3>Doodling Sessions</h3>
            </div>
            <div class="card-content">
              <div class="doodle-grid">
                <div 
                  v-for="(doodle, idx) in doodleStats.doodles.slice(0, 4)" 
                  :key="idx" 
                  class="doodle-box"
                  @click.stop="viewDoodle(doodle)"
                >
                  <div class="doodle-canvas" :style="{ backgroundColor: doodle.color }">
                    <div class="doodle-preview-content">
                      {{ doodle.emoji || '🎨' }}
                    </div>
                  </div>
                  <div class="doodle-footer">
                    <div class="doodle-name">{{ doodle.title }}</div>
                    <div class="doodle-date">{{ doodle.date }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Task Tracker -->
<div class="feature-card task-card">
  <div class="card-header">
    <div class="card-icon">🎯</div>
    <h3>Task Tracker</h3>
  </div>
  <div class="card-content">
    <div class="task-calendar">
      <div class="calendar-header">
        <span class="calendar-month">{{ getCurrentMonth() }}</span>
      </div>
      <div class="calendar-grid">
        <div 
          v-for="day in taskStats.calendar || []" 
          :key="day.date" 
          class="calendar-day"
          :class="{ 'today': day.isToday, 'has-tasks': day.taskCount > 0 }"
        >
          <div class="day-number">{{ day.day }}</div>
          <div class="day-tasks" v-if="day.taskCount > 0">
            {{ day.completedTasks }}/{{ day.taskCount }}
          </div>
        </div>
      </div>
    </div>
    <div class="recent-tasks">
  <div 
    v-for="task in taskStats.recent || []" 
    :key="task.id" 
    class="recent-task-item"
    @click="showRecentTasksModal"
    style="cursor:pointer;"
  >
    <div class="task-name">{{ task.title }}</div>
    <div class="task-session">{{ task.status }}</div>
  </div>
</div>
  </div>
</div>

          <!-- Emotional Insights -->
          <div class="feature-card emotional-card" @click="showEmotionalModal">
            <div class="card-header">
              <div class="card-icon">💭</div>
              <h3>Emotional Insights</h3>
            </div>
            <div class="card-content">
              <div class="mood-tracker">
                <div class="mood-chart">
                  <div v-for="mood in emotionalInsights.moodTrends" :key="mood.date" class="mood-day">
                    <div class="mood-emoji" :title="mood.feeling">{{ mood.emoji }}</div>
                    <div class="mood-date">{{ mood.date }}</div>
                  </div>
                </div>
              </div>
              <div class="conversation-summary">
                <div class="summary-cards">
                  <div v-for="summary in emotionalInsights.summaries" :key="summary.id" class="summary-card">
                    <div class="summary-topic">{{ summary.topic }}</div>
                    <div class="summary-text">{{ summary.text }}</div>
                    <div class="summary-sentiment" :class="[summary.sentiment, { 'highlighted': summary.sentiment === 'positive' || summary.sentiment === 'neutral' }]">
                      {{ summary.sentiment }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Skill Adventures -->
          <div class="feature-card skills-card" @click="showSkillsModal">
            <div class="card-header">
              <div class="card-icon">🚀</div>
              <h3>Skill Adventures</h3>
            </div>
            <div class="card-content">
              <div class="skills-grid">
                <div v-for="(skill, idx) in skillProgress" :key="idx" class="skill-box">
                  <div class="skill-icon">{{ skill.icon }}</div>
                  <div class="skill-info">
                    <div class="skill-name">{{ skill.name }}</div>
                    <div class="skill-progress-bar">
                      <div class="skill-progress-fill" :style="{ width: skill.progress + '%' }"></div>
                    </div>
                    <div class="skill-progress-text">{{ skill.progress }}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Magic -->
        <div class="floating-magic">
          <div class="magic-element" style="--delay: 0s; --x: 10%; --y: 20%;">🌟</div>
          <div class="magic-element" style="--delay: 2s; --x: 90%; --y: 30%;">⭐</div>
          <div class="magic-element" style="--delay: 4s; --x: 15%; --y: 70%;">💫</div>
          <div class="magic-element" style="--delay: 6s; --x: 85%; --y: 80%;">✨</div>
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


    <!-- Doodling Modal Component -->
    <div v-if="modalComponent === 'doodling-modal'" class="doodling-modal">
      <div class="doodling-detailed">
        <div class="doodle-gallery">
          <div v-for="(doodle, idx) in modalData.allDoodles" :key="idx" class="doodle-gallery-item">
            <div class="doodle-canvas-large" :style="{ backgroundColor: doodle.color }">
              <div class="doodle-artwork">
                {{ doodle.emoji || '🎨' }}
              </div>
            </div>
            <div class="doodle-details">
              <h4>{{ doodle.title }}</h4>
              <p class="doodle-date">{{ doodle.date }}</p>
              <p class="doodle-duration">{{ doodle.duration }} minutes</p>
              <div class="doodle-tags">
                <span v-for="tag in doodle.tags" :key="tag" class="doodle-tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Modal Component -->
    <div v-if="modalComponent === 'task-modal'" class="task-modal">
      <div class="task-detailed">
        <div class="task-calendar-detailed">
          <div class="calendar-navigation">
            <button @click="previousMonth" class="nav-btn">←</button>
            <h3>{{ getCurrentMonthYear() }}</h3>
            <button @click="nextMonth" class="nav-btn">→</button>
          </div>
          <div class="calendar-grid-detailed">
            <div class="calendar-weekdays">
              <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="weekday">
                {{ day }}
              </div>
            </div>
            <div class="calendar-dates">
              <div v-for="date in getDetailedCalendarDays()" :key="date.date" class="calendar-date" :class="{ 'today': date.isToday, 'has-tasks': date.taskCount > 0 }">
                <div class="date-number">{{ date.day }}</div>
                <div class="date-tasks" v-if="date.taskCount > 0">
                  <div class="task-indicator" :class="{ 'completed': date.completedTasks === date.taskCount }">
                    {{ date.completedTasks }}/{{ date.taskCount }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="task-list-detailed">
          <h4>Recent Tasks</h4>
          <div class="task-items">
            <div v-for="task in modalData.allTasks" :key="task.id" class="task-item-detailed">
              <div class="task-status-icon" :class="task.status">
                {{ task.status === 'completed' ? '✅' : task.status === 'in-progress' ? '🔄' : '⏳' }}
              </div>
              <div class="task-info">
                <h5>{{ task.title }}</h5>
                <p class="task-description">{{ task.description }}</p>
                <div class="task-meta">
                  <span class="task-date">{{ task.date }}</span>
                  <span class="task-duration">{{ task.sessionTime }} min</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Emotional Modal Component -->
    <div v-if="modalComponent === 'emotional-modal'" class="emotional-modal">
      <div class="emotional-detailed">
        <div class="mood-analysis">
          <h4>Weekly Mood Analysis</h4>
          <div class="mood-chart-detailed">
            <div v-for="mood in modalData.weeklyMoods" :key="mood.date" class="mood-day-detailed">
              <div class="mood-emoji-large">{{ mood.emoji }}</div>
              <div class="mood-label">{{ mood.feeling }}</div>
              <div class="mood-date">{{ mood.date }}</div>
              <div class="mood-notes">{{ mood.notes }}</div>
            </div>
          </div>
        </div>
        <div class="conversation-analysis">
          <h4>Conversation Insights</h4>
          <div class="conversation-topics">
            <div v-for="topic in modalData.conversationTopics" :key="topic.id" class="topic-card">
              <div class="topic-header">
                <h5>{{ topic.title }}</h5>
                <span class="topic-sentiment" :class="[topic.sentiment, { 'highlighted': topic.sentiment === 'positive' || topic.sentiment === 'neutral' }]">
                  {{ topic.sentiment }}
                </span>
              </div>
              <div class="topic-summary">{{ topic.summary }}</div>
              <div class="topic-keywords">
                <span v-for="keyword in topic.keywords" :key="keyword" class="keyword-tag">{{ keyword }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Skills Modal Component -->
    <div v-if="modalComponent === 'skills-modal'" class="skills-modal">
      <div class="skills-detailed">
        <div class="skills-overview">
          <h4>Skill Development Overview</h4>
          <div class="skills-grid-detailed">
            <div v-for="skill in modalData.allSkills" :key="skill.id" class="skill-card-detailed">
              <div class="skill-icon-large">{{ skill.icon }}</div>
              <div class="skill-info-detailed">
                <h5>{{ skill.name }}</h5>
                <div class="skill-level">Level {{ skill.level }}</div>
                <div class="skill-progress-detailed">
                  <div class="progress-bar-detailed">
                    <div class="progress-fill-detailed" :style="{ width: skill.progress + '%' }"></div>
                  </div>
                  <span class="progress-percentage">{{ skill.progress }}%</span>
                </div>
                <div class="skill-milestones">
                  <div v-for="milestone in skill.milestones" :key="milestone.id" class="milestone" :class="{ 'completed': milestone.completed }">
                    <span class="milestone-icon">{{ milestone.completed ? '✅' : '⏳' }}</span>
                    <span class="milestone-text">{{ milestone.text }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userUtils } from '@/services/api'
import { apiService } from '@/services/api' // adjust path as needed

// Reactive State

const selectedPeriod = ref('daily')
const showModal = ref(false)
const modalTitle = ref('')
const modalComponent = ref('')
const modalData = ref({})

const overallProgress = ref(78)
const screenTimeData = ref({
  total: '3h 45m',
  status: 'Within limits'
})
const todayAchievement = ref({
  text: 'Earned pocket money',
  amount: '₹20'
})
const getCurrentMonth = () => 'July 2025'

const getCurrentMonthYear = () => 'July 2025'

const getCalendarDays = () => [
  { date: '2025-07-01', day: 1, isToday: false, taskCount: 2, completedTasks: 1 },
  { date: '2025-07-02', day: 2, isToday: true, taskCount: 1, completedTasks: 1 },
  // Add more dummy days as needed
]

const getDetailedCalendarDays = () => [
  { date: '2025-07-01', day: 1, isToday: false, taskCount: 2, completedTasks: 1 },
  { date: '2025-07-02', day: 2, isToday: true, taskCount: 1, completedTasks: 1 },
  // Add more dummy days as needed
]

const previousMonth = () => console.log('Previous Month')
const nextMonth = () => console.log('Next Month')
const getStreakDays = () => Array.from({ length: 10 }, (_, i) => i + 1)


const psychometricData = ref({
  personality: '',
  interests: '',
  concentration: 0,
  memory: 0,
  traits: [],
  interestsList: [],
  memoryTypes: []
})

const fetchPsychometricData = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.get(`/api/psychometry/results/${childId.value}`)
    if (res.success && res.result) {
      const r = res.result
      // Map backend fields to frontend structure
      psychometricData.value = {
        personality: r.personality_type || '',
        interests: r.top_interest || '',
        concentration: r.concentration_level || 0,
        memory: r.memory_strength || 0,
        traits: Array.isArray(r.personality_breakdown?.traits) ? r.personality_breakdown.traits : [],
        interestsList: Array.isArray(r.detailed_scores?.interests)
          ? r.detailed_scores.interests.map(i => ({
              name: i.name,
              emoji: i.emoji || '',
              level: i.level || 0
            }))
          : [],
        memoryTypes: Array.isArray(r.detailed_scores?.memory_types)
          ? r.detailed_scores.memory_types.map(m => ({
              name: m.name,
              emoji: m.emoji || '',
              score: m.score || 0
            }))
          : [],
        taken_at: r.taken_at || '',
        duration_seconds: r.duration_seconds || 0,
        feedback: r.feedback || ''
      }
    }
  } catch (e) {
    console.error('Failed to fetch psychometric data', e)
  }
}

const fetchTaskStats = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.getTasksParent(childId.value)
    if (res.success && Array.isArray(res.tasks)) {
      // Prepare calendar stats for last 7 days
      const today = new Date()
      const calendarStats = []
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        const dateStr = date.toISOString().slice(0, 10)
        // Filter tasks for this day
        const dayTasks = res.tasks.filter(t => t.due_date?.slice(0, 10) === dateStr)
        const completedTasks = dayTasks.filter(t => t.status === 'completed').length
        calendarStats.push({
          date: dateStr,
          day: date.getDate(),
          isToday: i === 0,
          taskCount: dayTasks.length,
          completedTasks: completedTasks
        })
      }

      // Get latest 3 pending/in-progress tasks
      const recentTasks = res.tasks
        .filter(t => t.status === 'pending' || t.status === 'in-progress')
        .sort((a, b) => new Date(b.due_date) - new Date(a.due_date))
        .slice(0, 3)
        .map(t => ({
          id: t.id,
          title: t.task,
          status: t.status,
          subject: t.subject,
          due_date: t.due_date
        }))

      taskStats.value = {
        recent: recentTasks,
        calendar: calendarStats
      }
    }
  } catch (e) {
    console.error('Failed to fetch task stats', e)
  }
}

const skillProgress = ref([
  { id: 1, name: 'Math Magic', icon: '🔢', progress: 80, level: 2, milestones: [] },
  { id: 2, name: 'Science Lab', icon: '🔬', progress: 60, level: 1, milestones: [] }
])


const financeStats = ref({ savings: 0, recent: [] })
const childId = ref(null)

// Get the childId for this parent from ParentChild table
const fetchChildId = async () => {
  try {
    const res = await apiService.get('/api/parentchild')
    console.log('apiService.get(/api/parentchild) result:', res)
    const parentId = userUtils.getCurrentUser()?.id
    const link = Array.isArray(res.links) ? res.links.find(l => l.parent_id === parentId) : null
    if (link) childId.value = link.child_id
    console.log('Current parentId:', parentId)
    console.log('Links:', res.links)
  } catch (e) {
    console.error('Failed to fetch childId', e)
  }
}

// Fetch transactions and calculate savings
const fetchFinanceStats = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.getTransactions(childId.value)
    if (res.success) {
      financeStats.value.recent = res.transactions.slice(0, 5)
      financeStats.value.savings = res.transactions.reduce((sum, t) => {
        return sum + (t.type === 'income' ? t.amount : -t.amount)
      }, 0)
    }
  } catch (e) {
    console.error('Failed to fetch transactions', e)
  }
}

onMounted(async () => {
  await fetchChildId()
  if (childId.value) {
    await fetchFinanceStats()
    await fetchHealthStats()
    await fetchPsychometricData()
    await fetchTaskStats()
  }
})

const healthStats = ref({
  streak: 0,
  water_today: 0,
  tasks_completed: 0,
  completedTaskNames: [],
})

const fetchHealthStats = async () => {
  if (!childId.value) return;

  try {
    const tasks = await apiService.getHealthTasks(childId.value);
    const completed = tasks.filter(t => t.completed);
    healthStats.value.tasks_completed = completed.length;
    healthStats.value.completedTaskNames = completed.map(t => t.name);

    healthStats.value.water_today = await apiService.getWaterCount(childId.value);
    healthStats.value.streak = await apiService.getHealthStreak(childId.value);
  } catch (e) {
    console.error('Failed to fetch health stats', e);
  }
};


const doodleStats = ref({
  doodles: [
    { title: 'My Cat', date: '2025-07-03', duration: 10, tags: ['fun'], color: '#aaf', emoji: '🐱' }
  ],
  allDoodles: []
})

const taskStats = ref({
  recent: [],
  calendar: []
})

const emotionalInsights = ref({
  moodTrends: [
    { date: '2025-07-01', emoji: '😊', feeling: 'Happy' }
  ],
  summaries: [
    { id: 1, topic: 'School', text: 'Was happy at school.', sentiment: 'positive' }
  ],
  weeklyMoods: [
    { date: '2025-07-01', emoji: '😊', feeling: 'Happy', notes: 'Good day' }
  ],
  conversationTopics: [
    { id: 1, title: 'Friends', sentiment: 'positive', summary: 'Made new friends', keywords: ['play', 'share'] }
  ]
})

// Methods
const openModal = (title, component, data) => {
  modalTitle.value = title
  modalComponent.value = component
  modalData.value = data
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  modalComponent.value = ''
}

const showProgressModal = () => openModal('Overall Progress', 'progress-modal', { progress: overallProgress.value })
const showScreenTimeModal = () => openModal('Screen Time', 'screentime-modal', screenTimeData.value)
const showAchievementModal = () => openModal('Achievement', 'achievement-modal', todayAchievement.value)
const showFinanceModal = () => openModal('Recent Transactions', 'transactions-modal', financeStats.value)
const showHealthModal = () => openModal('Health', 'health-modal', {...healthStats.value, completedTaskNames: healthStats.value.completedTaskNames});
const showPsychometricModal = () => openModal('Psychometric', 'psychometric-modal', psychometricData.value)
const showDoodlingModal = () => openModal('Doodling', 'doodling-modal', doodleStats.value)
const showTaskModal = () => openModal('Tasks', 'task-modal', taskStats.value)
const showEmotionalModal = () => openModal('Emotions', 'emotional-modal', emotionalInsights.value)
const showSkillsModal = () => openModal('Skills', 'skills-modal', skillProgress.value)
const viewDoodle = (doodle) => openModal('Doodle View', 'doodling-modal', doodle)
const showRecentTasksModal = () => {
  openModal('Recent Tasks', 'recent-tasks-modal', { allTasks: taskStats.value.recent })
}

const logout = () => {
  userUtils.logout()
  console.log('Logged out')
}

const updatePeriod = () => {
  console.log('Period changed:', selectedPeriod.value)
}
const exportData = () => {
  console.log('Exporting data...')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.parent-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #31417A 0%, #667eea 100%);
    position: relative;
    font-family: 'Merriweather', serif;
}

/* Header */
.dashboard-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 1rem 0;
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
}

.parent-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  font-size: 2.5rem;
  animation: sparkle 3s infinite ease-in-out;
}

@keyframes sparkle {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.logo-text h1 {
  font-size: 1.8rem;
  color: #333;
  font-weight: 700;
  margin: 0;
}

.subtitle {
  font-size: 0.9rem;
  color: #666;
  font-weight: 400;
}

/* =========================
   HEADER SECTION
   ========================= */
.dashboard-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.parent-logo {
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

.date-selector select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 0.9rem;
  cursor: pointer;
  backdrop-filter: blur(5px);
}

.date-selector select:focus {
  outline: none;
  border-color: #ffd93d;
}

.export-btn, .logout-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.export-btn:hover, .logout-btn:hover {
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

/* =========================
   MAIN DASHBOARD
   ========================= */
.dashboard-main {
  padding: 30px 0;
}

/* =========================
   OVERVIEW GRID - WARM COMPLEMENTARY COLORS
   ========================= */
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
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.overview-card:nth-child(2) {
  background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
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

/* Progress Card Specific */
.progress-card .progress-circle {
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

.progress-text {
  color: #333;
  font-weight: 700;
  font-size: 1.1rem;
}

/* Screen Time Card */
.screentime-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Achievement Card */
.achievement-text {
  font-size: 1.1rem;
  color: white;
  margin: 10px 0;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.achievement-amount {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Money Card */
.money-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* =========================
   MAIN FEATURES GRID - VIBRANT COMPLEMENTARY COLORS
   ========================= */
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

/* Health Card Specific */
.health-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.health-item {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.health-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.health-emoji {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.health-label {
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 5px;
  display: block;
  font-weight: 500;
}

.health-value {
  color: #333;
  font-weight: 700;
  font-size: 1.1rem;
}

.streak-item {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.streak-item .health-label {
  color: rgba(255, 255, 255, 0.9);
}

.streak-item .health-value {
  color: white;
}

.streak-number {
  font-size: 1.8rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.completed-task-name {
  background-color: rgba(255, 255, 255, 0.2);
  color: #2c2c2c;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  margin: 2px 4px 0 0;
  display: inline-block;
  white-space: nowrap;
}

.stacked-tasks {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 100%;
}

/* Psychometric Card */
.psychometric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.psycho-item {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.psycho-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.psycho-emoji {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.psycho-label {
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 5px;
  display: block;
  font-weight: 500;
}

.psycho-value {
  color: #333;
  font-weight: 700;
  font-size: 1rem;
}

/* Doodling Card */
.doodle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.doodle-box {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.doodle-box:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.doodle-canvas {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 15px 15px 0 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.doodle-preview-content {
  font-size: 2rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.doodle-footer {
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.6);
}

.doodle-name {
  color: #333;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.doodle-date {
  color: #666;
  font-size: 0.8rem;
}

/* Task Card */
.task-calendar {
  margin-bottom: 20px;
}

.calendar-header {
  text-align: center;
  margin-bottom: 15px;
}

.calendar-month {
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-day {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  padding: 10px;
  text-align: center;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.calendar-day:hover {
  background: rgba(255, 255, 255, 0.6);
}

.calendar-day.today {
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
}

.calendar-day.has-tasks {
  border: 2px solid #FF6B6B;
}

.day-number {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.calendar-day.today .day-number {
  color: white;
}

.day-tasks {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 5px;
  padding: 2px 5px;
  font-size: 0.7rem;
  color: #333;
  font-weight: 500;
}

.recent-tasks {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.recent-task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-name {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
}

.task-session {
  color: #666;
  font-size: 0.8rem;
  background: rgba(255, 255, 255, 0.6);
  padding: 5px 10px;
  border-radius: 10px;
  font-weight: 500;
}

/* Emotional Card */
.mood-chart {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.mood-day {
  text-align: center;
  flex: 1;
}

.mood-emoji {
  font-size: 2rem;
  margin-bottom: 5px;
  display: block;
}

.mood-date {
  color: #666;
  font-size: 0.7rem;
  font-weight: 500;
}

.summary-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-card {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.summary-topic {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.summary-text {
  color: #555;
  font-size: 0.8rem;
  margin-bottom: 8px;
}

.summary-sentiment {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.summary-sentiment.positive {
  background: rgba(76, 175, 80, 0.8);
  color: white;
}

.summary-sentiment.neutral {
  background: rgba(255, 193, 61, 0.8);
  color: white;
}

.summary-sentiment.negative {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.summary-sentiment.highlighted {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.transactions-modal.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.psychometric-modal.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-tasks-modal.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.transactions-popup {
  background: #fff;
  border-radius: 18px;
  max-width: 400px;
  width: 90vw;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  padding: 0;
  position: relative;
  animation: fadeIn 0.2s;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem 0.5rem 1.5rem;
  font-size: 1.2rem;
  font-weight: bold;
  color: #31417A;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.7rem;
  color: #31417A;
  cursor: pointer;
  transition: color 0.2s;
}
.close-btn:hover {
  color: #ff5252;
}

.popup-body {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.transaction-list {
  max-height: 300px;
  overflow-y: auto;
}

.transaction-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  padding: 1rem 0;
  border-radius: 10px;
  margin-bottom: 0.5rem;
  border-left: 3px solid transparent;
  background: #f7f8fa;
  color: #31417A;
}

.transaction-item.income {
  background: rgba(76, 175, 80, 0.08);
  color: #388e3c;
  border-left-color: #4CAF50;
}

.transaction-item.expense {
  background: rgba(255, 82, 82, 0.08);
  color: #c62828;
  border-left-color: #ff5252;
}

.transaction-date { opacity: 0.8; font-size: 0.9rem; }
.transaction-desc { font-weight: bold; }
.transaction-amount { font-weight: bold; font-size: 1.1rem; }
.no-transactions { color: #888; text-align: center; padding: 1.5rem 0; }
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.95);}
  to { opacity: 1; transform: scale(1);}
}

/* Skills Card */
.skills-grid {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.skill-box {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.skill-box:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: translateX(5px);
}

.skill-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
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

.skill-info {
  flex: 1;
}

.skill-name {
  color: #333;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 8px;
}

.skill-progress-bar {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 10px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 5px;
}

.skill-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ecdc4, #45b7d1);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.skill-progress-text {
  color: #666;
  font-size: 0.8rem;
  font-weight: 600;
}

/* =========================
   FLOATING MAGIC ANIMATION
   ========================= */
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

/* =========================
   RESPONSIVE DESIGN
   ========================= */
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
  
  .health-grid, .psychometric-grid, .doodle-grid {
    grid-template-columns: 1fr;
  }
  
  .calendar-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .mood-chart {
    flex-wrap: wrap;
    gap: 10px;
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
}

</style>