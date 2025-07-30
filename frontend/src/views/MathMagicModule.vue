<template>
    <div class="math-magic-module">
        <!-- Header -->
        <header class="magic-header">
            <div class="container">
                <div class="header-content">
                    <button @click="goBack" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        <span>🏠 Back to Adventure Base</span>
                    </button>
                    <div class="magic-title">
                        <h1>📚✨ Math Story Adventures ✨📖</h1>
                        <p class="magic-subtitle">Discover Math Through Fascinating Stories and Picture Books!</p>
                    </div>
                    <button @click="markComplete" class="complete-magic-btn" v-if="!isCompleted">
                        ⭐ Master Math Stories! ⭐
                    </button>
                    <div v-if="isCompleted" class="completed-badge">
                        ✅ Mastered!
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="magic-main">
            <div class="magic-body">
                <div class="math-playground">
                    <div v-if="isLoading" class="loading-magic">
                        <div class="loading-animation">
                            <div class="loading-wand">🪄</div>
                            <div class="loading-numbers">
                                <span>1</span>
                                <span>2</span>
                                <span>3</span>
                                <span>🔢</span>
                            </div>
                        </div>
                        <h3>Preparing Your Story Adventure...</h3>
                        <p>Getting your interactive math stories ready!</p>
                    </div>

                    <div v-show="!isLoading && !hasError" class="math-storybook">
                        <div class="storybook-container">
                            <div class="story-header">
                                <h2>📚 Math Story Collection 📚</h2>
                                <p>Interactive Math Stories & Visual Learning</p>
                            </div>

                            <div class="story-navigation">
                                <button @click="currentStory = 0" :class="{ active: currentStory === 0 }"
                                    class="story-tab">
                                    🔢 Numbers Adventure
                                </button>
                                <button @click="currentStory = 1" :class="{ active: currentStory === 1 }"
                                    class="story-tab">
                                    📐 Shape Explorer
                                </button>
                                <button @click="currentStory = 2" :class="{ active: currentStory === 2 }"
                                    class="story-tab">
                                    ➕ Addition Fun
                                </button>
                            </div>

                            <div class="story-content" v-if="currentStory === 0">
                                <div class="story-page">
                                    <h3>🎯 The Great Number Detective</h3>
                                    <div class="story-visual">
                                        <div class="number-display">
                                            <div class="number-card">1</div>
                                            <div class="number-card">2</div>
                                            <div class="number-card">3</div>
                                            <div class="number-card">4</div>
                                            <div class="number-card">5</div>
                                        </div>
                                    </div>
                                    <p class="story-text">
                                        Once upon a time, there was a detective who loved numbers!
                                        Every day, he would count all the amazing things around him.
                                        Can you help him count? Point to each number and say it out loud!
                                    </p>
                                    <div class="interactive-area">
                                        <p><strong>Try this:</strong> Click on each number to see what happens! 🎉</p>
                                        <div class="clickable-numbers">
                                            <span v-for="n in 5" :key="n" @click="numberClicked(n)"
                                                class="clickable-number"
                                                :class="{ clicked: clickedNumbers.includes(n) }">
                                                {{ n }}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="story-content" v-if="currentStory === 1">
                                <div class="story-page">
                                    <h3>🔶 The Shape Kingdom</h3>
                                    <div class="story-visual">
                                        <div class="shapes-display">
                                            <div class="shape circle">⭕</div>
                                            <div class="shape square">🟦</div>
                                            <div class="shape triangle">🔺</div>
                                            <div class="shape star">⭐</div>
                                        </div>
                                    </div>
                                    <p class="story-text">
                                        In the magical Shape Kingdom, every shape has a special power!
                                        The circle rolls everywhere, the square builds strong walls,
                                        the triangle makes pointy mountains, and the star grants wishes!
                                    </p>
                                    <div class="interactive-area">
                                        <p><strong>Shape Challenge:</strong> Can you name each shape? Click to learn
                                            more!</p>
                                        <div class="shape-quiz">
                                            <div v-for="(shape, index) in shapes" :key="index"
                                                @click="shapeClicked(index)" class="quiz-shape"
                                                :class="{ revealed: revealedShapes.includes(index) }">
                                                <div class="shape-icon">{{ shape.icon }}</div>
                                                <div class="shape-name" v-if="revealedShapes.includes(index)">{{
                                                    shape.name }}</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="story-content" v-if="currentStory === 2">
                                <div class="story-page">
                                    <h3>🧮 The Addition Bakery</h3>
                                    <div class="story-visual">
                                        <div class="bakery-display">
                                            <div class="equation-visual">
                                                <div class="ingredient">🍎 2</div>
                                                <div class="plus">+</div>
                                                <div class="ingredient">🍎 3</div>
                                                <div class="equals">=</div>
                                                <div class="result">🍎 5</div>
                                            </div>
                                        </div>
                                    </div>
                                    <p class="story-text">
                                        Welcome to the Addition Bakery! Here, we combine ingredients to make delicious
                                        treats.
                                        When we add 2 apples and 3 apples together, we get 5 apples total!
                                        Math is everywhere in cooking and baking!
                                    </p>
                                    <div class="interactive-area">
                                        <p><strong>Baking Challenge:</strong> Try making your own recipe!</p>
                                        <div class="baking-game">
                                            <div class="recipe-maker">
                                                <select v-model="ingredient1" class="ingredient-select">
                                                    <option value="🍎">🍎 Apples</option>
                                                    <option value="🍪">🍪 Cookies</option>
                                                    <option value="🧁">🧁 Cupcakes</option>
                                                </select>
                                                <input v-model="num1" type="number" min="1" max="10"
                                                    class="number-input">
                                                <span class="operator">+</span>
                                                <select v-model="ingredient2" class="ingredient-select">
                                                    <option value="🍎">🍎 Apples</option>
                                                    <option value="🍪">🍪 Cookies</option>
                                                    <option value="🧁">🧁 Cupcakes</option>
                                                </select>
                                                <input v-model="num2" type="number" min="1" max="10"
                                                    class="number-input">
                                                <span class="equals-sign">=</span>
                                                <div class="result-display">
                                                    {{ ingredient1 === ingredient2 ? ingredient1 : '🍰' }} {{
                                                        parseInt(num1) + parseInt(num2) }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Info panel when stories are completed -->
                    <div v-if="allStoriesExplored" class="completion-panel">
                        <div class="completion-content">
                            <div class="completion-icon">🎉📚🎉</div>
                            <h3>Amazing! You've Explored All Stories!</h3>
                            <p>You've interacted with numbers, learned about shapes, and practiced addition!</p>
                            <p>Ready to become a Math Story Master?</p>

                            <div class="completion-actions">
                                <button @click="resetStories" class="reset-btn">
                                    🔄 Read Stories Again
                                </button>
                                <button @click="openAlternativeMath" class="explore-more-btn">
                                    🌟 Explore More Math Content
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import Swal from 'sweetalert2'

const router = useRouter()
const user = ref(userUtils.getCurrentUser())

// State management
const isLoading = ref(false) // No longer loading since we have embedded content
const hasError = ref(false)
const isCompleted = ref(false)

// Story navigation
const currentStory = ref(0)

// Interactive elements
const clickedNumbers = ref([])
const revealedShapes = ref([])
const shapes = ref([
    { icon: '⭕', name: 'Circle' },
    { icon: '🟦', name: 'Square' },
    { icon: '🔺', name: 'Triangle' },
    { icon: '⭐', name: 'Star' }
])

// Addition game
const ingredient1 = ref('🍎')
const ingredient2 = ref('🍎')
const num1 = ref(2)
const num2 = ref(3)

// Methods
const goBack = () => {
    router.push('/child-dashboard')
}

// Interactive story methods
const numberClicked = (number) => {
    if (!clickedNumbers.value.includes(number)) {
        clickedNumbers.value.push(number)
        console.log(`🎉 Number ${number} clicked!`)
    }
}

const shapeClicked = (index) => {
    if (!revealedShapes.value.includes(index)) {
        revealedShapes.value.push(index)
        console.log(`🎉 Shape ${shapes.value[index].name} revealed!`)
    }
}

const resetStories = () => {
    clickedNumbers.value = []
    revealedShapes.value = []
    currentStory.value = 0
    console.log('🔄 Stories reset - ready to explore again!')
}

// Computed property to check if all interactive elements have been explored
const allStoriesExplored = computed(() => {
    return clickedNumbers.value.length === 5 && revealedShapes.value.length === 4
})

const openAlternativeMath = () => {
    // Alternative math storybooks and picture books
    const alternatives = [
        { name: 'Clark Ness Math Picture Books', url: 'https://www.clarkness.com/Reading%20files/Picture%20Books/' },
        { name: 'Global Digital Library Math Stories', url: 'https://content.digitallibrary.io/book/level-up-multiplication-division-word-problems/' },
        { name: 'Archive.org Children\'s Math Books', url: 'https://archive.org/search.php?query=mathematics%20children%20picture%20books' }
    ]

    Swal.fire({
        title: '📚 Choose Your Math Story Adventure!',
        html: `
            <div style="text-align: left;">
                <p style="margin-bottom: 1rem;">Try these amazing math storybooks and picture books:</p>
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
        background: 'linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%)',
        color: 'white',
        width: '500px'
    })
}



const markComplete = async () => {
    try {
        const result = await Swal.fire({
            title: '🎉 Math Stories Mastered!',
            html: `
                <div style="text-align: center; line-height: 1.8;">
                    <div style="font-size: 4rem; margin: 1rem 0;">📚✨📖</div>
                    <p style="font-size: 1.2rem; color: #4a5568; font-weight: 600;">
                        Congratulations! You've mastered Math Story Adventures!
                    </p>
                    <p style="color: #718096; margin: 1rem 0;">
                        Your mathematical storytelling skills are now legendary! 🌟
                    </p>
                    <div style="font-size: 3rem; margin: 1rem 0;">⭐🏆⭐</div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: '🎯 Mark as Complete!',
            cancelButtonText: '🔢 Continue Learning',
            background: 'linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%)',
            color: 'white',
            customClass: {
                popup: 'math-magic-popup',
                confirmButton: 'magic-confirm-btn',
                cancelButton: 'magic-cancel-btn'
            }
        })

        if (result.isConfirmed) {
            isCompleted.value = true
            await saveProgress()

            // Success message
            await Swal.fire({
                title: 'Math Story Master!',
                html: `
                    <div style="text-align: center;">
                        <div style="font-size: 4rem; margin: 1rem 0;">🎊📚🎊</div>
                        <p style="font-size: 1.1rem; color: #4a5568;">
                            You are now a Math Story Adventures Master!
                        </p>
                        <div style="font-size: 3rem; margin: 1rem 0;">📈💪📖</div>
                    </div>
                `,
                timer: 3000,
                timerProgressBar: true,
                background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                color: 'white'
            })
        }
    } catch (error) {
        console.error('Error marking Math Magic complete:', error)
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
        localStorage.setItem(`mathMagic_${user.value?.id}`, JSON.stringify(progressData))

        // Save to backend
        await apiService.saveModuleProgress(user.value?.id, 'math_magic', progressData)

    } catch (error) {
        console.error('Error saving Math Magic progress:', error)
    }
}

const loadProgress = async () => {
    try {
        const response = await apiService.getModuleProgress(user.value?.id, 'math_magic')
        console.log('🔢 Math Magic progress response:', response)
        if (response.success && response.progress) {
            const progressData = response.progress.progress_data || response.progress
            isCompleted.value = progressData.completed || false
            console.log('✅ Math Magic progress loaded:', isCompleted.value)
        } else {
            // No backend progress, show not completed
            isCompleted.value = false
            console.log('📉 No backend progress for Math Magic, showing not completed')
        }
    } catch (error) {
        console.error('Error loading Math Magic progress:', error)
        // On error, show not completed
        isCompleted.value = false
    }
}

onMounted(() => {
    loadProgress()
    console.log('✅ Math Stories module loaded successfully!')
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.math-magic-module {
    min-height: 100vh;
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
    position: relative;
    overflow-x: hidden;
    font-family: 'Merriweather', serif;
}

/* Header */
.magic-header {
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

.magic-title {
    text-align: center;
    color: white;
    flex: 1;
}

.magic-title h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.magic-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    margin-top: 0.5rem;
}

.complete-magic-btn {
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

.complete-magic-btn:hover {
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

/* Main Content */
.magic-main {
    padding: 2rem 0;
    max-width: 1200px;
    margin: 0 auto;
}

.math-playground {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    background: white;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    margin: 0 1rem;
}

/* Math Storybook Styles */
.math-storybook {
    width: 100%;
    height: 600px;
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.storybook-container {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.story-header {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
    color: white;
    padding: 1.5rem;
    text-align: center;
    border-radius: 20px 20px 0 0;
}

.story-header h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.8rem;
    font-weight: 700;
}

.story-header p {
    margin: 0;
    opacity: 0.9;
    font-size: 1rem;
}

.story-navigation {
    display: flex;
    background: #f8f9fa;
    border-bottom: 2px solid #e9ecef;
}

.story-tab {
    flex: 1;
    padding: 1rem;
    background: none;
    border: none;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #6c757d;
}

.story-tab:hover {
    background: rgba(255, 107, 107, 0.1);
    color: #ff6b6b;
}

.story-tab.active {
    background: white;
    color: #ff6b6b;
    border-bottom: 3px solid #ff6b6b;
}

.story-content {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
    background: white;
}

.story-page h3 {
    color: #333;
    font-size: 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
}

.story-visual {
    background: linear-gradient(135deg, #fff3e0 0%, #ffeaa7 100%);
    border-radius: 15px;
    padding: 2rem;
    margin: 1rem 0;
    text-align: center;
}

.number-display,
.shapes-display {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.number-card {
    width: 60px;
    height: 60px;
    background: #ff6b6b;
    color: white;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    animation: bounce 2s ease-in-out infinite;
}

.number-card:nth-child(even) {
    animation-delay: 0.5s;
    background: #ffa726;
    box-shadow: 0 4px 15px rgba(255, 167, 38, 0.3);
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-10px);
    }
}

.shape {
    font-size: 3rem;
    margin: 0.5rem;
    animation: rotate 4s ease-in-out infinite;
}

@keyframes rotate {

    0%,
    100% {
        transform: rotate(0deg);
    }

    50% {
        transform: rotate(10deg);
    }
}

.story-text {
    font-size: 1.1rem;
    line-height: 1.6;
    color: #4a5568;
    margin: 1.5rem 0;
    text-align: center;
}

.interactive-area {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 15px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    border: 2px dashed #ff6b6b;
}

.clickable-numbers {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}

.clickable-number {
    width: 50px;
    height: 50px;
    background: #e9ecef;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #6c757d;
}

.clickable-number:hover {
    background: #ff6b6b;
    color: white;
    transform: scale(1.1);
}

.clickable-number.clicked {
    background: #28a745;
    color: white;
    transform: scale(1.2);
    animation: pulse 1s ease-in-out;
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1.2);
    }

    50% {
        transform: scale(1.3);
    }
}

.shape-quiz {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}

.quiz-shape {
    background: white;
    border: 3px solid #e9ecef;
    border-radius: 15px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    min-width: 100px;
}

.quiz-shape:hover {
    border-color: #ff6b6b;
    transform: translateY(-5px);
    box-shadow: 0 8px 20px rgba(255, 107, 107, 0.2);
}

.quiz-shape.revealed {
    border-color: #28a745;
    background: #d4edda;
}

.shape-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.shape-name {
    font-weight: bold;
    color: #28a745;
}

.equation-visual {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    font-size: 1.5rem;
    font-weight: bold;
    flex-wrap: wrap;
}

.ingredient,
.result {
    background: white;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    border: 2px solid #ffa726;
    color: #333;
}

.plus,
.equals {
    font-size: 2rem;
    color: #ff6b6b;
    font-weight: bold;
}

.recipe-maker {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}

.ingredient-select,
.number-input {
    padding: 0.5rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-size: 1rem;
    background: white;
}

.ingredient-select:focus,
.number-input:focus {
    border-color: #ff6b6b;
    outline: none;
}

.number-input {
    width: 60px;
    text-align: center;
    font-weight: bold;
}

.operator,
.equals-sign {
    font-size: 1.5rem;
    font-weight: bold;
    color: #ff6b6b;
    margin: 0 0.5rem;
}

.result-display {
    background: #d4edda;
    border: 2px solid #28a745;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: bold;
    color: #155724;
    min-width: 80px;
    text-align: center;
}

/* Completion Panel Styles */
.completion-panel {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 20px;
    z-index: 20;
}

.completion-content {
    text-align: center;
    color: white;
    padding: 2rem;
    max-width: 500px;
}

.completion-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.completion-content h3 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: white;
}

.completion-content p {
    margin-bottom: 1rem;
    line-height: 1.6;
    opacity: 0.9;
}

.completion-actions {
    display: flex;
    gap: 1rem;
    margin: 2rem 0;
    justify-content: center;
    flex-wrap: wrap;
}

.reset-btn,
.explore-more-btn {
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

.reset-btn:hover,
.explore-more-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.explore-more-btn {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
    border-color: transparent;
}

.loading-magic {
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
    min-height: 600px;
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

.loading-numbers {
    display: flex;
    gap: 0.5rem;
}

.loading-numbers span {
    font-size: 1.5rem;
    animation: bounce 1s ease-in-out infinite;
    font-weight: bold;
    color: #ff6b6b;
}

.loading-numbers span:nth-child(1) {
    animation-delay: 0s;
}

.loading-numbers span:nth-child(2) {
    animation-delay: 0.2s;
}

.loading-numbers span:nth-child(3) {
    animation-delay: 0.4s;
}

.loading-numbers span:nth-child(4) {
    animation-delay: 0.6s;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-10px);
    }
}

.loading-magic h3 {
    color: #4a5568;
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
}

.loading-magic p {
    color: #718096;
    font-size: 1rem;
}



/* Responsive Design */
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .magic-title h1 {
        font-size: 2rem;
    }

    .magic-main {
        padding: 1rem;
    }

    .math-storybook {
        height: 500px !important;
    }

    .story-navigation {
        flex-direction: column;
    }

    .story-tab {
        padding: 0.75rem;
        font-size: 0.9rem;
    }

    .story-content {
        padding: 1rem;
    }

    .number-display,
    .shapes-display {
        gap: 0.5rem;
    }

    .number-card {
        width: 50px;
        height: 50px;
        font-size: 1.5rem;
    }

    .clickable-numbers,
    .shape-quiz {
        gap: 0.5rem;
    }

    .recipe-maker {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }

    .ingredient-select,
    .number-input {
        font-size: 0.9rem;
    }

    .complete-magic-btn,
    .completed-badge {
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
    }

    .fallback-options {
        flex-direction: column;
        align-items: center;
    }
}

/* Custom SweetAlert styles */
:global(.math-magic-popup) {
    border-radius: 20px !important;
}

:global(.magic-confirm-btn) {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
}

:global(.magic-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
}
</style>