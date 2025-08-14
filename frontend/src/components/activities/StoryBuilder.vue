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

      <button class="btn save-btn" @click="saveStory" :disabled="isSaving">
        {{ isSaving ? '💫 Saving...' : (editingStory ? '📝 Update Story' : '✨ Save Story') }}
      </button>

      <!-- Saved Stories -->
      <div class="saved-stories" v-if="stories.length > 0">
        <h3>📝 Your Saved Stories ({{ stories.length }})</h3>
        <div class="story-card" v-for="story in stories" :key="story.id">
          <h4>{{ story.title }}</h4>
          <p>{{ story.content.substring(0, 150) }}{{ story.content.length > 150 ? '...' : '' }}</p>
          <div class="story-date" v-if="story.created_at">{{ formatDate(story.created_at) }}</div>
          <div class="story-actions">
            <button @click="editStory(story)" class="btn edit-btn" style="font-size: 0.8rem; padding: 0.3rem 0.8rem; margin-right: 0.5rem; background: linear-gradient(135deg, #4CAF50, #45a049);">✏️ Edit</button>
            <button @click="deleteStory(story.id)" class="btn delete-btn" style="font-size: 0.8rem; padding: 0.3rem 0.8rem; background: linear-gradient(135deg, #ff6b6b, #ff5252);">🗑️ Delete</button>
          </div>
        </div>
      </div>

      <div v-else-if="!isLoading" class="no-stories">
        <p style="text-align: center; color: rgba(255, 255, 255, 0.7); font-style: italic; margin-top: 2rem;">
          ✨ No stories yet! Create your first magical tale! ✨
        </p>
      </div>

      <div v-if="isLoading" class="loading" style="text-align: center; margin-top: 2rem;">
        <p style="color: rgba(255, 255, 255, 0.8);">📚 Loading your stories...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Swal from 'sweetalert2'
import { apiService } from '../../services/api'
import { userUtils } from '../../services/api'

const title = ref('')
const content = ref('')
const stories = ref([])
const currentPrompt = ref({})
const isLoading = ref(false)
const isSaving = ref(false)
const editingStory = ref(null)

const props = defineProps({
  isVisible: Boolean
})

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

// Load stories from backend when component mounts or becomes visible
async function loadStories() {
  console.log('loadStories() called')
  
  if (!userUtils.isLoggedIn()) {
    console.log('User not logged in, cannot load stories')
    return
  }

  try {
    isLoading.value = true
    const currentUser = userUtils.getCurrentUser()
    
    console.log('Current user:', currentUser)
    
    if (!currentUser || !currentUser.id) {
      console.log('No current user found')
      return
    }

    console.log('Fetching stories for user ID:', currentUser.id)
    const response = await apiService.getUserStories(currentUser.id)
    console.log('API response:', response)
    
    if (response.success) {
      stories.value = response.stories || []
      console.log('✅ Stories loaded successfully:', stories.value.length, 'stories')
    } else {
      console.error('Failed to load stories:', response.error)
      stories.value = []
    }
  } catch (error) {
    console.error('Error loading stories:', error)
    stories.value = []
    
    // Show user-friendly error message
    await Swal.fire({
      icon: 'error',
      title: 'Failed to Load Stories',
      text: 'Could not load your saved stories. Please try again.',
      background: 'linear-gradient(135deg, #ff6b6b, #ff5252)',
      color: 'white',
      confirmButtonColor: '#667eea'
    })
  } finally {
    isLoading.value = false
  }
}

// Save story to backend
async function saveStory() {
  if (!title.value.trim() || !content.value.trim()) {
    await Swal.fire({
      icon: 'warning',
      title: 'Incomplete Story! ✍️',
      text: 'Please enter both a title and some content for your story!',
      background: 'linear-gradient(135deg, #667eea, #764ba2)',
      color: 'white',
      confirmButtonColor: '#ff6b6b'
    })
    return
  }

  if (!userUtils.isLoggedIn()) {
    await Swal.fire({
      icon: 'error',
      title: 'Not Logged In',
      text: 'Please log in to save your stories!',
      background: 'linear-gradient(135deg, #667eea, #764ba2)',
      color: 'white',
      confirmButtonColor: '#ff6b6b'
    })
    return
  }

  try {
    isSaving.value = true
    
    const storyData = {
      title: title.value.trim(),
      content: content.value.trim(),
      prompt_used: currentPrompt.value.text || null
    }

    let response
    if (editingStory.value) {
      // Update existing story
      response = await apiService.updateStory(editingStory.value.id, storyData)
    } else {
      // Create new story
      response = await apiService.saveStory(storyData)
    }

    if (response.success) {
      await Swal.fire({
        icon: 'success',
        title: editingStory.value ? 'Story Updated! 📝' : 'Story Saved! 🎉',
        text: editingStory.value ? 'Your story has been updated successfully!' : 'Your magical story has been saved!',
        background: 'linear-gradient(135deg, #4caf50, #45a049)',
        color: 'white',
        timer: 2000,
        showConfirmButton: false
      })

      // Clear form
      title.value = ''
      content.value = ''
      editingStory.value = null
      
      // Reload stories to show the new/updated story
      await loadStories()
      
      // Generate new prompt
      generatePrompt()
    } else {
      throw new Error(response.error || 'Failed to save story')
    }
  } catch (error) {
    console.error('Error saving story:', error)
    await Swal.fire({
      icon: 'error',
      title: 'Save Failed! 😞',
      text: error.message || 'Failed to save your story. Please try again.',
      background: 'linear-gradient(135deg, #ff6b6b, #ff5252)',
      color: 'white',
      confirmButtonColor: '#667eea'
    })
  } finally {
    isSaving.value = false
  }
}

// Edit story
function editStory(story) {
  editingStory.value = story
  title.value = story.title
  content.value = story.content
  if (story.prompt_used) {
    currentPrompt.value = { text: story.prompt_used }
  }
}

// Delete story
async function deleteStory(storyId) {
  const result = await Swal.fire({
    icon: 'warning',
    title: 'Delete Story? 🗑️',
    text: 'Are you sure you want to delete this story? This action cannot be undone.',
    background: 'linear-gradient(135deg, #667eea, #764ba2)',
    color: 'white',
    showCancelButton: true,
    confirmButtonColor: '#ff6b6b',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Yes, delete it!',
    cancelButtonText: 'Cancel'
  })

  if (result.isConfirmed) {
    try {
      const response = await apiService.deleteStory(storyId)
      if (response.success) {
        await Swal.fire({
          icon: 'success',
          title: 'Story Deleted! 🗑️',
          text: 'Your story has been deleted successfully.',
          background: 'linear-gradient(135deg, #4caf50, #45a049)',
          color: 'white',
          timer: 2000,
          showConfirmButton: false
        })
        
        // Reload stories
        await loadStories()
      } else {
        throw new Error(response.error || 'Failed to delete story')
      }
    } catch (error) {
      console.error('Error deleting story:', error)
      await Swal.fire({
        icon: 'error',
        title: 'Delete Failed! 😞',
        text: error.message || 'Failed to delete the story. Please try again.',
        background: 'linear-gradient(135deg, #ff6b6b, #ff5252)',
        color: 'white',
        confirmButtonColor: '#667eea'
      })
    }
  }
}

// Format date for display
function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Watch for when component becomes visible to load stories
watch(() => props.isVisible, (newValue, oldValue) => {
  console.log('StoryBuilder visibility changed:', oldValue, '->', newValue)
  if (newValue) {
    console.log('Loading stories because component became visible')
    loadStories()
  }
}, { immediate: true })

// Generate initial prompt when component mounts
onMounted(() => {
  console.log('StoryBuilder mounted, isVisible:', props.isVisible)
  generatePrompt()
  // Always try to load stories on mount, regardless of visibility
  loadStories()
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

.story-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

.edit-btn:hover {
  box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
}

.delete-btn:hover {
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
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
