<!-- Edit User Form Component -->
<template>
  <BaseModal
    v-model="isVisible"
    title="Edit User"
    subtitle="Update user information"
    icon="✏️"
    @update:modelValue="$emit('update:modelValue', $event)"
  >
    <form @submit.prevent="handleSubmit" class="form-content">
      <div class="form-group">
        <label for="edit-username">Username</label>
        <div class="input-wrapper">
          <span class="input-icon">👤</span>
          <input
            id="edit-username"
            v-model="formData.username"
            type="text"
            required
            placeholder="Enter username"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="edit-email">Email</label>
        <div class="input-wrapper">
          <span class="input-icon">📧</span>
          <input
            id="edit-email"
            v-model="formData.email"
            type="email"
            required
            placeholder="Enter email address"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="edit-role">Role</label>
        <div class="input-wrapper">
          <span class="input-icon">🎭</span>
          <select
            id="edit-role"
            v-model="formData.role"
            required
          >
            <option value="">Select role</option>
            <option value="parent">Parent</option>
            <option value="child">Child</option>
            <option value="teacher">Teacher</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label for="edit-password">New Password (optional)</label>
        <div class="input-wrapper">
          <span class="input-icon">🔒</span>
          <input
            id="edit-password"
            v-model="formData.password"
            type="password"
            placeholder="Leave blank to keep current password"
          />
        </div>
      </div>

      <div class="form-actions">
        <button type="button" @click="cancel" class="btn-secondary">
          Cancel
        </button>
        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading">Updating...</span>
          <span v-else>Update User</span>
        </button>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </form>
  </BaseModal>
</template>

<script>
import { ref, computed, watch } from 'vue'
import axios from 'axios'
import BaseModal from '@/components/common/BaseModal.vue'

export default {
  name: 'EditUserForm',
  components: {
    BaseModal
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['update:modelValue', 'user-updated'],
  
  setup(props, { emit }) {
    const isVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const loading = ref(false)
    const error = ref('')

    const formData = ref({
      username: '',
      email: '',
      role: '',
      password: ''
    })

    // Watch for user prop changes and populate form
    watch(
      () => props.user,
      (newUser) => {
        if (newUser) {
          formData.value = {
            username: newUser.username || '',
            email: newUser.email || '',
            role: newUser.role || '',
            password: ''
          }
        }
      },
      { immediate: true }
    )

    const handleSubmit = async () => {
      try {
        loading.value = true
        error.value = ''

        if (!props.user?.id) {
          error.value = 'No user selected for editing'
          return
        }

        // Prepare data - only send password if it's not empty
        const updateData = {
          username: formData.value.username,
          email: formData.value.email,
          role: formData.value.role
        }

        if (formData.value.password.trim()) {
          updateData.password = formData.value.password
        }

        console.log('🔄 EditUserForm: Updating user:', props.user.id, updateData)
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
        const response = await axios.put(`${API_BASE_URL}/api/admin/users/${props.user.id}`, updateData)
        
        if (response.data.success) {
          console.log('✅ EditUserForm: User updated successfully')
          emit('user-updated', response.data.user)
          isVisible.value = false
          resetForm()
        } else {
          error.value = response.data.error || 'Failed to update user'
        }
      } catch (err) {
        console.error('❌ EditUserForm: Update failed:', err)
        error.value = err.response?.data?.error || 'Failed to update user'
      } finally {
        loading.value = false
      }
    }

    const resetForm = () => {
      formData.value = {
        username: '',
        email: '',
        role: '',
        password: ''
      }
      error.value = ''
    }

    const cancel = () => {
      isVisible.value = false
      resetForm()
    }

    return {
      isVisible,
      formData,
      loading,
      error,
      handleSubmit,
      cancel
    }
  }
}
</script>

<style scoped>
.form-content {
  padding: 0 2rem 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #FFFFFF;
  font-weight: 600;
  font-size: 0.9rem;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  z-index: 2;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

.input-wrapper input,
.input-wrapper select {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-wrapper input:focus,
.input-wrapper select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.input-wrapper input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-wrapper select option {
  background: #4a5568;
  color: white;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-primary,
.btn-secondary {
  padding: 0.8rem 2rem;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.error-message {
  background: rgba(244, 67, 54, 0.2);
  border: 1px solid rgba(244, 67, 54, 0.4);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
  color: #ffcdd2;
  font-size: 0.9rem;
}
</style>
