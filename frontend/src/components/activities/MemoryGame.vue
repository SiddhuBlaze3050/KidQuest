<template>
  <div class="memory-game-overlay">
    <div class="game-header">
      <h2>🧠 Memory Game</h2>
      <button @click="$emit('close')">❌ Close</button>
    </div>
    <div class="game-board">
      <div
        v-for="card in cards"
        :key="card.id"
        class="card"
        :class="{ flipped: card.flipped || card.matched }"
        @click="flipCard(card)"
      >
        <div class="card-front">❓</div>
        <div class="card-back">{{ card.icon }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const icons = ['🍎', '🍌', '🍇', '🍒', '🍓', '🍍']
const cards = ref([])

const generateCards = () => {
  const doubled = [...icons, ...icons]
  cards.value = doubled
    .map((icon, index) => ({ id: index, icon, flipped: false, matched: false }))
    .sort(() => 0.5 - Math.random())
}

const flippedCards = ref([])

const flipCard = (card) => {
  if (card.flipped || card.matched || flippedCards.value.length >= 2) return

  card.flipped = true
  flippedCards.value.push(card)

  if (flippedCards.value.length === 2) {
    const [first, second] = flippedCards.value
    if (first.icon === second.icon) {
      first.matched = true
      second.matched = true
    } else {
      setTimeout(() => {
        first.flipped = false
        second.flipped = false
      }, 1000)
    }
    flippedCards.value = []
  }
}

generateCards()
</script>

<style scoped>
.memory-game-overlay {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0, 0, 0, 0.2);
}
.game-board {
  display: grid;
  grid-template-columns: repeat(4, 60px);
  gap: 10px;
  justify-content: center;
}
.card {
  width: 60px;
  height: 60px;
  background: #eee;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 24px;
  border-radius: 6px;
  cursor: pointer;
}
.card.flipped,
.card.matched {
  background: #d4edda;
}
</style>
