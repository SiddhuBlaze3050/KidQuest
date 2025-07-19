<template>
  <button @click="handleLogout" class="logout-btn" :disabled="isLoading">
    <span v-if="!isLoading" class="btn-content">
      <span class="btn-icon">🚪</span>
      Logout
    </span>
    <span v-else class="btn-loading">
      <span class="spinner"></span>
      Logging out...
    </span>
  </button>
</template>

<script>
import { ref } from 'vue'
import authService from '@/services/authService'
import Swal from 'sweetalert2'

export default {
  name: 'LogoutButton',
  setup() {
    const isLoading = ref(false)

    const handleLogout = async () => {
      if (isLoading.value) return

      isLoading.value = true

      try {
        // Show confirmation dialog
        const result = await Swal.fire({
          title: 'Ready to End Your Adventure? 🏁',
          text: 'Are you sure you want to logout?',
          icon: 'question',
          showCancelButton: true,
          confirmButtonColor: '#3085d6',
          cancelButtonColor: '#d33',
          confirmButtonText: 'Yes, Logout!',
          cancelButtonText: 'Continue Adventure',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          color: 'white'
        })

        if (result.isConfirmed) {
          // Perform logout
          authService.logout()
          
          // Show success message
          await Swal.fire({
            icon: 'success',
            title: 'Adventure Paused! 🎯',
            text: 'Come back soon to continue your quest!',
            timer: 2000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            color: 'white'
          })
        }
      } catch (error) {
        console.error('Logout error:', error)
        
        await Swal.fire({
          icon: 'error',
          title: 'Oops! Something went wrong 🚫',
          text: 'Please try logging out again.',
          timer: 3000,
          showConfirmButton: false,
          background: 'linear-gradient(135deg, #ff6b6b, #ffa726)',
          color: 'white'
        })
      } finally {
        isLoading.value = false
      }
    }

    return {
      isLoading,
      handleLogout
    }
  }
}
</script>

<style scoped>
.logout-btn {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.logout-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.logout-btn:active:not(:disabled) {
  transform: translateY(0);
}

.logout-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  font-size: 16px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 