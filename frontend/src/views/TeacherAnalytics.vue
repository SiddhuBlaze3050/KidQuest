<template>
  <div class="teacher-analytics">
    <!-- Header -->
    <header class="analytics-header">
      <div class="container">
        <div class="header-content">
          <div class="analytics-logo">
            <span class="logo-icon">📊</span>
            <div class="logo-text">
              <h1>Class Analytics</h1>
              <span class="subtitle">Comprehensive insights for {{ currentUser?.username || 'Teacher' }}</span>
            </div>
          </div>
          <div class="header-actions">
            <button @click="goBackToDashboard" class="back-btn">
              <i class="fas fa-arrow-left"></i>
              Back to Dashboard
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
    <main class="analytics-main">
      <div class="container">
        <!-- Overview Analytics -->
        <div class="analytics-overview">
          <div class="overview-card">
            <div class="card-icon">📝</div>
            <div class="card-content">
              <h3>Total Tasks</h3>
              <div class="metric-value">{{ totalStudentTasks }}</div>
              <p>Tasks created by all students</p>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon">✅</div>
            <div class="card-content">
              <h3>Completed Tasks</h3>
              <div class="metric-value">{{ completedTasks }}</div>
              <p>Successfully finished tasks</p>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon">⏳</div>
            <div class="card-content">
              <h3>Pending Tasks</h3>
              <div class="metric-value">{{ pendingTasks }}</div>
              <p>Tasks still in progress</p>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon">📚</div>
            <div class="card-content">
              <h3>Assigned Homework</h3>
              <div class="metric-value">{{ assignedHomework.length }}</div>
              <p>Homework assignments given</p>
            </div>
          </div>
        </div>

        <!-- Detailed Analytics -->
        <div class="detailed-analytics">
          <!-- Task Status Distribution -->
          <div class="analytics-card">
            <div class="card-header">
              <div class="card-icon">📊</div>
              <h3>Task Status Distribution</h3>
            </div>
            <div class="card-content">
              <div class="status-chart">
                <div class="status-item">
                  <div class="status-bar">
                    <div class="bar-fill completed" :style="{ width: completionPercentage + '%' }"></div>
                  </div>
                  <div class="status-info">
                    <span class="status-label">Completed</span>
                    <span class="status-value">{{ completedTasks }} ({{ completionPercentage }}%)</span>
                  </div>
                </div>
                <div class="status-item">
                  <div class="status-bar">
                    <div class="bar-fill in-progress" :style="{ width: inProgressPercentage + '%' }"></div>
                  </div>
                  <div class="status-info">
                    <span class="status-label">In Progress</span>
                    <span class="status-value">{{ inProgressTasks }} ({{ inProgressPercentage }}%)</span>
                  </div>
                </div>
                <div class="status-item">
                  <div class="status-bar">
                    <div class="bar-fill pending" :style="{ width: pendingPercentage + '%' }"></div>
                  </div>
                  <div class="status-info">
                    <span class="status-label">Pending</span>
                    <span class="status-value">{{ pendingTasks }} ({{ pendingPercentage }}%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Student Performance -->
          <div class="analytics-card">
            <div class="card-header">
              <div class="card-icon">👥</div>
              <h3>Student Performance Overview</h3>
            </div>
            <div class="card-content">
              <div class="performance-list">
                <div v-for="student in myStudents" :key="student.id" class="performance-item">
                  <div class="student-info">
                    <div class="student-avatar">👨‍🎓</div>
                    <div class="student-details">
                      <div class="student-name">{{ student.username }}</div>
                      <div class="student-email">{{ student.email }}</div>
                    </div>
                  </div>
                  <div class="performance-metrics">
                    <div class="metric">
                      <span class="metric-label">Tasks</span>
                      <span class="metric-value">{{ getStudentTaskCount(student.id) }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">Completed</span>
                      <span class="metric-value">{{ getStudentCompletedTasks(student.id) }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">Progress</span>
                      <span class="metric-value">{{ getStudentProgress(student.id) }}%</span>
                    </div>
                  </div>
                  <div class="progress-visual">
                    <div class="progress-circle" :style="{ background: `conic-gradient(#4CAF50 ${getStudentProgress(student.id) * 3.6}deg, #e0e0e0 0deg)` }">
                      <div class="progress-inner">{{ getStudentProgress(student.id) }}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Subject Distribution -->
          <div class="analytics-card">
            <div class="card-header">
              <div class="card-icon">📖</div>
              <h3>Subject-wise Task Distribution</h3>
            </div>
            <div class="card-content">
              <div class="subject-stats">
                <div v-for="subject in subjectStats" :key="subject.name" class="subject-item">
                  <div class="subject-info">
                    <div class="subject-name">{{ subject.name }}</div>
                    <div class="subject-count">{{ subject.count }} tasks</div>
                  </div>
                  <div class="subject-bar">
                    <div class="subject-fill" :style="{ width: (subject.count / maxSubjectCount * 100) + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>Loading analytics...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService'
import { apiService } from '@/services/api'

export default {
  name: 'TeacherAnalytics',
  setup() {
    const router = useRouter()
    
    // Reactive data
    const currentUser = ref(authService.getCurrentUser())
    const isLoading = ref(true)
    const myStudents = ref([])
    const studentTasks = ref([])
    const assignedHomework = ref([])

    // Computed properties
    const totalStudentTasks = computed(() => studentTasks.value.length)
    const completedTasks = computed(() => studentTasks.value.filter(task => task.status === 'completed').length)
    const pendingTasks = computed(() => studentTasks.value.filter(task => task.status === 'pending').length)
    const inProgressTasks = computed(() => studentTasks.value.filter(task => task.status === 'in-progress').length)

    const completionPercentage = computed(() => {
      if (totalStudentTasks.value === 0) return 0
      return Math.round((completedTasks.value / totalStudentTasks.value) * 100)
    })

    const pendingPercentage = computed(() => {
      if (totalStudentTasks.value === 0) return 0
      return Math.round((pendingTasks.value / totalStudentTasks.value) * 100)
    })

    const inProgressPercentage = computed(() => {
      if (totalStudentTasks.value === 0) return 0
      return Math.round((inProgressTasks.value / totalStudentTasks.value) * 100)
    })

    const subjectStats = computed(() => {
      const subjects = {}
      studentTasks.value.forEach(task => {
        const subject = task.subject || 'Other'
        subjects[subject] = (subjects[subject] || 0) + 1
      })
      return Object.entries(subjects).map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count)
    })

    const maxSubjectCount = computed(() => {
      return Math.max(...subjectStats.value.map(s => s.count), 1)
    })

    // Methods
    const logout = () => {
      authService.logout()
      router.push('/')
    }

    const goBackToDashboard = () => {
      router.push('/teacher-dashboard')
    }

    const loadMyStudents = async () => {
      try {
        console.log('🔄 Loading students for teacher:', currentUser.value.id);
        const response = await apiService.getTeacherStudents(currentUser.value.id)
        console.log('📥 Students response:', response);
        if (response.success) {
          myStudents.value = response.students
          console.log('✅ Students loaded:', myStudents.value.length);
        } else {
          console.error('❌ Failed to load students:', response.error);
          myStudents.value = []
        }
      } catch (error) {
        console.error('❌ Error loading students:', error);
        myStudents.value = []
      }
    }

    const loadStudentTasks = async () => {
      try {
        console.log('🔄 Loading student tasks for teacher:', currentUser.value.id);
        // Use the teacher-specific endpoint instead of individual student endpoints
        const response = await apiService.getStudentTasksForTeacher(currentUser.value.id)
        console.log('📥 Student tasks response:', response);
        
        if (response.success) {
          studentTasks.value = response.tasks
          console.log('✅ Total student tasks loaded:', response.tasks.length);
        } else {
          console.error('❌ Failed to load student tasks:', response.error);
          studentTasks.value = []
        }
      } catch (error) {
        console.error('❌ Error loading student tasks:', error);
        studentTasks.value = []
      }
    }

    const loadAssignedHomework = async () => {
      try {
        console.log('🔄 Loading assigned homework for teacher:', currentUser.value.id);
        const response = await apiService.getTeacherHomework(currentUser.value.id)
        console.log('📥 Homework response:', response);
        if (response.success) {
          assignedHomework.value = response.homework
          console.log('✅ Assigned homework loaded:', assignedHomework.value.length);
        } else {
          console.error('❌ Failed to load homework:', response.error);
          assignedHomework.value = []
        }
      } catch (error) {
        console.error('❌ Error loading homework:', error);
        assignedHomework.value = []
      }
    }

    const getStudentTaskCount = (studentId) => {
      return studentTasks.value.filter(task => task.user_id === studentId).length
    }

    const getStudentCompletedTasks = (studentId) => {
      return studentTasks.value.filter(task => task.user_id === studentId && task.status === 'completed').length
    }

    const getStudentProgress = (studentId) => {
      const tasks = studentTasks.value.filter(task => task.user_id === studentId)
      if (tasks.length === 0) return 0
      const completed = tasks.filter(task => task.status === 'completed').length
      return Math.round((completed / tasks.length) * 100)
    }

    // Initialize analytics
    onMounted(async () => {
      try {
        console.log('🚀 Initializing Teacher Analytics for user:', currentUser.value);
        // Add a small delay to ensure token is properly set after login
        await new Promise(resolve => setTimeout(resolve, 100))
        
        console.log('📝 Step 1: Loading students...');
        await loadMyStudents()
        console.log('📝 Step 2: Loading student tasks...');
        await loadStudentTasks()
        console.log('📝 Step 3: Loading assigned homework...');
        await loadAssignedHomework()
        console.log('✅ Analytics initialization complete');
      } catch (error) {
        console.error('❌ Error initializing analytics:', error)
      } finally {
        isLoading.value = false
      }
    })

    return {
      // Data
      currentUser,
      isLoading,
      myStudents,
      studentTasks,
      assignedHomework,
      
      // Computed
      totalStudentTasks,
      completedTasks,
      pendingTasks,
      inProgressTasks,
      completionPercentage,
      pendingPercentage,
      inProgressPercentage,
      subjectStats,
      maxSubjectCount,
      
      // Methods
      logout,
      goBackToDashboard,
      getStudentTaskCount,
      getStudentCompletedTasks,
      getStudentProgress
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.teacher-analytics {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  font-family: 'Merriweather', serif;
}

/* Header Styles */
.analytics-header {
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

.analytics-logo {
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

.back-btn {
  background: rgba(33, 150, 243, 0.2);
  border: 1px solid rgba(33, 150, 243, 0.3);
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

.back-btn:hover {
  background: rgba(33, 150, 243, 0.3);
  transform: translateY(-2px);
}

.logout-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.3);
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

.logout-btn:hover {
  background: rgba(255, 107, 107, 0.3);
  transform: translateY(-2px);
}

/* Main Analytics */
.analytics-main {
  padding: 30px 0;
}

/* Overview Analytics */
.analytics-overview {
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
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
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

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Detailed Analytics */
.detailed-analytics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.analytics-card {
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
}

.analytics-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
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
  margin-right: 15px;
}

.card-header h3 {
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
}

/* Status Chart */
.status-chart {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.status-bar {
  flex: 1;
  height: 25px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: 12px;
  transition: width 0.8s ease;
}

.bar-fill.completed {
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
}

.bar-fill.in-progress {
  background: linear-gradient(90deg, #2196F3, #03DAC6);
}

.bar-fill.pending {
  background: linear-gradient(90deg, #FF9800, #FFC107);
}

.status-info {
  min-width: 200px;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.status-label {
  font-weight: 600;
  color: white;
  font-size: 0.9rem;
}

.status-value {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.8rem;
}

/* Performance List */
.performance-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.performance-item {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
}

.performance-item:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(5px);
}

.student-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.student-avatar {
  font-size: 2rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  padding: 12px;
  min-width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.student-details {
  flex: 1;
}

.student-name {
  font-weight: 600;
  color: white;
  font-size: 1rem;
  margin-bottom: 4px;
}

.student-email {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.performance-metrics {
  display: flex;
  gap: 20px;
  align-items: center;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
}

.progress-visual {
  display: flex;
  align-items: center;
}

.progress-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.progress-inner {
  background: white;
  border-radius: 50%;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
  color: #333;
}

/* Subject Stats */
.subject-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.subject-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.subject-info {
  min-width: 150px;
}

.subject-name {
  font-weight: 600;
  color: white;
  font-size: 0.9rem;
}

.subject-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.subject-bar {
  flex: 1;
  height: 20px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  overflow: hidden;
}

.subject-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 10px;
  transition: width 0.8s ease;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(102, 126, 234, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  backdrop-filter: blur(10px);
}

.loading-content {
  text-align: center;
  color: white;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-content p {
  font-size: 1.1rem;
  font-weight: 600;
}

/* Responsive Design */
@media (max-width: 768px) {
  .analytics-overview {
    grid-template-columns: 1fr;
  }
  
  .performance-item {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .performance-metrics {
    flex-direction: row;
    justify-content: space-around;
    width: 100%;
  }
  
  .status-item {
    flex-direction: column;
    gap: 10px;
  }
  
  .status-info {
    align-items: center;
  }
}

@media (max-width: 480px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .subject-item {
    flex-direction: column;
    gap: 8px;
  }
  
  .subject-info {
    text-align: center;
    min-width: auto;
  }
}
</style>
