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
                        <NotificationBell v-if="user" :user-id="user.id" />
                        <BubbleTimer v-if="sessionStartTime" :start-time="sessionStartTime" />
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
                        <div class="qoute-box">
                            <div class="quote-icon">💬</div>
                            <p class="quote-text">''{{ Quote }}''</p>
                        </div>
                        <div class="daily-streak">
                            <span class="streak-icon">🔥</span>
                            <span class="streak-text">{{ streakDays }} day streak!</span>
                        </div>
                    </div>
                </div>

                <!-- Quick Stats -->
                <div class="stats-row">
                    <div v-for="stat in statsCards" :key="stat.label" :class="['stat-card', stat.theme]">
                        <div class="stat-icon-wrapper">
                            <div class="stat-icon">{{ stat.icon }}</div>
                            <div class="sparkles">
                                <div class="sparkle" v-for="i in 3" :key="i"></div>
                            </div>
                        </div>
                        <div class="stat-info">
                            <div class="stat-number">{{ stat.value }}</div>
                            <div class="stat-label">{{ stat.label }}</div>
                        </div>
                    </div>
                </div>

                <!-- Major Features Section -->
                <div class="features-section">
                    <h2 class="section-title">
                        <span class="title-icon">🚀</span>
                        Your Main Adventures
                    </h2>
                    <div class="features-grid">
                        <div v-for="feature in mainFeatures" :key="feature.name" class="feature-card"
                            @click="handleFeatureClick(feature)" :style="{ background: feature.gradient }">
                            <div class="feature-icon-wrapper">
                                <div class="feature-icon">{{ feature.icon }}</div>
                            </div>
                            <div class="feature-info">
                                <h3>{{ feature.name }}</h3>
                                <p>{{ feature.description }}</p>
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
                            @click="openSkillArea(skill)" :style="{ background: skill.gradient }">
                            <div class="skill-header">
                                <div class="skill-icon" :style="{ background: skill.gradient }">
                                    {{ skill.icon }}
                                </div>
                                <h3>{{ skill.name }}</h3>
                            </div>
                            <div class="skill-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill"
                                        :style="{ width: skill.progress + '%', background: skill.gradient }"></div>
                                </div>
                                <span class="progress-text">{{ skill.progress }}% complete</span>
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
                    <!-- Memory Game component rendered conditionally -->
                    <MemoryGame v-if="selectedActivity === 'Memory Game'" @close="selectedActivity = null" />
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
        <!-- Update the finance tracker modal section -->
        <div v-if="showFinanceTracker" class="finance-tracker-modal">
            <div class="finance-tracker-content">
                <div class="finance-header">
                    <h2>💰 Treasure Chest</h2>
                    <button @click="showFinanceTracker = false" class="close-btn">×</button>
                </div>

                <div class="savings-container">
                    <!-- Money Plant Animation -->
                    <div class="money-plant-animation">
                        <div class="money-plant">
                            <div class="coin-leaves">
                                <span class="coin-leaf">₹</span>
                                <span class="coin-leaf">₹</span>
                                <span class="coin-leaf">₹</span>
                            </div>
                            <div class="plant-stem">
                                <div class="branch branch-1"></div>
                                <div class="branch branch-2"></div>
                                <div class="branch branch-3"></div>
                            </div>
                            <div class="pot"></div>
                        </div>
                    </div>

                    <!-- Current Savings Box -->
                    <div class="current-savings-box">
                        <div class="savings-content">
                            <h3>Your Treasure</h3>
                            <div class="savings-amount">₹{{ currentSavings }}</div>
                            <div v-if="completedGoals > 0" class="savings-badges">
                                <div class="badge">
                                    <span>🏆</span>
                                    <span>{{ completedGoals }} Goal{{ completedGoals > 1 ? 's' : '' }} Achieved!</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Treasure Animation -->
                    <div class="treasure-animation">
                        <div class="treasure-box">
                            <div class="treasure-lid">
                                <div class="lock"></div>
                            </div>
                            <div class="treasure-base">
                                <div class="coin-pile">
                                    <div class="coin-stack">
                                        <span class="floating-coin">₹</span>
                                        <span class="floating-coin">₹</span>
                                        <span class="floating-coin">₹</span>
                                    </div>
                                    <div class="sparkles">
                                        <span class="sparkle">✨</span>
                                        <span class="sparkle">✨</span>
                                        <span class="sparkle">✨</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="finance-grid">
                    <div class="transactions-box">
                        <h3>Manage Treasure</h3>
                        <div class="action-buttons">
                            <button @click="addTransaction('income')" class="add-income-btn">
                                <span>➕</span> Add Income
                            </button>
                            <button @click="addTransaction('expense')" class="add-expense-btn">
                                <span>➖</span> Add Expense
                            </button>
                        </div>

                        <div class="transaction-history">
                            <h4>Recent Adventures</h4>
                            <div class="transaction-list">
                                <div v-for="t in transactions" :key="t.id" :class="['transaction-item', t.type]">
                                    <div class="transaction-date">{{ formatDate(t.date) }}</div>
                                    <div class="transaction-desc">{{ t.description }}</div>
                                    <div class="transaction-amount">
                                        {{ t.type === 'income' ? '+' : '-' }}₹{{ t.amount }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="goals-box">
                        <div class="goals-header">
                            <h3>Treasure Goals</h3>
                            <button @click="addSavingsGoal" class="add-goal-btn">
                                <span>🎯</span> New Goal
                            </button>
                        </div>

                        <div class="goals-list">
                            <div v-for="goal in savingsGoals" :key="goal.id" class="goal-item">
                                <h4>{{ goal.label }}</h4>
                                <div class="goal-progress">
                                    <div class="progress-bar">
                                        <div class="progress-fill"
                                            :style="{ width: `${calculateGoalProgress(goal)}%` }">
                                        </div>
                                    </div>
                                    <div class="progress-text">
                                        ₹{{ goal.current_amount }} / ₹{{ goal.target_amount }}
                                        <span class="progress-percentage">
                                            ({{ calculateGoalProgress(goal) }}%)
                                        </span>
                                    </div>
                                </div>
                                <div v-if="goal.current_amount >= goal.target_amount" class="goal-complete">
                                    <div class="goal-status">
                                        {{ !goal.spent ? '🏆 Goal Complete!' : '✨ Goal Achieved & Spent!' }}
                                    </div>
                                    <button v-if="!goal.spent" @click="spendGoalSavings(goal)" class="spend-btn">
                                        Use Savings
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Health Tracker Modal -->
        <div v-if="showHealthTracker" class="modal-overlay">
            <div class="modal-content">
                <button class="close-btn" @click="showHealthTracker = false">✖</button>
                <HealthTracker />
            </div>
        </div>

        <!-- Floating Gandalf Chatbot -->
        <div class="floating-wizard" @click="showChat = true">
            <div class="wizard-icon">🧙‍♂️</div>
            <div class="wizard-sparkles">✨</div>
            <div class="wizard-tooltip">Ask Gandalf!</div>
        </div>

        <!-- 3D Chatbot Modal -->
        <EnhancedChatBot v-if="showChat" @close="showChat = false" :user="user" />

        <!-- Music Player Modal -->
        <MusicPlayer v-if="showMusicPlayer" @close="showMusicPlayer = false" />

        <!-- Pomodoro Timer Modal -->
        <PomodoroTimer v-if="showPomodoroTimer" @close="showPomodoroTimer = false" />

        <!-- Drawing Pad Modal -->
        <DrawingPad v-if="showDrawingPad" @close="showDrawingPad = false" />

        <!-- Story Builder Modal -->
        <StoryBuilder v-if="showStoryBuilder" @close="showStoryBuilder = false" />

        <!-- Task Tracker Modal -->
        <TaskTracker v-if="showTaskTracker" :user="user" @close="showTaskTracker = false" />



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
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import EnhancedChatBot from '@/components/chat/EnhancedChatBot.vue'
import Swal from 'sweetalert2'
import MemoryGame from '@/components/activities/MemoryGame.vue'
import MusicPlayer from '@/components/activities/MusicPlayer.vue'
import PomodoroTimer from '@/components/activities/PomodoroTimer.vue'
import DrawingPad from '@/components/activities/DrawingPad.vue'
import StoryBuilder from '@/components/activities/StoryBuilder.vue'
import TaskTracker from '@/components/activities/TaskTracker.vue'
import BubbleTimer from '@/components/activities/BubbleTimer.vue'
import NotificationBell from '@/components/NotificationBell.vue'
import axios from 'axios'
import HealthTracker from './HealthTracker.vue'

export default {
    name: 'ChildDashboard',
    components: {
        EnhancedChatBot,
        MemoryGame,
        MusicPlayer,
        PomodoroTimer,
        DrawingPad,
        StoryBuilder,
        TaskTracker,
        BubbleTimer,
        NotificationBell,
        HealthTracker
    },
    setup() {
        const router = useRouter()
        const showMusicPlayer = ref(false)
        const showPomodoroTimer = ref(false)
        const showDrawingPad = ref(false)
        const showStoryBuilder = ref(false)
        const showTaskTracker = ref(false)
        const user = ref(null)
        const selectedActivity = ref(null)
        const showChat = ref(false)
        const streakDays = ref(0)
        const userLevel = ref(1)
        const showFinanceTracker = ref(false)
        const currentSavings = ref(0)
        const transactions = ref([])
        const savingsGoals = ref([])
        const Quote = ref("Believe in yourself and magic will happen! ✨")
        const showHealthTracker = ref(false)


        // Screen Time Tracking
        const sessionStartTime = ref(null)

        const mainFeatures = ref([
            {
                name: 'Psychometric Test',
                icon: '🧠',
                description: 'Discover your unique learning style and personality traits.',
                action: 'startPsychometricTest',
                gradient: 'linear-gradient(135deg, #667eea, #764ba2)'
            },
            {
                name: 'Finance Tracker',
                icon: '💰',
                description: 'Manage your savings and learn about money.',
                action: 'openFinanceTracker',
                gradient: 'linear-gradient(135deg, #4CAF50, #81C784)'
            },
            {
                name: 'Health Tracker',
                icon: '❤️‍🩹',
                description: 'Monitor your physical wellness and healthy habits.',
                action: 'openHealthTracker',
                gradient: 'linear-gradient(135deg, #ff6b6b, #f093fb)'
            },
            {
                name: 'Task Tracker',
                icon: '🎯',
                description: 'Complete your daily goals and earn rewards.',
                action: 'openTaskTracker',
                gradient: 'linear-gradient(135deg, #ffa726, #f5576c)'
            }
        ]);

        // User stats
        const userStats = ref({
            totalStars: 0,
            questsCompleted: 0,
            skillsLearned: 0,
            todayGoals: 0
        })

        // Motivational quote
        const fetchQuote = async () => {
            try {
                const userId = user.value?.id
                if (!userId) return

                const { data } = await axios.get(`/api/quote/${userId}`)
                Quote.value = data.quote
            } catch (error) {
                console.error('Error fetching quote:', error)
                Quote.value = "Believe in yourself and magic will happen! ✨"
            }
        }

        const statsCards = ref([
            {
                label: "✨ Stars Collected",
                icon: "★",
                value: userStats.value.totalStars,
                theme: "stars-theme",
            },
            {
                label: "📜 Quests Cast",
                icon: "📜",
                value: userStats.value.questsCompleted,
                theme: "quests-theme",
            },
            {
                label: "🧠 Skills Mastered",
                icon: "🧠",
                value: userStats.value.skillsLearned,
                theme: "skills-theme",
            },
            {
                label: "🎯 Today's Goals",
                icon: "🎯",
                value: userStats.value.todayGoals,
                theme: "goals-theme",
            }
        ]);

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
                name: "Good Touch Bad Touch",
                description: "Learn about body safety and personal boundaries",
                icon: "🛡️",
                progress: 0,
                gradient: "linear-gradient(135deg, #fd79a8, #fdcb6e)"
            },
            {
                id: 7,
                name: "Safety Measures",
                description: "General safety tips and emergency procedures",
                icon: "🚨",
                progress: 0,
                gradient: "linear-gradient(135deg, #ff9a9e, #fecfef)"
            }
        ])

        // Fun activities
        const funActivities = ref([
            { id: 1, name: "Pomodoro Timer", icon: "⏰" },
            { id: 2, name: "Memory Game", icon: "🧠" },
            { id: 3, name: "Drawing Pad", icon: "🖌️" },
            { id: 4, name: "Music Player", icon: "🎵" },
            { id: 5, name: "Story Builder", icon: "📝" },
        ])
        const openFinanceTracker = async () => {
            showFinanceTracker.value = true
            await loadTransactions()
            await loadSavingsGoals()
            calculateCurrentSavings()
        }

        const loadTransactions = async () => {
            try {
                const response = await apiService.getTransactions(user.value.id)
                if (response.success) {
                    transactions.value = response.transactions
                    calculateCurrentSavings()
                }
            } catch (error) {
                console.error('Error loading transactions:', error)
            }
        }

        const loadSavingsGoals = async () => {
            try {
                const response = await apiService.getSavingsGoals(user.value.id)
                if (response.success) {
                    // Sort goals by creation date (assuming older goals get priority)
                    const sortedGoals = [...response.goals].sort((a, b) =>
                        new Date(a.created_at) - new Date(b.created_at)
                    )

                    let remainingSavings = currentSavings.value

                    // Update each goal's current amount based on available savings
                    savingsGoals.value = sortedGoals.map(goal => {
                        const currentAmount = Math.min(remainingSavings, goal.target_amount)
                        remainingSavings = Math.max(0, remainingSavings - currentAmount)

                        return {
                            ...goal,
                            current_amount: currentAmount
                        }
                    })
                }
            } catch (error) {
                console.error('Error loading goals:', error)
            }
        }

        const calculateCurrentSavings = () => {
            currentSavings.value = transactions.value.reduce((total, t) => {
                return total + (t.type === 'income' ? t.amount : -t.amount)
            }, 0)
        }

        const addTransaction = async (type, goalAmount = null) => {
            const { value: formValues } = await Swal.fire({
                title: `Add ${type}`,
                html: `
                    <input id="amount" class="swal2-input" type="number" placeholder="Amount" 
                        ${goalAmount ? `value="${goalAmount}" readonly` : ''}>
                    <input id="description" class="swal2-input" placeholder="Description">
                `,
                focusConfirm: false,
                preConfirm: () => {
                    const amount = document.getElementById('amount').value
                    const description = document.getElementById('description').value

                    if (!amount || amount <= 0) {
                        Swal.showValidationMessage('Please enter a valid amount')
                        return false
                    }
                    if (!description) {
                        Swal.showValidationMessage('Please enter a description')
                        return false
                    }

                    return { amount, description }
                }
            })

            if (formValues) {
                try {
                    const response = await apiService.addTransaction({
                        user_id: user.value.id,
                        amount: parseFloat(formValues.amount),
                        type,
                        description: formValues.description
                    })

                    if (response.success) {
                        await loadTransactions()
                        calculateCurrentSavings()
                        await loadSavingsGoals() // Reload goals to update progress
                        Swal.fire('Success!', `${type} added successfully!`, 'success')
                    }
                } catch (error) {
                    Swal.fire('Error', 'Failed to add transaction', 'error')
                }
            }
        }

        const addSavingsGoal = async () => {
            const { value: formValues } = await Swal.fire({
                title: 'Add Savings Goal',
                html: `
                    <div class="mb-3">Current Savings: ₹${currentSavings.value}</div>
                    <input id="goalAmount" class="swal2-input" type="number" placeholder="Goal Amount">
                    <input id="goalLabel" class="swal2-input" placeholder="Goal Description">
                `,
                focusConfirm: false,
                preConfirm: () => {
                    const amount = document.getElementById('goalAmount').value
                    const label = document.getElementById('goalLabel').value

                    if (!amount || amount <= 0) {
                        Swal.showValidationMessage('Please enter a valid goal amount')
                        return false
                    }
                    if (!label) {
                        Swal.showValidationMessage('Please enter a goal description')
                        return false
                    }

                    return { amount, label }
                }
            })

            if (formValues) {
                try {
                    const response = await apiService.addSavingsGoal({
                        user_id: user.value.id,
                        target_amount: parseFloat(formValues.amount),
                        label: formValues.label,
                        current_amount: Math.min(currentSavings.value, parseFloat(formValues.amount))
                    })

                    if (response.success) {
                        await loadSavingsGoals()
                        Swal.fire('Success!', 'Savings goal added!', 'success')
                    }
                } catch (error) {
                    Swal.fire('Error', 'Failed to add savings goal', 'error')
                }
            }
        }

        const spendGoalSavings = async (goal) => {
            await addTransaction('expense', goal.target_amount)
            goal.spent = true
            await apiService.updateSavingsGoal({
                ...goal,
                spent: true
            })
            await loadSavingsGoals() // Reload goals to update progress
        }


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

        // Screen Time Tracking Functions
        const startScreenTimeSession = () => {
            sessionStartTime.value = Date.now()
        }

        const logScreenTime = async () => {
            if (sessionStartTime.value && user.value) {
                const durationSeconds = Math.floor((Date.now() - sessionStartTime.value) / 1000)
                try {
                    await apiService.logScreenTime(user.value.id, durationSeconds)
                    console.log(`Screen time logged: ${durationSeconds} seconds`)
                } catch (error) {
                    console.error('Failed to log screen time:', error)
                }
            }
        }

        const logout = async () => {
            await logScreenTime()
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
            console.log('Starting activity:', skill.name)

            if (skill.name === 'Good Touch Bad Touch') {
                router.push('/good-touch-bad-touch')
            } else if (skill.name === 'Safety Measures') {
                openGeneralSafetyModule()
            } else {
                // TODO: Navigate to other skill detail pages
                Swal.fire({
                    icon: 'info',
                    title: `${skill.name} 🎓`,
                    text: 'This skill module is coming soon! Keep learning and growing.',
                    timer: 3000,
                    showConfirmButton: false,
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    color: 'white'
                })
            }
        }

        const openGeneralSafetyModule = () => {
            Swal.fire({
                icon: 'info',
                title: '🚨 Safety Measures',
                html: `
                    <div style="text-align: left; line-height: 1.6;">
                        <p><strong>This module will cover:</strong></p>
                        <ul style="margin-left: 1rem;">
                            <li>🏠 Home Safety Tips</li>
                            <li>🚸 Road Safety Rules</li>
                            <li>🌐 Internet Safety Guidelines</li>
                            <li>🔥 Fire Safety Procedures</li>
                            <li>📱 Emergency Contacts</li>
                            <li>🆘 What to do in emergencies</li>
                        </ul>
                        <p style="margin-top: 1rem;"><em>This comprehensive safety module is coming soon!</em></p>
                    </div>
                `,
                showConfirmButton: true,
                confirmButtonText: 'Got it! 👍',
                background: 'linear-gradient(135deg, #ff9a9e, #fecfef)',
                color: 'white',
                width: '500px'
            })
        }



        const startActivity = (activity) => {
            console.log('Starting activity:', activity.name)

            switch (activity.name) {
                case 'Pomodoro Timer':
                    showPomodoroTimer.value = true
                    break
                case 'Memory Game':
                    selectedActivity.value = 'Memory Game'
                    break
                case 'Drawing Pad':
                    showDrawingPad.value = true
                    break
                case 'Music Player':
                    showMusicPlayer.value = true;
                    break
                case 'Story Builder':
                    showStoryBuilder.value = true
                    break
                case 'Task Tracker':
                    showTaskTracker.value = true
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

        function openMusicPlayer() {
            console.log('Starting activity: Music Player')
            showMusicPlayer.value = true
        }

        function closeMusicPlayer() {
            showMusicPlayer.value = false
        }

        const handleFeatureClick = (feature) => {
            switch (feature.action) {
                case 'startPsychometricTest':
                    router.push('/psychometric-assessment');
                    break;
                case 'openFinanceTracker':
                    openFinanceTracker();
                    break;
                case 'openHealthTracker':
                    openHealthTracker();
                    break;
                case 'openTaskTracker':
                    showTaskTracker.value = true;
                    break;
            }
        };

        const openHealthTracker = () => {
            showHealthTracker.value = true;
        };

        const openTaskTracker = () => {
            showTaskTracker.value = true;
        };

        const completedGoals = computed(() => {
            return savingsGoals.value.filter(goal =>
                goal.current_amount >= goal.target_amount
            ).length
        })

        const calculateGoalProgress = (goal) => {
            return Math.min(Math.round((goal.current_amount / goal.target_amount) * 100), 100)
        }

        // Update your existing formatDate method to handle both Date objects and strings
        const formatDate = (date) => {
            if (typeof date === 'string') {
                return new Date(date).toLocaleDateString('en-IN', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                })
            }
            return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
        }
        // Load progress from localStorage for Good Touch Bad Touch
        const loadGoodTouchBadTouchProgress = () => {
            try {
                const savedProgress = localStorage.getItem(`safetyProgress_${user.value?.id || 'guest'}`)
                if (savedProgress) {
                    const progressData = JSON.parse(savedProgress)
                    if (progressData.lessons) {
                        const completedLessons = progressData.lessons.filter(lesson => lesson.completed).length
                        const totalLessons = 6 // Total number of lessons
                        const progress = Math.round((completedLessons / totalLessons) * 100)

                        const safetySkill = skillAreas.value.find(skill => skill.name === 'Good Touch Bad Touch')
                        if (safetySkill) {
                            safetySkill.progress = progress
                        }
                    }
                }
            } catch (error) {
                console.error('Error loading Good Touch Bad Touch progress:', error)
            }
        }

        onMounted(() => {
            checkChildAccess()
            startScreenTimeSession()
            fetchQuote()
            loadGoodTouchBadTouchProgress()

            // Add event listener for page unload
            window.addEventListener('beforeunload', logScreenTime)
        })

        onBeforeUnmount(() => {
            // Remove event listener and log screen time
            window.removeEventListener('beforeunload', logScreenTime)
            logScreenTime()
        })

        return {
            user,
            showChat,
            streakDays,
            userLevel,
            userStats,
            skillAreas,
            funActivities,
            selectedActivity,
            showMusicPlayer,
            showPomodoroTimer,
            showDrawingPad,
            showStoryBuilder,
            showTaskTracker,
            recentAchievements,
            sessionStartTime,

            logout,
            toggleQuest,
            openSkillArea,
            startActivity,
            formatDate,
            showFinanceTracker,
            currentSavings,
            transactions,
            savingsGoals,
            addTransaction,
            addSavingsGoal,
            completedGoals,
            calculateGoalProgress,
            spendGoalSavings,
            mainFeatures,
            handleFeatureClick,
            statsCards,
            Quote,
            showHealthTracker,
            openGeneralSafetyModule,
            loadGoodTouchBadTouchProgress
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.child-dashboard {
    min-height: 100vh;
    background: linear-gradient(135deg, #31417A 0%, #667eea 100%);
    position: relative;
    overflow-x: hidden;
    font-family: 'Merriweather', serif;
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
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
    margin-bottom: 3rem;
}

.stat-card {
    background: #F0E6D2;
    /* Parchment */
    border-radius: 15px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-top: 4px solid var(--theme-color);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
    transition: all 0.4s ease;
    text-align: center;
}

.stat-card:hover {
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), 0 0 20px var(--theme-color);
}

.stat-icon-wrapper {
    position: relative;
    margin-bottom: 1rem;
}

.stat-icon {
    font-size: 3rem;
    color: var(--theme-color);
    position: relative;
    z-index: 2;
    transition: transform 0.4s ease;
}

.stat-card:hover .stat-icon {
    animation: levitate 2s infinite ease-in-out;
}

@keyframes levitate {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-7px);
    }
}

.sparkles {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}

.sparkle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: var(--theme-color);
    border-radius: 50%;
    opacity: 0;
    animation: sparkle-anim 2s infinite;
}

.stat-card:hover .sparkle {
    opacity: 1;
}

.sparkle:nth-child(1) {
    top: 20%;
    left: 15%;
    animation-delay: 0.2s;
}

.sparkle:nth-child(2) {
    top: 40%;
    left: 80%;
    animation-delay: 0.8s;
}

.sparkle:nth-child(3) {
    top: 70%;
    left: 30%;
    animation-delay: 1.4s;
}

@keyframes sparkle-anim {
    0% {
        transform: translateY(0) scale(1);
        opacity: 0;
    }

    50% {
        transform: translateY(-15px) scale(1.2);
        opacity: 0.7;
    }

    100% {
        transform: translateY(-30px) scale(1);
        opacity: 0;
    }
}

.stat-info {
    color: #3B312E;
    /* Dark charcoal */
}

.stat-number {
    font-family: 'Merriweather', serif;
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.5rem;
    color: #3B312E;
    text-shadow: 1px 1px 1px rgba(255, 255, 255, 0.5);
}

.stat-label {
    font-size: 0.9rem;
    color: #5a4f4a;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Theme specific styles */
.stars-theme {
    --theme-color: #FFD700;
}

.quests-theme {
    --theme-color: #C9A270;
}

.skills-theme {
    --theme-color: #2A623D;
}

.goals-theme {
    --theme-color: #222F5B;
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

/* Features Section */
.features-section {
    margin-bottom: 3rem;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.feature-card {
    color: white;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
    overflow: hidden;
    position: relative;
}

.feature-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
}

.feature-icon-wrapper {
    background: rgba(255, 255, 255, 0.2);
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem auto;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.feature-icon {
    font-size: 2.5rem;
    color: white;
}

.feature-info h3 {
    color: white;
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
}

.feature-info p {
    color: white;
    opacity: 0.9;
    font-size: 0.9rem;
    line-height: 1.5;
}

/* Skills Section */
.skills-section {
    margin-bottom: 3rem;
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
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1.5rem;
}

.skill-card {
    border-radius: 15px;
    padding: 1.5rem;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.skill-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.skill-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.skill-icon {
    font-size: 2rem;
}

.skill-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: white;
    font-weight: 600;
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
    font-size: 0.8rem;
    color: white;
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
    color: #333;
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

.finance-tracker-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.finance-tracker-content {
    background: rgba(46, 38, 70, 0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    border-radius: 20px;
    width: 90%;
    max-width: 1200px;
    max-height: 90vh;
    overflow-y: auto;
    padding: 2rem;
    position: relative;
}

.finance-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.finance-header h2 {
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.close-btn {
    font-size: 2rem;
    background: none;
    border: none;
    cursor: pointer;
    color: rgba(255, 255, 255, 0.7);
    transition: color 0.3s;
}

.close-btn:hover {
    color: white;
}

.current-savings-box {
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.savings-amount {
    font-size: 3rem;
    font-weight: bold;
    margin-top: 1rem;
}

.finance-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
}

.transactions-box,
.goals-box {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 15px;
    padding: 1.5rem;
}

.transactions-box h3,
.goals-box h3,
.transactions-box h4 {
    color: white;
    opacity: 0.9;
    margin-bottom: 1rem;
}

.action-buttons {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.add-income-btn,
.add-expense-btn {
    flex: 1;
    padding: 1rem;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    transition: all 0.3s;
}

.add-income-btn {
    background: #4CAF50;
    color: white;
}

.add-income-btn:hover {
    box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
    transform: translateY(-2px);
}

.add-expense-btn {
    background: #ff5252;
    color: white;
}

.add-expense-btn:hover {
    box-shadow: 0 5px 15px rgba(255, 82, 82, 0.4);
    transform: translateY(-2px);
}

.transaction-list {
    max-height: 300px;
    overflow-y: auto;
}

.transaction-item {
    display: grid;
    grid-template-columns: auto 1fr auto;
    gap: 1rem;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
    border-left: 3px solid transparent;
}

.transaction-item.income {
    background: rgba(76, 175, 80, 0.2);
    color: #a5d6a7;
    border-left-color: #4CAF50;
}

.transaction-item.expense {
    background: rgba(255, 82, 82, 0.2);
    color: #ef9a9a;
    border-left-color: #ff5252;
}

.transaction-date {
    opacity: 0.8;
}

.transaction-desc {
    font-weight: bold;
}

.goals-list {
    margin-top: 1.5rem;
}

.goal-item {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.goal-item h4 {
    color: white;
}

.goal-progress {
    margin-top: 1rem;
}

.progress-bar {
    background: rgba(255, 255, 255, 0.2);
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
}

.progress-fill {
    background: #4CAF50;
    height: 100%;
    transition: width 0.3s;
}

.progress-text {
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
}

.progress-text .progress-percentage {
    opacity: 0.7;
}

.goal-complete {
    margin-top: 0.5rem;
    color: #81C784;
    /* Brighter green */
    font-weight: bold;
}

@media (max-width: 768px) {
    .finance-grid {
        grid-template-columns: 1fr;
    }
}

.current-savings-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    display: flex;
    align-items: center;
    max-width: 400px;
    margin: 0 auto 2rem;
    position: relative;
    overflow: hidden;
}

.savings-animation {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    opacity: 0.1;
}

.money-tree {
    position: relative;
    width: 100%;
    height: 100%;
}

.tree-trunk {
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 20px;
    height: 60%;
    background: #4a5568;
    transform: translateX(-50%);
}

.coin {
    position: absolute;
    font-size: 24px;
    color: #ffd700;
    animation: growCoin 3s infinite;
}

.coin-1 {
    left: 30%;
    bottom: 40%;
    animation-delay: 0s;
}

.coin-2 {
    left: 50%;
    bottom: 60%;
    animation-delay: 1s;
}

.coin-3 {
    left: 70%;
    bottom: 50%;
    animation-delay: 2s;
}

@keyframes growCoin {
    0% {
        transform: scale(1) translateY(0);
        opacity: 0;
    }

    50% {
        transform: scale(1.5) translateY(-20px);
        opacity: 1;
    }

    100% {
        transform: scale(1) translateY(-40px);
        opacity: 0;
    }
}

.savings-content {
    position: relative;
    z-index: 1;
    width: 100%;
    text-align: center;
}

.savings-amount {
    font-size: 2.5rem;
    font-weight: bold;
    color: white;
    margin: 0.5rem 0;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.savings-badges {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1rem;
}

.badge {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    color: white;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.add-goal-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 15px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s;
}

.add-goal-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.goals-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.savings-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
    padding: 0 2rem;
}

.plant-animation {
    width: 100px;
    height: 150px;
    position: relative;
}

.plant {
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    animation: growPlant 4s ease-in-out infinite;
}

.stem {
    width: 4px;
    height: 60px;
    background: #4CAF50;
    margin: 0 auto;
}

.leaf {
    width: 20px;
    height: 30px;
    background: #81C784;
    border-radius: 0 50% 50% 0;
    position: absolute;
}

.leaf-1 {
    left: 4px;
    top: 20px;
    transform: rotate(45deg);
}

.leaf-2 {
    right: 4px;
    top: 40px;
    transform: rotate(-45deg);
}

/* Money Plant Animation */
.money-plant-animation {
    width: 120px;
    height: 180px;
    position: relative;
}

.money-plant {
    position: relative;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.coin-leaves {
    position: relative;
    height: 80px;
    width: 80px;
}

.coin-leaf {
    position: absolute;
    color: #4CAF50;
    font-size: 24px;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
    animation: floatLeaf 3s ease-in-out infinite;
}

.coin-leaf:nth-child(1) {
    left: 0;
    animation-delay: 0s;
}

.coin-leaf:nth-child(2) {
    left: 50%;
    top: 20px;
    animation-delay: 0.5s;
}

.coin-leaf:nth-child(3) {
    right: 0;
    animation-delay: 1s;
}

@keyframes floatLeaf {

    0%,
    100% {
        transform: translateY(0) rotate(0deg);
    }

    50% {
        transform: translateY(-10px) rotate(5deg);
    }
}

.plant-stem {
    width: 8px;
    height: 100px;
    background: linear-gradient(to bottom, #4CAF50, #2E7D32);
    position: relative;
}

.branch {
    position: absolute;
    width: 30px;
    height: 4px;
    background: #4CAF50;
    border-radius: 2px;
}

.branch-1 {
    top: 30%;
    right: 0;
    transform: rotate(45deg);
}

.branch-2 {
    top: 50%;
    left: 0;
    transform: rotate(-45deg);
}

.branch-3 {
    top: 70%;
    right: 0;
    transform: rotate(45deg);
}

.pot {
    width: 40px;
    height: 35px;
    background: linear-gradient(to bottom, #795548, #5D4037);
    border-radius: 0 0 20px 20px;
    position: relative;
}

/* Treasure Animation */
.treasure-animation {
    width: 140px;
    height: 180px;
    position: relative;
}

.treasure-box {
    position: absolute;
    bottom: 20px;
    width: 120px;
    height: 90px;
}

.treasure-lid {
    width: 100%;
    height: 40px;
    background: linear-gradient(45deg, #CD853F, #8B4513);
    border-radius: 10px 10px 0 0;
    position: relative;
    transform-origin: bottom;
    animation: openLid 4s ease-in-out infinite;
}

.lock {
    position: absolute;
    width: 20px;
    height: 25px;
    background: #FFD700;
    border-radius: 5px;
    left: 50%;
    bottom: -10px;
    transform: translateX(-50%);
}

.treasure-base {
    width: 100%;
    height: 60px;
    background: linear-gradient(45deg, #8B4513, #654321);
    border-radius: 10px;
    position: relative;
    overflow: hidden;
}

.coin-pile {
    position: absolute;
    bottom: 5px;
    width: 100%;
    text-align: center;
}

.floating-coin {
    display: inline-block;
    color: #FFD700;
    font-size: 24px;
    text-shadow: 0 0 5px rgba(255, 215, 0, 0.5);
    animation: floatCoin 2s ease-in-out infinite;
    margin: 0 3px;
}

.floating-coin:nth-child(2) {
    animation-delay: 0.3s;
}

.floating-coin:nth-child(3) {
    animation-delay: 0.6s;
}

.sparkles {
    position: absolute;
    width: 100%;
    height: 100%;
}

.sparkle {
    position: absolute;
    font-size: 12px;
    animation: sparkle 1.5s ease-in-out infinite;
}

.sparkle:nth-child(1) {
    left: 20%;
    top: 20%;
    animation-delay: 0s;
}

.sparkle:nth-child(2) {
    left: 50%;
    top: 40%;
    animation-delay: 0.5s;
}

.sparkle:nth-child(3) {
    left: 80%;
    top: 60%;
    animation-delay: 1s;
}

@keyframes openLid {

    0%,
    100% {
        transform: rotate(0);
    }

    50% {
        transform: rotate(-30deg);
    }
}

@keyframes floatCoin {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-15px);
    }
}

@keyframes sparkle {

    0%,
    100% {
        transform: scale(1);
        opacity: 0.5;
    }

    50% {
        transform: scale(1.2);
        opacity: 1;
    }
}

@keyframes growPlant {

    0%,
    100% {
        transform: scale(1) translateY(0);
    }

    50% {
        transform: scale(1.2) translateY(-10px);
    }
}

.treasure-chest-animation {
    width: 100px;
    height: 150px;
    position: relative;
}

.chest {
    position: absolute;
    bottom: 0;
    width: 80px;
    height: 60px;
    background: #8B4513;
    border-radius: 10px;
    overflow: hidden;
}

.lid {
    width: 80px;
    height: 20px;
    background: #A0522D;
    border-radius: 10px 10px 0 0;
    position: absolute;
    top: 0;
    transform-origin: bottom;
    animation: openChest 4s ease-in-out infinite;
}

.coins {
    position: absolute;
    bottom: 10px;
    width: 100%;
    text-align: center;
}

.coin {
    display: inline-block;
    color: #FFD700;
    font-size: 20px;
    animation: bounceCoin 2s ease-in-out infinite;
    margin: 0 2px;
}

.coin:nth-child(2) {
    animation-delay: 0.3s;
}

.coin:nth-child(3) {
    animation-delay: 0.6s;
}

@keyframes openChest {

    0%,
    100% {
        transform: rotate(0);
    }

    50% {
        transform: rotate(-45deg);
    }
}

@keyframes bounceCoin {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-15px);
    }
}

/* Update your existing current-savings-box style */
.current-savings-box {
    flex: 1;
    margin: 0 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    color: white;
}

/* Update your existing spend-btn style */
.spend-btn {
    background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s;
}

.spend-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 176, 155, 0.4);
}

.spend-btn {
    background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 10px;
    margin-left: 1rem;
    cursor: pointer;
    transition: all 0.3s;
}

.spend-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 176, 155, 0.4);
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

.dashboard {
    padding: 2rem;
}


.fun-activities {
    margin-top: 2rem;
}

.activities-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.activity-card {
    width: 200px;
    height: 150px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: transform 0.2s;
}

.activity-card:hover {
    transform: scale(1.05);
}

.activity-card .icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.quote-box {
    background: linear-gradient(135deg, #fdfbfb, #ebedee);
    border-left: 6px solid #764ba2;
    padding: 1rem 1.5rem;
    border-radius: 1rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
    position: relative;
    animation: fadeInUp 0.8s ease;
}

.quote-icon {
    font-size: 1.8rem;
    position: absolute;
    top: -10px;
    left: -10px;
}

.quote-text {
    font-size: 1.1rem;
    font-style: italic;
    color: #333;
    margin: 0;
    padding-left: 1.5rem;
    line-height: 1.5;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 999;
    backdrop-filter: blur(5px);
}

.modal-content {
    background: transparent;
    padding: 0;
    border-radius: 20px;
    width: 95vw;
    max-width: 1200px;
    height: 90vh;
    overflow: hidden;
    position: relative;
    animation: fadeIn 0.3s ease-out;
}

.close-btn {
    position: absolute;
    top: 15px;
    right: 20px;
    background: rgba(255, 255, 255, 0.9);
    color: #333;
    font-size: 1.5rem;
    cursor: pointer;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1001;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.close-btn:hover {
    background: rgba(255, 255, 255, 1);
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.9);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
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

.control-btn span {
    font-size: 1.1rem;
}
</style>