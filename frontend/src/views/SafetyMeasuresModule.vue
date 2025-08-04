<template>
    <div class="safety-measures-module">
        <!-- Header -->
        <header class="safety-header">
            <div class="container">
                <div class="header-content">
                    <button @click="goBack" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        <span>🏠 Back to Dashboard</span>
                    </button>
                    <div class="safety-title">
                        <h1>🚨🛡️ Safety Champions Academy 🛡️🚨</h1>
                        <p class="safety-subtitle">Learn Essential Safety Skills Through Interactive Visual Cards!</p>
                    </div>
                    <div class="progress-display">
                        <span class="progress-text">{{ progressFraction }} Complete</span>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: `${overallProgress}%` }"></div>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="safety-main">
            <div class="safety-body">
                <div v-if="isLoading" class="loading-safety">
                    <div class="loading-animation">
                        <div class="loading-shield">🛡️</div>
                        <div class="loading-icons">
                            <span>🚨</span>
                            <span>🏠</span>
                            <span>🚗</span>
                            <span>🔥</span>
                        </div>
                    </div>
                    <h3>Loading Your Safety Adventure...</h3>
                    <p>Preparing interactive safety cards...</p>
                </div>

                <div v-show="!isLoading" class="safety-academy">
                    <div class="academy-container">
                        <div class="academy-header">
                            <h2>🎓 Safety Learning Center 🎓</h2>
                            <p>Click on the safety cards to learn important life skills!</p>
                        </div>

                        <div class="safety-categories">
                            <div v-for="(category, index) in safetyCategories" :key="category.id"
                                :class="['safety-card', { 'explored': exploredCards.includes(category.id), 'active': activeCard === category.id }]"
                                @click="exploreCard(category)">
                                <div class="card-icon">{{ category.icon }}</div>
                                <div class="card-content">
                                    <h3>{{ category.title }}</h3>
                                    <p>{{ category.description }}</p>
                                    <div class="card-progress">
                                        <span v-if="exploredCards.includes(category.id)" class="learned">✅
                                            Learned!</span>
                                        <span v-else class="learn-now">👆 Tap to Learn</span>
                                    </div>
                                </div>
                                <div v-if="exploredCards.includes(category.id)" class="completion-badge">
                                    <span>🌟</span>
                                </div>
                            </div>
                        </div>

                        <!-- Interactive Card Details Modal -->
                        <div v-if="selectedCard" class="card-detail-modal" @click.self="closeCard">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h3>{{ selectedCard.icon }} {{ selectedCard.title }}</h3>
                                    <button @click="closeCard" class="close-btn">×</button>
                                </div>

                                <div class="modal-body">
                                    <div class="safety-tips">
                                        <h4>🎯 Key Safety Tips:</h4>
                                        <div class="tips-grid">
                                            <div v-for="(tip, tipIndex) in selectedCard.tips" :key="tipIndex"
                                                :class="['tip-card', { 'discovered': discoveredTips[selectedCard.id]?.includes(tipIndex) }]"
                                                @click="discoverTip(selectedCard.id, tipIndex)">
                                                <div class="tip-icon">{{ tip.icon }}</div>
                                                <div class="tip-content">
                                                    <h5>{{ tip.title }}</h5>
                                                    <p v-if="discoveredTips[selectedCard.id]?.includes(tipIndex)">{{
                                                        tip.description }}</p>
                                                    <span v-else class="discover-hint">Click to discover!</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div v-if="selectedCard.emergency" class="emergency-section">
                                        <h4>🆘 Emergency Information:</h4>
                                        <div class="emergency-card">
                                            <div class="emergency-icon">{{ selectedCard.emergency.icon }}</div>
                                            <div class="emergency-content">
                                                <h5>{{ selectedCard.emergency.title }}</h5>
                                                <p>{{ selectedCard.emergency.description }}</p>
                                                <div class="emergency-numbers">
                                                    <span v-for="number in selectedCard.emergency.numbers"
                                                        :key="number">
                                                        📞 {{ number }}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="completion-check">
                                        <button v-if="isCardFullyExplored(selectedCard.id)"
                                            @click="markCardComplete(selectedCard.id)" class="complete-card-btn"
                                            :disabled="exploredCards.includes(selectedCard.id)">
                                            {{ exploredCards.includes(selectedCard.id) ? '✅ Mastered!' : '⭐ Master This Topic!' }}
                                            

                                        </button>
                                        <div v-else class="exploration-hint">
                                            <span>💡 Discover all tips to master this topic!</span>
                                            <div class="tip-progress">
                                                {{ (discoveredTips[selectedCard.id] || []).length }} / {{
                                                    selectedCard.tips.length }} tips discovered
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Completion Panel -->
                        <div v-if="allCardsExplored" class="completion-panel">
                            <div class="completion-content">
                                <div class="completion-icon">🏆🎉</div>
                                <h3>🌟 Safety Champion Achieved! 🌟</h3>
                                <p>Outstanding! You've mastered all essential safety skills!</p>
                                <div class="achievement-stats">
                                    <div class="stat">
                                        <span class="stat-number">{{ exploredCards.length }}</span>
                                        <span class="stat-label">Safety Topics Mastered</span>
                                    </div>
                                    <div class="stat">
                                        <span class="stat-number">{{ Object.values(discoveredTips).flat().length
                                        }}</span>
                                        <span class="stat-label">Safety Tips Learned</span>
                                    </div>
                                </div>
                                <div class="completion-actions">
                                    <button @click="markModuleComplete" class="complete-module-btn" v-if="!isCompleted">
                                        🏅 Become a Safety Champion!
                                    </button>
                                    <button @click="resetProgress" class="reset-btn">
                                        🔄 Learn Again
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import Swal from 'sweetalert2'

const router = useRouter()
const user = ref(userUtils.getCurrentUser())

// State management
const isLoading = ref(true)
const exploredCards = ref([])
const discoveredTips = ref({})
const selectedCard = ref(null)
const activeCard = ref(null)
const isCompleted = ref(false)
const backendCompletedCount = ref(0);
const progressFraction = computed(() => `${backendCompletedCount.value}/6`);

// Safety Categories Data
const safetyCategories = ref([
    {
        id: 'home_safety',
        title: 'Home Safety',
        icon: '🏠',
        description: 'Stay safe in your home environment',
        tips: [
            {
                icon: '🔌',
                title: 'Electrical Safety',
                description: 'Never touch electrical outlets with wet hands. Always unplug devices by pulling the plug, not the cord. Tell an adult if you see damaged wires.'
            },
            {
                icon: '🚰',
                title: 'Kitchen Safety',
                description: 'Always ask an adult before using kitchen appliances. Keep knives and sharp objects away from you. Clean up spills immediately to prevent slipping.'
            },
            {
                icon: '🛁',
                title: 'Bathroom Safety',
                description: 'Use non-slip mats in the bathroom. Never mix different cleaning products. Lock the door for privacy and safety.'
            },
            {
                icon: '🪜',
                title: 'Height Safety',
                description: 'Never climb on furniture or high places without adult supervision. Use a stable step stool when needed. Ask for help reaching high objects.'
            }
        ],
        emergency: {
            icon: '🆘',
            title: 'Home Emergency Contacts',
            description: 'Keep these numbers easily accessible at home',
            numbers: ['Emergency: 112', 'Police: 100', 'Fire: 101', 'Ambulance: 108']
        }
    },
    {
        id: 'road_safety',
        title: 'Road Safety',
        icon: '🚸',
        description: 'Rules for staying safe on roads and streets',
        tips: [
            {
                icon: '👀',
                title: 'Look Both Ways',
                description: 'Always look left, right, and left again before crossing any street. Make sure no vehicles are coming before you step onto the road.'
            },
            {
                icon: '🚥',
                title: 'Traffic Signals',
                description: 'Red means STOP, Green means GO, Yellow means SLOW DOWN. Always wait for the green signal before crossing at traffic lights.'
            },
            {
                icon: '🚶‍♀️',
                title: 'Sidewalk Safety',
                description: 'Always walk on sidewalks when available. If there\'s no sidewalk, walk facing traffic on the road\'s edge. Stay alert and avoid distractions.'
            },
            {
                icon: '🚌',
                title: 'Vehicle Safety',
                description: 'Always wear seatbelts in cars. Wait for the bus to completely stop before boarding. Never play around moving vehicles.'
            }
        ],
        emergency: {
            icon: '🚨',
            title: 'Road Emergency Help',
            description: 'If you\'re in a traffic accident or emergency',
            numbers: ['Emergency: 112', 'Traffic Police: 103', 'Ambulance: 108']
        }
    },
    {
        id: 'internet_safety',
        title: 'Internet Safety',
        icon: '🌐',
        description: 'Stay safe while using computers and phones',
        tips: [
            {
                icon: '🔒',
                title: 'Privacy Protection',
                description: 'Never share your full name, address, phone number, or school name with strangers online. Keep your personal information private.'
            },
            {
                icon: '👥',
                title: 'Stranger Awareness',
                description: 'Never meet someone in person that you only know from the internet. If someone makes you uncomfortable online, tell a trusted adult.'
            },
            {
                icon: '💬',
                title: 'Safe Communication',
                description: 'Be kind and respectful in messages. Don\'t respond to mean or inappropriate messages. Block and report users who make you uncomfortable.'
            },
            {
                icon: '🛡️',
                title: 'Content Safety',
                description: 'Only visit websites approved by your parents. If you see something scary or inappropriate, close it and tell an adult immediately.'
            }
        ],
        emergency: {
            icon: '⚠️',
            title: 'Cyberbullying & Online Safety',
            description: 'If someone is bothering you online',
            numbers: ['Child Helpline: 1098', 'Cyber Crime: 1930']
        }
    },
    {
        id: 'fire_safety',
        title: 'Fire Safety',
        icon: '🔥',
        description: 'How to prevent fires and stay safe',
        tips: [
            {
                icon: '💨',
                title: 'Smoke Detection',
                description: 'If you smell smoke or hear a smoke alarm, alert adults immediately. Get low and crawl under smoke to exit safely.'
            },
            {
                icon: '🚪',
                title: 'Escape Planning',
                description: 'Know two ways out of every room. Practice your family escape plan. Meet at your designated meeting spot outside.'
            },
            {
                icon: '🧯',
                title: 'Fire Prevention',
                description: 'Never play with matches, lighters, or candles. Keep flammable objects away from heat sources. Report damaged electrical cords.'
            },
            {
                icon: '🛑',
                title: 'Stop, Drop, Roll',
                description: 'If your clothes catch fire: STOP where you are, DROP to the ground, and ROLL back and forth to put out flames.'
            }
        ],
        emergency: {
            icon: '🚨',
            title: 'Fire Emergency Response',
            description: 'In case of fire emergency',
            numbers: ['Fire Department: 101', 'Emergency: 112']
        }
    },
    {
        id: 'emergency_procedures',
        title: 'Emergency Procedures',
        icon: '🆘',
        description: 'What to do in different emergency situations',
        tips: [
            {
                icon: '☎️',
                title: 'Emergency Calling',
                description: 'Memorize important emergency numbers. Stay calm when calling. Give your name, location, and describe the emergency clearly.'
            },
            {
                icon: '🏃‍♀️',
                title: 'Natural Disasters',
                description: 'During earthquakes: Drop, Cover, Hold. During storms: Stay indoors, away from windows. Follow your family emergency plan.'
            },
            {
                icon: '🏥',
                title: 'Medical Emergencies',
                description: 'If someone is hurt, get an adult immediately. Never move someone who might be seriously injured. Know basic first aid like applying pressure to cuts.'
            },
            {
                icon: '👨‍👩‍👧‍👦',
                title: 'Getting Lost',
                description: 'If lost, stay where you are. Look for police officers, security guards, or store employees. Never go with strangers looking to "help".'
            }
        ],
        emergency: {
            icon: '📞',
            title: 'All Emergency Numbers',
            description: 'Important numbers to remember',
            numbers: ['General Emergency: 112', 'Police: 100', 'Fire: 101', 'Ambulance: 108', 'Child Helpline: 1098']
        }
    },
    {
        id: 'personal_safety',
        title: 'Personal Safety',
        icon: '🛡️',
        description: 'Protecting yourself and staying aware',
        tips: [
            {
                icon: '👥',
                title: 'Trusted Adults',
                description: 'Know who your trusted adults are: parents, teachers, relatives. Always tell a trusted adult where you\'re going and when you\'ll be back.'
            },
            {
                icon: '🚶‍♂️',
                title: 'Walking Safely',
                description: 'Walk confidently and stay alert. Avoid wearing headphones in unfamiliar areas. Trust your instincts if something feels wrong.'
            },
            {
                icon: '🏠',
                title: 'Home Alone Rules',
                description: 'Lock doors and windows. Don\'t open the door for strangers. Don\'t tell callers you\'re alone. Know where to go if you need help.'
            },
            {
                icon: '📱',
                title: 'Communication Safety',
                description: 'Always tell trusted adults your plans. Carry emergency contact information. Know how to use phones in emergencies.'
            }
        ],
        emergency: {
            icon: '🆘',
            title: 'Personal Safety Emergency',
            description: 'If you feel unsafe or threatened',
            numbers: ['Emergency: 112', 'Police: 100', 'Child Helpline: 1098']
        }
    }
])

// Computed properties
const overallProgress = computed(() => {
    const totalCards = safetyCategories.value.length
    const exploredCount = exploredCards.value.length
    return totalCards > 0 ? (exploredCount / totalCards) * 100 : 0
})

const allCardsExplored = computed(() => {
    return exploredCards.value.length === safetyCategories.value.length
})

// Watch for completion
watch(allCardsExplored, async (newValue) => {
    if (newValue && !isCompleted.value) {
        console.log('🎉 All safety cards explored! Auto-completing module...')
        await markModuleComplete()
    }
})

// Methods
const goBack = () => {
    router.push('/child-dashboard')
}

const exploreCard = (category) => {
    activeCard.value = category.id
    selectedCard.value = category

    // Initialize tips tracking for this card if not exists
    if (!discoveredTips.value[category.id]) {
        discoveredTips.value[category.id] = []
    }
}

const closeCard = () => {
    selectedCard.value = null
    activeCard.value = null
}

const discoverTip = async (cardId, tipIndex) => {
    if (!discoveredTips.value[cardId]) {
        discoveredTips.value[cardId] = []
    }

    if (!discoveredTips.value[cardId].includes(tipIndex)) {
        discoveredTips.value[cardId].push(tipIndex)

        // Removed automatic progress saving
        // Removed progress save on tip discovery

        // Show discovery animation
        Swal.fire({
            icon: 'success',
            title: '💡 Safety Tip Discovered!',
            text: 'Great job learning this important safety information!',
            timer: 1500,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #4CAF50, #81C784)',
            color: 'white',
            position: 'top-end',
            toast: true
        })
    }
}

const isCardFullyExplored = (cardId) => {
    const card = safetyCategories.value.find(c => c.id === cardId)
    const discoveredCount = discoveredTips.value[cardId]?.length || 0
    return discoveredCount === card.tips.length
}

const markCardComplete = async (cardId) => {
    // Only proceed if the card is fully explored and not already explored
    if (isCardFullyExplored(cardId) && !exploredCards.value.includes(cardId)) {
        exploredCards.value.push(cardId)

        // Map card IDs to correct submodule names
        const submoduleMap = {
            'home_safety': 'home_safety',
            'road_safety': 'road_safety',
            'internet_safety': 'internet_safety',
            'fire_safety': 'fire_safety'
        }

        const submoduleName = submoduleMap[cardId]
        if (!submoduleName) {
            console.error(`❌ Invalid submodule: ${cardId}`)
            return
        }

        // Calculate progress percentage based on discovered tips
        const card = safetyCategories.value.find(c => c.id === cardId)
        const discoveredCount = discoveredTips.value[cardId]?.length || 0
        const progressPercentage = Math.round((discoveredCount / card.tips.length) * 100)

        // Verify the submodule name
        console.log(`🔍 Attempting to save progress for submodule: ${submoduleName}, Progress: ${progressPercentage}%`)

        // Save individual submodule progress
        if (user.value?.id) {
            try {
                const progressResponse = await apiService.updateModuleProgress({
                    user_id: user.value.id,
                    module_type: 'safety_measures', // Lowercase module type
                    submodule_name: submoduleName, // Correct submodule name
                    progress_percentage: progressPercentage, // Actual progress percentage
                    is_completed: progressPercentage === 100,
                    progress_data: {
                        exploredCards: exploredCards.value,
                        discoveredTips: discoveredTips.value
                    }
                })
                console.log(`✅ Saved submodule progress for ${submoduleName}:`, progressResponse)
            } catch (error) {
                console.warn(`❌ Failed to save submodule progress for ${submoduleName}:`, error)
                // Log the full error details for debugging
                console.error('Full error details:', JSON.stringify(error.response?.data || error))
            }
        }

        Swal.fire({
            icon: 'success',
            title: '🌟 Safety Topic Mastered!',
            text: 'Excellent work! You\'ve learned all the important safety tips for this topic.',
            timer: 2000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ff6b6b, #fecfef)',
            color: 'white'
        })

        // Save progress
        await saveProgress()
    }

    closeCard()
}

const markModuleComplete = async () => {
    if (isCompleted.value) {
        console.log('Module already completed, skipping...')
        return
    }

    try {
        const result = await Swal.fire({
            title: '🛡️ Safety Skills Mastered!',
            html: `
                <div style="text-align: center; line-height: 1.8;">
                    <div style="font-size: 4rem; margin: 1rem 0;">🛡️🏆🌟</div>
                    <p style="font-size: 1.2rem; color: #4a5568; font-weight: 600;">
                        Congratulations! You've mastered Safety Champions Academy!
                    </p>
                    <p style="color: #718096; margin: 1rem 0;">
                        You now have essential safety skills to protect yourself and others! 🚨
                    </p>
                    <div style="font-size: 3rem; margin: 1rem 0;">⭐🚨⭐</div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: '🛡️ Mark as Complete!',
            cancelButtonText: '🚨 Continue Learning',
            background: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            color: 'white',
            customClass: {
                popup: 'safety-measures-popup',
                confirmButton: 'safety-confirm-btn',
                cancelButton: 'safety-cancel-btn'
            }
        })

        if (result.isConfirmed) {
            console.log('Marking Safety Measures module as complete...')
            isCompleted.value = true
            await saveProgress()

            // Save to backend
            if (user.value?.id) {
                try {
                    const progressData = {
                        isCompleted: isCompleted.value,
                        completedAt: Date.now(),
                        lastAccessed: Date.now(),
                        exploredCards: exploredCards.value,
                        discoveredTips: discoveredTips.value
                    }

                    console.log('Saving Safety Measures completion to backend:', progressData)
                    const response = await apiService.saveModuleProgress(user.value.id, 'safety_measures', progressData)
                    console.log('✅ Safety Measures module completion saved to backend successfully:', response)
                } catch (error) {
                    console.error('❌ Failed to save Safety Measures module completion to backend:', error)
                }
            }

            // Success message
            await Swal.fire({
                title: '🏆 Safety Champion Certified!',
                html: `
                    <div style="text-align: center; line-height: 1.8;">
                        <div style="font-size: 4rem; margin: 1rem 0;">🛡️🏆🌟</div>
                        <p style="font-size: 1.2rem; color: #ffffff; font-weight: 600;">
                            Congratulations! You are now a certified Safety Champion!
                        </p>
                        <p style="color: #ffffff; margin: 1rem 0; opacity: 0.9;">
                            You've mastered essential safety skills that will help keep you and others safe. 
                            Remember to always follow these safety rules!
                        </p>
                        <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 15px; margin: 1rem 0;">
                            <p style="color: #ffffff; font-weight: 600; margin: 0.5rem 0;">
                                🏅 Achievement: Safety Champion Certified
                            </p>
                            <p style="color: #ffffff; font-size: 0.9rem; margin: 0.5rem 0;">
                                📚 Topics Mastered: ${exploredCards.value.length}/${safetyCategories.value.length}
                            </p>
                            <p style="color: #ffffff; font-size: 0.9rem; margin: 0.5rem 0;">
                                💡 Safety Tips Learned: ${Object.values(discoveredTips.value).flat().length}
                            </p>
                        </div>
                        <div style="font-size: 3rem; margin: 1rem 0;">🚨🛡️⭐</div>
                    </div>
                `,
                timer: 6000,
                showConfirmButton: true,
                confirmButtonText: 'I\'m a Safety Champion! 🏆',
                background: 'linear-gradient(135deg, #ff9a9e, #fecfef)',
                color: 'white'
            })
        }
    } catch (error) {
        console.error('Error in markModuleComplete:', error)
    }
}

const resetProgress = async () => {
    Swal.fire({
        icon: 'warning',
        title: '🔄 Reset Learning Progress?',
        text: 'This will reset all your safety learning progress. You can learn everything again!',
        showCancelButton: true,
        confirmButtonText: 'Yes, Reset!',
        cancelButtonText: 'Keep Progress',
        confirmButtonColor: '#ff6b6b',
        cancelButtonColor: '#6c757d',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
    }).then(async (result) => {
        if (result.isConfirmed) {
            exploredCards.value = []
            discoveredTips.value = {}
            isCompleted.value = false
            selectedCard.value = null
            activeCard.value = null

            await saveProgress()

            Swal.fire({
                icon: 'success',
                title: '✅ Progress Reset!',
                text: 'Ready to start your safety learning journey again!',
                timer: 2000,
                showConfirmButton: false,
                background: 'linear-gradient(135deg, #4CAF50, #81C784)',
                color: 'white'
            })
        }
    })
}

const saveProgress = async () => {
    const progressData = {
        isCompleted: isCompleted.value,
        exploredCards: exploredCards.value,
        discoveredTips: discoveredTips.value,
        completedAt: isCompleted.value ? Date.now() : null,
        lastAccessed: Date.now()
    }

    // Store with module-specific key
    localStorage.setItem(`safetyMeasuresProgress_${user.value?.id || 'guest'}`, JSON.stringify(progressData))

    console.log('✅ Safety Measures progress saved locally:', progressData)

    // Also save to backend if user is logged in
    if (user.value?.id) {
        try {
            const response = await apiService.saveModuleProgress(user.value.id, 'safety_measures', progressData)
            console.log('✅ Safety Measures progress saved to backend:', response)
        } catch (error) {
            console.error('❌ Failed to save Safety Measures progress to backend:', error)
        }
    }
}



const loadProgress = async () => {
    try {
        console.log('🦺 Loading Safety Measures progress for user:', user.value?.id)
        // First try to load from backend if user is logged in
        if (user.value?.id) {
            try {
                console.log('Attempting to load from backend...')
                const backendProgress = await apiService.getModuleProgress(user.value.id, 'safety_measures')
                console.log('Backend response:', backendProgress)
                if (backendProgress.success && backendProgress.progress && Array.isArray(backendProgress.progress.submodule_progress)) {
                    const submodules = backendProgress.progress.submodule_progress;
                    backendCompletedCount.value = submodules.filter(sub => sub.is_completed).length;
                    // Optionally update exploredCards to match backend
                    exploredCards.value = submodules.filter(sub => sub.is_completed).map(sub => sub.submodule_name);
                } else {
                    backendCompletedCount.value = 0;
                }
            } catch (error) {
                console.log('❌ Backend progress load failed:', error.message)
            }
        }
        // No backend progress, show not completed
        isCompleted.value = false
        exploredCards.value = []
        discoveredTips.value = {}
        console.log('📉 No backend progress for Safety Measures, showing not completed')
    } catch (error) {
        console.error('Error loading Safety Measures progress:', error)
        // On error, show not completed
        isCompleted.value = false
        exploredCards.value = []
        discoveredTips.value = {}
    }
}

// Lifecycle
onMounted(async () => {
    await loadProgress()

    // Show welcome message
    setTimeout(() => {
        isLoading.value = false

        const progressMessage = isCompleted.value
            ? `Welcome back, Safety Champion! You've already completed this module with ${exploredCards.value.length}/${safetyCategories.value.length} topics mastered. You can review the content or reset your progress.`
            : `Welcome to the Safety Champions Academy! Learn essential safety skills through interactive visual cards. Click on each safety topic to discover important tips and information.`

        Swal.fire({
            icon: isCompleted.value ? 'success' : 'info',
            title: '🛡️ Safety Champions Academy',
            text: progressMessage,
            timer: 4000,
            showConfirmButton: false,
            background: 'linear-gradient(135deg, #ff9a9e, #fecfef)',
            color: 'white'
        })
    }, 1000)
})
</script>

<style scoped>
.safety-measures-module {
    min-height: 100vh;
    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
    display: flex;
    flex-direction: column;
    font-family: 'Merriweather', serif;
    position: relative;
}

/* Header */
.safety-header {
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

.safety-title h1 {
    margin: 0;
    font-size: 1.8rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    text-align: center;
}

.safety-subtitle {
    margin: 0.5rem 0 0 0;
    font-size: 1rem;
    opacity: 0.9;
    text-align: center;
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

.progress-display {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.progress-text {
    font-size: 0.9rem;
    opacity: 0.9;
    color: white;
    font-weight: 600;
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
.safety-main {
    flex: 1;
    padding: 2rem 0;
}

.safety-body {
    min-height: 80vh;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    margin: 0 1rem;
}

/* Loading Animation */
.loading-safety {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 60vh;
    color: white;
}

.loading-animation {
    position: relative;
    margin-bottom: 2rem;
}

.loading-shield {
    font-size: 4rem;
    animation: pulse 2s ease-in-out infinite;
}

.loading-icons {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
}

.loading-icons span {
    font-size: 2rem;
    animation: bounce 1.5s ease-in-out infinite;
}

.loading-icons span:nth-child(2) {
    animation-delay: 0.2s;
}

.loading-icons span:nth-child(3) {
    animation-delay: 0.4s;
}

.loading-icons span:nth-child(4) {
    animation-delay: 0.6s;
}

@keyframes pulse {

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }
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

/* Academy Content */
.academy-container {
    padding: 2rem;
    color: white;
}

.academy-header {
    text-align: center;
    margin-bottom: 3rem;
}

.academy-header h2 {
    font-size: 2rem;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.academy-header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

/* Safety Categories Grid */
.safety-categories {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.safety-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
}

.safety-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
}

.safety-card.explored {
    background: rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.5);
}

.safety-card.active {
    transform: scale(1.02);
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
}

.card-icon {
    font-size: 3rem;
    text-align: center;
    margin-bottom: 1rem;
}

.card-content h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.card-content p {
    font-size: 0.9rem;
    opacity: 0.8;
    text-align: center;
    margin-bottom: 1rem;
}

.card-progress {
    text-align: center;
    font-weight: 600;
}

.learned {
    color: #4CAF50;
    font-size: 0.9rem;
}

.learn-now {
    color: #FFD700;
    font-size: 0.9rem;
    animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
    from {
        opacity: 0.7;
    }

    to {
        opacity: 1;
    }
}

.completion-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background: linear-gradient(135deg, #4CAF50, #81C784);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4);
    animation: celebration 1s ease-in-out;
}

@keyframes celebration {
    0% {
        transform: scale(0) rotate(0deg);
    }

    50% {
        transform: scale(1.2) rotate(180deg);
    }

    100% {
        transform: scale(1) rotate(360deg);
    }
}

/* Modal Styles */
.card-detail-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
}

.modal-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    max-width: 800px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    color: white;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-header h3 {
    font-size: 1.5rem;
    margin: 0;
}

.close-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.close-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.1);
}

.modal-body {
    padding: 1.5rem;
}

/* Safety Tips Grid */
.safety-tips h4 {
    margin-bottom: 1rem;
    font-size: 1.2rem;
}

.tips-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}

.tip-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}

.tip-card:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

.tip-card.discovered {
    background: rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.5);
}

.tip-icon {
    font-size: 2rem;
    text-align: center;
    margin-bottom: 0.5rem;
}

.tip-content h5 {
    font-size: 1rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.tip-content p {
    font-size: 0.9rem;
    line-height: 1.4;
    opacity: 0.9;
}

.discover-hint {
    font-size: 0.8rem;
    color: #FFD700;
    font-style: italic;
    text-align: center;
}

/* Emergency Section */
.emergency-section {
    margin-bottom: 2rem;
}

.emergency-section h4 {
    margin-bottom: 1rem;
    font-size: 1.2rem;
    color: #ff6b6b;
}

.emergency-card {
    background: rgba(255, 107, 107, 0.2);
    border-radius: 15px;
    padding: 1.5rem;
    border: 2px solid rgba(255, 107, 107, 0.5);
}

.emergency-icon {
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 1rem;
}

.emergency-content h5 {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.emergency-content p {
    margin-bottom: 1rem;
    opacity: 0.9;
    text-align: center;
}

.emergency-numbers {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
}

.emergency-numbers span {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.9rem;
    font-weight: 600;
}

/* Completion Section */
.completion-check {
    text-align: center;
}

.complete-card-btn {
    background: linear-gradient(135deg, #4CAF50, #81C784);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.complete-card-btn:hover:not(:disabled) {
    background: linear-gradient(135deg, #45a049, #66bb6a);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
}

.complete-card-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
}

.exploration-hint {
    color: #FFD700;
}

.tip-progress {
    font-size: 0.9rem;
    margin-top: 0.5rem;
    opacity: 0.8;
}

/* Completion Panel */
.completion-panel {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin-top: 2rem;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

.completion-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
}

.completion-content h3 {
    font-size: 1.8rem;
    margin-bottom: 1rem;
    color: #FFD700;
}

.completion-content p {
    font-size: 1.1rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.achievement-stats {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-bottom: 2rem;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #4CAF50;
}

.stat-label {
    font-size: 0.9rem;
    opacity: 0.8;
}

.completion-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

.complete-module-btn {
    background: linear-gradient(135deg, #FFD700, #FFA726);
    color: #333;
    border: none;
    padding: 1rem 2rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 700;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
}

.complete-module-btn:hover {
    background: linear-gradient(135deg, #FFC107, #FF9800);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

.reset-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.reset-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
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

    .safety-title h1 {
        font-size: 1.5rem;
    }

    .progress-bar {
        width: 150px;
    }

    .safety-categories {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .safety-card {
        padding: 1rem;
    }

    .tips-grid {
        grid-template-columns: 1fr;
    }

    .achievement-stats {
        flex-direction: column;
        gap: 1rem;
    }

    .completion-actions {
        flex-direction: column;
        align-items: center;
    }

    .modal-content {
        margin: 0.5rem;
        max-height: 95vh;
    }
}

/* Additional safety-themed animations */
.safety-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    transition: left 0.5s;
}

.safety-card:hover::before {
    left: 100%;
}

/* Safety Measures Module Button Styling */
:global(.safety-confirm-btn) {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    transition: all 0.3s ease !important;
}

:global(.safety-confirm-btn:hover) {
    background: linear-gradient(135deg, #ff5252 0%, #ff9800 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4) !important;
}

:global(.safety-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

:global(.safety-cancel-btn:hover) {
    background: rgba(255, 255, 255, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* Alternative approach with higher specificity */
:global(.swal2-popup .safety-confirm-btn) {
    background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
}

:global(.swal2-popup .safety-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
}
</style>