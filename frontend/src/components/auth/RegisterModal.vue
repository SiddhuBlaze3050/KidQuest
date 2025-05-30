<template>
    <div class="modal-backdrop" @click="closeModal">
        <div class="auth-modal" @click.stop>
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
                        <label for="username">
                            <i class="fas fa-user"></i>
                            Adventurer Name
                        </label>
                        <input id="username" v-model="username" type="text" placeholder="Choose your adventure name"
                            required class="form-input" />
                    </div>

                    <div class="form-group">
                        <label for="email">
                            <i class="fas fa-envelope"></i>
                            Magic Mail
                        </label>
                        <input id="email" v-model="email" type="email" placeholder="your.magic@email.com" required
                            class="form-input" />
                    </div>

                    <div class="form-group">
                        <label for="password">
                            <i class="fas fa-lock"></i>
                            Secret Code
                        </label>
                        <input id="password" v-model="password" type="password"
                            placeholder="Create a strong secret code" required class="form-input" />
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword">
                            <i class="fas fa-shield-alt"></i>
                            Confirm Secret Code
                        </label>
                        <input id="confirmPassword" v-model="confirmPassword" type="password"
                            placeholder="Confirm your secret code" required class="form-input" />
                    </div>

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
                <button @click="$emit('switchToLogin')" class="link-btn">
                    Continue Your Quest <span>🗝️</span>
                </button>
            </div>

            <!-- Decorative Elements -->
            <div class="floating-icons">
                <div class="float-icon" style="--delay: 0s; --x: 15%; --y: 20%;">🌟</div>
                <div class="float-icon" style="--delay: 1s; --x: 80%; --y: 15%;">🎯</div>
                <div class="float-icon" style="--delay: 2s; --x: 20%; --y: 80%;">🏆</div>
                <div class="float-icon" style="--delay: 3s; --x: 85%; --y: 75%;">⚡</div>
                <div class="float-icon" style="--delay: 4s; --x: 50%; --y: 90%;">🌈</div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { apiService } from '@/services/api'
import Swal from 'sweetalert2'

export default {
    name: 'RegisterModal',
    emits: ['close', 'success', 'switchToLogin'],
    setup(props, { emit }) {
        const username = ref('')
        const email = ref('')
        const password = ref('')
        const confirmPassword = ref('')
        const isLoading = ref(false)

        const handleRegister = async () => {
            if (isLoading.value) return

            // Validation
            if (password.value !== confirmPassword.value) {
                await Swal.fire({
                    icon: 'warning',
                    title: 'Secret Codes Don\'t Match! 🔐',
                    text: 'Make sure both secret codes are identical, young adventurer!',
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
                    text: 'Your secret code needs at least 6 characters to protect your quest!',
                    timer: 3000,
                    showConfirmButton: false,
                    background: 'linear-gradient(135deg, #ffa726, #ff9800)',
                    color: 'white'
                })
                return
            }

            isLoading.value = true

            try {
                const response = await apiService.register(username.value, email.value, password.value)

                if (response.success) {
                    await Swal.fire({
                        icon: 'success',
                        title: 'Welcome to KidQuest! 🎉',
                        text: `Adventure awaits you, ${username.value}! Your quest begins now!`,
                        timer: 3000,
                        showConfirmButton: false,
                        background: 'linear-gradient(135deg, #4caf50, #8bc34a)',
                        color: 'white',
                        backdrop: 'rgba(0,0,0,0.8)'
                    })

                    emit('success', response)
                }
            } catch (error) {
                console.error('Registration failed:', error)

                let errorMessage = 'Something went wrong! Please try again, brave adventurer!'
                if (error.response?.data?.error) {
                    errorMessage = error.response.data.error
                }

                await Swal.fire({
                    icon: 'error',
                    title: 'Quest Creation Failed! 😔',
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

        const closeModal = () => {
            emit('close')
        }

        return {
            username,
            email,
            password,
            confirmPassword,
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
    max-width: 480px;
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
    background: linear-gradient(135deg, #4caf50, #8bc34a, #ff6b6b, #ffa726);
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
    background: linear-gradient(135deg, #4caf50, #8bc34a);
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
    color: #4caf50;
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
    border-color: #4caf50;
    background: white;
    box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    transform: translateY(-2px);
}

.form-input::placeholder {
    color: #9ca3af;
    font-style: italic;
}

.btn-primary {
    background: linear-gradient(135deg, #4caf50, #8bc34a);
    color: white;
    border: none;
    padding: 1.2rem 2rem;
    border-radius: 50px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
    margin-top: 1rem;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(76, 175, 80, 0.6);
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
    color: #4caf50;
    font-weight: 600;
    cursor: pointer;
    font-size: 1rem;
    transition: all 0.3s ease;
    padding: 0.5rem 1rem;
    border-radius: 10px;
}

.link-btn:hover {
    background: rgba(76, 175, 80, 0.1);
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
    background: #4caf50;
    border-radius: 10px;
}

.auth-modal::-webkit-scrollbar-thumb:hover {
    background: #8bc34a;
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
</style>