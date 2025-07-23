<template>
  <div class="modal-backdrop" @click="closeModal">
    <div class="auth-modal fade-in" @click.stop>

      <!-- Step 1: Role Selection View -->
      <div v-if="!userType" class="user-role-selection">
        <h2>Who’s Signing Up?</h2>
        <div class="role-buttons">
          <button @click="userType = 'kid'" class="role-btn kid-btn">🧒 I am a Kid</button>
          <button @click="userType = 'parent'" class="role-btn parent-btn">👨‍👩‍👧 I am a Parent</button>
          <button @click="userType = 'teacher'" class="role-btn teacher-btn">👩‍🏫 I am a Teacher</button>
        </div>
      </div>

      <!-- Step 2: Kid Registration -->
      <div v-else-if="userType === 'kid'">
        <!-- Header -->
        <div class="modal-header">
          <div class="header-icon">🚀</div>
          <h2>Start Your Adventure</h2>
          <p>Create your quest profile and begin the journey!</p>
          <button @click="$emit('close')" class="close-btn">&times;</button>
        </div>

        <!-- Form -->
        <div class="modal-body">
          <form @submit.prevent="handleRegister" class="auth-form">
            <div class="form-group">
              <label for="username"><i class="fas fa-user"></i> Adventurer Name</label>
              <input id="username" v-model="username" type="text" placeholder="Choose your adventure name" required
                class="form-input" />
            </div>

            <div class="form-group">
              <label for="email"><i class="fas fa-envelope"></i> Magic Mail</label>
              <input id="email" v-model="email" type="email" placeholder="your.magic@email.com" required
                class="form-input" />
            </div>

            <div class="form-group">
              <label for="password"><i class="fas fa-lock"></i> Secret Code</label>
              <input id="password" v-model="password" type="password" placeholder="Create a strong secret code" required
                class="form-input" />
            </div>

            <div class="form-group">
              <label for="confirmPassword"><i class="fas fa-shield-alt"></i> Confirm Secret Code</label>
              <input id="confirmPassword" v-model="confirmPassword" type="password"
                placeholder="Confirm your secret code" required class="form-input" />
            </div>

            <!--
            <div class="form-group">
              <label for="dob"><i class="fas fa-birthday-cake"></i> Birthday</label>
              <input id="dob" v-model="dateOfBirth" type="date" required class="form-input" />
            </div>

            <div class="form-group">
              <label for="gender"><i class="fas fa-venus-mars"></i> Identity</label>
              <select id="gender" v-model="gender" class="form-input" required>
                <option disabled value="">Choose your identity</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>

            <div class="form-group">
              <label for="grade"><i class="fas fa-school"></i> Level of Wisdom</label>
              <input id="grade" v-model="gradeLevel" type="number" min="1" max="12" placeholder="Your grade in school" class="form-input" />
            </div>

            <div class="form-group">
              <label for="interests"><i class="fas fa-star"></i> Quest Interests</label>
              <textarea id="interests" v-model="interests" class="form-input" placeholder="e.g. Math, Space, Dragons"></textarea>
            </div>
            -->

            <button type="submit" class="btn-primary" :disabled="isLoading">
              <span v-if="!isLoading" class="btn-content">
                <span class="btn-icon">✨</span>
                Begin My Quest
              </span>
              <span v-else class="btn-loading">
                <span class="spinner"></span>
                Creating...
              </span>
            </button>
          </form>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <p>Already have an adventure?</p>
          <button @click="$emit('switchToLogin')" class="link-btn">Continue Your Quest <span>🗝️</span></button>
        </div>
      </div>

      <!-- Step 3: Parent Registration -->
      <div v-else-if="userType === 'parent'">
        <!-- Header -->
        <div class="modal-header">
          <div class="header-icon">🛡️</div>
          <h2>Protect the Quest</h2>
          <p>Register as a guardian to oversee the adventure!</p>
          <button @click="$emit('close')" class="close-btn">&times;</button>
        </div>

        <!-- Form -->
        <div class="modal-body">
          <form @submit.prevent="handleRegister" class="auth-form">
            <div class="form-group">
              <label for="parentName"><i class="fas fa-user-shield"></i> Guardian Username</label>
              <input id="parentName" v-model="parentName" type="text" placeholder="Your full name" required
                class="form-input" />
            </div>

            <div class="form-group">
              <label for="parentPassword"><i class="fas fa-lock"></i> Guardian Code</label>
              <input id="parentPassword" v-model="parentPassword" type="password" placeholder="Strong password" required
                class="form-input" />
            </div>


            <div class="form-group">
              <label for="parentConfirmPassword"><i class="fas fa-shield-alt"></i> Confirm Guardian Code</label>
              <input id="parentConfirmPassword" v-model="parentConfirmPassword" type="password"
                placeholder="Re-enter password" required class="form-input" />
            </div>

            <div class="form-group">
              <label for="parentEmail"><i class="fas fa-envelope"></i> Contact Scroll</label>
              <input id="parentEmail" v-model="parentEmail" type="email" placeholder="you@guardian.com" required
                class="form-input" />
            </div>


            <div class="form-group">
              <label for="relationship"><i class="fas fa-user-friends"></i> Bond of Guardianship</label>
              <select id="relationship" v-model="relationshipType" class="form-input" required>
                <option disabled value="">Choose relationship</option>
                <option>Mother</option>
                <option>Father</option>
                <option>Guardian</option>
              </select>
            </div>

            <div class="form-group">
              <label for="childUsername"><i class="fas fa-child"></i> Adventurer Username</label>
              <input id="childUsername" v-model="childUsername" type="text" placeholder="Your child's username" required
                class="form-input" />
            </div>

            <button type="submit" class="btn-primary" :disabled="isLoading">
              <span v-if="!isLoading" class="btn-content">
                <span class="btn-icon">🛡️</span>
                Register as Guardian
              </span>
              <span v-else class="btn-loading">
                <span class="spinner"></span>
                Creating...
              </span>
            </button>
          </form>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <p>Already guarding an adventure?</p>
          <button @click="$emit('switchToLogin')" class="link-btn">Continue as Guardian <span>🔐</span></button>
        </div>
      </div>


      <!-- Step 4: Teacher Registration -->
      <div v-else-if="userType === 'teacher'">
        <!-- Header -->
        <div class="modal-header">
          <div class="header-icon">👩‍🏫</div>
          <h2>Guide the Quest</h2>
          <p>Register as a teacher to lead the learning adventure!</p>
          <button @click="$emit('close')" class="close-btn">&times;</button>
        </div>

        <!-- Form -->
        <div class="modal-body">
          <form @submit.prevent="handleRegister" class="auth-form">
            <div class="form-group">
              <label for="teacherName"><i class="fas fa-chalkboard-teacher"></i> Teacher Username</label>
              <input id="teacherName" v-model="teacherName" type="text" placeholder="Your educator name" required
                class="form-input" />
            </div>

            <div class="form-group">
              <label for="teacherPassword"><i class="fas fa-lock"></i> Teacher Code</label>
              <input id="teacherPassword" v-model="teacherPassword" type="password" placeholder="Strong password" required
                class="form-input" />
            </div>

            <div class="form-group">
              <label for="teacherConfirmPassword"><i class="fas fa-shield-alt"></i> Confirm Teacher Code</label>
              <input id="teacherConfirmPassword" v-model="teacherConfirmPassword" type="password"
                placeholder="Re-enter password" required class="form-input" />
            </div>

            <div class="form-group">
              <label for="teacherEmail"><i class="fas fa-envelope"></i> Contact Scroll</label>
              <input id="teacherEmail" v-model="teacherEmail" type="email" placeholder="you@school.edu" required
                class="form-input" />
            </div>

            <!-- Student Selection Section -->
            <div class="form-group student-selection">
              <div class="selection-header">
                <label class="section-label">
                  <i class="fas fa-graduation-cap"></i> Select Your Adventurers
                </label>
                <p class="helper-text">Choose the students you'll be guiding on their learning quest</p>
              </div>
              
              <!-- Search and Filter Bar -->
              <div class="search-filter-container">
                <div class="search-wrapper">
                  <i class="fas fa-search search-icon"></i>
                  <input 
                    v-model="studentSearchQuery" 
                    type="text" 
                    placeholder="Search by name or email..." 
                    class="search-input"
                    @input="filterStudents"
                  />
                  <button 
                    v-if="studentSearchQuery" 
                    @click="clearSearch" 
                    type="button" 
                    class="clear-search-btn"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </div>
                
                <!-- Quick Stats -->
                <div class="selection-stats">
                  <span class="stat-item">
                    <i class="fas fa-users"></i>
                    {{ filteredStudents.length }} Available
                  </span>
                  <span class="stat-item selected" v-if="selectedStudents.length > 0">
                    <i class="fas fa-check-circle"></i>
                    {{ selectedStudents.length }} Selected
                  </span>
                  <button 
                    v-if="selectedStudents.length > 0" 
                    @click="clearAllSelected" 
                    type="button" 
                    class="clear-all-btn"
                  >
                    <i class="fas fa-times-circle"></i>
                    Clear All
                  </button>
                </div>
              </div>

              <!-- Loading State -->
              <div v-if="loadingStudents" class="loading-students">
                <div class="loading-spinner"></div>
                <span>Loading adventurers...</span>
              </div>

              <!-- Student List -->
              <div v-else class="student-list-container">
                <!-- Select All Option -->
                <div v-if="filteredStudents.length > 0" class="select-all-section">
                  <label class="select-all-checkbox">
                    <input 
                      type="checkbox" 
                      :checked="allStudentsSelected"
                      @change="toggleAllStudents"
                      class="checkbox-input"
                    />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-label">
                      Select All {{ filteredStudents.length }} Student{{ filteredStudents.length !== 1 ? 's' : '' }}
                    </span>
                  </label>
                </div>

                <!-- Student Grid -->
                <div class="student-grid">
                  <div 
                    v-for="student in filteredStudents" 
                    :key="student.id" 
                    class="student-card"
                    :class="{ 'selected': selectedStudents.includes(student.id) }"
                    @click="toggleStudent(student.id)"
                  >
                    <div class="student-content">
                      <div class="student-avatar">
                        <span class="avatar-emoji">{{ student.avatar || '🎓' }}</span>
                        <div class="selection-badge" v-if="selectedStudents.includes(student.id)">
                          <i class="fas fa-check"></i>
                        </div>
                      </div>
                      <div class="student-info">
                        <h4 class="student-name">{{ student.username }}</h4>
                        <p class="student-email">{{ student.email || 'No email provided' }}</p>
                      </div>
                    </div>
                    <div class="card-overlay"></div>
                  </div>
                </div>

                <!-- No Results -->
                <div v-if="filteredStudents.length === 0 && !loadingStudents" class="no-results">
                  <div class="no-results-content">
                    <i class="fas fa-search no-results-icon"></i>
                    <h3>No Students Found</h3>
                    <p>No adventurers match your search criteria</p>
                    <button @click="clearSearch" type="button" class="clear-search-action">
                      <i class="fas fa-refresh"></i>
                      Show All Students
                    </button>
                  </div>
                </div>
              </div>
            </div>            <button type="submit" class="btn-primary" :disabled="isLoading || selectedStudents.length === 0">
              <span v-if="!isLoading" class="btn-content">
                <span class="btn-icon">👩‍🏫</span>
                Register as Teacher
              </span>
              <span v-else class="btn-loading">
                <span class="spinner"></span>
                Creating...
              </span>
            </button>

            <div v-if="selectedStudents.length === 0" class="validation-message">
              Please select at least one student to continue
            </div>
          </form>
        </div>

        <!-- Footer -->
        <div class="modal-footer">
          <p>Already teaching an adventurer?</p>
          <button @click="$emit('switchToLogin')" class="link-btn">Continue as Teacher <span>🔐</span></button>
        </div>
      </div>


      <!-- Floating Icons -->
      <div v-if="userType" class="floating-icons" :class="userType">
        <div class="float-icon fade-in" style="--delay: 0s; --x: 15%; --y: 20%;">🌟</div>
        <div class="float-icon fade-in" style="--delay: 1s; --x: 80%; --y: 15%;">🎯</div>
        <div class="float-icon fade-in" style="--delay: 2s; --x: 20%; --y: 80%;">🏆</div>
        <div class="float-icon fade-in" style="--delay: 3s; --x: 85%; --y: 75%;">⚡</div>
        <div class="float-icon fade-in" style="--delay: 4s; --x: 50%; --y: 90%;">🌈</div>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, computed, watch, onMounted } from 'vue'
import { apiService } from '@/services/api'
import Swal from 'sweetalert2'

export default {
  name: 'RegisterModal',
  emits: ['close', 'success', 'switchToLogin'],
  setup(props, { emit }) {
    const userType = ref(null)

    // Kid fields
    const username = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const email = ref('')
    // Parent fields
    const parentName = ref('')
    const parentPassword = ref('')
    const parentConfirmPassword = ref('')
    const parentEmail = ref('')
    const relationshipType = ref('')
    const childUsername = ref('')

    // Teacher fields (add after parent fields)
    const teacherName = ref('')
    const teacherPassword = ref('')
    const teacherConfirmPassword = ref('')
    const teacherEmail = ref('')
    const selectedStudents = ref([])
    const studentSearchQuery = ref('')
    const loadingStudents = ref(false)
    const availableStudents = ref([])
    const filteredStudents = ref([])    


    const isLoading = ref(false)


    const handleRegister = async () => {
      console.log('Register clicked', userType.value)
      if (isLoading.value) return

      let payload = {}

      if (userType.value === 'kid') {
        if (password.value !== confirmPassword.value) {
          await Swal.fire({
            icon: 'warning',
            title: 'Secret Codes Don\'t Match! 🔐',
            text: 'Make sure both secret codes are identical!',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white'
          })
          return
        }
        if (password.value.length < 6) {
          await Swal.fire({
            icon: 'warning',
            title: 'Secret Code Too Weak! ⚠️',
            text: 'Your secret code needs at least 6 characters!',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white'
          })
          return
        }

        payload = {
          role: 'child',
          username: username.value,
          password: password.value,
          email: email.value,
        }
      } else if (userType.value === 'parent') {
        if (parentPassword.value !== parentConfirmPassword.value) {
          await Swal.fire({
            icon: 'warning',
            title: 'Guardian Codes Don\'t Match! 🔐',
            text: 'Make sure both passwords match!',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white'
          })
          return
        }
        if (parentPassword.value.length < 6) {
          await Swal.fire({
            icon: 'warning',
            title: 'Guardian Code Too Weak! ⚠️',
            text: 'Your password needs at least 6 characters!',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white'
          })
          return
        }

        payload = {
          role: 'parent',
          username: parentName.value,
          email: parentEmail.value,
          password: parentPassword.value,
          relationship_type: relationshipType.value,
          child_username: childUsername.value
        }
      } else if (userType.value === 'teacher') {
      // Teacher validation
        if (teacherPassword.value !== teacherConfirmPassword.value) {
          await Swal.fire({
            icon: 'warning',
            title: 'Teacher Codes Don\'t Match! 🔐',
            text: 'Make sure both passwords match!',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white'
          })
          return
        }

        if (teacherPassword.value.length < 6) {
          await Swal.fire({
            icon: 'warning',
            title: 'Teacher Code Too Weak! ⚠️',
            text: 'Your password needs at least 6 characters!',
            timer: 3000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ffa726, #ff9800)',
            color: 'white'
          })
          return
        }

        payload = {
          role: 'teacher',
          username: teacherName.value,
          email: teacherEmail.value,
          password: teacherPassword.value,
          relationship_type: 'teacher',
          selectedStudents: selectedStudents.value
        }
      }

      isLoading.value = true

      try {
        const response = await apiService.register(payload)

        if (response.success) {
          // Emit success immediately to close modal
          isLoading.value = false
          emit('success', response)

          // Show success message after modal closes
          setTimeout(() => {
            const successMessage = userType.value === 'teacher' 
              ? 'Registration successful! Please log in to access your teacher dashboard.'
              : userType.value === 'parent'
              ? 'Registration successful! Please log in to access your guardian dashboard.'
              : 'Registration successful! Please log in to start your quest!'
            
            Swal.fire({
              icon: 'success',
              title: userType.value === 'kid' ? 'Welcome to KidQuest! 🎉' : userType.value === 'parent' ? 'Welcome, Guardian! 🛡️' : 'Welcome, Educator! 👩‍🏫',
              text: successMessage,
              timer: 2500,
              showConfirmButton: false,
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              backdrop: 'rgba(0,0,0,0.8)',
              customClass: {
                popup: 'success-popup'
              }
            })
          }, 300)
        }
      } catch (error) {
        console.error('Registration failed:', error)
        let errorMessage = 'Something went wrong! Please try again.'
        if (error.response?.data?.error) {
          errorMessage = error.response.data.error
        }

        await Swal.fire({
          icon: 'error',
          title: 'Registration Failed! 😔',
          text: errorMessage,
          timer: 4000,
          showConfirmButton: false,
          background: 'linear-gradient(135deg, #ff6b6b, #f44336)',
          color: 'white'
        })
      } finally {
        isLoading.value = false
      }
    }

    // Add this computed property in your setup function
    const allStudentsSelected = computed(() => {
      return filteredStudents.value.length > 0 && 
            selectedStudents.value.length === filteredStudents.value.length
    })

    // Add these methods in your setup function
    const filterStudents = () => {
      const query = studentSearchQuery.value.toLowerCase().trim()
      if (!query) {
        filteredStudents.value = availableStudents.value
      } else {
        filteredStudents.value = availableStudents.value.filter(student => 
          student.username.toLowerCase().includes(query) ||
          (student.email && student.email.toLowerCase().includes(query))
        )
      }
    }

    const toggleAllStudents = (event) => {
      if (event.target.checked) {
        selectedStudents.value = filteredStudents.value.map(student => student.id)
      } else {
        selectedStudents.value = []
      }
    }

    const toggleStudent = (studentId) => {
      const index = selectedStudents.value.indexOf(studentId)
      if (index > -1) {
        selectedStudents.value.splice(index, 1)
      } else {
        selectedStudents.value.push(studentId)
      }
    }

    const clearSearch = () => {
      studentSearchQuery.value = ''
      filterStudents()
    }

    const clearAllSelected = () => {
      selectedStudents.value = []
    }

    // Load students when teacher type is selected
    const loadStudents = async () => {
      if (userType.value !== 'teacher') return
      
      loadingStudents.value = true
      try {
        // Fetch students from backend API
        const response = await apiService.getAvailableStudents()
        availableStudents.value = response.data || []
        
        // Fallback mock data for development/testing
        if (availableStudents.value.length === 0) {
          availableStudents.value = [
            { id: 1, username: 'Emma_Explorer', email: 'emma@example.com', avatar: '🌟' },
            { id: 2, username: 'Alex_Adventurer', email: 'alex@example.com', avatar: '🚀' },
            { id: 3, username: 'Sofia_Scientist', email: 'sofia@example.com', avatar: '🔬' },
            { id: 4, username: 'Max_Mathematician', email: 'max@example.com', avatar: '🧮' },
            { id: 5, username: 'Luna_Learner', email: 'luna@example.com', avatar: '📚' },
            { id: 6, username: 'Oliver_Oracle', email: 'oliver@example.com', avatar: '🎯' },
            { id: 7, username: 'Zoe_Zoologist', email: 'zoe@example.com', avatar: '🦋' },
            { id: 8, username: 'Ryan_Reader', email: 'ryan@example.com', avatar: '📖' }
          ]
        }
        
        filterStudents()
      } catch (error) {
        console.error('Failed to load students:', error)
        availableStudents.value = []
        filteredStudents.value = []
      } finally {
        loadingStudents.value = false
      }
    }

    // Watch for userType changes to load students
    watch(userType, (newType) => {
      if (newType === 'teacher') {
        loadStudents()
      } else {
        // Reset student data when switching away from teacher
        availableStudents.value = []
        filteredStudents.value = []
        selectedStudents.value = []
        studentSearchQuery.value = ''
      }
    })


    const closeModal = () => {
      emit('close')
    }

    return {
      userType,
      username,
      password,
      email,
      confirmPassword,
      parentName,
      parentConfirmPassword,
      parentEmail,
      parentPassword,
      relationshipType,
      childUsername,
      teacherName,
      teacherPassword,
      teacherConfirmPassword,
      teacherEmail,
      selectedStudents,
      studentSearchQuery,
      loadingStudents,
      availableStudents,
      filteredStudents,
      allStudentsSelected,
      filterStudents,
      toggleAllStudents,
      toggleStudent,
      clearSearch,
      clearAllSelected,
      loadStudents,
      isLoading,
      handleRegister,
      closeModal
    }
  }
}
</script>

<style scoped>
.modal-backdrop {
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

.auth-modal {
  background: white;
  border-radius: 25px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.4s ease-out;
  position: relative;
  overflow: hidden;
  border: 3px solid transparent;
  background-clip: padding-box;
  max-height: 90vh;
  overflow-y: auto;
}

.auth-modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea, #764ba2, #ff6b6b, #ffa726);
  border-radius: 25px;
  padding: 3px;
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  z-index: -1;
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

/* Header */
.modal-header {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 2.5rem 2rem 2rem;
  text-align: center;
  position: relative;
}

.header-icon {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  animation: rocketLaunch 2s infinite;
}

@keyframes rocketLaunch {

  0%,
  100% {
    transform: translateY(0) rotate(-5deg);
  }

  50% {
    transform: translateY(-15px) rotate(5deg);
  }
}

.modal-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
}

.modal-header p {
  margin: 0;
  opacity: 0.9;
  font-size: 1rem;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  background: none;
  border: none;
  font-size: 2rem;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(90deg);
}

/* Body */
.modal-body {
  padding: 2.5rem 2rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.form-group label i {
  color: #667eea;
  width: 16px;
}

.form-input {
  padding: 1rem 1.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 15px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f9fafb;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.form-input::placeholder {
  color: #9ca3af;
  font-style: italic;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 1.2rem 2rem;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  margin-top: 1rem;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-icon {
  font-size: 1.2rem;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Footer */
.modal-footer {
  padding: 1.5rem 2rem 2.5rem;
  text-align: center;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.modal-footer p {
  margin: 0 0 1rem 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.link-btn {
  background: none;
  border: none;
  color: #667eea;
  font-weight: 600;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s ease;
  padding: 0.5rem 1rem;
  border-radius: 10px;
}

.link-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.link-btn span {
  margin-left: 0.5rem;
  display: inline-block;
  animation: keyTwinkle 1.5s infinite;
}

@keyframes keyTwinkle {

  0%,
  100% {
    opacity: 0.5;
    transform: scale(0.8) rotate(-5deg);
  }

  50% {
    opacity: 1;
    transform: scale(1.2) rotate(5deg);
  }
}

/* Floating Icons */
.floating-icons {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.float-icon {
  position: absolute;
  font-size: 1.2rem;
  opacity: 0.6;
  animation: floatIcon 4s infinite ease-in-out;
  animation-delay: var(--delay);
  left: var(--x);
  top: var(--y);
}

@keyframes floatIcon {

  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }

  50% {
    transform: translateY(-15px) rotate(180deg);
  }
}

/* Custom Scrollbar */
.auth-modal::-webkit-scrollbar {
  width: 8px;
}

.auth-modal::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.auth-modal::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 10px;
}

.auth-modal::-webkit-scrollbar-thumb:hover {
  background: #764ba2;
}

/* Responsive */
@media (max-width: 480px) {
  .auth-modal {
    width: 95%;
    margin: 1rem;
    max-height: 95vh;
  }

  .modal-header {
    padding: 2rem 1.5rem 1.5rem;
  }

  .modal-body {
    padding: 2rem 1.5rem;
  }

  .modal-footer {
    padding: 1.5rem;
  }

  .header-icon {
    font-size: 2.5rem;
  }

  .modal-header h2 {
    font-size: 1.5rem;
  }

  .auth-form {
    gap: 1.2rem;
  }
}

/* Role Selection */
.user-role-selection {
  text-align: center;
  padding: 2rem 1rem;
}

.role-buttons {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.role-btn {
  flex: 1 1 30%;
  min-width: 140px;
  padding: 1rem;
  font-size: 1rem;
  font-weight: bold;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.kid-btn {
  background-color: #fff3cd;
  color: #333;
}

.kid-btn:hover {
  background-color: #ffe082;
}

.parent-btn {
  background-color: #c8e6c9;
  color: #333;
}

.parent-btn:hover {
  background-color: #81c784;
}

.teacher-btn {
  background-color: #e1f5fe;
  color: #333;
}

.teacher-btn:hover {
  background-color: #81d4fa;
}

/* Ensure success popup appears above everything */
:global(.success-popup) {
  z-index: 9999 !important;
}

:global(.swal2-container) {
  z-index: 9999 !important;
}

/* Enhanced Student Selection Styles */
.student-selection {
  margin-top: 1.5rem;
}

.selection-header {
  margin-bottom: 1.5rem;
}

.section-label {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.section-label i {
  color: #667eea;
  font-size: 1.2rem;
}

.helper-text {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

.search-filter-container {
  background: #f8fafc;
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  border: 1px solid #e2e8f0;
}

.search-wrapper {
  position: relative;
  margin-bottom: 0.75rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 0.95rem;
  background: white;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  position: absolute;
  left: 0.875rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  pointer-events: none;
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

.clear-search-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.selection-stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.85rem;
  color: #6b7280;
  background: white;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
}

.stat-item.selected {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-color: #667eea;
}

.clear-all-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.85rem;
  color: white;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  border: 1px solid #ef4444;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
}

.clear-all-btn:hover {
  background: linear-gradient(135deg, #dc2626, #b91c1c);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.loading-students {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  color: #6b7280;
  background: #f8fafc;
  border-radius: 12px;
  border: 2px dashed #e5e7eb;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.student-list-container {
  max-height: 400px;
  overflow-y: auto;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: white;
}

.select-all-section {
  padding: 1rem;
  border-bottom: 1px solid #f1f5f9;
  background: #fafbfc;
}

.select-all-checkbox {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  font-weight: 600;
  color: #374151;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: relative;
}

.checkbox-input:checked + .checkbox-custom {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: #667eea;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.student-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.75rem;
  padding: 1rem;
}

.student-card {
  position: relative;
  background: white;
  border: 2px solid #f1f5f9;
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
}

.student-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #e2e8f0;
}

.student-card.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
}

.student-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  position: relative;
  z-index: 2;
}

.student-avatar {
  position: relative;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #ffeaa7, #fab1a0);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.avatar-emoji {
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.selection-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  border: 2px solid white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-email {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.student-card.selected .card-overlay {
  opacity: 1;
}

.no-results {
  padding: 3rem 1rem;
  text-align: center;
}

.no-results-content {
  max-width: 300px;
  margin: 0 auto;
}

.no-results-icon {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.no-results h3 {
  color: #374151;
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
}

.no-results p {
  color: #6b7280;
  margin: 0 0 1.5rem 0;
  font-size: 0.95rem;
}

.clear-search-action {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 auto;
}

.clear-search-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .student-grid {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .selection-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .search-filter-container {
    padding: 0.75rem;
  }
}
</style>