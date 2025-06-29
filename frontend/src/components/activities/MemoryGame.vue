<template>
  <div class="memory-game-overlay" @click.self="$emit('close')">
    <div class="game-container">
      <div class="game-header">
        <h2>🧠 Memory Game</h2>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>

      <div class="stats-bar">
        <div class="stat">Moves: <strong>{{ moves }}</strong></div>
        <div class="stat">Time: <strong>{{ formattedTime }}</strong></div>
      </div>

      <div class="game-board" :class="{ 'completed': gameComplete }">
        <div v-for="card in cards" :key="card.id" class="card" :class="{ flipped: card.flipped, matched: card.matched }"
          @click="flipCard(card)">
          <div class="card-inner">
            <div class="card-front">
              <span class="card-icon">✨</span>
            </div>
            <div class="card-back">
              {{ card.icon }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="gameComplete" class="win-screen">
        <div class="win-content">
          <h2>Congratulations! 🎉</h2>
          <p>You matched all the cards!</p>
          <div class="final-stats">
            <div>Final Time: {{ formattedTime }}</div>
            <div>Total Moves: {{ moves }}</div>
          </div>
          <button @click="resetGame" class="play-again-btn">Play Again</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const emit = defineEmits(['close']);
const icons = ['🧙‍♂️', '🐉', '🏰', '🔮', '⚔️', '🛡️', '📜', '💎'];
const cards = ref([]);
const flippedCards = ref([]);
const moves = ref(0);
const timer = ref(0);
let timerInterval = null;

const gameComplete = computed(() => cards.value.length > 0 && cards.value.every(c => c.matched));
const formattedTime = computed(() => {
  const minutes = Math.floor(timer.value / 60);
  const seconds = timer.value % 60;
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
});

const startTimer = () => {
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timer.value++;
  }, 1000);
};

const resetGame = () => {
  moves.value = 0;
  timer.value = 0;
  startTimer();

  const doubledIcons = [...icons, ...icons];
  cards.value = doubledIcons
    .map((icon, index) => ({ id: index, icon, flipped: false, matched: false }))
    .sort(() => 0.5 - Math.random());
};

const flipCard = (card) => {
  if (card.flipped || card.matched || flippedCards.value.length >= 2 || gameComplete.value) {
    return;
  }

  card.flipped = true;
  flippedCards.value.push(card);
  moves.value++;

  if (flippedCards.value.length === 2) {
    const [first, second] = flippedCards.value;
    if (first.icon === second.icon) {
      first.matched = true;
      second.matched = true;
      flippedCards.value = [];

      if (gameComplete.value) {
        clearInterval(timerInterval);
      }
    } else {
      setTimeout(() => {
        first.flipped = false;
        second.flipped = false;
        flippedCards.value = [];
      }, 1000);
    }
  }
};

onMounted(() => {
  resetGame();
});

onUnmounted(() => {
  clearInterval(timerInterval);
});
</script>

<style scoped>
.memory-game-overlay {
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
  z-index: 1000;
}

.game-container {
  background: rgba(46, 38, 70, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 20px;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  position: relative;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.game-header h2 {
  margin: 0;
  font-size: 1.8rem;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.8rem;
  cursor: pointer;
  transition: color 0.3s;
}

.close-btn:hover {
  color: white;
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  background: rgba(0, 0, 0, 0.2);
  padding: 0.8rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.stat {
  font-size: 1.1rem;
}

.stat strong {
  color: #89f7fe;
}

.game-board {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  justify-content: center;
}

.card {
  width: 100%;
  aspect-ratio: 1 / 1;
  perspective: 1000px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.card.flipped .card-inner {
  transform: rotateY(180deg);
}

.card.matched {
  cursor: default;
}

.card.matched .card-inner {
  box-shadow: 0 0 15px #a6ffcb;
  border-radius: 12px;
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2.5rem;
}

.card-front {
  background: linear-gradient(145deg, #667eea, #764ba2);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.card-icon {
  animation: sparkle 2s infinite ease-in-out;
}

@keyframes sparkle {

  0%,
  100% {
    transform: scale(1);
    opacity: 0.7;
  }

  50% {
    transform: scale(1.1);
    opacity: 1;
  }
}

.card-back {
  background: linear-gradient(145deg, #a8edea, #fed6e3);
  color: #333;
  transform: rotateY(180deg);
}

.win-screen {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(46, 38, 70, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

.win-content h2 {
  font-size: 2.5rem;
  color: #81C784;
}

.final-stats {
  margin: 1.5rem 0;
  font-size: 1.2rem;
}

.play-again-btn {
  padding: 0.8rem 1.8rem;
  background: linear-gradient(145deg, #00b09b, #96c93d);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.play-again-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 176, 155, 0.4);
}
</style>
