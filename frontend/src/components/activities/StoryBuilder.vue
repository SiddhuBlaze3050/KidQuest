<template>
  <div class="story-builder-modal" @click.self="$emit('close')">
    <div class="modal-content">
      <!-- Close button -->
      <button class="close-btn" @click="$emit('close')">×</button>

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
      <input v-model="title" class="story-input" placeholder="Enter a captivating title..." />
      <textarea v-model="content" class="story-textarea" placeholder="Write your wonderful story here..."
        rows="6"></textarea>

      <button class="btn save-btn" @click="saveStory">✨ Save Story</button>

      <!-- Saved Stories -->
      <div class="saved-stories" v-if="stories.length > 0">
        <h3>📝 Your Saved Stories</h3>
        <div class="story-card" v-for="(story, i) in stories" :key="i">
          <h4>{{ story.title }}</h4>
          <p>{{ story.content }}</p>
          <div class="story-date" v-if="story.date">{{ story.date }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'

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
  { text: "A unicorn invites you to a secret rainbow kingdom.", image: "https://cdn-icons-png.flaticon.com/512/3595/3595455.png" },
  { text: "Your stuffed animal comes to life and needs your help!", image: "https://cdn-icons-png.flaticon.com/512/3038/3038994.png" },
  { text: "You discover a time machine in your grandmother's attic.", image: "https://cdn-icons-png.flaticon.com/512/1686/1686769.png" },
  { text: "A friendly monster under your bed wants to be friends.", image: "https://cdn-icons-png.flaticon.com/512/616/616408.png" }
]

function generatePrompt() {
  const i = Math.floor(Math.random() * prompts.length)
  currentPrompt.value = prompts[i]
}

function saveStory() {
  if (title.value.trim() && content.value.trim()) {
    stories.value.unshift({
      title: title.value.trim(),
      content: content.value.trim(),
      date: new Date().toLocaleDateString()
    })

    // Clear the form
    title.value = ''
    content.value = ''

    // Show success message
    Swal.fire({
      icon: 'success',
      title: 'Story Saved! 📚',
      text: 'Your magical story has been added to your collection!',
      timer: 2000,
      showConfirmButton: false,
      background: 'linear-gradient(135deg, #667eea, #764ba2)',
      color: 'white'
    })

    // Generate a new prompt for next story
    generatePrompt()
  } else {
    Swal.fire({
      icon: 'warning',
      title: 'Incomplete Story! ✍️',
      text: 'Please enter both a title and some content for your story!',
      background: 'linear-gradient(135deg, #667eea, #764ba2)',
      color: 'white',
      confirmButtonColor: '#ff6b6b'
    })
  }
}

// Generate initial prompt when component mounts
onMounted(() => {
  generatePrompt()
})
</script>

<style scoped>
.story-builder-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: rgba(46, 38, 70, 0.9);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 20px;
  padding: 2rem;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  overflow-y: auto;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  position: relative;
}

h2 {
  font-size: 2rem;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 1.5rem;
}

.prompt-area {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 1.5rem;
  border-left: 5px solid #ba68c8;
}

.prompt-text {
  font-size: 1.1rem;
  font-weight: 500;
  color: white;
  margin-bottom: 1rem;
}

.prompt-image {
  width: 80px;
  height: 80px;
  object-fit: contain;
  filter: brightness(1.2);
}

.prompt-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin: 1.5rem 0;
}

.story-input,
.story-textarea {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  margin-bottom: 1rem;
  font-family: inherit;
  color: white;
  resize: vertical;
}

.story-input::placeholder,
.story-textarea::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.story-input:focus,
.story-textarea:focus {
  outline: none;
  border-color: #ba68c8;
  box-shadow: 0 0 10px rgba(186, 104, 200, 0.3);
}

.btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: bold;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.save-btn {
  margin: 1rem 0;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  font-size: 1.1rem;
  padding: 1rem 2rem;
}

.save-btn:hover {
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

.saved-stories {
  margin-top: 2rem;
  text-align: left;
}

.saved-stories h3 {
  color: white;
  text-align: center;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.story-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 1.5rem;
  margin-bottom: 1rem;
  border-left: 5px solid #673ab7;
  border-radius: 12px;
  transition: all 0.3s;
}

.story-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.story-card h4 {
  color: white;
  margin-bottom: 0.5rem;
  font-size: 1.1rem;
}

.story-card p {
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.5;
  margin: 0;
}

.story-date {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  margin-top: 0.5rem;
  font-style: italic;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: rgba(255, 82, 82, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 50%;
  font-weight: bold;
  border: none;
  cursor: pointer;
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 82, 82, 1);
  transform: scale(1.1);
}
</style>
