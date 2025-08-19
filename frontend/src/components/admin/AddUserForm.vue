<!-- Add User Form Component -->
<template>
  <BaseModal
    v-model="isVisible"
    title="Add New User"
    subtitle="Create a new user account"
    icon="➕"
    @update:modelValue="$emit('update:modelValue', $event)"
  >
    <form @submit.prevent="handleSubmit" class="form-content">
      <div class="form-group">
        <label for="username">Username</label>
        <div class="input-wrapper">
          <span class="input-icon">👤</span>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            required
            placeholder="Enter username"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <div class="input-wrapper">
          <span class="input-icon">📧</span>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            required
            placeholder="Enter email address"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <div class="input-wrapper">
          <span class="input-icon">🔒</span>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            placeholder="Enter password"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="role">Role</label>
        <div class="input-wrapper">
          <span class="input-icon">👥</span>
          <select id="role" v-model="formData.role" required>
            <option value="" disabled>Select Role</option>
            <option value="admin">Admin</option>
            <option value="parent">Parent</option>
            <option value="teacher">Teacher</option>
            <option value="child">Child</option>
          </select>
        </div>
      </div>

      <div class="form-actions">
        <button type="submit" class="submit-btn">
          <span class="btn-icon">✨</span>
          Create User
        </button>
        <button type="button" @click="resetForm" class="reset-btn">
          <span class="btn-icon">🔄</span>
          Reset
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'
import BaseModal from '@/components/common/BaseModal.vue'

export default {
  name: 'AddUserForm',
  components: {
    BaseModal
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true
    }
  },
  emits: ['update:modelValue', 'user-added'],
  
  setup(props, { emit }) {
    const isVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const formData = ref({
      username: '',
      email: '',
      password: '',
      role: ''
    })

    const handleSubmit = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
        const response = await axios.post(`${API_BASE_URL}/api/admin/users`, formData.value)
        if (response.data.success) {
          console.log('✅ User created successfully:', response.data.user)
          emit('user-created', response.data.user)
          resetForm()
          isVisible.value = false
        }
      } catch (error) {
        console.error('❌ Error creating user:', error)
        const errorMessage = error.response?.data?.error || error.message || 'Failed to create user'
        alert('Error: ' + errorMessage)
      }
    }

    const resetForm = () => {
      formData.value = {
        username: '',
        email: '',
        password: '',
        role: ''
      }
    }

    return {
      isVisible,
      formData,
      handleSubmit,
      resetForm
    }
  }
}
</script>

<style scoped>
/* Form Content */
.form-content {
  padding: 2rem;
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
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.95rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 1rem;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
}

.input-wrapper input,
.input-wrapper select {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 3rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-wrapper input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-wrapper input:focus,
.input-wrapper select:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.input-wrapper select {
  appearance: none;
  padding-right: 2.5rem;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255, 255, 255, 0.8)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
}

.input-wrapper select option {
  background: #eae6fa;
  color: #6c4ccf;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  border-radius: 6px;
  margin: 2px 0;
  transition: background 0.2s;
}

.input-wrapper select option:checked, .input-wrapper select option:hover {
  background: #d1c4e9;
  color: #4b2aad;
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.submit-btn,
.reset-btn {
  flex: 1;
  padding: 0.8rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn {
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #FFFFFF;
  border: none;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.reset-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
}

.reset-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 1.1rem;
}

/* Responsive Design */
@media (max-width: 640px) {
  .form-content {
    padding: 1.5rem;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style> 