<template>
    <div class="pomodoro-overlay" :class="{ minimized: minimized }">
        <!-- Full Timer -->
        <div v-if="!minimized" class="pomodoro-container" @click.self="toggleMinimize">
            <div class="modal-content">
                <!-- Main View -->
                <div v-if="!showSettings">
                    <button @click="toggleMinimize" class="minimize-btn">−</button>
                    <button @click="$emit('close')" class="close-btn">×</button>

                    <h2 class="title">🍅 Pomodoro Timer</h2>

                    <div class="timer-display">
                        <div class="timer-circle" :class="currentMode.id">
                            <div class="time-text">{{ formattedTime }}</div>
                        </div>
                    </div>

                    <div class="mode-text">{{ currentMode.label }}</div>

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
                <button @click.stop="$emit('close')" class="minimized-control-btn">×</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch, defineProps, defineEmits } from 'vue';
import { apiService } from '@/services/api';

const props = defineProps({
    task: {
        type: Object,
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
const activeSessionId = ref(null);

const showSettings = ref(false);
const tempWorkMinutes = ref(workMinutes.value);
const tempBreakMinutes = ref(breakMinutes.value);

const formattedTime = computed(() => {
    const minutes = Math.floor(timeRemaining.value / 60);
    const seconds = timeRemaining.value % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
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

const startTimer = async () => {
    if (isRunning.value) return;

    if (currentMode.value.id === 'WORK' && !activeSessionId.value) {
        try {
            const response = await apiService.startPomodoro(props.task.user_id, props.task.id);
            if (response.success) {
                activeSessionId.value = response.session_id;
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
    timerInterval = setInterval(() => {
        if (timeRemaining.value > 0) {
            timeRemaining.value--;
        } else {
            playBeep();
            switchMode(true);
        }
    }, 1000);
};

const pauseTimer = () => {
    isRunning.value = false;
    clearInterval(timerInterval);
};

const toggleTimer = () => {
    if (isRunning.value) {
        pauseTimer();
    } else {
        startTimer();
    }
};

const completeSession = async () => {
    if (activeSessionId.value) {
        const duration = workMinutes.value; // Always record the full duration for a completed session
        try {
            await apiService.completePomodoro(activeSessionId.value, duration);
            emit('session-complete');
            activeSessionId.value = null;
        } catch (error) {
            console.error("Error completing pomodoro session:", error);
        }
    }
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

onUnmounted(() => {
    clearInterval(timerInterval);
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
</style>