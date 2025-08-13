<template>
    <div class="pomodoro-overlay" :class="{ minimized: minimized }">
        <!-- Full Timer -->
        <div v-if="!minimized" class="pomodoro-container" @click.self="toggleMinimize">
            <div class="modal-content">
                <!-- Main View -->
                <div v-if="!showSettings">
                    <button @click="toggleMinimize" class="minimize-btn">−</button>
                    <button @click="handleClose" class="close-btn">×</button>

                    <h2 class="title">🍅 Pomodoro Timer</h2>

                    <div class="timer-display">
                        <div class="timer-circle" :class="currentMode.id">
                            <div class="time-text">{{ formattedTime }}</div>
                        </div>
                    </div>

                    <div class="mode-text">{{ currentMode.label }}</div>

                    <!-- Real-time tracking info -->
             <!--   <div v-if="activeSessionId" class="tracking-info">
                        <div class="tracking-stats">
                            <div class="stat">
                                <span class="stat-label">Session Work:</span>
                                <span class="stat-value">{{ currentSessionWorkTimeFormatted }}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Session Break:</span>
                                <span class="stat-value">{{ currentSessionBreakTimeFormatted }}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Pauses:</span>
                                <span class="stat-value">{{ pauseCount }}</span>
                            </div>
                        </div>
                        <div v-if="isSessionPaused" class="session-status">
                            <span class="status-indicator paused">Session Paused</span>
                        </div>
                    </div>-->
                    <!-- Simplified tracking info -->
                    <div v-if="activeSessionId" class="tracking-info">
                        <div class="tracking-stats">
                            <div class="stat">
                                <span class="stat-label">Work Time:</span>
                                <span class="stat-value">{{ formatTime(totalWorkTime) }}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Session Duration:</span>
                                <span class="stat-value">{{ formatTime(sessionDuration) }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="controls">
                        <button @click="resetTimer" class="control-btn reset-btn" title="Reset">
                            🔄
                        </button>
                        <button @click="toggleTimer" class="control-btn play-btn" :class="{ 'is-running': isRunning }">
                            {{ isRunning ? '⏸' : '▶' }}
                        </button>
                        <button @click="skipMode" class="control-btn skip-btn" title="Skip">
                            ⏭
                        </button>
                    </div>

                    <!-- Enhanced controls for active sessions -->
                   
                   <!-- <div v-if="activeSessionId" class="enhanced-controls">
                        <button 
                            @click="pauseSession" 
                            class="control-btn pause-btn" 
                            :disabled="isSessionPaused"
                        >
                            ⏸ {{ isSessionPaused ? 'Paused' : 'Pause Session' }}
                        </button>
                        <button 
                            @click="resumeSession" 
                            class="control-btn resume-btn" 
                            :disabled="!isSessionPaused"
                        >
                            ▶ Resume Session
                        </button>
                        <button @click="abandonSession" class="control-btn abandon-btn">
                            ❌ Abandon
                        </button>
                    </div> -->
                    <button @click="openSettings" class="settings-btn" title="Settings">⚙️</button>
                </div>

                <!-- Settings View -->
                <div v-if="showSettings" class="settings-view">
                    <h2 class="title">Settings</h2>
                    <div class="setting-input">
                        <label for="work-duration">Focus (minutes)</label>
                        <input type="number" id="work-duration" v-model.number="tempWorkMinutes" min="1"
                            class="custom-input">
                    </div>
                    <div class="setting-input">
                        <label for="break-duration">Break (minutes)</label>
                        <input type="number" id="break-duration" v-model.number="tempBreakMinutes" min="1"
                            class="custom-input">
                    </div>
                    <div class="settings-controls">
                        <button @click="cancelSettings" class="settings-control-btn cancel">Cancel</button>
                        <button @click="saveSettings" class="settings-control-btn save">Save</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Minimized Timer -->
        <div v-if="minimized" class="minimized-timer" @click="toggleMinimize">
            <div class="minimized-icon" :class="currentMode.id">🍅</div>
            <div class="minimized-time">{{ formattedTime }}</div>
            <div class="minimized-controls">
                <button @click.stop="toggleTimer" class="minimized-control-btn">{{ isRunning ? '⏸' : '▶' }}</button>
                <button @click.stop="handleClose" class="minimized-control-btn">×</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch, defineProps, defineEmits, onMounted } from 'vue';
import { apiService } from '@/services/api';

const props = defineProps({
    task: {
        type: Object,
        required: false,
        default: null,
    },
    userId: {
        type: Number,
        required: true,
    },
});
const emit = defineEmits(['close', 'session-complete']);

const workMinutes = ref(25);
const breakMinutes = ref(5);
const audioCtx = ref(null);

const MODES = computed(() => ({
    WORK: {
        id: 'work',
        label: 'Focus Time',
        duration: workMinutes.value * 60,
    },
    BREAK: {
        id: 'break',
        label: 'Short Break',
        duration: breakMinutes.value * 60,
    },
}));

const minimized = ref(false);
const isRunning = ref(false);
const currentModeId = ref('WORK');
const currentMode = computed(() => MODES.value[currentModeId.value]);
const timeRemaining = ref(currentMode.value.duration);
let timerInterval = null;
let sessionDurationTimer = null;
const activeSessionId = ref(null);

// Simplified tracking variables
const sessionStartTime = ref(null);
const sessionEndTime = ref(null);
const totalWorkTime = ref(0); // Only time when timer was actually running
const showSettings = ref(false);
const tempWorkMinutes = ref(workMinutes.value);
const tempBreakMinutes = ref(breakMinutes.value);
// Add a reactive variable to force session duration updates
const currentTime = ref(Date.now());

const formattedTime = computed(() => {
    const minutes = Math.floor(timeRemaining.value / 60);
    const seconds = timeRemaining.value % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
});

const formatTime = (seconds) => {
    if (!seconds || seconds < 0) return "0:00";
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
};
// Computed property for session duration
const sessionDuration = computed(() => {
    if (!sessionStartTime.value) return 0;
    const endTime = sessionEndTime.value || currentTime.value
    return Math.floor((endTime - sessionStartTime.value) / 1000);
});

watch(currentMode, (newMode) => {
    if (!isRunning.value) {
        timeRemaining.value = newMode.duration;
    }
});


const playBeep = () => {
    try {
        if (!audioCtx.value) {
            audioCtx.value = new (window.AudioContext || window.webkitAudioContext)();
        }
        const oscillator = audioCtx.value.createOscillator();
        const gainNode = audioCtx.value.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.value.destination);
        gainNode.gain.value = 0.1;
        oscillator.frequency.value = 523.25; // C5
        oscillator.type = 'sine';
        oscillator.start(audioCtx.value.currentTime);
        oscillator.stop(audioCtx.value.currentTime + 0.5);
    } catch (e) {
        console.error("Could not play beep sound", e);
    }
};

/*const updateTrackingTime = () => {
    if (!activeSessionId.value || !lastActiveTime.value) return;
    
    const currentTime = Date.now();
    const elapsedSeconds = Math.floor((currentTime - lastActiveTime.value) / 1000);
    
    if (currentMode.value.id === 'work') {

        currentSessionWorkTime.value += elapsedSeconds;
        totalWorkTime.value += elapsedSeconds;
    } else {
        currentSessionBreakTime.value += elapsedSeconds;
        totalBreakTime.value += elapsedSeconds;
    }
    
    lastActiveTime.value = currentTime;
};*/
const startTimer = async () => {
    if (isRunning.value) return;

    // Start new session if in work mode, no active session, and we have a task
    if (currentMode.value.id === 'work' && !activeSessionId.value && props.task?.id) {
        try {
            console.log(props.task);
            const response = await apiService.startPomodoro(props.userId, props.task.id);
            if (response.success) {
                activeSessionId.value = response.session_id;
                console.log("Pomodoro session started with ID:", activeSessionId.value);
                if (!sessionStartTime.value) {
                    sessionStartTime.value = Date.now();
                }
                totalWorkTime.value = 0;
            } else {
                console.error("Failed to start pomodoro session");
                return;
            }
        } catch (error) {
            console.error("Error starting pomodoro session:", error);
            return;
        }
    }

    isRunning.value = true;
    //lastActiveTime.value = Date.now();
    
    timerInterval = setInterval(() => {
        if (timeRemaining.value > 0) {
            timeRemaining.value--;
            
             // Only count work time when timer is running
             if (activeSessionId.value && currentMode.value.id === 'work') {
                totalWorkTime.value++;
            }
        } else {
            playBeep();
            switchMode(true);
        }
    }, 1000);
};

const pauseTimer = () => {
    if (!isRunning.value) return;
    
    // Update tracking time before pausing
  /*  if (activeSessionId.value) {
        updateTrackingTime();
    }*/
    
    isRunning.value = false;
    clearInterval(timerInterval);
    //lastActiveTime.value = null;
};

const toggleTimer = () => {
    if (isRunning.value) {
        pauseTimer();
    } else {
        startTimer();
    }
};

// =============================================================================
// SECTION 3: Updated Enhanced Control Functions (replace existing ones)
// =============================================================================

/*const pauseSession = async () => {
    if (!activeSessionId.value) return;
    
    // Don't allow session pause if already paused
    if (isSessionPaused.value) return;
    
    try {
        // Update tracking time before pausing
        if (isRunning.value) {
            updateTrackingTime();
        }
        
        await apiService.pausePomodoro(activeSessionId.value);
        
        // Pause the timer if it's running
        if (isRunning.value) {
            pauseTimer();
        }
        
        isSessionPaused.value = true;
        pauseCount.value++;
        
    } catch (error) {
        console.error("Error pausing session:", error);
        // Revert pause count if API call failed
        if (pauseCount.value > 0) {
            pauseCount.value--;
        }
    }
};

const resumeSession = async () => {
    if (!activeSessionId.value || !isSessionPaused.value) return;

    try {
        await apiService.resumePomodoro(activeSessionId.value);
        isSessionPaused.value = false;
        
        // Don't auto-start timer, let user control it
        // startTimer(); // Remove this line
        
    } catch (error) {
        console.error("Error resuming session:", error);
        // Revert pause state if API call failed
        isSessionPaused.value = true;
    }
};

const abandonSession = async () => {
    if (!activeSessionId.value) return;

    try {
        // Update tracking time before abandoning
        if (isRunning.value) {
            updateTrackingTime();
        }
        
        await apiService.abandonPomodoro(
            activeSessionId.value, 
            currentSessionWorkTime.value, 
            currentSessionBreakTime.value
        );
        
        // Reset session state
        pauseTimer();
        activeSessionId.value = null;
        isSessionPaused.value = false;
        currentSessionWorkTime.value = 0;
        currentSessionBreakTime.value = 0;
        pauseCount.value = 0;
        
        emit('session-complete');
    } catch (error) {
        console.error("Error abandoning session:", error);
    }
};*/

/*const completeSession = async () => {
    if (!activeSessionId.value) return;
    
    try {
        // Update tracking time before completing
        if (isRunning.value) {
            updateTrackingTime();
        }
        
        await apiService.completePomodoro(
            activeSessionId.value, 
            currentSessionWorkTime.value, 
            currentSessionBreakTime.value
        );
        
        emit('session-complete');
        
        // Reset session state
        activeSessionId.value = null;
        isSessionPaused.value = false;
        currentSessionWorkTime.value = 0;
        currentSessionBreakTime.value = 0;
        pauseCount.value = 0;
        
    } catch (error) {
        console.error("Error completing pomodoro session:", error);
    }
};*/
// Handle session completion when popup closes
const handleClose = async () => {
    if (activeSessionId.value) {
        sessionEndTime.value = Date.now();
        
        // Calculate total duration
        const totalDuration = Math.floor((sessionEndTime.value - sessionStartTime.value) / 1000);
        
        // Calculate break duration (total duration - work duration)
        const breakDuration = Math.max(0, totalDuration - totalWorkTime.value);
        
        try {
            const response= await apiService.completePomodoro(
                activeSessionId.value, 
                totalWorkTime.value, 
                breakDuration
            );
        } catch (error) {
            console.error("Error completing pomodoro session:", error);
        }
    }
    emit('close');
};


const resetTimer = () => {
    pauseTimer();
    timeRemaining.value = currentMode.value.duration;
};

const switchMode = (autoStartNext = false) => {
    if (currentMode.value.id === 'WORK') {
        completeSession();
    }
    pauseTimer();
    const newModeId = currentModeId.value === 'WORK' ? 'BREAK' : 'WORK';
    currentModeId.value = newModeId;

    if (autoStartNext && newModeId === 'BREAK') {
        setTimeout(() => {
            startTimer();
        }, 1000);
    }
};

const skipMode = () => {
    // When skipping, we don't count it as a completed session.
    // We just switch modes without auto-starting.
    pauseTimer();
    const newModeId = currentModeId.value === 'WORK' ? 'BREAK' : 'WORK';
    currentModeId.value = newModeId;
    timeRemaining.value = MODES.value[newModeId].duration;
};

const toggleMinimize = () => {
    minimized.value = !minimized.value;
};

const openSettings = () => {
    tempWorkMinutes.value = workMinutes.value;
    tempBreakMinutes.value = breakMinutes.value;
    showSettings.value = true;
};

const saveSettings = () => {
    if (tempWorkMinutes.value > 0 && tempBreakMinutes.value > 0) {
        workMinutes.value = tempWorkMinutes.value;
        breakMinutes.value = tempBreakMinutes.value;
        showSettings.value = false;
        if (!isRunning.value) {
            timeRemaining.value = currentMode.value.duration;
        }
    } else {
        alert('Please enter valid durations (greater than 0).');
    }
};

const cancelSettings = () => {
    showSettings.value = false;
};

// Initialize session start time when component mounts
onMounted(() => {
    sessionStartTime.value = Date.now();
    
    // Start a timer to update currentTime every second for real-time session duration
    sessionDurationTimer = setInterval(() => {
        currentTime.value = Date.now();
    }, 1000);
});

onUnmounted(() => {
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    if (sessionDurationTimer) {
        clearInterval(sessionDurationTimer);
    }
    // Ensure session is completed when component is unmounted
    if (activeSessionId.value) {
        handleClose();
    }
});
</script>

<style scoped>
.pomodoro-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1000;
    pointer-events: none;
}

.pomodoro-container {
    pointer-events: all;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(5px);
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal-content {
    background: rgba(46, 38, 70, 0.9);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    border-radius: 20px;
    padding: 2rem;
    width: 90%;
    max-width: 400px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    position: relative;
}

.title {
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
}

.minimize-btn,
.close-btn {
    position: absolute;
    top: 15px;
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    font-size: 1.8rem;
    cursor: pointer;
    transition: color 0.3s;
}

.minimize-btn {
    right: 55px;
    line-height: 1;
}

.close-btn {
    right: 15px;
}

.minimize-btn:hover,
.close-btn:hover {
    color: white;
}

.timer-display {
    margin: 1.5rem 0;
}

.timer-circle {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    margin: 0 auto;
    display: flex;
    justify-content: center;
    align-items: center;
    border: 5px solid;
    transition: border-color 0.5s;
}

.timer-circle.work {
    border-color: #ff6b6b;
}

.timer-circle.break {
    border-color: #4facfe;
}

.time-text {
    font-size: 3.5rem;
    font-weight: bold;
}

.mode-text {
    font-size: 1.2rem;
    opacity: 0.8;
    margin-bottom: 1.5rem;
}

.controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1.5rem;
}

.control-btn {
    background: none;
    border: 2px solid rgba(255, 255, 255, 0.5);
    color: white;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    font-size: 1.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
}

.control-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    border-color: white;
}

.play-btn {
    width: 70px;
    height: 70px;
    font-size: 2.5rem;
    background: linear-gradient(145deg, #667eea, #764ba2);
    border: none;
}

.play-btn.is-running {
    background: linear-gradient(145deg, #ff6b6b, #f093fb);
}

.settings-btn {
    position: absolute;
    bottom: 20px;
    right: 20px;
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.5);
    font-size: 1.5rem;
    cursor: pointer;
    transition: all 0.3s;
}

.settings-btn:hover {
    color: white;
    transform: rotate(45deg);
}

/* Settings View Styles */
.settings-view {
    padding: 1rem;
}

.setting-input {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    font-size: 1.1rem;
}

.custom-input {
    width: 80px;
    padding: 8px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    background: rgba(0, 0, 0, 0.2);
    color: white;
    font-size: 1.1rem;
    text-align: center;
}

.settings-controls {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1rem;
}

.settings-control-btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: bold;
    transition: all 0.3s;
}

.settings-control-btn.cancel {
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

.settings-control-btn.save {
    background: #4CAF50;
    color: white;
}

.settings-control-btn:hover {
    transform: translateY(-2px);
}

/* Tracking Info Styles */
.tracking-info {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.tracking-stats {
    display: flex;
    justify-content: space-around;
    gap: 1rem;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.stat-label {
    font-size: 0.8rem;
    opacity: 0.8;
    margin-bottom: 0.3rem;
}

.stat-value {
    font-size: 1.1rem;
    font-weight: bold;
    color: #4facfe;
}

/* Enhanced Controls Styles */
.enhanced-controls {
    display: flex;
    justify-content: center;
    gap: 0.8rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}

.pause-btn,
.resume-btn,
.abandon-btn {
    padding: 0.6rem 1rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: bold;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.pause-btn {
    background: #ffa726;
    color: white;
}

.pause-btn:hover:not(:disabled) {
    background: #ff9800;
    transform: translateY(-2px);
}

.pause-btn:disabled,
.resume-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
}

.pause-btn:disabled:hover,
.resume-btn:disabled:hover {
    background: inherit;
    transform: none;
}

.resume-btn {
    background: #4CAF50;
    color: white;
}

.resume-btn:hover:not(:disabled) {
    background: #45a049;
    transform: translateY(-2px);
}

.resume-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.abandon-btn {
    background: #f44336;
    color: white;
}

.abandon-btn:hover {
    background: #d32f2f;
    transform: translateY(-2px);
}

/* Minimized Styles */
.minimized-timer {
    pointer-events: all;
    position: fixed;
    top: 15px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(46, 38, 70, 0.95);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 15px;
    transition: all 0.3s;
}

.minimized-timer:hover {
    background: rgba(56, 48, 80, 0.98);
}

.minimized-icon {
    font-size: 1.5rem;
}

.minimized-icon.break {
    filter: hue-rotate(150deg);
}

.minimized-time {
    font-size: 1.2rem;
    font-weight: bold;
}

.minimized-controls {
    display: flex;
    align-items: center;
    gap: 10px;
}

.minimized-control-btn {
    background: none;
    border: none;
    color: white;
    font-size: 1.2rem;
    cursor: pointer;
    opacity: 0.8;
    transition: all 0.3s;
    padding: 5px;
    line-height: 1;
}

.minimized-control-btn:hover {
    opacity: 1;
    transform: scale(1.1);
}
.session-status {
    margin-top: 0.5rem;
    text-align: center;
}

.status-indicator {
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: bold;
}

.status-indicator.paused {
    background: rgba(255, 167, 38, 0.2);
    color: #ffa726;
    border: 1px solid #ffa726;
}
</style>