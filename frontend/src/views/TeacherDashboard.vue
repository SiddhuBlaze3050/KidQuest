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
              <span class="subtitle">Welcome, {{ currentUser?.username || 'Teacher' }}</span>
            </div>
          </div>
          <div class="header-actions">
            <button @click="goToAnalytics" class="analytics-btn">
              <i class="fas fa-chart-bar"></i>
              Analytics
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
        <div class="overview-grid">
          <div class="overview-card students-card">
            <div class="card-icon">👥</div>
            <div class="card-content">
              <h3>My Students</h3>
              <div class="students-count">{{ myStudents.length }}</div>
              <p>Active students under your guidance</p>
            </div>
          </div>

          <div class="overview-card tasks-card">
            <div class="card-icon">📝</div>
            <div class="card-content">
              <h3>Student Tasks</h3>
              <div class="tasks-count">{{ totalStudentTasks }}</div>
              <p>Tasks created by students</p>
            </div>
          </div>

          <div class="overview-card homework-card">
            <div class="card-icon">📚</div>
            <div class="card-content">
              <h3>Assigned Homework</h3>
              <div class="homework-count">{{ assignedHomework.length }}</div>
              <p>Homework you've assigned</p>
            </div>
          </div>

          <div class="overview-card completion-card">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <h3>Completion Rate</h3>
              <div class="completion-rate">{{ calculateCompletionRate() }}%</div>
              <p>Overall student progress</p>
            </div>
          </div>
        </div>

        <!-- Second Row: Student Task Tracker and Student Progress -->
        <div class="second-row-grid">
          <!-- Student Task Tracker -->
          <div class="feature-card task-tracker-card">
            <div class="card-header">
              <div class="card-icon">🎯</div>
              <h3>Student Task Tracker</h3>
              <div class="refresh-btn" @click="loadStudentTasks">
                <i class="fas fa-sync-alt"></i>
              </div>
            </div>
            <div class="card-content">
              <div class="task-filters">
                <select v-model="selectedStudent" @change="filterTasks" :disabled="myStudents.length === 0">
                  <option value="">All Students</option>
                  <option v-for="student in myStudents" :key="student.id" :value="student.id">
                    {{ student.username }}
                  </option>
                </select>
                <select v-model="selectedStatus" @change="filterTasks" :disabled="filteredStudentTasks.length === 0">
                  <option value="">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="in-progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>
              <div class="task-list">
                <div v-if="myStudents.length === 0" class="no-tasks">
                  <div class="no-data-icon">👥</div>
                  <p>No students assigned</p>
                  <small>You need students assigned to your class before you can track their tasks</small>
                </div>
                <div v-else-if="filteredStudentTasks.length === 0 && studentTasks.length === 0" class="no-tasks">
                  <div class="no-data-icon">📝</div>
                  <p>No tasks created yet</p>
                  <small>Student tasks will appear here once they start creating tasks</small>
                </div>
                <div v-else-if="filteredStudentTasks.length === 0" class="no-tasks">
                  <div class="no-data-icon">🔍</div>
                  <p>No tasks found for the selected filters</p>
                  <small>Try adjusting your filters to see more tasks</small>
                </div>
                <div v-for="task in filteredStudentTasks" :key="task.id" class="task-item">
                  <div class="task-info">
                    <div class="task-title">{{ task.task }}</div>
                    <div class="task-details">
                      <span class="student-name">{{ getStudentName(task.user_id) }}</span>
                      <span class="task-subject">{{ task.subject }}</span>
                      <span class="task-due">Due: {{ formatDate(task.due_date) }}</span>
                    </div>
                  </div>
                  <div class="task-status">
                    <span class="status-badge" :class="task.status">{{ task.status }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Student Progress Overview -->
          <div class="feature-card progress-card">
            <div class="card-header">
              <div class="card-icon">📈</div>
              <h3>Student Progress</h3>
            </div>
            <div class="card-content">
              <div class="progress-list">
                <div v-if="myStudents.length === 0" class="no-students">
                  <div class="no-data-icon">👥</div>
                  <p>No students assigned to you yet</p>
                  <small>Students will appear here once they are assigned to your class</small>
                </div>
                <div v-for="student in myStudents" :key="student.id" class="progress-item">
                  <div class="student-info">
                    <div class="student-avatar">👨‍🎓</div>
                    <div class="student-details">
                      <div class="student-name">{{ student.username }}</div>
                      <div class="student-email">{{ student.email }}</div>
                    </div>
                  </div>
                  <div class="progress-stats">
                    <div class="task-count">{{ getStudentTaskCount(student.id) }} tasks</div>
                    <div class="completion-progress">
                      <div class="progress-bar">
                        <div class="progress-fill" :style="{ width: getStudentProgress(student.id) + '%' }"></div>
                      </div>
                      <span class="progress-text">{{ getStudentProgress(student.id) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Third Row: Homework Assignment (Full Width) -->
        <div class="third-row-grid">
          <!-- Homework Assignment -->
          <div class="feature-card homework-card full-width">
            <div class="card-header">
              <div class="card-icon">✏️</div>
              <h3>Assign Homework</h3>
              <div class="header-actions">
                <button @click="showAssignHomeworkModal = true" class="assign-btn" :disabled="myStudents.length === 0">
                  <i class="fas fa-plus"></i>
                  Assign
                </button>
                <button @click="showRemoveHomeworkModal = true" class="remove-btn" :disabled="assignedHomework.length === 0">
                  <i class="fas fa-trash"></i>
                  Remove
                </button>
              </div>
            </div>
            <div class="card-content">
              <div class="homework-list">
                <div v-if="myStudents.length === 0" class="no-homework">
                  <div class="no-data-icon">👥</div>
                  <p>No students to assign homework to</p>
                  <small>Students need to be assigned to your class first</small>
                </div>
                <div v-else-if="assignedHomework.length === 0" class="no-homework">
                  <div class="no-data-icon">📚</div>
                  <p>No homework assigned yet</p>
                  <small>Click the "Assign" button to create homework for your students</small>
                </div>
                <div v-for="homework in assignedHomework" :key="homework.id" class="homework-item">
                  <div class="homework-info">
                    <div class="homework-title">{{ homework.task }}</div>
                    <div class="homework-details">
                      <span class="homework-subject">{{ homework.subject }}</span>
                      <span class="homework-due">Due: {{ formatDate(homework.due_date) }}</span>
                      <span class="assigned-to">Assigned to: {{ getAssignedStudentsNames(homework.assigned_to) }}</span>
                    </div>
                  </div>
                  <div class="homework-actions">
                    <button @click="editHomework(homework)" class="edit-btn">
                      <i class="fas fa-edit"></i>
                    </button>
                    <button @click="deleteHomework(homework.id)" class="delete-btn">
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Assign Homework Modal -->
    <div v-if="showAssignHomeworkModal" class="modal-overlay" @click="closeAssignHomeworkModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Assign Homework</h3>
          <button @click="closeAssignHomeworkModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="assignHomework" class="homework-form">
            <div class="form-group">
              <label for="subject">Subject</label>
              <input 
                id="subject" 
                v-model="newHomework.subject" 
                type="text" 
                placeholder="e.g., Mathematics" 
                required 
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="task">Task Description</label>
              <textarea 
                id="task" 
                v-model="newHomework.task" 
                placeholder="Describe the homework task..." 
                required 
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="dueDate">Due Date</label>
              <input 
                id="dueDate" 
                v-model="newHomework.due_date" 
                type="date" 
                required 
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label>Assign to Students</label>
              <div v-if="myStudents.length === 0" class="no-students-message">
                <p>No students available to assign homework to.</p>
                <small>Students need to be assigned to your class first.</small>
              </div>
              <div v-else class="student-checkboxes">
                <div v-for="student in myStudents" :key="student.id" class="checkbox-item">
                  <input 
                    :id="'student-' + student.id" 
                    v-model="newHomework.assigned_to" 
                    :value="student.id" 
                    type="checkbox" 
                    class="checkbox"
                  />
                  <label :for="'student-' + student.id" class="checkbox-label">
                    {{ student.username }}
                  </label>
                </div>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeAssignHomeworkModal" class="btn-cancel">
                Cancel
              </button>
              <button type="submit" class="btn-assign" :disabled="isAssigning">
                <span v-if="!isAssigning">Assign Homework</span>
                <span v-else>Assigning...</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Remove Homework Modal -->
    <div v-if="showRemoveHomeworkModal" class="modal-overlay" @click="closeRemoveHomeworkModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Remove Assigned Homework</h3>
          <button @click="closeRemoveHomeworkModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="assignedHomework.length === 0" class="no-homework-message">
            <p>No homework assigned yet.</p>
            <small>There's no homework to remove.</small>
          </div>
          <div v-else class="homework-removal-list">
            <p class="removal-instruction">Select the homework you want to remove:</p>
            <div class="homework-checkboxes">
              <div v-for="homework in assignedHomework" :key="homework.id" class="checkbox-item homework-checkbox">
                <input 
                  :id="'homework-' + homework.id" 
                  v-model="homeworkToRemove" 
                  :value="homework.id" 
                  type="checkbox" 
                  class="checkbox"
                />
                <label :for="'homework-' + homework.id" class="checkbox-label homework-label">
                  <div class="homework-info">
                    <div class="homework-title">{{ homework.task }}</div>
                    <div class="homework-details">
                      <span class="homework-subject">{{ homework.subject }}</span>
                      <span class="homework-due">Due: {{ formatDate(homework.due_date) }}</span>
                      <span class="assigned-to">Assigned to: {{ getAssignedStudentsNames(homework.assigned_to) }}</span>
                    </div>
                  </div>
                </label>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="button" @click="closeRemoveHomeworkModal" class="btn-cancel">
                Cancel
              </button>
              <button @click="removeSelectedHomework" class="btn-remove" :disabled="isRemoving || homeworkToRemove.length === 0">
                <span v-if="!isRemoving">Remove Selected ({{ homeworkToRemove.length }})</span>
                <span v-else>Removing...</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-content">
        <div class="spinner"></div>
        <p>Loading teacher dashboard...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import authService from '@/services/authService'
import { apiService } from '@/services/api'
import Swal from 'sweetalert2'

export default {
  name: 'TeacherDashboard',
  setup() {
    const router = useRouter()
    
    // Reactive data
    const currentUser = ref(authService.getCurrentUser())
    const isLoading = ref(true)
    const myStudents = ref([])
    const studentTasks = ref([])
    const assignedHomework = ref([])
    const filteredStudentTasks = ref([])
    const selectedStudent = ref('')
    const selectedStatus = ref('')
    const showAssignHomeworkModal = ref(false)
    const showRemoveHomeworkModal = ref(false)
    const isAssigning = ref(false)
    const isRemoving = ref(false)
    const homeworkToRemove = ref([])

    // New homework form data
    const newHomework = ref({
      subject: '',
      task: '',
      due_date: '',
      assigned_to: []
    })

    // Computed properties
    const totalStudentTasks = computed(() => studentTasks.value.length)
    const completedTasks = computed(() => studentTasks.value.filter(task => task.status === 'completed').length)
    const pendingTasks = computed(() => studentTasks.value.filter(task => task.status === 'pending').length)

    // Methods
    const logout = () => {
      authService.logout()
      router.push('/')
    }

    const goToAnalytics = () => {
      router.push('/teacher-analytics')
    }

    const loadMyStudents = async () => {
      try {
        console.log('🔄 Loading students for teacher:', currentUser.value.id);
        // Get students assigned to this teacher
        const response = await apiService.getTeacherStudents(currentUser.value.id)
        console.log('📥 Students response:', response);
        if (response.success) {
          myStudents.value = response.students
          console.log('✅ Students loaded:', myStudents.value);
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
        const response = await apiService.getStudentTasksForTeacher(currentUser.value.id)
        console.log('📥 Student tasks response:', response);
        
        if (response.success) {
          studentTasks.value = response.tasks
          filteredStudentTasks.value = response.tasks
          console.log('✅ Total student tasks loaded:', response.tasks.length);
        } else {
          console.error('❌ Failed to load student tasks:', response.error);
          studentTasks.value = []
          filteredStudentTasks.value = []
        }
      } catch (error) {
        console.error('❌ Error loading student tasks:', error)
        studentTasks.value = []
        filteredStudentTasks.value = []
      }
    }

    const loadAssignedHomework = async () => {
      try {
        console.log('🔄 Loading assigned homework for teacher:', currentUser.value.id);
        const response = await apiService.getTeacherHomework(currentUser.value.id)
        console.log('📥 Homework response:', response);
        if (response.success) {
          assignedHomework.value = response.homework
          console.log('✅ Assigned homework loaded:', assignedHomework.value);
        } else {
          console.error('❌ Failed to load homework:', response.error);
          assignedHomework.value = []
        }
      } catch (error) {
        console.error('❌ Error loading homework:', error);
        assignedHomework.value = []
      }
    }

    const filterTasks = () => {
      let filtered = studentTasks.value

      if (selectedStudent.value) {
        filtered = filtered.filter(task => task.user_id == selectedStudent.value)
      }

      if (selectedStatus.value) {
        filtered = filtered.filter(task => task.status === selectedStatus.value)
      }

      filteredStudentTasks.value = filtered
    }

    const getStudentName = (userId) => {
      const student = myStudents.value.find(s => s.id === userId)
      return student ? student.username : 'Unknown Student'
    }

    const getStudentTaskCount = (studentId) => {
      const count = studentTasks.value.filter(task => task.user_id === studentId).length
      console.log('📊 Task count for student', studentId, ':', count);
      return count
    }

    const getStudentProgress = (studentId) => {
      const tasks = studentTasks.value.filter(task => task.user_id === studentId)
      if (tasks.length === 0) {
        console.log('📊 No tasks found for student', studentId);
        return 0
      }
      const completed = tasks.filter(task => task.status === 'completed').length
      const progress = Math.round((completed / tasks.length) * 100)
      console.log('📊 Progress for student', studentId, ':', completed, '/', tasks.length, '=', progress + '%');
      return progress
    }

    const calculateCompletionRate = () => {
      if (totalStudentTasks.value === 0) return 0
      return Math.round((completedTasks.value / totalStudentTasks.value) * 100)
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString()
    }

    const getAssignedStudentsNames = (studentIds) => {
      if (!Array.isArray(studentIds)) return 'None'
      const names = studentIds.map(id => {
        const student = myStudents.value.find(s => s.id === id)
        return student ? student.username : 'Unknown'
      })
      return names.join(', ')
    }

    const assignHomework = async () => {
      if (newHomework.value.assigned_to.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'No Students Selected',
          text: 'Please select at least one student to assign homework to.',
          timer: 3000,
          showConfirmButton: false
        })
        return
      }

      isAssigning.value = true

      try {
        console.log('🔄 Assigning homework to students:', newHomework.value.assigned_to);
        
        // Use the dedicated assignHomework API endpoint
        const homeworkData = {
          subject: newHomework.value.subject,
          task: newHomework.value.task,
          due_date: newHomework.value.due_date,
          assigned_to: newHomework.value.assigned_to
        }

        const result = await apiService.assignHomework(homeworkData)
        console.log('✅ Homework assignment result:', result);

        if (result.success) {
          Swal.fire({
            icon: 'success',
            title: 'Homework Assigned!',
            text: result.message || 'Homework has been successfully assigned to selected students.',
            timer: 3000,
            showConfirmButton: false
          })

          closeAssignHomeworkModal()
          
          // Refresh both student tasks and assigned homework
          await loadStudentTasks()
          await loadAssignedHomework()
        } else {
          throw new Error(result.error || 'Failed to assign homework')
        }

      } catch (error) {
        console.error('❌ Error assigning homework:', error)
        Swal.fire({
          icon: 'error',
          title: 'Assignment Failed',
          text: 'Failed to assign homework. Please try again.',
          timer: 3000,
          showConfirmButton: false
        })
      } finally {
        isAssigning.value = false
      }
    }

    const closeAssignHomeworkModal = () => {
      showAssignHomeworkModal.value = false
      newHomework.value = {
        subject: '',
        task: '',
        due_date: '',
        assigned_to: []
      }
    }

    const closeRemoveHomeworkModal = () => {
      showRemoveHomeworkModal.value = false
      homeworkToRemove.value = []
    }

    const removeSelectedHomework = async () => {
      if (homeworkToRemove.value.length === 0) {
        Swal.fire({
          icon: 'warning',
          title: 'No Homework Selected',
          text: 'Please select at least one homework to remove.',
          timer: 3000,
          showConfirmButton: false
        })
        return
      }

      const result = await Swal.fire({
        title: 'Remove Selected Homework?',
        text: `Are you sure you want to remove ${homeworkToRemove.value.length} homework assignment(s)? This action cannot be undone.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, remove them!'
      })

      if (result.isConfirmed) {
        isRemoving.value = true

        try {
          console.log('🗑️ Removing homework:', homeworkToRemove.value);
          
          // Create promises to delete each selected homework
          const deletePromises = homeworkToRemove.value.map(homeworkId => 
            apiService.deleteTask(homeworkId)
          )

          const results = await Promise.all(deletePromises)
          console.log('✅ Homework removal results:', results);

          Swal.fire({
            icon: 'success',
            title: 'Homework Removed!',
            text: `${homeworkToRemove.value.length} homework assignment(s) have been successfully removed.`,
            timer: 3000,
            showConfirmButton: false
          })

          closeRemoveHomeworkModal()
          
          // Refresh both student tasks and assigned homework
          await loadStudentTasks()
          await loadAssignedHomework()

        } catch (error) {
          console.error('❌ Error removing homework:', error)
          Swal.fire({
            icon: 'error',
            title: 'Removal Failed',
            text: 'Failed to remove homework. Please try again.',
            timer: 3000,
            showConfirmButton: false
          })
        } finally {
          isRemoving.value = false
        }
      }
    }

    const editHomework = (homework) => {
      // Implementation for editing homework
      console.log('Edit homework:', homework)
    }

    const deleteHomework = async (homeworkId) => {
      const result = await Swal.fire({
        title: 'Delete Homework?',
        text: 'This action cannot be undone.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
      })

      if (result.isConfirmed) {
        try {
          // Remove from local list
          assignedHomework.value = assignedHomework.value.filter(hw => hw.id !== homeworkId)
          
          Swal.fire({
            icon: 'success',
            title: 'Deleted!',
            text: 'Homework has been deleted.',
            timer: 2000,
            showConfirmButton: false
          })
        } catch (error) {
          console.error('Error deleting homework:', error)
        }
      }
    }

    // Initialize dashboard
    onMounted(async () => {
      try {
        console.log('🚀 Initializing Teacher Dashboard for user:', currentUser.value);
        // Add a small delay to ensure token is properly set after login
        await new Promise(resolve => setTimeout(resolve, 100))
        
        console.log('📝 Step 1: Loading students...');
        await loadMyStudents()
        console.log('📝 Step 2: Loading student tasks...');
        await loadStudentTasks()
        console.log('📝 Step 3: Loading assigned homework...');
        await loadAssignedHomework()
        console.log('✅ Dashboard initialization complete');
      } catch (error) {
        console.error('❌ Error initializing dashboard:', error)
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
      filteredStudentTasks,
      selectedStudent,
      selectedStatus,
      showAssignHomeworkModal,
      showRemoveHomeworkModal,
      isAssigning,
      isRemoving,
      homeworkToRemove,
      newHomework,
      
      // Computed
      totalStudentTasks,
      completedTasks,
      pendingTasks,
      
      // Methods
      logout,
      goToAnalytics,
      loadStudentTasks,
      filterTasks,
      getStudentName,
      getStudentTaskCount,
      getStudentProgress,
      calculateCompletionRate,
      formatDate,
      getAssignedStudentsNames,
      assignHomework,
      closeAssignHomeworkModal,
      closeRemoveHomeworkModal,
      removeSelectedHomework,
      editHomework,
      deleteHomework
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

.analytics-btn {
  background: rgba(76, 175, 80, 0.2);
  border: 1px solid rgba(76, 175, 80, 0.3);
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

.analytics-btn:hover {
  background: rgba(76, 175, 80, 0.3);
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

.students-count,
.tasks-count,
.homework-count,
.completion-rate {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Main Features Grid */
.second-row-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.third-row-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.feature-card {
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
}

.feature-card.full-width {
  min-height: 300px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
  flex: 1;
  margin-left: 15px;
}

.refresh-btn,
.assign-btn {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.remove-btn {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 5px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-btn:hover,
.assign-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.remove-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
}

.assign-btn:disabled,
.remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.assign-btn:disabled {
  background: rgba(76, 175, 80, 0.3);
}

.remove-btn:disabled {
  background: rgba(244, 67, 54, 0.3);
}

.assign-btn:disabled:hover,
.remove-btn:disabled:hover {
  transform: none;
  box-shadow: none;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* Task Filters */
.task-filters {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.task-filters select {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.task-filters select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.1);
}

.task-filters select option {
  background: #333;
  color: white;
}

/* Task List */
.task-list,
.homework-list,
.progress-list {
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
}

.task-item,
.homework-item,
.progress-item {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 10px;
  transition: all 0.3s ease;
}

.task-item:hover,
.homework-item:hover,
.progress-item:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateX(5px);
}

.task-info,
.homework-info {
  flex: 1;
}

.task-title,
.homework-title {
  font-weight: 600;
  color: white;
  margin-bottom: 8px;
}

.task-details,
.homework-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.student-name,
.task-subject,
.task-due,
.homework-subject,
.homework-due,
.assigned-to {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-badge.pending {
  background: rgba(255, 152, 0, 0.8);
  color: white;
}

.status-badge.in-progress {
  background: rgba(33, 150, 243, 0.8);
  color: white;
}

.status-badge.completed {
  background: rgba(76, 175, 80, 0.8);
  color: white;
}

/* Progress Styles */
.progress-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.student-details {
  flex: 1;
}

.student-name {
  font-weight: 600;
  color: white;
  font-size: 0.9rem;
}

.student-email {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
}

.progress-stats {
  text-align: right;
}

.task-count {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 5px;
}

.completion-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 60px;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
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
  color: white;
  min-width: 35px;
}

/* Analytics Grid */
.analytics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.analytics-item {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  transition: all 0.3s ease;
}

.analytics-item:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.analytics-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.analytics-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.analytics-label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
}

/* No Data States */
.no-tasks,
.no-homework,
.no-students {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.7);
}

.no-data-icon {
  font-size: 3rem;
  margin-bottom: 15px;
  opacity: 0.6;
}

.no-tasks p,
.no-homework p,
.no-students p {
  font-size: 1.1rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.no-tasks small,
.no-homework small,
.no-students small {
  font-size: 0.9rem;
  opacity: 0.8;
  line-height: 1.4;
}

.no-students-message {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.no-students-message p {
  color: #6c757d;
  margin-bottom: 5px;
  font-weight: 600;
}

.no-students-message small {
  color: #6c757d;
  font-size: 0.8rem;
}

/* Homework Actions */
.homework-actions {
  display: flex;
  gap: 8px;
}

.edit-btn,
.delete-btn {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn:hover {
  background: rgba(33, 150, 243, 0.3);
  border-color: rgba(33, 150, 243, 0.5);
}

.delete-btn:hover {
  background: rgba(244, 67, 54, 0.3);
  border-color: rgba(244, 67, 54, 0.5);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.4s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 20px;
  border-radius: 20px 20px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 30px;
}

/* Form Styles */
.homework-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-input,
.form-textarea {
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.student-checkboxes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  max-height: 150px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.checkbox {
  width: 16px;
  height: 16px;
}

.checkbox-label {
  font-size: 0.9rem;
  color: #333;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-cancel,
.btn-assign {
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-assign {
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
}

.btn-assign:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.btn-assign:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-remove {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
  padding: 12px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-remove:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
}

.btn-remove:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Removal Modal Styles */
.no-homework-message {
  text-align: center;
  padding: 40px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
}

.no-homework-message p {
  color: #6c757d;
  margin-bottom: 5px;
  font-weight: 600;
}

.no-homework-message small {
  color: #6c757d;
  font-size: 0.8rem;
}

.homework-removal-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.removal-instruction {
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.homework-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f9fafb;
}

.homework-checkbox {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s ease;
}

.homework-checkbox:hover {
  border-color: #f44336;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.1);
}

.homework-checkbox .checkbox {
  margin-right: 12px;
}

.homework-label {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
}

.homework-label .homework-info {
  flex: 1;
}

.homework-label .homework-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.homework-label .homework-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.homework-label .homework-subject,
.homework-label .homework-due,
.homework-label .assigned-to {
  font-size: 0.8rem;
  color: #6c757d;
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
  .second-row-grid {
    grid-template-columns: 1fr;
  }
  
  .third-row-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  }
  
  .task-filters {
    flex-direction: column;
  }
  
  .student-checkboxes {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .modal-content {
    width: 95%;
    margin: 10px;
  }
}
</style>
