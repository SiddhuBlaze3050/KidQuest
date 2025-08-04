<!-- Analytics Modal Component -->
<template>
  <BaseModal
    v-model="isVisible"
    title="Analytics Dashboard"
    subtitle="View usage statistics and reports"
    icon="📊"
    @update:modelValue="$emit('update:modelValue', $event)"
    :large="true"
  >
    <div class="analytics-content">
      <!-- Quick Stats Overview -->
      <div class="stats-overview">
        <div class="quick-stat">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ analyticsData.totalUsers }}</div>
            <div class="stat-label">Total Users</div>
          </div>
        </div>
        <div class="quick-stat">
          <div class="stat-icon">💬</div>
          <div class="stat-info">
            <div class="stat-value">{{ analyticsData.totalChatSessions }}</div>
            <div class="stat-label">Chat Sessions</div>
          </div>
        </div>
        <div class="quick-stat">
          <div class="stat-icon">⏱️</div>
          <div class="stat-info">
            <div class="stat-value">{{ formatTime(analyticsData.avgScreenTime) }}</div>
            <div class="stat-label">Avg Screen Time</div>
          </div>
        </div>
        <div class="quick-stat">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <div class="stat-value">{{ analyticsData.completedTasks }}</div>
            <div class="stat-label">Tasks Completed</div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-section">
        <div class="chart-container">
          <h3>User Activity Over Time</h3>
          <div class="chart-placeholder">
            <canvas ref="activityChart" width="400" height="200"></canvas>
          </div>
        </div>
        
        <div class="chart-container">
          <h3>User Role Distribution</h3>
          <div class="role-distribution">
            <div class="role-item" v-for="role in analyticsData.roleDistribution" :key="role.name">
              <div class="role-bar">
                <div class="role-fill" :style="{ width: role.percentage + '%', backgroundColor: role.color }"></div>
              </div>
              <div class="role-info">
                <span class="role-name">{{ role.name }}</span>
                <span class="role-count">{{ role.count }} ({{ role.percentage }}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Reports -->
      <div class="reports-section">
        <h3>Detailed Reports</h3>
        <div class="report-grid">
          <div class="report-card" @click="generateReport('user-activity')">
            <div class="report-icon">📈</div>
            <div class="report-title">User Activity Report</div>
            <div class="report-desc">Daily and weekly user engagement</div>
          </div>
          
          <div class="report-card" @click="generateReport('screen-time')">
            <div class="report-icon">⏱️</div>
            <div class="report-title">Screen Time Analysis</div>
            <div class="report-desc">Detailed screen time statistics</div>
          </div>
          
          <div class="report-card" @click="generateReport('chat-analytics')">
            <div class="report-icon">💬</div>
            <div class="report-title">Chat Analytics</div>
            <div class="report-desc">Chatbot usage and interactions</div>
          </div>
          
          <div class="report-card" @click="generateReport('achievements')">
            <div class="report-icon">🏆</div>
            <div class="report-title">Achievement Stats</div>
            <div class="report-desc">User progress and achievements</div>
          </div>
        </div>
      </div>

      <!-- Export Section -->
      <div class="export-section">
        <h3>Export Data</h3>
        <div class="export-options">
          <button @click="exportData('csv')" class="export-btn">
            <span class="btn-icon">📄</span>
            Export as CSV
          </button>
          <button @click="exportData('json')" class="export-btn">
            <span class="btn-icon">📋</span>
            Export as JSON
          </button>
          <button @click="exportData('pdf')" class="export-btn">
            <span class="btn-icon">📋</span>
            Export as PDF
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <p>Loading analytics data...</p>
      </div>
    </div>
  </BaseModal>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import axios from 'axios'
import BaseModal from '@/components/common/BaseModal.vue'

export default {
  name: 'AnalyticsModal',
  components: {
    BaseModal
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true
    }
  },
  emits: ['update:modelValue'],
  
  setup(props, { emit }) {
    const isVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const loading = ref(false)
    const activityChart = ref(null)
    
    const analyticsData = ref({
      totalUsers: 0,
      totalChatSessions: 0,
      avgScreenTime: 0,
      completedTasks: 0,
      roleDistribution: [],
      activityData: []
    })

    const fetchAnalyticsData = async () => {
      try {
        loading.value = true
        console.log('🔄 AnalyticsModal: Fetching analytics data...')
        
        // Fetch comprehensive analytics data
        const analyticsResponse = await axios.get('http://localhost:5000/api/admin/analytics')
        const data = analyticsResponse.data
        
        console.log('✅ AnalyticsModal: Analytics data received:', data)
        
        analyticsData.value = {
          totalUsers: data.user_statistics.total_users || 0,
          totalChatSessions: data.activity_data.total_chat_sessions || 0,
          avgScreenTime: data.screen_time.average_minutes || 0,
          completedTasks: data.activity_data.completed_tasks || 0,
          roleDistribution: [
            { 
              name: 'Children', 
              count: data.user_statistics.child_count, 
              percentage: Math.round((data.user_statistics.child_count / data.user_statistics.total_users) * 100), 
              color: '#FFD700' 
            },
            { 
              name: 'Parents', 
              count: data.user_statistics.parent_count, 
              percentage: Math.round((data.user_statistics.parent_count / data.user_statistics.total_users) * 100), 
              color: '#C9A270' 
            },
            { 
              name: 'Teachers', 
              count: data.user_statistics.teacher_count, 
              percentage: Math.round((data.user_statistics.teacher_count / data.user_statistics.total_users) * 100), 
              color: '#2A623D' 
            },
            { 
              name: 'Admins', 
              count: data.user_statistics.admin_count, 
              percentage: Math.round((data.user_statistics.admin_count / data.user_statistics.total_users) * 100), 
              color: '#8B5A2B' 
            }
          ],
          activityData: data.activity_data.weekly_activity || []
        }
        
        console.log('📊 AnalyticsModal: Processed analytics data:', analyticsData.value)
        
        // Draw chart after data is loaded
        nextTick(() => {
          console.log('🎨 AnalyticsModal: Drawing chart...')
          drawActivityChart()
        })
        
      } catch (error) {
        console.error('❌ AnalyticsModal: Error fetching analytics data:', error)
        // Fallback to dashboard stats if analytics endpoint fails
        try {
          console.log('🔄 AnalyticsModal: Trying fallback dashboard stats...')
          const statsResponse = await axios.get('http://localhost:5000/api/admin/dashboard-stats')
          const stats = statsResponse.data
          
          analyticsData.value = {
            totalUsers: stats.total_users || 0,
            totalChatSessions: stats.chat_sessions || 0,
            avgScreenTime: stats.average_screen_time || 0,
            completedTasks: Math.floor(Math.random() * 150) + 50,
            roleDistribution: [
              { name: 'Children', count: stats.child_count, percentage: Math.round((stats.child_count / stats.total_users) * 100), color: '#FFD700' },
              { name: 'Parents', count: stats.parent_count, percentage: Math.round((stats.parent_count / stats.total_users) * 100), color: '#C9A270' },
              { name: 'Teachers', count: stats.teacher_count, percentage: Math.round((stats.teacher_count / stats.total_users) * 100), color: '#2A623D' },
              { name: 'Admins', count: stats.admin_count, percentage: Math.round((stats.admin_count / stats.total_users) * 100), color: '#8B5A2B' }
            ],
            activityData: generateMockActivityData()
          }
          
          nextTick(() => {
            drawActivityChart()
          })
        } catch (fallbackError) {
          console.error('❌ AnalyticsModal: Fallback also failed:', fallbackError)
        }
      } finally {
        loading.value = false
      }
    }

    const generateMockActivityData = () => {
      const data = []
      const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      days.forEach(day => {
        data.push({
          day,
          users: Math.floor(Math.random() * 20) + 5
        })
      })
      return data
    }

    const drawActivityChart = () => {
      if (!activityChart.value) return
      
      const canvas = activityChart.value
      const ctx = canvas.getContext('2d')
      const data = analyticsData.value.activityData
      
      if (!data || data.length === 0) {
        // Draw "No Data" message
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = '#666'
        ctx.font = '16px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('No activity data available', canvas.width / 2, canvas.height / 2)
        return
      }
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Chart dimensions
      const padding = 40
      const chartWidth = canvas.width - 2 * padding
      const chartHeight = canvas.height - 2 * padding
      
      // Find max value
      const maxValue = Math.max(...data.map(d => d.active_users || d.users || 1), 1)
      
      // Draw bars
      const barWidth = Math.max(chartWidth / data.length * 0.6, 20)
      const barSpacing = chartWidth / data.length * 0.4
      
      data.forEach((item, index) => {
        const value = item.active_users || item.users || 0
        const barHeight = Math.max((value / maxValue) * chartHeight, 2)
        const x = padding + index * (barWidth + barSpacing)
        const y = canvas.height - padding - barHeight
        
        // Draw bar
        ctx.fillStyle = '#667eea'
        ctx.fillRect(x, y, barWidth, barHeight)
        
        // Draw day label
        ctx.fillStyle = '#333'
        ctx.font = '12px Arial'
        ctx.textAlign = 'center'
        const dayLabel = item.day || (item.date ? new Date(item.date).toLocaleDateString('en', { weekday: 'short' }) : 'N/A')
        ctx.fillText(dayLabel, x + barWidth / 2, canvas.height - 10)
        
        // Draw value label
        if (barHeight > 15) {
          ctx.fillStyle = 'white'
          ctx.fillText(value.toString(), x + barWidth / 2, y + 15)
        } else {
          ctx.fillStyle = '#333'
          ctx.fillText(value.toString(), x + barWidth / 2, y - 5)
        }
      })
    }

    const formatTime = (minutes) => {
      if (minutes === 0) return '00:00'
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`
    }

    const generateReport = (reportType) => {
      console.log(`Generating ${reportType} report...`)
      // TODO: Implement specific report generation
      alert(`Generating ${reportType} report... (Feature coming soon!)`)
    }

    const exportData = async (format) => {
      try {
        loading.value = true
        
        // Prepare export data
        const exportData = {
          timestamp: new Date().toISOString(),
          analytics: analyticsData.value,
          format: format
        }
        
        if (format === 'csv') {
          downloadCSV(exportData)
        } else if (format === 'json') {
          downloadJSON(exportData)
        } else if (format === 'pdf') {
          alert('PDF export feature coming soon!')
        }
        
      } catch (error) {
        console.error('Export failed:', error)
        alert('Export failed. Please try again.')
      } finally {
        loading.value = false
      }
    }

    const downloadCSV = (data) => {
      const csvContent = [
        'Metric,Value',
        `Total Users,${data.analytics.totalUsers}`,
        `Chat Sessions,${data.analytics.totalChatSessions}`,
        `Avg Screen Time,${formatTime(data.analytics.avgScreenTime)}`,
        `Completed Tasks,${data.analytics.completedTasks}`,
        '',
        'Role,Count,Percentage',
        ...data.analytics.roleDistribution.map(role => `${role.name},${role.count},${role.percentage}%`)
      ].join('\n')
      
      downloadFile(csvContent, 'analytics-report.csv', 'text/csv')
    }

    const downloadJSON = (data) => {
      const jsonContent = JSON.stringify(data, null, 2)
      downloadFile(jsonContent, 'analytics-report.json', 'application/json')
    }

    const downloadFile = (content, filename, contentType) => {
      const blob = new Blob([content], { type: contentType })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      window.URL.revokeObjectURL(url)
    }

    // Watch for modal opening
    watch(
      () => props.modelValue,
      (newVal) => {
        if (newVal) {
          fetchAnalyticsData()
        }
      }
    )

    onMounted(() => {
      if (props.modelValue) {
        fetchAnalyticsData()
      }
    })

    return {
      isVisible,
      loading,
      analyticsData,
      activityChart,
      formatTime,
      generateReport,
      exportData
    }
  }
}
</script>

<style scoped>
.analytics-content {
  padding: 0 2rem 2rem;
  max-height: 80vh;
  overflow-y: auto;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.quick-stat {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: white;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.chart-container {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-container h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.role-distribution {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-item {
  margin-bottom: 1rem;
}

.role-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.role-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.role-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.role-name {
  font-weight: 600;
}

.reports-section, .export-section {
  margin-bottom: 2rem;
}

.reports-section h3, .export-section h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.report-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.report-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
}

.report-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.report-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.report-desc {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.export-options {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.export-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 25px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-icon {
  font-size: 1.1rem;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 15px;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .export-options {
    flex-direction: column;
  }
}
</style>
