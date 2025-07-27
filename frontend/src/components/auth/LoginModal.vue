<template>
    <div class="modal-backdrop" @click="handleBackdropClick">
        <div class="auth-modal" @click.stop>
            <!-- Header -->
            <div class="modal-header">
                <div class="header-icon">🗝️</div>
                <h2>Continue Your Adventure</h2>
                <p>Welcome back, young adventurer!</p>
                <button @click="handleCloseClick" class="close-btn" :disabled="isLoading">&times;</button>
            </div>

            <!-- Form -->
            <div class="modal-body">
                <form @submit.prevent="handleLogin" class="auth-form">
                    <div class="form-group">
                        <label for="username">
                            <i class="fas fa-user"></i>
                            Username
                        </label>
                        <input id="username" v-model="username" type="text" placeholder="Enter your username" required
                            class="form-input" :disabled="isLoading" @input="clearError" />
                    </div>

                    <div class="form-group">
                        <label for="password">
                            <i class="fas fa-lock"></i>
                            Password
                        </label>
                        <input id="password" v-model="password" type="password" placeholder="Enter your password"
                            required class="form-input" :disabled="isLoading" @input="clearError" />
                    </div>

                    <!-- Error Message Display -->
                    <div v-if="errorMessage" class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        {{ errorMessage }}
                    </div>

                    <button type="submit" class="btn-primary" :disabled="isLoading">
                        <span v-if="!isLoading" class="btn-content">
                            <span class="btn-icon">🚀</span>
                            Start Adventure
                        </span>
                        <span v-else class="btn-loading">
                            <span class="spinner"></span>
                            Loading...
                        </span>
                    </button>
                </form>
            </div>

            <!-- Footer -->
            <div class="modal-footer">
                <p>New to KidQuest?</p>
                <button @click="handleSwitchToRegister" class="link-btn" :disabled="isLoading">
                    Create Your Quest <span>✨</span>
                </button>
            </div>

            <!-- Loading Overlay -->
            <div v-if="isLoading" class="loading-overlay">
                <div class="loading-content">
                    <div class="large-spinner"></div>
                    <p>Authenticating your adventure...</p>
                </div>
            </div>

            <!-- Decorative Elements -->
            <div class="floating-icons">
                <div class="float-icon" style="--delay: 0s; --x: 10%; --y: 15%;">⭐</div>
                <div class="float-icon" style="--delay: 1s; --x: 85%; --y: 25%;">🎯</div>
                <div class="float-icon" style="--delay: 2s; --x: 15%; --y: 75%;">💫</div>
                <div class="float-icon" style="--delay: 3s; --x: 80%; --y: 80%;">🌟</div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import authService from '@/services/authService'
import Swal from 'sweetalert2'

export default {
    name: 'LoginModal',
    emits: ['close', 'success', 'switchToRegister'],
    setup(props, { emit }) {
        const username = ref('')
        const password = ref('')
        const isLoading = ref(false)
        const errorMessage = ref('')

        const clearError = () => {
            errorMessage.value = ''
        }

        const handleLogin = async () => {
            if (isLoading.value) return

            isLoading.value = true
            clearError() // Clear any previous error messages

            try {
                console.log('🔐 LoginModal: Attempting login with:', username.value)
                console.log('🔐 LoginModal: Calling authService.login...')
                
                const response = await authService.login(username.value, password.value)
                
                console.log('📊 LoginModal: Received response from authService:', response)
                console.log('📊 LoginModal: Response type:', typeof response)
                console.log('📊 LoginModal: Response success property:', response?.success)
                console.log('📊 LoginModal: Response success check result:', response && response.success === true)

                if (response && response.success === true) {
                    console.log('🎉 LoginModal: Login successful!')
                    console.log('📋 LoginModal: Response data:', response)
                    console.log('👤 LoginModal: User data:', response.user)
                    console.log('🎭 LoginModal: User role:', response.user.role)
                    
                    // Emit success immediately without waiting for alert
                    isLoading.value = false
                    emit('success', response)

                    // Show success message after modal closes
                    setTimeout(() => {
                        Swal.fire({
                            icon: 'success',
                            title: 'Welcome Back, Adventurer! 🎉',
                            text: 'Your quest continues with JWT security!',
                            timer: 2000,
                            showConfirmButton: false,
                            background: 'linear-gradient(135deg, #667eea, #764ba2)',
                            color: 'white'
                        })
                    }, 300)
                } else {
                    // Handle failed login response (wrong credentials)
                    console.log('❌ LoginModal: Login failed with response:', response)
                    console.log('❌ LoginModal: Response success:', response?.success)
                    console.log('❌ LoginModal: Response error:', response?.error)
                    
                    isLoading.value = false
                    const errorText = response?.error || 'Invalid username or password. Please try again.'
                    errorMessage.value = errorText

                    // Show prominent error popup for failed login
                    console.log('🚨 LoginModal: About to show error popup for failed login:', errorText)
                    console.log('🚨 LoginModal: Calling Swal.fire...')
                    
                    Swal.fire({
                        icon: 'error',
                        title: 'Login Failed! 🚫',
                        html: `<div style="font-size: 1.1rem; line-height: 1.5;">
                            <strong>Authentication Error</strong><br>
                            ${errorText}<br><br>
                            <em>Please check your credentials and try again.</em>
                        </div>`,
                        timer: 0, // No auto-close
                        showConfirmButton: true,
                        confirmButtonText: 'Try Again',
                        background: 'linear-gradient(135deg, #ff4444, #cc0000)',
                        color: 'white',
                        confirmButtonColor: '#ff6666',
                        backdrop: 'rgba(0,0,0,0.9)',
                        customClass: {
                            popup: 'error-popup-large',
                            confirmButton: 'error-confirm-btn'
                        },
                        width: '500px',
                        padding: '2rem'
                    }).then(() => {
                        console.log('🚨 LoginModal: Error popup closed')
                    })
                    
                    console.log('🚨 LoginModal: Error popup should now be visible')
                }
            } catch (error) {
                console.error('❌ LoginModal: Login error caught:', error)
                console.error('❌ LoginModal: Error details:', {
                    message: error.message,
                    status: error.response?.status,
                    statusText: error.response?.statusText,
                    data: error.response?.data
                })
                
                isLoading.value = false

                let errorText = 'Connection error. Please check your internet connection and try again.'
                
                // Handle different error types
                if (error.response) {
                    console.log('🌐 LoginModal: Server error response:', error.response)
                    // Server responded with error status
                    if (error.response.status === 401) {
                        errorText = 'Invalid username or password. Please try again.'
                    } else if (error.response.data?.error) {
                        errorText = error.response.data.error
                    }
                } else if (error.request) {
                    // Network error
                    console.log('🌐 LoginModal: Network error:', error.request)
                    errorText = 'Connection error. Please check your internet connection.'
                } else {
                    // Other error
                    console.log('⚠️ LoginModal: Other error:', error.message)
                    errorText = error.message || 'An unexpected error occurred.'
                }

                errorMessage.value = errorText

                // Always show error popup for any login failure
                console.log('🚨 LoginModal: Showing error popup for network/other error:', errorText)
                Swal.fire({
                    icon: 'error',
                    title: 'Login Failed! 🚫',
                    html: `<div style="font-size: 1.1rem; line-height: 1.5;">
                        <strong>Connection Error</strong><br>
                        ${errorText}<br><br>
                        <em>Please check your connection and try again.</em>
                    </div>`,
                    timer: 0, // No auto-close
                    showConfirmButton: true,
                    confirmButtonText: 'Try Again',
                    background: 'linear-gradient(135deg, #ff4444, #cc0000)',
                    color: 'white',
                    confirmButtonColor: '#ff6666',
                    backdrop: 'rgba(0,0,0,0.9)',
                    customClass: {
                        popup: 'error-popup-large',
                        confirmButton: 'error-confirm-btn'
                    },
                    width: '500px',
                    padding: '2rem'
                })
            }
        }

        const handleBackdropClick = () => {
            if (!isLoading.value) {
                emit('close')
            }
        }

        const handleCloseClick = () => {
            if (!isLoading.value) {
                emit('close')
            }
        }

        const handleSwitchToRegister = () => {
            if (!isLoading.value) {
                emit('switchToRegister')
            }
        }

        return {
            username,
            password,
            isLoading,
            errorMessage,
            handleLogin,
            handleBackdropClick,
            handleCloseClick,
            handleSwitchToRegister,
            clearError
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
    max-width: 450px;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    animation: modalSlideIn 0.4s ease-out;
    position: relative;
    overflow: hidden;
    border: 3px solid transparent;
    background-clip: padding-box;
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
    animation: bounce 2s infinite;
}

@keyframes bounce {

    0%,
    20%,
    50%,
    80%,
    100% {
        transform: translateY(0);
    }

    40% {
        transform: translateY(-10px);
    }

    60% {
        transform: translateY(-5px);
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

.close-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
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
    color: #6366f1;
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
    border-color: #6366f1;
    background: white;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    transform: translateY(-2px);
}

.form-input::placeholder {
    color: #9ca3af;
    font-style: italic;
}

.form-input:disabled {
    background: #f3f4f6;
    color: #9ca3af;
    cursor: not-allowed;
    opacity: 0.7;
}

/* Error Message Styles */
.error-message {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    border: 2px solid #ef4444;
    color: #dc2626;
    padding: 1.25rem 1.5rem;
    border-radius: 15px;
    font-size: 1rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 0.5rem;
    animation: errorSlideIn 0.3s ease-out, errorPulse 0.5s ease-in-out;
    box-shadow: 0 8px 25px rgba(220, 38, 38, 0.2);
    position: relative;
    overflow: hidden;
}

.error-message::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ef4444, #dc2626, #ef4444);
    animation: errorGlow 2s linear infinite;
}

.error-message i {
    color: #dc2626;
    font-size: 1.3rem;
    flex-shrink: 0;
    animation: errorIconShake 0.5s ease-in-out;
}

@keyframes errorSlideIn {
    from {
        opacity: 0;
        transform: translateY(-10px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

@keyframes errorPulse {
    0% {
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.2);
    }
    50% {
        box-shadow: 0 8px 35px rgba(220, 38, 38, 0.4);
    }
    100% {
        box-shadow: 0 8px 25px rgba(220, 38, 38, 0.2);
    }
}

@keyframes errorGlow {
    0% {
        background-position: -200% 0;
    }
    100% {
        background-position: 200% 0;
    }
}

@keyframes errorIconShake {
    0%, 100% {
        transform: translateX(0);
    }
    25% {
        transform: translateX(-3px);
    }
    75% {
        transform: translateX(3px);
    }
}

.btn-primary {
    background: linear-gradient(135deg, #ff6b6b, #ffa726);
    color: white;
    border: none;
    padding: 1.2rem 2rem;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
    margin-top: 1rem;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(255, 107, 107, 0.6);
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
    color: #6366f1;
    font-weight: 600;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
    padding: 0.5rem 1rem;
    border-radius: 10px;
}

.link-btn:hover {
    background: rgba(99, 102, 241, 0.1);
    transform: translateY(-2px);
}

.link-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

.link-btn span {
    margin-left: 0.5rem;
    display: inline-block;
    animation: twinkle 1.5s infinite;
}

@keyframes twinkle {

    0%,
    100% {
        opacity: 0.5;
        transform: scale(0.8);
    }

    50% {
        opacity: 1;
        transform: scale(1.2);
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

/* Responsive */
@media (max-width: 480px) {
    .auth-modal {
        width: 95%;
        margin: 1rem;
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
}

/* Loading Overlay */
.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    border-radius: 25px;
}

.loading-content {
    text-align: center;
    color: #667eea;
}

.large-spinner {
    width: 60px;
    height: 60px;
    border: 4px solid #e3f2fd;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.loading-content p {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #667eea;
}

/* Enhanced Error Popup Styles */
:global(.error-popup-large) {
    font-size: 1.1rem !important;
    border-radius: 20px !important;
    box-shadow: 0 20px 60px rgba(255, 68, 68, 0.4) !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
}

:global(.error-confirm-btn) {
    border-radius: 25px !important;
    padding: 12px 30px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.3s ease !important;
}

:global(.error-confirm-btn:hover) {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
}
</style>