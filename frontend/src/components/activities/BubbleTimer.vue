<template>
    <div class="bubble-timer" :class="{ 'jiggle': isJiggling }" @click="handleBubbleClick">
        <div class="bubble-content">
            <div v-if="showingTime" class="time-display">
                {{ formattedTime }}
            </div>
            <div v-else class="bubble-icon">📱</div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export default {
    name: 'BubbleTimer',
    props: {
        startTime: {
            type: Number,
            required: true
        }
    },
    setup(props) {
        const showingTime = ref(false)
        const isJiggling = ref(false)
        const currentTime = ref(Date.now())
        let timeUpdateInterval = null
        let hideTimeTimeout = null

        const elapsedSeconds = computed(() => {
            return Math.floor((currentTime.value - props.startTime) / 1000)
        })

        const formattedTime = computed(() => {
            const seconds = elapsedSeconds.value
            const hours = Math.floor(seconds / 3600)
            const minutes = Math.floor((seconds % 3600) / 60)
            const secs = seconds % 60

            // Format as HH:MM:SS
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
        })

        const handleBubbleClick = () => {
            // Trigger jiggle animation
            isJiggling.value = true
            setTimeout(() => {
                isJiggling.value = false
            }, 600)

            // Toggle between showing time and icon
            showingTime.value = !showingTime.value

            // Clear existing timeout if any
            if (hideTimeTimeout) {
                clearTimeout(hideTimeTimeout)
                hideTimeTimeout = null
            }

            // If we're now showing time, set timeout to hide it after 10 seconds
            if (showingTime.value) {
                hideTimeTimeout = setTimeout(() => {
                    showingTime.value = false
                }, 10000)
            }
        }

        const updateCurrentTime = () => {
            currentTime.value = Date.now()
        }

        onMounted(() => {
            // Update current time every second
            timeUpdateInterval = setInterval(updateCurrentTime, 1000)
        })

        onBeforeUnmount(() => {
            if (timeUpdateInterval) {
                clearInterval(timeUpdateInterval)
            }
            if (hideTimeTimeout) {
                clearTimeout(hideTimeTimeout)
            }
        })

        return {
            showingTime,
            isJiggling,
            formattedTime,
            handleBubbleClick
        }
    }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.bubble-timer {
    position: relative;
    /* Change from fixed to relative for header placement */
    width: 50px;
    /* Smaller size for header */
    height: 50px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    border: 2px solid rgba(255, 255, 255, 0.3);
    user-select: none;
    font-family: 'Merriweather', serif;
    margin-right: 1rem;
    /* Space from exit button */
}

.bubble-timer:hover {
    transform: translateY(-2px) scale(1.05);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5);
}

.bubble-content {
    text-align: center;
    color: white;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
}

.bubble-icon {
    font-size: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.time-display {
    font-size: 0.7rem;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    letter-spacing: 0.3px;
    line-height: 1;
}

.jiggle {
    animation: jiggle 0.6s ease-in-out;
}

@keyframes jiggle {

    0%,
    100% {
        transform: rotate(0deg);
    }

    10% {
        transform: rotate(-8deg);
    }

    20% {
        transform: rotate(8deg);
    }

    30% {
        transform: rotate(-6deg);
    }

    40% {
        transform: rotate(6deg);
    }

    50% {
        transform: rotate(-4deg);
    }

    60% {
        transform: rotate(4deg);
    }

    70% {
        transform: rotate(-2deg);
    }

    80% {
        transform: rotate(2deg);
    }

    90% {
        transform: rotate(-1deg);
    }
}
</style>