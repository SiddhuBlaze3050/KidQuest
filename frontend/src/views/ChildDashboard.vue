<template>
    <div class="child-dashboard">
        <!-- Header -->
        <header class="child-header">
            <div class="container">
                <div class="header-content">
                    <div class="child-logo">
                        <span class="logo-icon">🌟</span>
                        <span class="logo-text">My Adventure World</span>
                    </div>
                    <div class="child-user">
                        <div class="user-avatar">{{ user?.username?.charAt(0)?.toUpperCase() || '👤' }}</div>
                        <div class="user-info">
                            <span class="user-greeting">Hi {{ user?.username }}! 👋</span>
                            <span class="user-level">Level {{ userLevel }} Adventurer</span>
                        </div>
                        <button @click="logout" class="logout-btn">
                            <i class="fas fa-sign-out-alt"></i>
                            Exit
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="child-main">
            <div class="container">
                <!-- Welcome Section -->
                <div class="welcome-section">
                    <div class="welcome-card">
                        <h1>Welcome back, brave adventurer! 🏰</h1>
                        <p>Ready for today's exciting quests? Let's learn and have fun together!</p>
                        <div class="daily-streak">
                            <span class="streak-icon">🔥</span>
                            <span class="streak-text">{{ streakDays }} day streak!</span>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats -->
                <div class="stats-row">
                    <div class="stat-bubble">
                        <div class="stat-icon">⭐</div>
                        <div class="stat-number">{{ userStats.totalStars }}</div>
                        <div class="stat-label">Stars Earned</div>
                    </div>

                    <div class="stat-bubble">
                        <div class="stat-icon">🏆</div>
                        <div class="stat-number">{{ userStats.questsCompleted }}</div>
                        <div class="stat-label">Quests Done</div>
                    </div>

                    <div class="stat-bubble">
                        <div class="stat-icon">📚</div>
                        <div class="stat-number">{{ userStats.skillsLearned }}</div>
                        <div class="stat-label">Skills Learned</div>
                    </div>

                    <div class="stat-bubble">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-number">{{ userStats.todayGoals }}</div>
                        <div class="stat-label">Today's Goals</div>
                    </div>
                </div>

                <!-- Today's Quests -->
                <div class="quest-section">
                    <h2 class="section-title">
                        <span class="title-icon">🎯</span>
                        Today's Epic Quests
                    </h2>
                    <div class="quest-grid">
                        <div v-for="quest in todayQuests" :key="quest.id" class="quest-card"
                            :class="{ 'completed': quest.completed }" @click="toggleQuest(quest)">
                            <div class="quest-icon">{{ quest.icon }}</div>
                            <div class="quest-info">
                                <h3>{{ quest.title }}</h3>
                                <p>{{ quest.description }}</p>
                                <div class="quest-reward">
                                    <span class="reward-icon">⭐</span>
                                    <span>{{ quest.stars }} stars</span>
                                </div>
                            </div>
                            <div class="quest-status">
                                <div v-if="quest.completed" class="completed-badge">✅</div>
                                <div v-else class="incomplete-badge">○</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Skills Adventure -->
                <div class="skills-section">
                    <h2 class="section-title">
                        <span class="title-icon">🎨</span>
                        Skill Adventures
                    </h2>
                    <div class="skills-grid">
                        <div v-for="skill in skillAreas" :key="skill.id" class="skill-card"
                            @click="openSkillArea(skill)">
                            <div class="skill-background" :style="{ background: skill.gradient }">
                                <div class="skill-icon">{{ skill.icon }}</div>
                                <h3>{{ skill.name }}</h3>
                                <p>{{ skill.description }}</p>
                                <div class="skill-progress">
                                    <div class="progress-bar">
                                        <div class="progress-fill" :style="{ width: skill.progress + '%' }"></div>
                                    </div>
                                    <span class="progress-text">{{ skill.progress }}% complete</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Fun Activities -->
                <div class="activities-section">
                    <h2 class="section-title">
                        <span class="title-icon">🎮</span>
                        Fun Activities
                    </h2>
                    <div class="activities-grid">
                        <button v-for="activity in funActivities" :key="activity.id" class="activity-btn"
                            @click="startActivity(activity)">
                            <div class="activity-icon">{{ activity.icon }}</div>
                            <div class="activity-name">{{ activity.name }}</div>
                        </button>
                    </div>
                </div>

                <!-- Achievements Showcase -->
                <div class="achievements-section">
                    <h2 class="section-title">
                        <span class="title-icon">🏅</span>
                        My Awesome Achievements
                    </h2>
                    <div class="achievements-grid">
                        <div v-for="achievement in recentAchievements" :key="achievement.id" class="achievement-card">
                            <div class="achievement-medal">{{ achievement.medal }}</div>
                            <h4>{{ achievement.title }}</h4>
                            <p>{{ achievement.description }}</p>
                            <div class="achievement-date">{{ formatDate(achievement.earnedDate) }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <!-- Floating Gandalf Chatbot -->
        <div class="floating-wizard" @click="showChat = true">
            <div class="wizard-icon">🧙‍♂️</div>
            <div class="wizard-sparkles">✨</div>
            <div class="wizard-tooltip">Ask Gandalf!</div>
        </div>

        <!-- 3D Chatbot Modal -->
        <EnhancedChatBot v-if="showChat" @close="showChat = false" :user="user" />

        <!-- Floating Magic Elements -->
        <div class="floating-magic">
            <div class="magic-element" style="--delay: 0s; --x: 10%; --y: 20%;">🌟</div>
            <div class="magic-element" style="--delay: 2s; --x: 90%; --y: 30%;">⭐</div>
            <div class="magic-element" style="--delay: 4s; --x: 15%; --y: 70%;">💫</div>
            <div class="magic-element" style="--delay: 6s; --x: 85%; --y: 80%;">✨</div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { userUtils, apiService } from '@/services/api'
import EnhancedChatBot from '@/components/chat/EnhancedChatBot.vue'
import Swal from 'sweetalert2'

export default {
    name: 'ChildDashboard',
    components: {
        EnhancedChatBot
    },
    setup() {
        const user = ref(null)
        const showChat = ref(false)
        const streakDays = ref(0)
        const userLevel = ref(1)

        // User stats
        const userStats = ref({
            totalStars: 0,
            questsCompleted: 0,
            skillsLearned: 0,
            todayGoals: 0
        })

        // Today's quests
        const todayQuests = ref([
            {
                id: 1,
                title: "Math Adventure",
                description: "Solve 10 fun math puzzles",
                icon: "🔢",
                stars: 10,
                completed: false
            },
            {
                id: 2,
                title: "Reading Quest",
                description: "Read for 20 minutes",
                icon: "📖",
                stars: 8,
                completed: false
            },
            {
                id: 3,
                title: "Tidy Up Mission",
                description: "Clean your room",
                icon: "🧹",
                stars: 5,
                completed: false
            },
            {
                id: 4,
                title: "Hydration Hero",
                description: "Drink 6 glasses of water",
                icon: "💧",
                stars: 6,
                completed: false
            }
        ])

        // Skill areas
        const skillAreas = ref([
            {
                id: 1,
                name: "Math Magic",
                description: "Numbers and problem solving",
                icon: "🔢",
                progress: 0,
                gradient: "linear-gradient(135deg, #ff6b6b, #ffa726)"
            },
            {
                id: 2,
                name: "Word Wizard",
                description: "Reading and writing adventures",
                icon: "📚",
                progress: 0,
                gradient: "linear-gradient(135deg, #4facfe, #00f2fe)"
            },
            {
                id: 3,
                name: "Science Explorer",
                description: "Discover how things work",
                icon: "🔬",
                progress: 0,
                gradient: "linear-gradient(135deg, #a8edea, #fed6e3)"
            },
            {
                id: 4,
                name: "Art Creator",
                description: "Express your creativity",
                icon: "🎨",
                progress: 0,
                gradient: "linear-gradient(135deg, #fbc2eb, #a6c1ee)"
            },
            {
                id: 5,
                name: "Life Skills",
                description: "Important daily habits",
                icon: "🌱",
                progress: 0,
                gradient: "linear-gradient(135deg, #89f7fe, #66a6ff)"
            },
            {
                id: 6,
                name: "Safety Measures",
                description: "Stay safe and protect yourself",
                icon: "🛡️",
                progress: 0,
                gradient: "linear-gradient(135deg, #fd79a8, #fdcb6e)"
            }
        ])

        // Fun activities
        const funActivities = ref([
            { id: 1, name: "Pomodoro Timer", icon: "⏰" },
            { id: 2, name: "Memory Game", icon: "🧠" },
            { id: 3, name: "Drawing Pad", icon: "🖌️" },
            { id: 4, name: "Music Player", icon: "🎵" },
            { id: 5, name: "Story Builder", icon: "📝" },
            { id: 6, name: "Quiz Time", icon: "❓" },
            { id: 7, name: "Psychometric Test", icon: "🧩" }
        ])

        // Recent achievements
        const recentAchievements = ref([
            {
                id: 1,
                title: "Math Master",
                description: "Solved 100 math problems!",
                medal: "🥇",
                earnedDate: new Date('2025-01-20')
            },
            {
                id: 2,
                title: "Reading Warrior",
                description: "Read for 7 days straight!",
                medal: "🥈",
                earnedDate: new Date('2025-01-18')
            },
            {
                id: 3,
                title: "Helpful Hero",
                description: "Completed all chores this week!",
                medal: "🥉",
                earnedDate: new Date('2025-01-15')
            }
        ])

        // Check child access
        const checkChildAccess = () => {
            const currentUser = userUtils.getCurrentUser()
            if (!currentUser || currentUser.role !== 'child') {
                // For demo purposes, allow any user to access child dashboard
                // In production, you would redirect to home
                // window.location.href = '/'
                // return
            }
            user.value = currentUser
        }

        const logout = () => {
            userUtils.logout()
        }

        const toggleQuest = async (quest) => {
            quest.completed = !quest.completed

            if (quest.completed) {
                userStats.value.totalStars += quest.stars

                await Swal.fire({
                    icon: 'success',
                    title: 'Quest Complete! 🎉',
                    text: `Awesome job! You earned ${quest.stars} stars!`,
                    timer: 2000,
                    showConfirmButton: false,
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    color: 'white'
                })
            }
        }

        const openSkillArea = (skill) => {
            console.log('Opening skill area:', skill.name)
            // TODO: Navigate to skill detail page
        }

        const startActivity = (activity) => {
            console.log('Starting activity:', activity.name)

            switch (activity.name) {
                case 'Pomodoro Timer':
                    startPomodoroTimer()
                    break
                case 'Psychometric Test':
                    startPsychometricTest()
                    break
                default:
                    Swal.fire({
                        icon: 'info',
                        title: `${activity.name} 🎮`,
                        text: 'This activity is coming soon! Keep checking back for updates.',
                        timer: 3000,
                        showConfirmButton: false,
                        background: 'linear-gradient(135deg, #667eea, #764ba2)',
                        color: 'white'
                    })
            }
        }

        const startPomodoroTimer = () => {
            Swal.fire({
                title: '🍅 Pomodoro Timer',
                html: `
                    <div style="text-align: center; padding: 20px;">
                        <div style="font-size: 3rem; margin: 20px 0;" id="timer-display">25:00</div>
                        <div style="margin: 20px 0;">
                            <button id="start-timer" style="background: #4CAF50; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer;">Start</button>
                            <button id="pause-timer" style="background: #FF9800; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer;">Pause</button>
                            <button id="reset-timer" style="background: #F44336; color: white; border: none; padding: 10px 20px; margin: 5px; border-radius: 5px; cursor: pointer;">Reset</button>
                        </div>
                        <p style="font-size: 0.9rem; color: #666;">Work for 25 minutes, then take a 5-minute break!</p>
                    </div>
                `,
                showConfirmButton: false,
                showCloseButton: true,
                allowOutsideClick: false,
                width: 400,
                didOpen: () => {
                    let minutes = 25
                    let seconds = 0
                    let isRunning = false
                    let interval

                    const display = document.getElementById('timer-display')
                    const startBtn = document.getElementById('start-timer')
                    const pauseBtn = document.getElementById('pause-timer')
                    const resetBtn = document.getElementById('reset-timer')

                    const updateDisplay = () => {
                        display.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
                    }

                    const startTimer = () => {
                        if (!isRunning) {
                            isRunning = true
                            interval = setInterval(() => {
                                if (seconds === 0) {
                                    if (minutes === 0) {
                                        clearInterval(interval)
                                        isRunning = false
                                        Swal.fire({
                                            icon: 'success',
                                            title: 'Time\'s Up! 🎉',
                                            text: 'Great job! Time for a break!',
                                            timer: 3000,
                                            showConfirmButton: false
                                        })
                                        return
                                    }
                                    minutes--
                                    seconds = 59
                                } else {
                                    seconds--
                                }
                                updateDisplay()
                            }, 1000)
                        }
                    }

                    const pauseTimer = () => {
                        if (isRunning) {
                            clearInterval(interval)
                            isRunning = false
                        }
                    }

                    const resetTimer = () => {
                        clearInterval(interval)
                        isRunning = false
                        minutes = 25
                        seconds = 0
                        updateDisplay()
                    }

                    startBtn.addEventListener('click', startTimer)
                    pauseBtn.addEventListener('click', pauseTimer)
                    resetBtn.addEventListener('click', resetTimer)
                }
            })
        }

        const startPsychometricTest = () => {
            Swal.fire({
                title: '🧩 Psychometric Test',
                html: `
                    <div style="text-align: center; padding: 20px;">
                        <p style="margin-bottom: 20px;">Discover your learning style and personality traits!</p>
                        <div style="margin: 20px 0;">
                            <div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <h4>🎨 Learning Style Assessment</h4>
                                <p>Find out if you're a visual, auditory, or kinesthetic learner</p>
                            </div>
                            <div style="background: linear-gradient(135deg, #ff6b6b, #ffa726); color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <h4>🌟 Personality Discovery</h4>
                                <p>Explore your unique strengths and interests</p>
                            </div>
                            <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; padding: 15px; border-radius: 10px; margin: 10px 0;">
                                <h4>🎯 Focus & Attention</h4>
                                <p>Test your concentration and memory skills</p>
                            </div>
                        </div>
                    </div>
                `,
                showCancelButton: true,
                confirmButtonText: 'Start Test! 🚀',
                cancelButtonText: 'Maybe Later',
                confirmButtonColor: '#667eea',
                width: 500
            }).then((result) => {
                if (result.isConfirmed) {
                    Swal.fire({
                        icon: 'info',
                        title: 'Coming Soon! 🔬',
                        text: 'Our psychometric test is being developed by education experts. Stay tuned!',
                        timer: 3000,
                        showConfirmButton: false,
                        background: 'linear-gradient(135deg, #667eea, #764ba2)',
                        color: 'white'
                    })
                }
            })
        }



        const formatDate = (date) => {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        }

        onMounted(() => {
            checkChildAccess()
        })

        return {
            user,
            showChat,
            streakDays,
            userLevel,
            userStats,
            todayQuests,
            skillAreas,
            funActivities,
            recentAchievements,
            logout,
            toggleQuest,
            openSkillArea,
            startActivity,
            startPomodoroTimer,
            startPsychometricTest,
            formatDate
        }
    }
}
</script>

<style scoped>
.child-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    overflow-x: hidden;
}

/* Header */
.child-header {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
}

.child-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    font-weight: bold;
    color: #6366f1;
}

.logo-icon {
    font-size: 2rem;
    animation: sparkle 2s infinite ease-in-out;
}

@keyframes sparkle {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }
}

.child-user {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.user-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6b6b, #ffa726);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 1.2rem;
}

.user-info {
    display: flex;
    flex-direction: column;
}

.user-greeting {
    font-weight: bold;
    color: #333;
}

.user-level {
    font-size: 0.8rem;
    color: #666;
}

.logout-btn {
    padding: 0.5rem 1rem;
    background: #ff6b6b;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 0.9rem;
}

.logout-btn:hover {
    background: #ff5252;
    transform: translateY(-2px);
}

/* Main Content */
.child-main {
    padding: 2rem 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Welcome Section */
.welcome-section {
    margin-bottom: 2rem;
}

.welcome-card {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.welcome-card h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.welcome-card p {
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    opacity: 0.9;
}

.daily-streak {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255, 107, 107, 0.3);
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-weight: bold;
}

.streak-icon {
    font-size: 1.5rem;
}

/* Stats Row */
.stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 3rem;
}

.stat-bubble {
    background: white;
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
    cursor: pointer;
}

.stat-bubble:hover {
    transform: translateY(-5px);
}

.stat-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.stat-number {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 0.25rem;
}

.stat-label {
    color: #666;
    font-size: 0.9rem;
}

/* Section Titles */
.section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: white;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.title-icon {
    font-size: 2rem;
}

/* Quest Section */
.quest-section {
    margin-bottom: 3rem;
}

.quest-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.quest-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s;
    border: 3px solid transparent;
}

.quest-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.quest-card.completed {
    border-color: #4caf50;
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
}

.quest-icon {
    font-size: 2.5rem;
    min-width: 60px;
    text-align: center;
}

.quest-info {
    flex: 1;
}

.quest-info h3 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.quest-info p {
    margin: 0 0 0.5rem 0;
    color: #666;
    font-size: 0.9rem;
}

.quest-reward {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    color: #ffa726;
    font-weight: bold;
    font-size: 0.9rem;
}

.quest-status {
    font-size: 1.5rem;
}

.completed-badge {
    color: #4caf50;
}

.incomplete-badge {
    color: #ddd;
    font-size: 2rem;
}

/* Skills Section */
.skills-section {
    margin-bottom: 3rem;
}

.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.skill-card {
    border-radius: 20px;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.3s;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.skill-card:hover {
    transform: translateY(-5px);
}

.skill-background {
    padding: 2rem;
    color: white;
    text-align: center;
}

.skill-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.skill-background h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.3rem;
}

.skill-background p {
    margin: 0 0 1.5rem 0;
    opacity: 0.9;
}

.skill-progress {
    text-align: left;
}

.progress-bar {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    height: 8px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

.progress-fill {
    background: white;
    height: 100%;
    border-radius: 10px;
    transition: width 0.3s;
}

.progress-text {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Activities Section */
.activities-section {
    margin-bottom: 3rem;
}

.activities-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.activity-btn {
    background: white;
    border: none;
    border-radius: 15px;
    padding: 1.5rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.activity-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.activity-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.activity-name {
    font-weight: bold;
    color: #333;
}

/* Achievements Section */
.achievements-section {
    margin-bottom: 3rem;
}

.achievements-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.achievement-card {
    background: white;
    border-radius: 15px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s;
}

.achievement-card:hover {
    transform: translateY(-3px);
}

.achievement-medal {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.achievement-card h4 {
    margin: 0 0 0.5rem 0;
    color: #333;
}

.achievement-card p {
    margin: 0 0 1rem 0;
    color: #666;
    font-size: 0.9rem;
}

.achievement-date {
    font-size: 0.8rem;
    color: #999;
}

/* Floating Wizard */
.floating-wizard {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: linear-gradient(135deg, #8b4513, #daa520);
    border-radius: 50%;
    width: 70px;
    height: 70px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 25px rgba(139, 69, 19, 0.4);
    transition: all 0.3s ease;
    border: 3px solid rgba(255, 255, 255, 0.3);
    z-index: 999;
}

.floating-wizard:hover {
    transform: translateY(-5px) scale(1.1);
    box-shadow: 0 15px 35px rgba(139, 69, 19, 0.6);
}

.floating-wizard:hover .wizard-tooltip {
    opacity: 1;
    transform: translateX(-50%) translateY(-10px);
}

.wizard-icon {
    font-size: 2.5rem;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {

    0%,
    100% {
        transform: rotate(-5deg);
    }

    50% {
        transform: rotate(5deg);
    }
}

.wizard-sparkles {
    position: absolute;
    top: -5px;
    right: -5px;
    font-size: 1.2rem;
    animation: sparkles 2s linear infinite;
}

@keyframes sparkles {
    0% {
        opacity: 0.5;
        transform: scale(0.8) rotate(0deg);
    }

    50% {
        opacity: 1;
        transform: scale(1.2) rotate(180deg);
    }

    100% {
        opacity: 0.5;
        transform: scale(0.8) rotate(360deg);
    }
}

.wizard-tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-5px);
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    opacity: 0;
    transition: all 0.3s;
    white-space: nowrap;
}

/* Floating Magic Elements */
.floating-magic {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 1;
}

.magic-element {
    position: absolute;
    font-size: 1.5rem;
    animation: floatMagic 8s infinite ease-in-out;
    animation-delay: var(--delay);
    left: var(--x);
    top: var(--y);
}

@keyframes floatMagic {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
        opacity: 0.6;
    }

    50% {
        transform: translateY(-30px) rotate(180deg);
        opacity: 1;
    }
}

/* Responsive Design */
@media (max-width: 768px) {
    .stats-row {
        grid-template-columns: repeat(2, 1fr);
    }

    .quest-grid {
        grid-template-columns: 1fr;
    }

    .skills-grid {
        grid-template-columns: 1fr;
    }

    .activities-grid {
        grid-template-columns: repeat(3, 1fr);
    }

    .welcome-card h1 {
        font-size: 2rem;
    }

    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .stats-row {
        grid-template-columns: 1fr;
    }

    .activities-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .quest-card {
        flex-direction: column;
        text-align: center;
    }
}
</style>