<template>
  <div class="story-builder-modal">
    <div class="modal-content">
      <!-- Header -->
      <h2>📖 Story Builder</h2>
      <p class="subtitle">Create your own magical story using fun prompts!</p>

      <!-- Prompt Area -->
      <div class="prompt-area" v-if="currentPrompt.text">
        <p class="prompt-text">{{ currentPrompt.text }}</p>
        <img :src="currentPrompt.image" alt="Prompt" class="prompt-image" />
      </div>

      <div class="prompt-actions">
        <button class="btn" @click="generatePrompt">🔁 New Prompt</button>
        <button class="btn" v-if="currentPrompt.text" @click="content = currentPrompt.text">
          ✍️ Use This Prompt
        </button>
      </div>

      <!-- Story Writing -->
      <input
        v-model="title"
        class="story-input"
        placeholder="Enter a captivating title..."
      />
      <textarea
        v-model="content"
        class="story-textarea"
        placeholder="Write your wonderful story here..."
        rows="6"
      ></textarea>

      <button class="btn save-btn" @click="saveStory">✨ Save Story</button>

      <!-- Saved Stories -->
      <div class="saved-stories" v-if="stories.length > 0">
        <h3>📝 Your Saved Stories</h3>
        <div class="story-card" v-for="(story, i) in stories" :key="i">
          <h4>{{ story.title }}</h4>
          <p>{{ story.content }}</p>
        </div>
      </div>

      <button class="close-btn" @click="$emit('close')">❌ Close</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('')
const content = ref('')
const stories = ref([])
const currentPrompt = ref({})

const prompts = [
  { text: "A dragon who loves pizza meets a robot at school.", image: "https://cdn-icons-png.flaticon.com/512/616/616408.png" },
  { text: "You wake up with superpowers, but only for 24 hours!", image: "https://cdn-icons-png.flaticon.com/512/3774/3774298.png" },
  { text: "A talking dog invites you on a treasure hunt.", image: "https://cdn-icons-png.flaticon.com/512/616/616408.png" },
  { text: "Your drawing comes to life and runs away!", image: "https://cdn-icons-png.flaticon.com/512/3038/3038994.png" },
  { text: "You invent a machine that controls the weather.", image: "https://cdn-icons-png.flaticon.com/512/1686/1686769.png" },
  { text: "A magical portal appears in your backyard.", image: "https://cdn-icons-png.flaticon.com/512/3595/3595455.png" },
  { text: "You find a mysterious map hidden inside a book.", image: "https://cdn-icons-png.flaticon.com/512/1828/1828919.png" },
  { text: "Aliens visit Earth to play video games with you.", image: "https://cdn-icons-png.flaticon.com/512/2060/2060936.png" },
]

function generatePrompt() {
  const i = Math.floor(Math.random() * prompts.length)
  currentPrompt.value = prompts[i]
}

function saveStory() {
  if (title.value && content.value) {
    stories.value.unshift({ title: title.value, content: content.value })
    title.value = ''
    content.value = ''
  } else {
    alert("Please enter both a title and some content!")
  }
}
</script>

<style scoped>
.story-builder-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  width: 90%;
  max-width: 500px;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

h2 {
  font-size: 1.8rem;
  color: #4a148c;
  margin-bottom: 0.5rem;
}

.subtitle {
  font-size: 1rem;
  color: #666;
  margin-bottom: 1rem;
}

.prompt-area {
  background: #f3e5f5;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  border-left: 5px solid #ba68c8;
}

.prompt-text {
  font-size: 1rem;
  font-weight: 500;
  color: #6a1b9a;
}

.prompt-image {
  width: 80px;
  margin-top: 0.5rem;
}

.prompt-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 1rem 0;
}

.story-input,
.story-textarea {
  width: 100%;
  padding: 0.8rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 10px;
  margin-bottom: 1rem;
  font-family: inherit;
}

.btn {
  background: #673ab7;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn:hover {
  background: #512da8;
}

.save-btn {
  margin-top: 0.5rem;
  margin-bottom: 1.2rem;
}

.saved-stories {
  margin-top: 1rem;
  text-align: left;
}

.story-card {
  background: #f9f9f9;
  padding: 1rem;
  margin-top: 0.5rem;
  border-left: 5px solid #673ab7;
  border-radius: 8px;
}

.close-btn {
  margin-top: 1rem;
  background: crimson;
  color: white;
  padding: 0.4rem 1rem;
  border-radius: 10px;
  font-weight: bold;
  border: none;
  cursor: pointer;
}
</style>
