<template>
    <div class="good-touch-bad-touch-module">
        <!-- Header -->
        <header class="module-header">
            <div class="container">
                <div class="header-content">
                    <button @click="goBack" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        Back to Dashboard
                    </button>
                    <h1>🛡️ Good Touch & Bad Touch Safety Module</h1>
                    <div class="completion-progress">
                        <span class="progress-text">{{ isCompleted ? '100' : '0' }}% Completed</span>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: `${isCompleted ? 100 : 0}%` }"></div>
                        </div>
                    </div>
                    <button @click="showSafetyInfo" class="info-btn" title="About this module">
                        <span>ℹ️</span>
                    </button>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="module-main">
            <div class="module-body">
                <!-- Main Content Area -->
                <div class="safety-iframe-container">
                    <iframe ref="safetyIframe" src="https://www.childchapter.org/GoodTouch%26BadTouch.html"
                        class="safety-iframe" title="Good Touch & Bad Touch Safety Module" frameborder="0"
                        allowfullscreen @load="onIframeLoad">
                    </iframe>
                    <div v-if="isLoadingSafety" class="loading-overlay">
                        <div class="loading-spinner">🔄</div>
                        <p>Loading Safety Module...</p>
                    </div>
                </div>
            </div>
        </main>

        <!-- Controls Footer -->
        <footer class="module-controls">
            <div class="container">
                <div class="controls-content">
                    <div class="utility-controls">
                        <button @click="resetZoom" class="control-btn">
                            <span>🔍</span> Reset Zoom
                        </button>
                        <button @click="toggleFullscreen" class="control-btn">
                            <span>📱</span> Fullscreen
                        </button>
                        <button @click="resetProgress" class="control-btn reset-btn">
                            <span>🔄</span> Reset Completion
                        </button>
                    </div>
                    <div class="completion-controls">
                        <button @click="markModuleComplete" class="control-btn complete-btn">
                            <span>✅</span> {{ isCompleted ? 'Module Completed!' : 'Mark Complete' }}
                        </button>
                    </div>
                </div>
            </div>
        </footer>
    </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import Swal from 'sweetalert2'

export default {
    name: 'GoodTouchBadTouchModule',
    setup() {
        const router = useRouter()
        const user = ref(userUtils.getCurrentUser())
        const isLoadingSafety = ref(false)
        const safetyIframe = ref(null)
        const isCompleted = ref(false)

        // Navigation Functions
        const goBack = () => {
            router.push('/child-dashboard')
        }

        const markModuleComplete = async () => {
            if (isCompleted.value) {
                console.log('Module already completed, skipping...')
                return
            }

            try {
                const result = await Swal.fire({
                    title: '🛡️ Safety Learning Complete!',
                    html: `
                        <div style="text-align: center; line-height: 1.8;">
                            <div style="font-size: 4rem; margin: 1rem 0;">🛡️🌟💚</div>
                            <p style="font-size: 1.2rem; color: #4a5568; font-weight: 600;">
                                Congratulations! You've learned important safety skills!
                            </p>
                            <p style="color: #718096; margin: 1rem 0;">
                                You now know how to recognize good touch and bad touch to stay safe! 🛡️
                            </p>
                            <div style="font-size: 3rem; margin: 1rem 0;">⭐🛡️⭐</div>
                        </div>
                    `,
                    showCancelButton: true,
                    confirmButtonText: '🛡️ Mark as Complete!',
                    cancelButtonText: '📚 Continue Learning',
                    background: 'linear-gradient(135deg, #4CAF50 0%, #81C784 100%)',
                    color: 'white',
                    customClass: {
                        popup: 'good-touch-popup',
                        confirmButton: 'good-touch-confirm-btn',
                        cancelButton: 'good-touch-cancel-btn'
                    }
                })

                if (result.isConfirmed) {
                    console.log('Marking module as complete...')
                    isCompleted.value = true
                    updateModuleProgress()

                    // Save to backend
                    if (user.value?.id) {
                        try {
                            const progressData = {
                                isCompleted: isCompleted.value,
                                completed: isCompleted.value, // Also include this field for API compatibility
                                is_completed: isCompleted.value, // Include this field as well
                                progress_percentage: isCompleted.value ? 100 : 0,
                                completedAt: Date.now(),
                                lastAccessed: Date.now()
                            }

                            console.log('Saving completion to backend:', progressData)
                            const response = await apiService.saveModuleProgress(user.value.id, 'good_touch_bad_touch', progressData)
                            console.log('✅ Module completion saved to backend successfully:', response)
                        } catch (error) {
                            console.error('❌ Failed to save module completion to backend:', error)
                        }
                    }

                    // Success message
                    await Swal.fire({
                        icon: 'success',
                        title: '🎉 Safety Champion!',
                        text: 'Excellent work! You\'ve completed the Good Touch & Bad Touch safety module. You now know important ways to stay safe and protect yourself.',
                        timer: 4000,
                        showConfirmButton: true,
                        confirmButtonText: 'Great! 👍',
                        background: 'linear-gradient(135deg, #4CAF50, #81C784)',
                        color: 'white'
                    })
                }
            } catch (error) {
                console.error('Error in markModuleComplete:', error)
            }
        }

        const updateModuleProgress = () => {
            const progressData = {
                isCompleted: isCompleted.value,
                completedAt: isCompleted.value ? Date.now() : null,
                lastAccessed: Date.now()
            }

            // Store with new key for module-specific progress
            localStorage.setItem(`safetyModuleProgress_${user.value?.id || 'guest'}`, JSON.stringify(progressData))

            // Also update the dashboard-compatible format
            updateDashboardProgress()
        }

        const loadModuleProgress = async () => {
            try {
                console.log('Loading module progress for user:', user.value?.id)

                // First try to load from backend if user is logged in
                if (user.value?.id) {
                    try {
                        console.log('Attempting to load from backend...')
                        const backendProgress = await apiService.getModuleProgress(user.value.id, 'good_touch_bad_touch')
                        console.log('Backend response:', backendProgress)

                        if (backendProgress.success && backendProgress.progress) {
                            // Check for completion in the main progress object (for modules without submodules)
                            isCompleted.value = backendProgress.progress.is_completed || false
                            console.log(`✅ Module progress loaded from backend: completed: ${isCompleted.value}`)

                            // Also update localStorage with backend data
                            updateModuleProgress()
                            return
                        }
                    } catch (error) {
                        console.log('❌ Backend progress load failed:', error.message)
                    }
                }

                // Fallback to localStorage
                console.log('Attempting to load from localStorage...')
                const savedProgress = localStorage.getItem(`safetyModuleProgress_${user.value?.id || 'guest'}`)
                if (savedProgress) {
                    const progressData = JSON.parse(savedProgress)
                    isCompleted.value = progressData.isCompleted || false
                    console.log(`✅ Module progress loaded from localStorage: completed: ${isCompleted.value}`)
                } else {
                    console.log('📝 No saved progress found - starting fresh')
                }
            } catch (error) {
                console.error('❌ Error loading module progress:', error)
            }
        }

        const updateDashboardProgress = () => {
            // Update the dashboard-compatible format
            const dashboardData = {
                lessons: [
                    { id: 1, completed: isCompleted.value }
                ],
                currentLessonIndex: 0,
                lastAccessed: Date.now()
            }

            localStorage.setItem(`safetyProgress_${user.value?.id || 'guest'}`, JSON.stringify(dashboardData))
        }



        const resetProgress = () => {
            Swal.fire({
                icon: 'warning',
                title: '🔄 Reset Completion?',
                text: 'Are you sure you want to reset your completion status? This will mark the module as incomplete.',
                showCancelButton: true,
                confirmButtonText: 'Yes, Reset',
                cancelButtonText: 'Cancel',
                confirmButtonColor: '#ff6b6b',
                cancelButtonColor: '#6c757d',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white'
            }).then(async (result) => {
                if (result.isConfirmed) {
                    // Reset completion status
                    isCompleted.value = false

                    // Update localStorage
                    updateModuleProgress()

                    // Also reset backend data if user is logged in
                    if (user.value?.id) {
                        try {
                            const resetData = {
                                isCompleted: false,
                                completedAt: null,
                                lastAccessed: Date.now()
                            }

                            console.log('Resetting completion in backend...')
                            const response = await apiService.saveModuleProgress(user.value.id, 'good_touch_bad_touch', resetData)
                            console.log('✅ Completion reset in backend successfully:', response)
                        } catch (error) {
                            console.error('❌ Failed to reset completion in backend:', error)
                        }
                    }

                    // Show success message
                    Swal.fire({
                        icon: 'success',
                        title: '✅ Completion Reset!',
                        text: 'Your completion status has been reset. You can mark the module as complete again.',
                        timer: 2000,
                        showConfirmButton: false,
                        background: 'linear-gradient(135deg, #4CAF50, #81C784)',
                        color: 'white',
                        position: 'top-end',
                        toast: true
                    })
                }
            })
        }

        const showSafetyInfo = () => {
            Swal.fire({
                icon: 'info',
                title: '🛡️ About This Safety Module',
                html: `
                    <div style="text-align: left; line-height: 1.6;">
                        <p><strong>Source:</strong> Child Chapter Association</p>
                        <p><strong>Purpose:</strong> Educational content about Good Touch & Bad Touch</p>
                        <p><strong>Age Group:</strong> Children and adolescents</p>
                        <hr style="margin: 1rem 0;">
                        <p><strong>How to Complete:</strong></p>
                        <ul style="margin-left: 1rem;">
                            <li>Read through the safety content carefully</li>
                            <li>Take your time to understand the important safety information</li>
                            <li>Click "Mark Complete" when you're finished reading</li>
                            <li>Progress will show as 0% until completed, then 100%</li>
                        </ul>
                        <hr style="margin: 1rem 0;">
                        <p><strong>Safety Tips:</strong></p>
                        <ul style="margin-left: 1rem;">
                            <li>Always talk to trusted adults about what you learn</li>
                            <li>Remember: It's okay to say "NO" to uncomfortable situations</li>
                            <li>Your body belongs to you</li>
                            <li>Tell a trusted adult if someone makes you feel unsafe</li>
                        </ul>
                        <p><em>For help in India: Child Helpline 1098</em></p>
                    </div>
                `,
                showConfirmButton: true,
                confirmButtonText: 'Got it! 👍',
                background: 'linear-gradient(135deg, #fd79a8, #fdcb6e)',
                color: 'white',
                width: '600px'
            })
        }

        const onIframeLoad = () => {
            isLoadingSafety.value = false

            try {
                const iframe = safetyIframe.value
                if (iframe && iframe.contentDocument) {
                    const iframeDoc = iframe.contentDocument

                    // Try to hide headers/navigation if possible
                    const style = iframeDoc.createElement('style')
                    style.textContent = `
                        header, nav, .header, .navbar, .navigation { display: none !important; }
                        .container { margin-top: 0 !important; padding-top: 0 !important; }
                        body { margin-top: 0 !important; padding-top: 0 !important; }
                    `
                    iframeDoc.head.appendChild(style)
                }
            } catch (error) {
                console.log('Cannot access iframe content due to CORS policy')
            }
        }

        const resetZoom = () => {
            const iframe = safetyIframe.value
            if (iframe) {
                iframe.style.transform = 'scale(1)'
                iframe.style.transformOrigin = 'top left'
            }
        }

        const toggleFullscreen = () => {
            const module = document.querySelector('.good-touch-bad-touch-module')
            if (module) {
                if (document.fullscreenElement) {
                    document.exitFullscreen()
                } else {
                    module.requestFullscreen().catch(err => {
                        console.log('Fullscreen request failed:', err)
                    })
                }
            }
        }

        // Lifecycle
        onMounted(async () => {
            await loadModuleProgress()

            // Module loads directly since welcome popup is now handled by dashboard
            isLoadingSafety.value = true

            // Show loading message
            const progressMessage = isCompleted.value
                ? 'Welcome back! You have already completed this module. You can review the content or reset your completion status if needed.'
                : 'Loading the Good Touch & Bad Touch safety module. This will help you learn important safety skills!'

            Swal.fire({
                icon: isCompleted.value ? 'success' : 'info',
                title: '🛡️ Loading Safety Module',
                text: progressMessage,
                timer: 3000,
                showConfirmButton: false,
                background: 'linear-gradient(135deg, #4CAF50, #81C784)',
                color: 'white'
            })

            setTimeout(() => {
                isLoadingSafety.value = false
            }, 1500)
        })

        onBeforeUnmount(() => {
            // Cleanup if needed
        })

        return {
            user,
            isLoadingSafety,
            safetyIframe,
            isCompleted,
            goBack,
            markModuleComplete,
            updateModuleProgress,
            loadModuleProgress,
            showSafetyInfo,
            onIframeLoad,
            resetProgress,
            resetZoom,
            toggleFullscreen
        }
    }
}
</script>

<style scoped>
.good-touch-bad-touch-module {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    flex-direction: column;
    font-family: 'Merriweather', serif;
}

/* Header */
.module-header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    color: white;
}

.header-content h1 {
    margin: 0;
    font-size: 1.8rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.back-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.info-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    font-size: 1.5rem;
}

.info-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.1);
}

/* Progress */
.completion-progress {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.progress-text {
    font-size: 0.9rem;
    opacity: 0.9;
    color: white;
}

.progress-bar {
    width: 200px;
    height: 8px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #81C784);
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* Main Content */
.module-main {
    flex: 1;
    padding: 2rem 0;
}

.module-body {
    display: flex;
    height: 75vh;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
}

/* iFrame Container */
.safety-iframe-container {
    flex: 1;
    position: relative;
    background: white;
    margin: 1rem;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: inset 0 5px 15px rgba(0, 0, 0, 0.1);
}

.safety-iframe {
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 15px;
    background: white;
}

.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    color: #333;
    z-index: 10;
}

.loading-spinner {
    font-size: 4rem;
    animation: spin 2s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

/* Footer Controls */
.module-controls {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-top: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 0;
}

.controls-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.utility-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.completion-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.control-btn {
    background: rgba(255, 255, 255, 0.9);
    color: #333;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.control-btn:hover {
    background: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.complete-btn {
    background: linear-gradient(135deg, #4CAF50, #81C784);
    color: white;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.complete-btn:hover {
    background: linear-gradient(135deg, #45a049, #66bb6a);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.reset-btn {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
    color: white;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.reset-btn:hover {
    background: linear-gradient(135deg, #ff5252, #e53935);
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }

    .header-content h1 {
        font-size: 1.5rem;
        text-align: center;
    }

    .progress-bar {
        width: 150px;
    }

    .module-body {
        height: 60vh;
        margin: 0.5rem;
    }

    .safety-iframe-container {
        margin: 0.5rem;
    }

    .controls-content {
        flex-direction: column;
        gap: 1rem;
    }

    .utility-controls {
        order: 2;
    }

    .completion-controls {
        order: 1;
    }
}

/* Fullscreen styles */
.good-touch-bad-touch-module:fullscreen {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Good Touch Bad Touch Module Button Styling */
:global(.good-touch-confirm-btn) {
    background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
    transition: all 0.3s ease !important;
}

:global(.good-touch-confirm-btn:hover) {
    background: linear-gradient(135deg, #45a049 0%, #66bb6a 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
}

:global(.good-touch-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

:global(.good-touch-cancel-btn:hover) {
    background: rgba(255, 255, 255, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* Alternative approach with higher specificity */
:global(.swal2-popup .good-touch-confirm-btn) {
    background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
}

:global(.swal2-popup .good-touch-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
}

/* Welcome Popup Button Styling */
:global(.good-touch-welcome-confirm-btn) {
    background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3) !important;
    transition: all 0.3s ease !important;
}

:global(.good-touch-welcome-confirm-btn:hover) {
    background: linear-gradient(135deg, #45a049 0%, #66bb6a 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4) !important;
}

:global(.good-touch-welcome-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

:global(.good-touch-welcome-cancel-btn:hover) {
    background: rgba(255, 255, 255, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* Alternative approach with higher specificity for welcome popup */
:global(.swal2-popup .good-touch-welcome-confirm-btn) {
    background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
}

:global(.swal2-popup .good-touch-welcome-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
}
</style>