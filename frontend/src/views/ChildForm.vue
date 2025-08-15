<template>
  <div class="child-form-container">
    <!-- Header -->
    <header class="form-header">
      <div class="header-content">
        <button @click="goBack" class="back-btn">
          <i class="fas fa-arrow-left"></i>
          Back to Dashboard
        </button>
        <h1 class="form-title">
          <span class="title-icon">📝</span>
          Tell Us About Yourself!
        </h1>
        <p class="form-subtitle">Help us personalize your learning adventure</p>
      </div>
    </header>

    <!-- Main Form -->
    <main class="form-main">
      <div class="container">
        <div class="form-card">
          <div class="form-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            </div>
            <span class="progress-text">{{ completedFields }}/4 fields completed</span>
          </div>

          <form @submit.prevent="submitForm" class="child-profile-form">
            <!-- Grade Level Field -->
            <div class="form-field">
              <label class="field-label">
                <span class="label-icon">🎓</span>
                What grade are you in?
              </label>
              <select v-model="formData.grade_level" class="form-select" required>
                <option value="">Select your grade</option>
                <option v-for="grade in grades" :key="grade" :value="grade">
                  Grade {{ grade }}
                </option>
              </select>
            </div>

            <!-- Date of Birth Field -->
            <div class="form-field">
              <label class="field-label">
                <span class="label-icon">🎂</span>
                When is your birthday?
              </label>
              <input 
                type="date" 
                v-model="formData.date_of_birth" 
                class="form-input"
                :max="maxDate"
                required
              />
            </div>

            <!-- Gender Field -->
            <div class="form-field">
              <label class="field-label">
                <span class="label-icon">👤</span>
                How would you like to be identified?
              </label>
              <div class="gender-options">
                <div 
                  v-for="option in genderOptions" 
                  :key="option.value"
                  class="gender-option"
                  :class="{ active: formData.gender === option.value }"
                  @click="formData.gender = option.value"
                >
                  <span class="gender-icon">{{ option.icon }}</span>
                  <span class="gender-label">{{ option.label }}</span>
                </div>
              </div>
            </div>

            <!-- Interests Field -->
            <div class="form-field">
              <label class="field-label">
                <span class="label-icon">🌟</span>
                What are you interested in? (Tell us about your hobbies, favorite subjects, etc.)
              </label>
              <textarea 
                v-model="formData.interests"
                class="form-textarea"
                placeholder="I love drawing, playing soccer, reading adventure books, learning about animals..."
                rows="4"
                required
              ></textarea>
              <div class="character-count">{{ characterCount }}/500</div>
            </div>

            <!-- Submit Button -->
            <div class="form-actions">
              <button 
                type="submit" 
                class="submit-btn"
                :disabled="!isFormValid || isSubmitting"
                :class="{ submitting: isSubmitting }"
              >
                <span v-if="!isSubmitting">
                  <i class="fas fa-save"></i>
                  Save My Profile
                </span>
                <span v-else>
                  <i class="fas fa-spinner fa-spin"></i>
                  Saving...
                </span>
              </button>
            </div>
          </form>
        </div>

        <!-- Fun Motivational Section -->
        <div class="motivation-card">
          <div class="motivation-icon">🚀</div>
          <h3>Why we need this info?</h3>
          <ul class="motivation-list">
            <li>📚 To suggest the best learning activities for your grade</li>
            <li>🎯 To create personalized quests just for you</li>
            <li>🎨 To recommend fun activities based on your interests</li>
            <li>🏆 To celebrate your achievements in the best way</li>
          </ul>
        </div>
      </div>
    </main>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="success-modal">
        <div class="success-content">
          <div class="success-icon">🎉</div>
          <h2>Profile Saved Successfully!</h2>
          <p>Your adventure is now personalized just for you!</p>
          <button @click="goToDashboard" class="success-btn">
            Start My Adventure!
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import Swal from 'sweetalert2'

export default {
  name: 'ChildForm',
  setup() {
    const router = useRouter()
    const user = ref(null)
    const isSubmitting = ref(false)
    const showSuccessModal = ref(false)

    // Form data
    const formData = ref({
      grade_level: '',
      date_of_birth: '',
      gender: '',
      interests: ''
    })

    // Form options
    const grades = ref([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    
    const genderOptions = ref([
      { value: 'male', label: 'Boy', icon: '👦' },
      { value: 'female', label: 'Girl', icon: '👧' },
      { value: 'other', label: 'Other', icon: '👤' },
      { value: 'prefer_not_to_say', label: 'Prefer not to say', icon: '🤐' }
    ])

    // Computed properties
    const maxDate = computed(() => {
      const today = new Date()
      const maxDate = new Date(today.getFullYear() - 5, today.getMonth(), today.getDate())
      return maxDate.toISOString().split('T')[0]
    })

    const characterCount = computed(() => {
      return formData.value.interests.length
    })

    const completedFields = computed(() => {
      let count = 0
      if (formData.value.grade_level) count++
      if (formData.value.date_of_birth) count++
      if (formData.value.gender) count++
      if (formData.value.interests.trim()) count++
      return count
    })

    const progressPercentage = computed(() => {
      return (completedFields.value / 4) * 100
    })

    const isFormValid = computed(() => {
      return formData.value.grade_level && 
             formData.value.date_of_birth && 
             formData.value.gender && 
             formData.value.interests.trim() &&
             formData.value.interests.length <= 500
    })

    // Methods
    const goBack = () => {
      router.push('/child-dashboard')
    }

    const goToDashboard = () => {
      showSuccessModal.value = false
      router.push('/child-dashboard')
    }

    const loadExistingProfile = async () => {
      try {
        // For demo purposes, use a default user ID if no user is logged in
        const userId = user.value?.id || 1; // Use ID 1 as default for demo
        
        const response = await apiService.getChildProfile(userId)
        if (response.success && response.profile) {
          const profile = response.profile
          formData.value = {
            grade_level: profile.grade_level || '',
            date_of_birth: profile.date_of_birth || '',
            gender: profile.gender || '',
            interests: profile.interests || ''
          }
        }
      } catch (error) {
        console.error('Error loading existing profile:', error)
      }
    }

    const submitForm = async () => {
      if (!isFormValid.value) return

      isSubmitting.value = true

      try {
        // For demo purposes, use a default user ID if no user is logged in
        const userId = user.value?.id || 1; // Use ID 1 as default for demo
        
        const profileData = {
          user_id: userId,
          grade_level: parseInt(formData.value.grade_level),
          date_of_birth: formData.value.date_of_birth,
          gender: formData.value.gender,
          interests: formData.value.interests.trim()
        }

        console.log('Submitting profile data:', profileData)

        const response = await apiService.createChildProfile(profileData)

        if (response.success) {
          showSuccessModal.value = true
        } else {
          throw new Error(response.error || 'Failed to save profile')
        }
      } catch (error) {
        console.error('Error saving profile:', error)
        Swal.fire({
          icon: 'error',
          title: 'Oops!',
          text: error.response?.data?.error || 'Failed to save your profile. Please try again!',
          background: 'linear-gradient(135deg, #ff6b6b, #ffa726)',
          color: 'white'
        })
      } finally {
        isSubmitting.value = false
      }
    }

    // Initialize
    onMounted(() => {
      user.value = userUtils.getCurrentUser()
      // Load existing profile regardless of authentication status
      loadExistingProfile()
    })

    return {
      formData,
      grades,
      genderOptions,
      maxDate,
      characterCount,
      completedFields,
      progressPercentage,
      isFormValid,
      isSubmitting,
      showSuccessModal,
      goBack,
      goToDashboard,
      submitForm
    }
  }
}
</script>

<style scoped>
.child-form-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Merriweather', serif;
}

/* Header */
.form-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  padding: 1rem 0;
}

.header-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
}

.back-btn {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  position: absolute;
  left: 2rem;
  top: 50%;
  transform: translateY(-50%);
}

.back-btn:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: translateY(-50%) translateY(-2px);
}

.form-title {
  text-align: center;
  color: #333;
  font-size: 2rem;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.title-icon {
  font-size: 2.5rem;
}

.form-subtitle {
  text-align: center;
  color: #666;
  margin: 0.5rem 0 0 0;
  font-size: 1.1rem;
}

/* Main Content */
.form-main {
  padding: 2rem 0;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.form-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

/* Progress Bar */
.form-progress {
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(102, 126, 234, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.5s ease;
  border-radius: 4px;
}

.progress-text {
  display: block;
  text-align: center;
  margin-top: 0.5rem;
  color: #667eea;
  font-weight: 600;
  font-size: 0.9rem;
}

/* Form Fields */
.form-field {
  margin-bottom: 2rem;
}

.field-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
}

.label-icon {
  font-size: 1.3rem;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Gender Options */
.gender-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.gender-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: white;
}

.gender-option:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.gender-option.active {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.gender-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.gender-label {
  font-weight: 600;
}

/* Character Count */
.character-count {
  text-align: right;
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
}

/* Submit Button */
.form-actions {
  text-align: center;
  margin-top: 2rem;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 200px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn.submitting {
  background: linear-gradient(135deg, #999, #666);
}

/* Motivation Card */
.motivation-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  height: fit-content;
}

.motivation-icon {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 1rem;
}

.motivation-card h3 {
  text-align: center;
  color: #333;
  margin-bottom: 1rem;
}

.motivation-list {
  list-style: none;
  padding: 0;
}

.motivation-list li {
  margin-bottom: 0.8rem;
  color: #666;
  font-weight: 500;
}

/* Success Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.success-modal {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  max-width: 400px;
  width: 90%;
  animation: slideUp 0.3s ease-out;
}

.success-content {
  color: #333;
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.success-btn {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.success-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .form-title {
    font-size: 1.5rem;
  }

  .back-btn {
    position: static;
    transform: none;
    margin-bottom: 1rem;
  }

  .header-content {
    text-align: center;
  }

  .gender-options {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
