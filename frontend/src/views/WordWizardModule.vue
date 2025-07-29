<template>
    <div class="word-wizard-module">
        <!-- Header -->
        <header class="wizard-header">
            <div class="container">
                <div class="header-content">
                    <button @click="goBack" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        <span>🏠 Back to Adventure Base</span>
                    </button>
                    <div class="wizard-title">
                        <h1>📚✨ Word Wizard Academy ✨📖</h1>
                        <p class="wizard-subtitle">Cast Spells with Words and Expand Your Vocabulary!</p>
                    </div>
                    <button @click="markComplete" class="complete-spell-btn" v-if="!isCompleted">
                        ⭐ Master This Spell Book! ⭐
                    </button>
                    <div v-if="isCompleted" class="completed-badge">
                        ✅ Mastered!
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="wizard-main">
            <div class="wizard-body">
                <div class="vocabulary-playground">
                    <iframe v-if="!iframeError" ref="vocabularyIframe" :src="gameUrl" class="vocabulary-iframe"
                        title="Word Wizard Vocabulary Game" width="100%" height="600" frameborder="0"
                        @load="onIframeLoad" @error="onIframeError"></iframe>

                    <!-- Fallback content when iframe fails -->
                    <div v-if="iframeError" class="iframe-fallback">
                        <div class="fallback-content">
                            <div class="fallback-icon">🚫📱</div>
                            <h3>Oops! Magical Spell Book Blocked</h3>
                            <p>The spell book cannot be displayed here due to security restrictions.</p>
                            <p>But don't worry! You can still access your vocabulary adventure:</p>

                            <div class="fallback-options">
                                <button @click="openInNewTab" class="open-new-tab-btn">
                                    🌟 Open in New Magic Portal
                                </button>
                                <button @click="tryAlternativeContent" class="try-alternative-btn">
                                    🎯 Try Alternative Activities
                                </button>
                            </div>

                            <div class="fallback-instructions">
                                <p><strong>💡 Tip:</strong> After completing activities in the new tab, come back here
                                    and click "Master This Spell Book!" to track your progress.</p>
                            </div>
                        </div>
                    </div>

                    <div v-if="isLoading && !iframeError" class="loading-spell">
                        <div class="loading-animation">
                            <div class="loading-wand">🪄</div>
                            <div class="loading-stars">
                                <span>⭐</span>
                                <span>✨</span>
                                <span>🌟</span>
                                <span>💫</span>
                            </div>
                        </div>
                        <h3>Preparing Your Magical Vocabulary Adventure...</h3>
                        <p>Getting ready for your word learning journey!</p>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import Swal from 'sweetalert2'

const router = useRouter()
const user = ref(userUtils.getCurrentUser())

// State management
const isLoading = ref(true)
const iframeError = ref(false)
const isCompleted = ref(false)

// Single vocabulary game URL
const gameUrl = 'https://www.gamestolearnenglish.com/vocab-game/'

// Methods
const goBack = () => {
    router.push('/child-dashboard')
}

const onIframeLoad = () => {
    isLoading.value = false
}

const onIframeError = () => {
    console.warn('Iframe failed to load, showing fallback options')
    isLoading.value = false
    iframeError.value = true
}

const openInNewTab = () => {
    window.open(gameUrl, '_blank', 'noopener,noreferrer')

    // Show success message
    Swal.fire({
        title: '🌟 Magic Portal Opened!',
        html: `
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin: 1rem 0;">✨🚪✨</div>
                <p>Your vocabulary adventure is now open in a new tab!</p>
                <p style="margin-top: 1rem; color: #666;">
                    Complete the activities there, then come back here to mark as complete.
                </p>
            </div>
        `,
        timer: 4000,
        timerProgressBar: true,
        background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        color: 'white'
    })
}

const tryAlternativeContent = () => {
    // Alternative vocabulary activities that work better with iframes
    const alternatives = [
        { name: 'Room Recess Vocab Games', url: 'https://www.roomrecess.com/mobile/VocabVik/play.html' },
        { name: 'Fast Vocab Game', url: 'https://www.gamestolearnenglish.com/fast-vocab/' },
        { name: 'English Vocabulary Games', url: 'https://www.gamestolearnenglish.com/vocab-game/' }
    ]

    Swal.fire({
        title: '🎯 Choose Your Alternative Adventure!',
        html: `
            <div style="text-align: left;">
                <p style="margin-bottom: 1rem;">Try these vocabulary games instead:</p>
                ${alternatives.map((alt, index) => `
                    <div style="margin: 0.5rem 0; padding: 0.5rem; background: rgba(255,255,255,0.1); border-radius: 8px;">
                        <button onclick="window.open('${alt.url}', '_blank')" 
                                style="background: none; border: none; color: white; text-decoration: underline; cursor: pointer;">
                            ${index + 1}. ${alt.name} →
                        </button>
                    </div>
                `).join('')}
            </div>
        `,
        showConfirmButton: true,
        confirmButtonText: '👍 Got it!',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        width: '500px'
    })
}

const markComplete = async () => {
    try {
        const result = await Swal.fire({
            title: '🎉 Word Wizard Mastered!',
            html: `
                <div style="text-align: center; line-height: 1.8;">
                    <div style="font-size: 4rem; margin: 1rem 0;">🧙‍♂️📚✨</div>
                    <p style="font-size: 1.2rem; color: #4a5568; font-weight: 600;">
                        Congratulations! You've mastered the Word Wizard Academy!
                    </p>
                    <p style="color: #718096; margin: 1rem 0;">
                        Your vocabulary powers are now legendary! 🌟
                    </p>
                    <div style="font-size: 3rem; margin: 1rem 0;">⭐🏆⭐</div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: '🎯 Mark as Complete!',
            cancelButtonText: '📚 Continue Learning',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            customClass: {
                popup: 'word-wizard-popup',
                confirmButton: 'wizard-confirm-btn',
                cancelButton: 'wizard-cancel-btn'
            }
        })

        if (result.isConfirmed) {
            isCompleted.value = true
            await saveProgress()

            // Success message
            await Swal.fire({
                title: 'Word Wizard Level Up!',
                html: `
                    <div style="text-align: center;">
                        <div style="font-size: 4rem; margin: 1rem 0;">🎊🧙‍♂️🎊</div>
                        <p style="font-size: 1.1rem; color: #4a5568;">
                            You are now a Word Wizard Master!
                        </p>
                        <div style="font-size: 3rem; margin: 1rem 0;">📈💪📚</div>
                    </div>
                `,
                timer: 3000,
                timerProgressBar: true,
                background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                color: 'white'
            })
        }
    } catch (error) {
        console.error('Error marking Word Wizard complete:', error)
    }
}

const saveProgress = async () => {
    try {
        const progressData = {
            is_completed: isCompleted.value,
            progress_percentage: isCompleted.value ? 100 : 0,
            completed: isCompleted.value,  // Keep for backward compatibility
            completionPercentage: isCompleted.value ? 100 : 0,  // Keep for backward compatibility
            lastAccessed: new Date().toISOString()
        }

        // Save to localStorage as backup
        localStorage.setItem(`wordWizard_${user.value?.id}`, JSON.stringify(progressData))

        // Save to backend
        await apiService.saveModuleProgress(user.value?.id, 'word_wizard', progressData)

    } catch (error) {
        console.error('Error saving Word Wizard progress:', error)
    }
}

const loadProgress = async () => {
    try {
        const response = await apiService.getModuleProgress(user.value?.id, 'word_wizard')
        console.log('📚 Word Wizard progress response:', response)
        if (response.success && response.progress) {
            const progressData = response.progress.progress_data || response.progress
            isCompleted.value = progressData.completed || false
            console.log('✅ Word Wizard progress loaded:', isCompleted.value)
        } else {
            // No backend progress, show not completed
            isCompleted.value = false
            console.log('📉 No backend progress for Word Wizard, showing not completed')
        }
    } catch (error) {
        console.error('Error loading Word Wizard progress:', error)
        // On error, show not completed
        isCompleted.value = false
    }
}

onMounted(() => {
    loadProgress()

    // Set a timeout to detect if iframe fails to load
    setTimeout(() => {
        if (isLoading.value) {
            console.warn('Iframe loading timeout, showing fallback')
            onIframeError()
        }
    }, 10000) // 10 second timeout
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.word-wizard-module {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    overflow-x: hidden;
    font-family: 'Merriweather', serif;
}

/* Header */
.wizard-header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.back-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 50px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.wizard-title {
    text-align: center;
    color: white;
    flex: 1;
}

.wizard-title h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.wizard-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-top: 0.5rem;
}

.completion-progress {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem;
    min-width: 250px;
    backdrop-filter: blur(5px);
}

.progress-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.progress-icon {
    font-size: 1.5rem;
}

.progress-text {
    font-weight: 700;
    color: white;
}

.progress-details {
    margin-bottom: 0.75rem;
}

.progress-stats {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.stat {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
}

.progress-bar {
    height: 8px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);
    transition: width 0.5s ease;
}

.progress-sparkles {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
}

.sparkle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: white;
    border-radius: 50%;
    animation: sparkle 2s ease-in-out infinite;
}

.sparkle:nth-child(1) {
    left: 10%;
    animation-delay: 0s;
}

.sparkle:nth-child(2) {
    left: 30%;
    animation-delay: 0.4s;
}

.sparkle:nth-child(3) {
    left: 50%;
    animation-delay: 0.8s;
}

.sparkle:nth-child(4) {
    left: 70%;
    animation-delay: 1.2s;
}

.sparkle:nth-child(5) {
    left: 90%;
    animation-delay: 1.6s;
}

@keyframes sparkle {

    0%,
    100% {
        opacity: 0;
        transform: scale(0);
    }

    50% {
        opacity: 1;
        transform: scale(1);
    }
}

/* Main Content */
.wizard-main {
    padding: 2rem 0;
    max-width: 1200px;
    margin: 0 auto;
}

.complete-spell-btn {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 25px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    animation: pulse 2s ease-in-out infinite;
}

.complete-spell-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(67, 233, 123, 0.3);
}

.completed-badge {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    color: white;
    padding: 1rem 2rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.05);
    }
}

/* Vocabulary Playground */
.vocabulary-playground {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    background: white;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.vocabulary-iframe {
    width: 100%;
    height: 600px;
    border: none;
    border-radius: 20px;
}

.loading-spell {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.95);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 10;
}

.loading-animation {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.loading-wand {
    font-size: 3rem;
    animation: float 2s ease-in-out infinite;
}

@keyframes float {

    0%,
    100% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-10px);
    }
}

.loading-stars {
    display: flex;
    gap: 0.5rem;
}

.loading-stars span {
    font-size: 1.5rem;
    animation: twinkle 1s ease-in-out infinite;
}

.loading-stars span:nth-child(1) {
    animation-delay: 0s;
}

.loading-stars span:nth-child(2) {
    animation-delay: 0.2s;
}

.loading-stars span:nth-child(3) {
    animation-delay: 0.4s;
}

.loading-stars span:nth-child(4) {
    animation-delay: 0.6s;
}

@keyframes twinkle {

    0%,
    100% {
        opacity: 0.3;
        transform: scale(0.8);
    }

    50% {
        opacity: 1;
        transform: scale(1.2);
    }
}

.loading-spell h3 {
    color: #4a5568;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.loading-spell p {
    color: #718096;
    font-size: 1rem;
}

/* Iframe Fallback Styles */
.iframe-fallback {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    z-index: 10;
}

.fallback-content {
    text-align: center;
    color: white;
    padding: 2rem;
    max-width: 500px;
}

.fallback-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.fallback-content h3 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
}

.fallback-content p {
    margin-bottom: 1rem;
    line-height: 1.6;
    opacity: 0.9;
}

.fallback-options {
    display: flex;
    gap: 1rem;
    margin: 2rem 0;
    justify-content: center;
    flex-wrap: wrap;
}

.open-new-tab-btn,
.try-alternative-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: 2px solid rgba(255, 255, 255, 0.3);
    padding: 1rem 1.5rem;
    border-radius: 25px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.open-new-tab-btn:hover,
.try-alternative-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.open-new-tab-btn {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    border-color: transparent;
}

.fallback-instructions {
    background: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 15px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.fallback-instructions p {
    margin: 0;
    font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .wizard-title h1 {
        font-size: 2rem;
    }

    .wizard-main {
        padding: 1rem;
    }

    .vocabulary-iframe {
        height: 500px;
    }

    .complete-spell-btn,
    .completed-badge {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
    }
}

/* Custom SweetAlert styles */
:global(.word-wizard-popup) {
    border-radius: 20px !important;
}

:global(.wizard-confirm-btn) {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
}

:global(.wizard-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
}
</style>