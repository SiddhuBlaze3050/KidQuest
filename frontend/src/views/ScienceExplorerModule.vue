<template>
    <div class="science-adventure-module">
        <!-- Header -->
        <header class="adventure-header">
            <div class="container">
                <div class="header-content">
                    <button @click="goBack" class="back-btn">
                        <i class="fas fa-arrow-left"></i>
                        <span>🏠 Back to Adventure Base</span>
                    </button>
                    <div class="adventure-title">
                        <h1>🔬✨ My Science Adventure World ✨🚀</h1>
                        <p class="adventure-subtitle">Explore, Discover, and Learn Amazing Things!</p>
                    </div>
                    <div class="completion-progress">
                        <div class="progress-info">
                            <span class="progress-icon">🏆</span>
                            <span class="progress-text">{{ completionPercentage }}% Adventure Complete!</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: `${completionPercentage}%` }"></div>
                            <div class="progress-sparkles">
                                <div class="sparkle" v-for="i in 5" :key="i"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="adventure-main">
            <div class="adventure-body">
                <!-- Quest Selection Panel -->
                <div class="quest-selector" v-if="!currentSimulation">
                    <div class="quest-header">
                        <h2>🧪✨ Choose Your Science Quest! ✨🎯</h2>
                        <p class="quest-description">Each quest teaches you amazing science through fun experiments!</p>
                    </div>
                    <div class="quests-grid">
                        <div v-for="sim in simulations" :key="sim.id" class="quest-card" @click="loadSimulation(sim)"
                            :class="{ completed: sim.completed, started: sim.started && !sim.completed }"
                            :style="{ background: sim.gradient }">
                            <div class="quest-sparkles">
                                <div class="sparkle" v-for="i in 3" :key="i"></div>
                            </div>
                            <div class="quest-icon-wrapper">
                                <div class="quest-icon">{{ sim.icon }}</div>
                                <div class="quest-weight">{{ sim.progressWeight }}%</div>
                            </div>
                            <div class="quest-content">
                                <h3>{{ sim.title }}</h3>
                                <p>{{ sim.description }}</p>
                                <div class="quest-meta">
                                    <span class="difficulty-tag">{{ sim.difficulty }}</span>
                                    <span class="time-tag">{{ sim.estimatedTime }}</span>
                                </div>
                                <div class="quest-status">
                                    <span v-if="sim.completed" class="completed-badge">
                                        ⭐ Quest Complete! ⭐
                                    </span>
                                    <span v-else-if="sim.started" class="in-progress-badge">
                                        🔄 In Progress (25% Credit)
                                    </span>
                                    <span v-else class="start-badge">
                                        🚀 Start Quest! 🚀
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Adventure In Progress -->
                <div class="adventure-container" v-if="currentSimulation">
                    <div class="adventure-header-panel">
                        <button @click="goBackToSelection" class="back-to-quests-btn">
                            ← 🎯 Back to Quest Selection
                        </button>
                        <div class="current-quest-title">
                            <h2>{{ currentSimulation.title }} Quest</h2>
                            <div class="quest-badges">
                                <span class="quest-badge">🔬 Science Explorer</span>
                                <span class="difficulty-badge">{{ currentSimulation.difficulty || 'Fun Level' }}</span>
                            </div>
                        </div>
                        <button @click="markSimulationComplete" class="complete-quest-btn"
                            v-if="!currentSimulation.completed">
                            ⭐ Complete Quest! ⭐
                        </button>
                    </div>

                    <div class="science-playground">
                        <iframe ref="scienceIframe" :src="currentSimulation.url" class="science-iframe"
                            :title="currentSimulation.title" frameborder="0" allowfullscreen
                            @load="onIframeLoad"></iframe>
                        <div v-if="isLoadingSimulation" class="loading-adventure">
                            <div class="loading-animation">
                                <div class="loading-rocket">🚀</div>
                                <div class="loading-stars">
                                    <span>⭐</span>
                                    <span>✨</span>
                                    <span>🌟</span>
                                    <span>💫</span>
                                </div>
                            </div>
                            <h3>Loading Your Adventure...</h3>
                            <p>Getting {{ currentSimulation.title }} ready for you!</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { userUtils, apiService } from '@/services/api'
import Swal from 'sweetalert2'

const router = useRouter()
const user = ref(userUtils.getCurrentUser())

// State management
const currentSimulation = ref(null)
const isLoadingSimulation = ref(false)
const completedSimulations = ref(new Set())

// State for tracking progress
const moduleProgress = ref(0)

// PhET Simulations with adventure theme and proper progress weights
const simulations = ref([
    {
        id: 'balancing-act',
        title: 'Balance Master',
        description: 'Learn about balance and weight distribution by becoming a balance master!',
        icon: '⚖️',
        url: 'https://phet.colorado.edu/sims/html/balancing-act/latest/balancing-act_en.html',
        completed: false,
        started: false,
        timeSpent: 0,
        gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        difficulty: 'Explorer',
        progressWeight: 16.67, // Matches backend submodule progress weight
        estimatedTime: '10-15 min',
        submodule_name: 'balance_master' // Updated to match backend
    },
    {
        id: 'forces-motion',
        title: 'Force Detective',
        description: 'Discover the secrets of forces and motion in this exciting physics adventure!',
        icon: '⚡',
        url: 'https://phet.colorado.edu/sims/html/forces-and-motion-basics/latest/forces-and-motion-basics_en.html',
        completed: false,
        started: false,
        timeSpent: 0,
        gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        difficulty: 'Detective',
        progressWeight: 16.67, // Matches backend submodule progress weight
        estimatedTime: '15-20 min',
        submodule_name: 'force_detective' // Updated to match backend
    },
    {
        id: 'gravity-orbits',
        title: 'Space Explorer',
        description: 'Journey through space and learn about gravity and planetary orbits!',
        icon: '🌌',
        url: 'https://phet.colorado.edu/sims/html/gravity-and-orbits/latest/gravity-and-orbits_en.html',
        completed: false,
        started: false,
        timeSpent: 0,
        gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        difficulty: 'Astronaut',
        progressWeight: 16.67, // Matches backend submodule progress weight
        estimatedTime: '20-25 min',
        submodule_name: 'space_explorer' // Updated to match backend
    },
    {
        id: 'wave-string',
        title: 'Wave Wizard',
        description: 'Master the magic of waves and vibrations with your wave powers!',
        icon: '🌊',
        url: 'https://phet.colorado.edu/sims/html/wave-on-a-string/latest/wave-on-a-string_en.html',
        completed: false,
        started: false,
        timeSpent: 0,
        gradient: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        difficulty: 'Wizard',
        progressWeight: 16.67, // Matches backend submodule progress weight
        estimatedTime: '15-20 min',
        submodule_name: 'wave_wizard' // Updated to match backend
    },
    {
        id: 'states-matter',
        title: 'Matter Transformer',
        description: 'Transform between solids, liquids, and gases in this molecular adventure!',
        icon: '🧪',
        url: 'https://phet.colorado.edu/sims/html/states-of-matter/latest/states-of-matter_en.html',
        completed: false,
        started: false,
        timeSpent: 0,
        gradient: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        difficulty: 'Scientist',
        progressWeight: 16.67, // Matches backend submodule progress weight
        estimatedTime: '15-20 min',
        submodule_name: 'matter_transformer' // Updated to match backend
    },
    {
        id: 'energy-skate-park',
        title: 'Energy Master',
        description: 'Master the laws of energy conservation in this thrilling skate park adventure!',
        icon: '🛹',
        url: 'https://phet.colorado.edu/sims/html/energy-skate-park/latest/energy-skate-park_en.html',
        completed: false,
        started: false,
        timeSpent: 0,
        gradient: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
        difficulty: 'Master',
        progressWeight: 16.65, // Matches backend submodule progress weight (slightly less to total 100%)
        estimatedTime: '10-15 min',
        submodule_name: 'energy_master' // Updated to match backend
    }
])

// Computed properties with proper progress calculation
const completionPercentage = computed(() => {
    return moduleProgress.value
})

const questsStarted = computed(() => {
    return simulations.value.filter(sim => sim.started || sim.completed).length
})

const questsCompleted = computed(() => {
    return simulations.value.filter(sim => sim.completed).length
})

const totalEstimatedTime = computed(() => {
    const remainingQuests = simulations.value.filter(sim => !sim.completed)
    if (remainingQuests.length === 0) return '0 min'

    const totalMinutes = remainingQuests.reduce((sum, quest) => {
        const timeRange = quest.estimatedTime.match(/(\d+)-(\d+)/)
        if (timeRange) {
            return sum + parseInt(timeRange[2]) // Use max time for estimation
        }
        return sum + 15 // Default fallback
    }, 0)

    if (totalMinutes > 60) {
        return `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m`
    }
    return `${totalMinutes} min`
})

// Methods
const goBack = () => {
    router.push('/child-dashboard')
}

const goBackToSelection = () => {
    currentSimulation.value = null
}

const loadSimulation = (simulation) => {
    currentSimulation.value = simulation
    isLoadingSimulation.value = true

    // Mark as started if not already
    if (!simulation.started && !simulation.completed) {
        simulation.started = true
        simulation.startTime = Date.now()
        saveProgress() // Save that we started this quest
    }

    // Show exciting loading message
    Swal.fire({
        title: '🚀 Adventure Starting!',
        html: `
            <div style="text-align: center;">
                <div style="font-size: 3rem; margin: 1rem 0;">✨🔬⚡</div>
                <p style="font-size: 1.1rem; color: #667eea;">
                    Preparing your ${simulation.title} adventure...
                </p>
                <div style="background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 10px; margin: 1rem 0;">
                    <p style="font-size: 0.9rem; margin: 0;">
                        <strong>Progress Weight:</strong> ${simulation.progressWeight}% of total adventure<br>
                        <strong>Estimated Time:</strong> ${simulation.estimatedTime}
                    </p>
                </div>
            </div>
        `,
        timer: 2000,
        timerProgressBar: true,
        showConfirmButton: false,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
    })
}

const onIframeLoad = () => {
    setTimeout(() => {
        isLoadingSimulation.value = false
    }, 1000)
}

const saveSubmoduleProgress = async (simulation) => {
    if (!user.value || !simulation.submodule_name) return

    try {
        // Save individual submodule progress
        const response = await apiService.updateModuleProgress({
            user_id: user.value.id,
            module_type: 'science_explorer', // Ensure lowercase
            submodule_name: simulation.submodule_name,
            progress_percentage: 100, // Individual submodule is 100% complete
            is_completed: true,
            progress_data: {
                simulation_id: simulation.id,
                title: simulation.title,
                completed_at: Date.now(),
                progress_weight: simulation.progressWeight
            }
        })
        console.log(`✅ Saved submodule progress for ${simulation.submodule_name}:`, response)
    } catch (error) {
        console.warn(`⚠️ Failed to save submodule progress for ${simulation.submodule_name}:`, error)
    }
}

const markSimulationComplete = async () => {
    if (!currentSimulation.value || !user.value) return

    try {
        const result = await Swal.fire({
            title: '🎉 Science Quest Mastered!',
            html: `
                <div style="text-align: center; line-height: 1.8;">
                    <div style="font-size: 4rem; margin: 1rem 0;">🧪✨🔬</div>
                    <p style="font-size: 1.2rem; color: #4a5568; font-weight: 600;">
                        Amazing! You've mastered the ${currentSimulation.value.title} quest!
                    </p>
                    <p style="color: #718096; margin: 1rem 0;">
                        Your scientific discovery skills are legendary! 🌟
                    </p>
                    <div style="font-size: 3rem; margin: 1rem 0;">⭐🏆⭐</div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: '🎯 Mark as Complete!',
            cancelButtonText: '🔬 Continue Exploring',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            customClass: {
                popup: 'science-quest-popup',
                confirmButton: 'quest-confirm-btn',
                cancelButton: 'quest-cancel-btn'
            }
        })

        if (!result.isConfirmed) {
            return // User cancelled, don't mark as complete
        }

        // Calculate time spent
        if (currentSimulation.value.startTime) {
            currentSimulation.value.timeSpent = Math.floor((Date.now() - currentSimulation.value.startTime) / 1000 / 60) // in minutes
        }

        // Mark as completed
        currentSimulation.value.completed = true
        currentSimulation.value.started = true // Ensure it's marked as started too
        completedSimulations.value.add(currentSimulation.value.id)

        // Recalculate progress - sum the progress weights of completed submodules
        const completedSubmodules = simulations.value.filter(sim => sim.completed)
        moduleProgress.value = completedSubmodules.reduce((total, sim) => total + sim.progressWeight, 0)

        // Save progress locally first (most important)
        await saveProgress()

        // Save individual submodule progress
        await saveSubmoduleProgress(currentSimulation.value)

        // Try to create achievement (but don't fail if it doesn't work)
        try {
            const achievementData = {
                user_id: user.value.id,
                badge_name: `Science: ${currentSimulation.value.title} Master`,
                description: `Completed the ${currentSimulation.value.title} science quest in ${currentSimulation.value.timeSpent || 'unknown'} minutes!`,
                badge_type: 'science_quest',
                icon: currentSimulation.value.icon
            }
            await apiService.createAchievement(achievementData)
            console.log('✅ SIMPLE: Achievement created successfully')
        } catch (achievementError) {
            console.warn('⚠️ SIMPLE: Achievement creation failed, but quest completion is saved:', achievementError)
        }

        // Try additional module progress update (redundant but helpful)
        try {
            await apiService.updateModuleProgress({
                user_id: user.value.id,
                module_type: 'science_explorer', // Use the correct module type
                submodule_name: currentSimulation.value.submodule_name, // Send submodule name
                progress_percentage: currentSimulation.value.progressWeight, // Use actual progress weight
                is_completed: true
            })
            console.log('✅ SIMPLE: Module progress updated successfully')
        } catch (moduleError) {
            console.warn('⚠️ SIMPLE: Module progress update failed, but local progress is saved:', moduleError)
        }

        // Success message
        await Swal.fire({
            title: '� Science Champion!',
            html: `
                <div style="text-align: center;">
                    <div style="font-size: 4rem; margin: 1rem 0;">�🧪🎊</div>
                    <p style="font-size: 1.1rem; color: #4a5568;">
                        You are now a ${currentSimulation.value.title} Master!
                    </p>
                    <div style="font-size: 3rem; margin: 1rem 0;">📈💪🔬</div>
                    ${moduleProgress.value === 100 ? '<p style="color: #28a745; font-weight: 700; font-size: 1.2rem;">� CONGRATULATIONS! You\'ve completed the entire Science Adventure! 🎊</p>' : ''}
                </div>
            `,
            timer: 3000,
            timerProgressBar: true,
            background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            color: 'white'
        })
    } catch (error) {
        console.error('❌ Error completing simulation:', error)
        Swal.fire({
            icon: 'error',
            title: 'Oops!',
            text: 'Something went wrong. Please try again.',
            background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)',
            color: 'white'
        })
    }
}

const saveProgress = async () => {
    if (!user.value) {
        console.log('⚠️ No user found, skipping progress save')
        return
    }

    try {
        // Prepare simulation progress data
        const simulationProgressData = simulations.value.map(sim => ({
            id: sim.id,
            submodule_name: sim.submodule_name,
            completed: sim.completed,
            started: sim.started,
            timeSpent: sim.timeSpent || 0,
            startTime: sim.startTime,
            progress_weight: sim.progressWeight
        }))

        // Track submodule progress
        const submoduleProgress = {}
        simulations.value.forEach(sim => {
            if (sim.submodule_name) {
                // Use the actual progress weight for each submodule
                submoduleProgress[sim.submodule_name] = {
                    progress_percentage: sim.completed ? sim.progressWeight : 0,
                    is_completed: sim.completed
                }
            }
        })

        // Calculate total module progress by summing submodule percentages
        const totalProgress = Object.values(submoduleProgress).reduce((sum, submodule) =>
            sum + submodule.progress_percentage, 0)

        // Prepare full progress data
        const progressData = {
            simulations: simulationProgressData,
            completionPercentage: totalProgress,
            submodule_progress: submoduleProgress,
            lastAccessed: Date.now()
        }

        // Save to backend
        try {
            const response = await apiService.updateModuleProgress({
                user_id: user.value.id,
                module_type: 'science_explorer',
                progress_percentage: totalProgress,
                is_completed: totalProgress === 100,
                progress_data: progressData,
                submodule_progress: submoduleProgress
            })
            console.log('✅ Saved progress to backend:', response)
        } catch (apiError) {
            console.warn('⚠️ Backend save failed:', apiError)
        }

        console.log('✅ Progress save completed')
    } catch (error) {
        console.error('❌ Progress save error:', error)
    }
}

const loadProgress = async () => {
    if (!user.value) return;
    try {
        const response = await apiService.getModuleProgress(user.value.id, 'science_explorer');
        let backendProgress = 0;

        // Use the correct structure: response.progress.submodule_progress (array)
        if (response.success && response.progress && Array.isArray(response.progress.submodule_progress)) {
            const submodules = response.progress.submodule_progress;

            // Calculate progress by summing actual progress weights of completed submodules
            backendProgress = 0;
            submodules.forEach(sub => {
                if (sub.is_completed) {
                    // Find the corresponding simulation to get the correct progress weight
                    const sim = simulations.value.find(s => s.submodule_name === sub.submodule_name);
                    if (sim) {
                        backendProgress += sim.progressWeight;
                    }
                }
            });

            // Update simulation states
            submodules.forEach(sub => {
                const sim = simulations.value.find(s => s.submodule_name === sub.submodule_name);
                if (sim) {
                    sim.completed = !!sub.is_completed;
                    sim.started = !!sub.is_completed;
                }
            });
        } else {
            backendProgress = 0;
            simulations.value.forEach(sim => {
                sim.completed = false;
                sim.started = false;
            });
        }

        moduleProgress.value = backendProgress;
    } catch (error) {
        moduleProgress.value = 0;
        simulations.value.forEach(sim => {
            sim.completed = false;
            sim.started = false;
        });
    }
};

// Lifecycle
onMounted(() => {
    loadProgress()
})
</script>

<style scoped>
.science-adventure-module {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.adventure-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    position: relative;
    overflow: hidden;
}

.adventure-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="80" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="60" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="30" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
    pointer-events: none;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

.header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    flex-wrap: wrap;
}

.back-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.back-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.adventure-title {
    text-align: center;
    flex: 1;
}

.adventure-title h1 {
    font-size: 2.5rem;
    margin: 0;
    font-weight: 800;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.adventure-subtitle {
    font-size: 1.2rem;
    margin: 0.5rem 0 0 0;
    opacity: 0.9;
    font-weight: 500;
}

.completion-progress {
    text-align: right;
    min-width: 200px;
}

.progress-info {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.progress-icon {
    font-size: 1.2rem;
}

.progress-text {
    font-weight: 600;
    font-size: 1.1rem;
}

.progress-details {
    margin-bottom: 0.5rem;
}

.progress-stats {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
}

.stat {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.progress-bar {
    position: relative;
    background: rgba(255, 255, 255, 0.2);
    height: 12px;
    border-radius: 10px;
    overflow: hidden;
    backdrop-filter: blur(10px);
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #28a745, #20c997, #17a2b8);
    border-radius: 10px;
    transition: width 0.8s ease;
    position: relative;
}

.progress-sparkles {
    position: absolute;
    top: -5px;
    left: 0;
    right: 0;
    height: 22px;
    pointer-events: none;
}

.sparkle {
    position: absolute;
    width: 4px;
    height: 4px;
    background: white;
    border-radius: 50%;
    animation: twinkle 1.5s infinite;
}

.sparkle:nth-child(1) {
    left: 20%;
    animation-delay: 0s;
}

.sparkle:nth-child(2) {
    left: 40%;
    animation-delay: 0.3s;
}

.sparkle:nth-child(3) {
    left: 60%;
    animation-delay: 0.6s;
}

.sparkle:nth-child(4) {
    left: 80%;
    animation-delay: 0.9s;
}

.sparkle:nth-child(5) {
    left: 90%;
    animation-delay: 1.2s;
}

@keyframes twinkle {

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

.adventure-main {
    padding: 2rem 0;
}

.adventure-body {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1.5rem;
}

.quest-selector {
    text-align: center;
}

.quest-header {
    margin-bottom: 3rem;
}

.quest-header h2 {
    font-size: 3rem;
    color: white;
    margin-bottom: 1rem;
    font-weight: 800;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.quest-description {
    font-size: 1.3rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 2rem;
    font-weight: 500;
}

.quests-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.quest-card {
    position: relative;
    background: white;
    border-radius: 25px;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    border: 3px solid transparent;
}

.quest-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
}

.quest-card:hover::before {
    left: 100%;
}

.quest-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    border-color: rgba(255, 255, 255, 0.3);
}

.quest-sparkles {
    position: absolute;
    top: 1rem;
    right: 1rem;
    display: flex;
    gap: 0.5rem;
}

.quest-sparkles .sparkle {
    width: 6px;
    height: 6px;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 50%;
    animation: sparkleFloat 2s infinite;
}

.quest-sparkles .sparkle:nth-child(2) {
    animation-delay: 0.5s;
}

.quest-sparkles .sparkle:nth-child(3) {
    animation-delay: 1s;
}

@keyframes sparkleFloat {

    0%,
    100% {
        transform: translateY(0px) rotate(0deg);
        opacity: 0.6;
    }

    50% {
        transform: translateY(-10px) rotate(180deg);
        opacity: 1;
    }
}

.quest-icon-wrapper {
    background: rgba(255, 255, 255, 0.1);
    width: 100px;
    height: 100px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem;
    backdrop-filter: blur(10px);
    position: relative;
    /* Added for quest-weight positioning */
}

.quest-icon {
    font-size: 3rem;
}

.quest-weight {
    position: absolute;
    top: 0;
    right: 0;
    background: rgba(255, 255, 255, 0.2);
    color: white;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    backdrop-filter: blur(10px);
    transform: translate(50%, -50%);
}

.quest-content h3 {
    font-size: 1.8rem;
    color: white;
    margin-bottom: 1rem;
    font-weight: 700;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.quest-content p {
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: 1.5rem;
    line-height: 1.6;
    font-size: 1.1rem;
}

.quest-meta {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    margin-bottom: 1rem;
}

.difficulty-tag,
.time-tag {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    backdrop-filter: blur(10px);
}

.quest-status {
    margin-top: 1rem;
}

.completed-badge {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.in-progress-badge {
    background: linear-gradient(135deg, #ffc107, #ff9800);
    color: white;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}

.start-badge {
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
    color: white;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    font-weight: 700;
    font-size: 1.1rem;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.quest-card.completed {
    background: linear-gradient(135deg, #d4edda, #c3e6cb);
    border-color: #28a745;
    transform: scale(0.98);
}

.quest-card.started {
    background: linear-gradient(135deg, #e0f2f7, #cce5ff);
    border-color: #007bff;
    transform: scale(1.01);
}

.adventure-container {
    background: white;
    border-radius: 25px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.adventure-header-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
}

.back-to-quests-btn {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.back-to-quests-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
}

.current-quest-title {
    text-align: center;
    flex: 1;
}

.current-quest-title h2 {
    font-size: 2rem;
    margin: 0 0 0.5rem 0;
    font-weight: 700;
}

.quest-badges {
    display: flex;
    justify-content: center;
    gap: 1rem;
    flex-wrap: wrap;
}

.quest-badge,
.difficulty-badge {
    background: rgba(255, 255, 255, 0.2);
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    backdrop-filter: blur(10px);
}

.complete-quest-btn {
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    border: none;
    padding: 1rem 2rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 700;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
}

.complete-quest-btn:hover {
    background: linear-gradient(135deg, #20c997, #17a2b8);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

.science-playground {
    position: relative;
    height: 75vh;
    min-height: 600px;
}

.science-iframe {
    width: 100%;
    height: 100%;
    border: none;
    background: #f8f9fa;
}

.loading-adventure {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: white;
    text-align: center;
}

.loading-animation {
    position: relative;
    margin-bottom: 2rem;
}

.loading-rocket {
    font-size: 4rem;
    animation: rocketBounce 2s infinite;
}

@keyframes rocketBounce {

    0%,
    100% {
        transform: translateY(0px) rotate(-5deg);
    }

    50% {
        transform: translateY(-20px) rotate(5deg);
    }
}

.loading-stars {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 1rem;
}

.loading-stars span {
    font-size: 1.5rem;
    animation: starTwinkle 1.5s infinite;
}

.loading-stars span:nth-child(2) {
    animation-delay: 0.3s;
}

.loading-stars span:nth-child(3) {
    animation-delay: 0.6s;
}

.loading-stars span:nth-child(4) {
    animation-delay: 0.9s;
}

@keyframes starTwinkle {

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

.loading-adventure h3 {
    font-size: 2rem;
    margin-bottom: 1rem;
    font-weight: 700;
}

.loading-adventure p {
    font-size: 1.2rem;
    opacity: 0.9;
}

/* Responsive Design */
@media (max-width: 768px) {
    .adventure-title h1 {
        font-size: 2rem;
    }

    .quest-header h2 {
        font-size: 2.2rem;
    }

    .quests-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }

    .quest-card {
        padding: 1.5rem;
    }

    .science-playground {
        height: 60vh;
        min-height: 500px;
    }

    .header-content {
        flex-direction: column;
        gap: 1rem;
    }

    .completion-progress {
        text-align: center;
        min-width: auto;
    }

    .progress-stats {
        justify-content: center;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .stat {
        font-size: 0.8rem;
        padding: 0.3rem 0.6rem;
    }

    .quest-meta {
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .difficulty-tag,
    .time-tag {
        font-size: 0.8rem;
        padding: 0.3rem 0.8rem;
    }

    .quest-weight {
        font-size: 0.7rem;
        padding: 0.3rem 0.6rem;
    }
}

@media (max-width: 480px) {
    .adventure-title h1 {
        font-size: 1.5rem;
    }

    .quest-header h2 {
        font-size: 1.8rem;
    }

    .container,
    .adventure-body {
        padding: 0 1rem;
    }

    .progress-stats {
        flex-direction: column;
        align-items: center;
        gap: 0.3rem;
    }

    .stat {
        font-size: 0.75rem;
    }

    .quest-icon-wrapper {
        width: 80px;
        height: 80px;
    }

    .quest-icon {
        font-size: 2.5rem;
    }

    .completed-badge,
    .in-progress-badge,
    .start-badge {
        padding: 0.6rem 1.2rem;
        font-size: 1rem;
    }
}

/* Science Explorer Module Button Styling */
:global(.quest-confirm-btn) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.3s ease !important;
}

:global(.quest-confirm-btn:hover) {
    background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
}

:global(.quest-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

:global(.quest-cancel-btn:hover) {
    background: rgba(255, 255, 255, 0.3) !important;
    transform: translateY(-2px) !important;
}

/* Alternative approach with higher specificity */
:global(.swal2-popup .quest-confirm-btn) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 700 !important;
    margin: 0 10px !important;
    color: white !important;
}

:global(.swal2-popup .quest-cancel-btn) {
    background: rgba(255, 255, 255, 0.2) !important;
    border: none !important;
    padding: 12px 24px !important;
    border-radius: 25px !important;
    font-weight: 600 !important;
    margin: 0 10px !important;
    color: white !important;
}
</style>