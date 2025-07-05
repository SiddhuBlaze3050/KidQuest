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
                    <h1>🛡️ {{ getCurrentLesson().title }}</h1>
                    <div class="lesson-progress">
                        <span class="progress-text">Lesson {{ currentLessonIndex + 1 }} of {{ safetyLessons.length
                            }}</span>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: `${getOverallProgress()}%` }"></div>
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
                <!-- Lesson Navigation Sidebar -->
                <div class="lesson-sidebar">
                    <h3>📚 Lessons</h3>
                    <div class="lesson-list">
                        <div v-for="(lesson, index) in safetyLessons" :key="lesson.id"
                            :class="['lesson-item', { active: index === currentLessonIndex, completed: lesson.completed }]"
                            @click="selectLesson(index)">
                            <div class="lesson-icon">{{ lesson.icon }}</div>
                            <div class="lesson-info">
                                <div class="lesson-title">{{ lesson.title }}</div>
                                <div class="lesson-desc">{{ lesson.description }}</div>
                            </div>
                            <div class="lesson-status">
                                <span v-if="lesson.completed">✅</span>
                                <span v-else-if="index === currentLessonIndex">👀</span>
                                <span v-else>⏳</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Main Content Area -->
                <div class="safety-iframe-container">
                    <iframe ref="safetyIframe" :src="getCurrentLesson().url" class="safety-iframe"
                        :title="getCurrentLesson().title" frameborder="0" allowfullscreen @load="onIframeLoad">
                    </iframe>
                    <div v-if="isLoadingSafety" class="loading-overlay">
                        <div class="loading-spinner">🔄</div>
                        <p>Loading {{ getCurrentLesson().title }}...</p>
                    </div>
                </div>
            </div>
        </main>

        <!-- Controls Footer -->
        <footer class="module-controls">
            <div class="container">
                <div class="controls-content">
                    <div class="nav-controls">
                        <button @click="previousLesson" :disabled="currentLessonIndex === 0"
                            class="control-btn nav-btn">
                            <span>⬅️</span> Previous
                        </button>
                        <button @click="markCurrentLessonComplete" class="control-btn complete-btn">
                            <span>✅</span> Mark Complete
                        </button>
                        <button @click="nextLesson" :disabled="currentLessonIndex === safetyLessons.length - 1"
                            class="control-btn nav-btn">
                            <span>➡️</span> Next
                        </button>
                    </div>
                    <div class="utility-controls">
                        <button @click="resetZoom" class="control-btn">
                            <span>🔍</span> Reset Zoom
                        </button>
                        <button @click="toggleFullscreen" class="control-btn">
                            <span>📱</span> Fullscreen
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
import { userUtils } from '@/services/api'
import Swal from 'sweetalert2'

export default {
    name: 'GoodTouchBadTouchModule',
    setup() {
        const router = useRouter()
        const user = ref(userUtils.getCurrentUser())
        const isLoadingSafety = ref(false)
        const safetyIframe = ref(null)
        const currentLessonIndex = ref(0)

        // Safety Module Lessons from Child Chapter
        const safetyLessons = ref([
            {
                id: 1,
                title: 'Private Body Parts',
                description: 'Learn about private body parts and body boundaries',
                url: 'https://www.childchapter.org/GoodTouch%26BadTouch.html',
                icon: '👤',
                completed: false
            },
            {
                id: 2,
                title: 'Good Touch & Bad Touch',
                description: 'Understanding the difference between good and bad touch',
                url: 'https://www.childchapter.org/GoodTouch%26BadTouch.html',
                icon: '🛡️',
                completed: false
            },
            {
                id: 3,
                title: 'How To Protect Yourself',
                description: 'Learn strategies to stay safe and protect yourself',
                url: 'https://www.childchapter.org/GoodTouch%26BadTouch.html',
                icon: '🔒',
                completed: false
            },
            {
                id: 4,
                title: 'Say Stop',
                description: 'Learn when and how to say NO and STOP',
                url: 'https://www.childchapter.org/GoodTouch%26BadTouch.html',
                icon: '✋',
                completed: false
            },
            {
                id: 5,
                title: 'Tell Trusted People',
                description: 'Identify and talk to trusted adults',
                url: 'https://www.childchapter.org/GoodTouch%26BadTouch.html',
                icon: '👨‍👩‍👧‍👦',
                completed: false
            },
            {
                id: 6,
                title: 'Call Child Helpline',
                description: 'When and how to call for help (1098 in India)',
                url: 'https://www.childchapter.org/GoodTouch%26BadTouch.html',
                icon: '📞',
                completed: false
            }
        ])

        // Navigation Functions
        const goBack = () => {
            router.push('/child-dashboard')
        }

        const getCurrentLesson = () => {
            return safetyLessons.value[currentLessonIndex.value] || safetyLessons.value[0]
        }

        const selectLesson = (index) => {
            currentLessonIndex.value = index
            isLoadingSafety.value = true
            updateSafetyProgress()

            setTimeout(() => {
                isLoadingSafety.value = false
            }, 1000)
        }

        const nextLesson = () => {
            if (currentLessonIndex.value < safetyLessons.value.length - 1) {
                currentLessonIndex.value++
                isLoadingSafety.value = true
                updateSafetyProgress()

                setTimeout(() => {
                    isLoadingSafety.value = false
                }, 1000)
            }
        }

        const previousLesson = () => {
            if (currentLessonIndex.value > 0) {
                currentLessonIndex.value--
                isLoadingSafety.value = true
                updateSafetyProgress()

                setTimeout(() => {
                    isLoadingSafety.value = false
                }, 1000)
            }
        }

        const markCurrentLessonComplete = () => {
            const currentLesson = safetyLessons.value[currentLessonIndex.value]
            if (!currentLesson.completed) {
                currentLesson.completed = true
                updateSafetyProgress()

                Swal.fire({
                    icon: 'success',
                    title: '🎉 Lesson Completed!',
                    text: `Great job completing "${currentLesson.title}"! You're making great progress in staying safe.`,
                    timer: 3000,
                    showConfirmButton: false,
                    background: 'linear-gradient(135deg, #4CAF50, #81C784)',
                    color: 'white'
                })

                // Auto-advance to next lesson if available
                if (currentLessonIndex.value < safetyLessons.value.length - 1) {
                    setTimeout(() => {
                        nextLesson()
                    }, 2000)
                }
            }
        }

        const getOverallProgress = () => {
            const completedLessons = safetyLessons.value.filter(lesson => lesson.completed).length
            return Math.round((completedLessons / safetyLessons.value.length) * 100)
        }

        const updateSafetyProgress = () => {
            const progressData = {
                currentLessonIndex: currentLessonIndex.value,
                lessons: safetyLessons.value.map(lesson => ({
                    id: lesson.id,
                    completed: lesson.completed
                })),
                lastAccessed: Date.now()
            }

            localStorage.setItem(`safetyProgress_${user.value?.id || 'guest'}`, JSON.stringify(progressData))
        }

        const loadSafetyProgress = () => {
            try {
                const savedProgress = localStorage.getItem(`safetyProgress_${user.value?.id || 'guest'}`)
                if (savedProgress) {
                    const progressData = JSON.parse(savedProgress)
                    currentLessonIndex.value = progressData.currentLessonIndex || 0

                    if (progressData.lessons) {
                        progressData.lessons.forEach(savedLesson => {
                            const lesson = safetyLessons.value.find(l => l.id === savedLesson.id)
                            if (lesson) {
                                lesson.completed = savedLesson.completed
                            }
                        })
                    }
                }
            } catch (error) {
                console.error('Error loading safety progress:', error)
            }
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
                    const style = iframeDoc.createElement('style')
                    style.textContent = `
                        header, nav, .header, .navbar, .navigation { display: none !important; }
                        .container { margin-top: 0 !important; padding-top: 0 !important; }
                        body { margin-top: 0 !important; padding-top: 0 !important; }
                    `
                    iframeDoc.head.appendChild(style)
                }
            } catch (error) {
                console.log('Cannot access iframe content due to CORS policy - this is expected for external sites')
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
        onMounted(() => {
            loadSafetyProgress()
            isLoadingSafety.value = true

            // Show welcome message
            Swal.fire({
                icon: 'info',
                title: '🛡️ Safety Learning Adventure',
                text: 'Welcome to your safety learning module! Learn about Good Touch & Bad Touch to stay safe and protected.',
                timer: 3000,
                showConfirmButton: false,
                background: 'linear-gradient(135deg, #fd79a8, #fdcb6e)',
                color: 'white'
            })

            setTimeout(() => {
                isLoadingSafety.value = false
            }, 1500)
        })

        return {
            user,
            isLoadingSafety,
            safetyIframe,
            currentLessonIndex,
            safetyLessons,
            goBack,
            getCurrentLesson,
            selectLesson,
            nextLesson,
            previousLesson,
            markCurrentLessonComplete,
            getOverallProgress,
            updateSafetyProgress,
            loadSafetyProgress,
            showSafetyInfo,
            onIframeLoad,
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
.lesson-progress {
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
    height: 70vh;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
}

/* Sidebar */
.lesson-sidebar {
    width: 300px;
    background: rgba(255, 255, 255, 0.1);
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1.5rem;
    overflow-y: auto;
    color: white;
}

.lesson-sidebar h3 {
    color: white;
    margin-bottom: 1.5rem;
    font-size: 1.2rem;
}

.lesson-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.lesson-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.lesson-item:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
}

.lesson-item.active {
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.lesson-item.completed {
    background: rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.3);
}

.lesson-icon {
    font-size: 1.8rem;
    min-width: 35px;
}

.lesson-info {
    flex: 1;
}

.lesson-title {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 0.5rem;
}

.lesson-desc {
    font-size: 0.8rem;
    opacity: 0.8;
    line-height: 1.4;
}

.lesson-status {
    font-size: 1.5rem;
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

.nav-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.utility-controls {
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

.nav-btn:disabled {
    background: rgba(255, 255, 255, 0.3);
    color: rgba(255, 255, 255, 0.6);
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
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
    }

    .progress-bar {
        width: 150px;
    }

    .module-body {
        flex-direction: column;
        height: auto;
    }

    .lesson-sidebar {
        width: 100%;
        height: 200px;
        border-right: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }

    .lesson-list {
        flex-direction: row;
        gap: 1rem;
        overflow-x: auto;
        padding-bottom: 1rem;
    }

    .lesson-item {
        min-width: 250px;
        flex-shrink: 0;
    }

    .controls-content {
        flex-direction: column;
        gap: 1rem;
    }
}

/* Fullscreen styles */
.good-touch-bad-touch-module:fullscreen {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>