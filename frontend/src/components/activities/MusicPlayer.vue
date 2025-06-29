<template>
  <div class="music-player-modal" :class="{ minimized: minimized }" @click.self="!minimized && $emit('close')">
    <!-- Full player -->
    <div v-if="!minimized" class="modal-content">
      <button @click="toggleMinimize" class="minimize-btn">−</button>
      <button @click="$emit('close')" class="close-btn">×</button>

      <div class="album-art">
        <span class="music-icon">🎵</span>
      </div>

      <div class="track-info">
        <h3 class="track-title">{{ currentTrack.name }}</h3>
        <p class="track-artist">Your Adventure Soundtrack</p>
      </div>

      <audio ref="audioPlayer" :src="currentTrack.url" @timeupdate="updateProgress" @loadeddata="onLoadedData"
        @ended="handleTrackEnd"></audio>

      <div class="progress-container">
        <input type="range" min="0" :max="duration" step="0.1" v-model="currentTime" @input="seekAudio" class="seek-bar"
          :style="{ backgroundSize: (currentTime / duration) * 100 + '% 100%' }" />
        <div class="time-stamps">
          <span>{{ formatTime(currentTime) }}</span>
          <span>{{ formatTime(duration) }}</span>
        </div>
      </div>

      <div class="controls">
        <button @click="prevTrack" class="control-btn prev-btn">⏮</button>
        <button @click="togglePlay" class="control-btn play-btn">{{ isPlaying ? '⏸' : '▶' }}</button>
        <button @click="nextTrack" class="control-btn next-btn">⏭</button>
      </div>

      <div class="volume-control">
        <span class="volume-icon">🔉</span>
        <input type="range" min="0" max="1" step="0.01" v-model="volume" @input="setVolume" class="volume-slider"
          :style="{ backgroundSize: volume * 100 + '% 100%' }" />
        <span class="volume-icon">🔊</span>
      </div>
    </div>

    <!-- Minimized player -->
    <div v-if="minimized" class="minimized-player" @click="toggleMinimize">
      <div class="album-art-small">
        <span class="music-icon-small">🎵</span>
      </div>
      <div class="track-info-small">
        <p class="track-title-small">Now Playing: {{ currentTrack.name }}</p>
      </div>
      <div class="controls-small">
        <button @click.stop="togglePlay" class="control-btn-small">{{ isPlaying ? '⏸' : '▶' }}</button>
        <button @click.stop="nextTrack" class="control-btn-small">⏭</button>
        <button @click.stop="$emit('close')" class="control-btn-small close-small-btn">×</button>
      </div>
    </div>

    <!-- Audio element moved here to persist during minimize -->
    <audio ref="audioPlayer" :src="currentTrack.url" @timeupdate="updateProgress" @loadeddata="onLoadedData"
      @ended="handleTrackEnd"></audio>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'MusicPlayer',
  setup() {
    const minimized = ref(false)
    const audioPlayer = ref(null)
    const isPlaying = ref(false)
    const currentTime = ref(0)
    const duration = ref(0)
    const volume = ref(0.8)

    const tracks = [
      { name: 'Embrace', url: '/audio/embrace-364091.mp3' },
      { name: 'Eona Ambient', url: '/audio/eona-emotional-ambient-pop-351436.mp3' }
    ]

    const currentTrackIndex = ref(0)
    const currentTrack = ref(tracks[currentTrackIndex.value])
    const autoPlayOnLoad = ref(false)

    const play = () => {
      audioPlayer.value?.play().then(() => {
        isPlaying.value = true
      }).catch(err => {
        console.warn('Play failed:', err.message)
      })
    }

    const pause = () => {
      audioPlayer.value?.pause()
      isPlaying.value = false
    }

    const togglePlay = () => {
      if (isPlaying.value) pause()
      else play()
    }

    const nextTrack = () => {
      currentTrackIndex.value = (currentTrackIndex.value + 1) % tracks.length
      currentTrack.value = tracks[currentTrackIndex.value]
      autoPlayOnLoad.value = true
    }

    const prevTrack = () => {
      currentTrackIndex.value = (currentTrackIndex.value - 1 + tracks.length) % tracks.length
      currentTrack.value = tracks[currentTrackIndex.value]
      autoPlayOnLoad.value = true
    }

    const updateProgress = () => {
      if (audioPlayer.value) {
        currentTime.value = audioPlayer.value.currentTime
        duration.value = audioPlayer.value.duration || 0
      }
    }

    const seekAudio = () => {
      if (audioPlayer.value) {
        audioPlayer.value.currentTime = currentTime.value
      }
    }

    const setVolume = () => {
      if (audioPlayer.value) {
        audioPlayer.value.volume = volume.value
      }
    }

    const handleTrackEnd = () => {
      nextTrack()
    }

    const toggleMinimize = () => {
      minimized.value = !minimized.value
    }

    const onLoadedData = () => {
      setVolume()
      if (autoPlayOnLoad.value) {
        play()
        autoPlayOnLoad.value = false
      }
    }

    const formatTime = (secs) => {
      if (isNaN(secs) || secs === Infinity) return '00:00'
      const minutes = Math.floor(secs / 60)
      const seconds = Math.floor(secs % 60)
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }

    watch(currentTrack, () => {
      if (audioPlayer.value) {
        audioPlayer.value.load()
      }
    })

    onMounted(() => {
      setVolume()
      autoPlayOnLoad.value = true
    })

    onUnmounted(() => {
      pause()
    })

    return {
      audioPlayer,
      isPlaying,
      currentTrack,
      currentTime,
      duration,
      volume,
      togglePlay,
      nextTrack,
      prevTrack,
      updateProgress,
      seekAudio,
      setVolume,
      handleTrackEnd,
      onLoadedData,
      minimized,
      toggleMinimize,
      formatTime
    }
  }
}
</script>

<style scoped>
.music-player-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  transition: all 0.3s ease;
  pointer-events: auto;
}

.modal-content {
  background: rgba(46, 38, 70, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  position: relative;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.3s;
}

.close-btn:hover {
  color: white;
}

.minimize-btn {
  position: absolute;
  top: 15px;
  right: 55px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  transition: color 0.3s;
}

.minimize-btn:hover {
  color: white;
}

.album-art {
  width: 180px;
  height: 180px;
  margin: 1rem auto;
  background: linear-gradient(145deg, #89f7fe, #66a6ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(102, 166, 255, 0.5);
  animation: pulse 4s infinite ease-in-out;
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

.music-icon {
  font-size: 5rem;
  text-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
}

.track-info {
  margin-bottom: 1.5rem;
}

.track-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
}

.track-artist {
  font-size: 1rem;
  opacity: 0.8;
  margin: 0.25rem 0 0 0;
}

.progress-container {
  margin-bottom: 1.5rem;
}

.time-stamps {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  opacity: 0.7;
  padding: 0 5px;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
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

.play-btn:hover {
  box-shadow: 0 0 20px rgba(118, 75, 162, 0.7);
}

.volume-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.volume-icon {
  font-size: 1.2rem;
  opacity: 0.8;
}

/* Custom Range Input Styles */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  background-image: linear-gradient(to right, #89f7fe, #66a6ff);
  background-repeat: no-repeat;
  cursor: pointer;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  background: white;
  border-radius: 50%;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

.volume-slider {
  max-width: 120px;
}

/* Minimized Styles */
.music-player-modal.minimized {
  top: auto;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: auto;
  background: none;
  backdrop-filter: none;
  align-items: flex-end;
  pointer-events: none;
}

.minimized-player {
  pointer-events: all;
  background: rgba(46, 38, 70, 0.95);
  backdrop-filter: blur(15px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 20px;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  border-radius: 15px 15px 0 0;
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.4);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.3s;
}

.minimized-player:hover {
  background: rgba(56, 48, 80, 0.98);
}

.album-art-small {
  width: 45px;
  height: 45px;
  background: linear-gradient(145deg, #89f7fe, #66a6ff);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.music-icon-small {
  font-size: 1.8rem;
}

.track-info-small {
  flex-grow: 1;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 0.9rem;
}

.track-title-small {
  margin: 0;
}

.controls-small {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-btn-small {
  background: none;
  border: none;
  color: white;
  font-size: 1.6rem;
  cursor: pointer;
  opacity: 0.8;
  transition: all 0.3s;
  padding: 5px;
  line-height: 1;
}

.control-btn-small:hover {
  opacity: 1;
  transform: scale(1.1);
}

.close-small-btn {
  font-size: 1.2rem;
}
</style>
