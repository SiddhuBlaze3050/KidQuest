<template>
  <div class="music-player-modal">
    <div class="modal-content">
      <h2>🎵 Music Player</h2>
      <p>Enjoy soothing background music while you focus or relax!</p>

      <audio
        ref="audioPlayer"
        :src="currentTrack.url"
        @timeupdate="updateProgress"
        @loadeddata="onLoadedData"
        @ended="handleTrackEnd"
      ></audio>

      <input
        type="range"
        min="0"
        :max="duration"
        step="0.1"
        v-model="currentTime"
        @input="seekAudio"
        class="seek-bar"
      />

      <div class="controls">
        <button @click="prevTrack">⏮ Prev</button>
        <button @click="togglePlay">{{ isPlaying ? '⏸ Pause' : '▶ Play' }}</button>
        <button @click="nextTrack">⏭ Next</button>
      </div>

      <div class="volume-control">
        Volume:
        <input type="range" min="0" max="1" step="0.01" v-model="volume" @input="setVolume" />
      </div>

      <p class="track-title">Now Playing: {{ currentTrack.name }}</p>

      <button @click="$emit('close')" class="close-btn">❌ Close</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'MusicPlayer',
  setup() {
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

    const onLoadedData = () => {
      setVolume()
      if (autoPlayOnLoad.value) {
        play()
        autoPlayOnLoad.value = false
      }
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
      onLoadedData
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
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #fff;
  border-radius: 12px;
  padding: 30px;
  max-width: 450px;
  text-align: center;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}
.controls button {
  margin: 8px;
  padding: 10px 15px;
  font-size: 16px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  background: #667eea;
  color: white;
}
.track-title {
  margin-top: 15px;
  font-weight: bold;
}
.seek-bar {
  width: 100%;
  margin: 10px 0;
}
.volume-control {
  margin-top: 10px;
}
.close-btn {
  margin-top: 20px;
  background: crimson;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
}
</style>
