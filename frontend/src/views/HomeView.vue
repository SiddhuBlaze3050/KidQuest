<script>
import { ref, onMounted } from 'vue'
import { userUtils } from '@/services/api'
import LoginModal from '@/components/auth/LoginModal.vue'
import RegisterModal from '@/components/auth/RegisterModal.vue'
import EnhancedChatBot from '@/components/chat/EnhancedChatBot.vue'

export default {
  name: 'HomeView',
  components: {
    LoginModal,
    RegisterModal,
    EnhancedChatBot
  },
  setup() {
    const user = ref(null)
    const showLogin = ref(false)
    const showRegister = ref(false)
    const showChat = ref(false)

    const skills = ref([
      {
        id: 1,
        title: 'Time Mastery',
        emoji: '⏰',
        description: 'Master the ancient art of time management',
        progress: 25,
        house: 'gryffindor'
      },
      {
        id: 2,
        title: 'Galleon Management',
        emoji: '💰',
        description: 'Learn the wizarding ways of financial wisdom',
        progress: 40,
        house: 'slytherin'
      },
      {
        id: 3,
        title: 'Vitality Spells',
        emoji: '🌿',
        description: 'Discover the secrets of health and wellness',
        progress: 60,
        house: 'hufflepuff'
      },
      {
        id: 4,
        title: 'Creative Charms',
        emoji: '🎨',
        description: 'Unleash your artistic magical potential',
        progress: 15,
        house: 'ravenclaw'
      },
      {
        id: 5,
        title: 'Communication Magic',
        emoji: '💬',
        description: 'Master the spells of effective communication',
        progress: 30,
        house: 'gryffindor'
      },
      {
        id: 6,
        title: 'Protection Charms',
        emoji: '🛡️',
        description: 'Learn defensive spells for safety',
        progress: 80,
        house: 'hufflepuff'
      },
      {
        id: 7,
        title: 'Knowledge Trials',
        emoji: '📚',
        description: 'Test your mastery with magical quizzes',
        progress: 70,
        house: 'slytherin'
      }
    ])

    const magicElements = ['⭐', '✨', '🌟', '💫', '🔮', '🪄']

    const checkUserLogin = () => {
      user.value = userUtils.getCurrentUser()

      // Redirect users based on their role
      if (user.value) {
        if (user.value.role === 'admin') {
          window.location.href = '/admin'
        } else if (user.value.role === 'child') {
          window.location.href = '/child-dashboard'
        } else if (user.value.role === 'parent') {
          window.location.href = '/parent-dashboard'
        }
      }
    }

    const handleLoginSuccess = (userData) => {
      user.value = userData.user
      showLogin.value = false

      // Redirect users based on their role
      if (userData.user.role === 'admin') {
        window.location.href = '/admin'
      } else if (userData.user.role === 'child') {
        window.location.href = '/child-dashboard'
      } else if (userData.user.role === 'parent') {
        window.location.href = '/parent-dashboard'
      }
    }

    const handleRegisterSuccess = (userData) => {
      user.value = userData.user
      showRegister.value = false

      // Delay redirect to allow success message to show
      setTimeout(() => {
        // Redirect users based on their role
        if (userData.user.role === 'admin') {
          window.location.href = '/admin'
        } else if (userData.user.role === 'child') {
          window.location.href = '/child-dashboard'
        } else if (userData.user.role === 'parent') {
          window.location.href = '/parent-dashboard'
        }
      }, 3500) // Wait for success message to finish (3000ms timer + 500ms buffer)
    }

    const logout = () => {
      userUtils.logout()
      user.value = null
    }

    const openSkill = (skill) => {
      // Navigate to skill page (implement later)
      console.log('Opening skill:', skill.title)
    }

    const switchToRegister = () => {
      showLogin.value = false
      showRegister.value = true
    }

    const switchToLogin = () => {
      showRegister.value = false
      showLogin.value = true
    }

    const getMagicElement = () => {
      return magicElements[Math.floor(Math.random() * magicElements.length)]
    }

    onMounted(() => {
      checkUserLogin()
    })

    return {
      user,
      showLogin,
      showRegister,
      showChat,
      skills,
      handleLoginSuccess,
      handleRegisterSuccess,
      logout,
      openSkill,
      switchToRegister,
      switchToLogin,
      getMagicElement
    }
  }
}
</script>

<template>
  <div class="kidquest-home">
    <!-- Navigation -->
    <nav class="main-nav">
      <div class="container">
        <div class="nav-content">
          <div class="logo">
            <span class="logo-icon">🏰</span>
            <span class="logo-text">KidQuest</span>
          </div>
          <div class="nav-links" v-if="user">
            <button @click="logout" class="nav-btn logout-btn">
              <i class="fas fa-sign-out-alt"></i>
              Logout
            </button>
          </div>
          <div class="nav-links" v-else>
            <button @click="showLogin = true" class="nav-btn">Login</button>
            <button @click="showRegister = true" class="nav-btn primary">Sign Up</button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
      <div class="container">
        <div class="row align-items-center">
          <!-- Left Content -->
          <div class="col-lg-6">
            <div class="hero-content">
              <h1 class="hero-title">
                <span class="title-highlight">Adventure</span><br>
                Awaits You!
              </h1>
              <p class="hero-subtitle">
                Join the ultimate quest to master life skills! Track homework, build habits,
                and unlock amazing rewards in your personal adventure.
              </p>
              <div class="hero-buttons" v-if="!user">
                <button @click="showRegister = true" class="btn-quest primary">
                  <span class="btn-icon">🚀</span>
                  Start Your Quest
                </button>
                <button @click="showLogin = true" class="btn-quest secondary">
                  <span class="btn-icon">🗝️</span>
                  Continue Adventure
                </button>
              </div>
              <div class="hero-buttons" v-else>
                <div class="welcome-back">
                  <h3>Welcome back, {{ user.username }}! 🎉</h3>
                  <p>Your quest continues...</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Illustration -->
          <div class="col-lg-6">
            <div class="hero-illustration">
              <div class="phone-mockup">
                <div class="phone-screen">
                  <div class="screen-header">
                    <div class="status-bar">
                      <span class="time">9:41</span>
                      <span class="battery">🔋</span>
                    </div>
                  </div>
                  <div class="screen-content">
                    <div class="quest-card">
                      <div class="quest-icon">📚</div>
                      <h4>Today's Quest</h4>
                      <p>Complete 3 tasks</p>
                      <div class="progress-ring">
                        <span>2/3</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Character Illustration -->
              <div class="character-float">
                <div class="character">🧙‍♂️</div>
                <div class="magic-sparkles">
                  <span>✨</span>
                  <span>⭐</span>
                  <span>🌟</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Floating Elements -->
      <div class="floating-elements">
        <div class="float-item" style="--delay: 0s; --x: 10%; --y: 20%;">🎯</div>
        <div class="float-item" style="--delay: 1s; --x: 85%; --y: 30%;">⚡</div>
        <div class="float-item" style="--delay: 2s; --x: 20%; --y: 70%;">🏆</div>
        <div class="float-item" style="--delay: 3s; --x: 80%; --y: 60%;">💫</div>
        <div class="float-item" style="--delay: 4s; --x: 50%; --y: 85%;">🌈</div>
      </div>
    </section>

    <!-- Features Section (only show if not logged in) -->
    <section class="features-section" v-if="!user">
      <div class="container">
        <div class="section-header">
          <h2>Feel the Magic of Learning</h2>
          <p>Discover amazing tools that make growing up an adventure!</p>
        </div>

        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>Quest Tracker</h3>
            <p>Turn homework into epic quests with rewards!</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">💧</div>
            <h3>Hydration Hero</h3>
            <p>Stay healthy with fun water reminders!</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">⏰</div>
            <h3>Focus Timer</h3>
            <p>Master time management with Pomodoro magic!</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Dashboard Section (only show if logged in) -->
    <section class="dashboard-section" v-else>
      <div class="container">
        <div class="dashboard-header">
          <h2>Your Adventure Dashboard</h2>
          <p>Ready to continue your quest?</p>
        </div>

        <div class="dashboard-grid">
          <div class="dashboard-card quick-actions">
            <h3>🚀 Quick Start</h3>
            <div class="action-buttons">
              <button class="action-btn homework">
                <span class="action-icon">📚</span>
                <span>Homework</span>
              </button>
              <button class="action-btn water">
                <span class="action-icon">💧</span>
                <span>Water</span>
              </button>
              <button class="action-btn focus">
                <span class="action-icon">⏰</span>
                <span>Focus</span>
              </button>
              <button class="action-btn mood">
                <span class="action-icon">😊</span>
                <span>Mood</span>
              </button>
            </div>
          </div>

          <div class="dashboard-card stats">
            <h3>📊 Your Progress</h3>
            <div class="stat-item">
              <span class="stat-label">Quests Completed</span>
              <span class="stat-value">12 🏆</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Streak</span>
              <span class="stat-value">5 days 🔥</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Level</span>
              <span class="stat-value">Adventure 3 ⭐</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Modals -->
    <LoginModal v-if="showLogin" @close="showLogin = false" @success="handleLoginSuccess"
      @switchToRegister="switchToRegister" />

    <RegisterModal v-if="showRegister" @close="showRegister = false" @success="handleRegisterSuccess"
      @switchToLogin="switchToLogin" />

    <!-- 3D Chatbot -->
    <EnhancedChatBot v-if="showChat" @close="showChat = false" :user="user" />

    <!-- Floating Gandalf Button (only if logged in) -->
    <div v-if="user" class="floating-gandalf" @click="showChat = true">
      <div class="gandalf-icon">🧙‍♂️</div>
      <div class="gandalf-sparkles">✨</div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&display=swap');

* {
  box-sizing: border-box;
}

.kidquest-home {
  min-height: 100vh;
  background: linear-gradient(135deg, #31417A 0%, #667eea 100%);
  position: relative;
  overflow-x: hidden;
  font-family: 'Merriweather', serif;
}

/* Navigation */
.main-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  z-index: 1000;
  padding: 1rem 0;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  color: #6366f1;
}

.logo-icon {
  font-size: 2rem;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-btn {
  padding: 0.5rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.5);
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  background: transparent;
  color: white;
}

.nav-btn.primary {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
  border-color: transparent;
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  background: rgba(255, 255, 255, 0.1);
}

/* Hero Section */
.hero-section {
  padding: 120px 0 80px;
  position: relative;
  z-index: 2;
}

.hero-content {
  color: white;
  padding: 2rem 0;
}

.hero-title {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.title-highlight {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2.5rem;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-quest {
  padding: 1rem 2rem;
  border: none;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
  justify-content: center;
}

.btn-quest.primary {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
  box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
}

.btn-quest.secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
}

.btn-quest:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
}

.btn-icon {
  font-size: 1.3rem;
}

.welcome-back {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.welcome-back h3 {
  margin-bottom: 0.5rem;
  color: #ffa726;
}

/* Hero Illustration */
.hero-illustration {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  height: 500px;
}

.phone-mockup {
  background: #1a1a1a;
  border-radius: 25px;
  padding: 20px;
  width: 250px;
  height: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  transform: rotate(-10deg);
  z-index: 2;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.phone-screen {
  background: linear-gradient(135deg, #222F5B, #0B0C10);
  border-radius: 15px;
  height: 100%;
  padding: 1rem;
  color: white;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  margin-bottom: 1rem;
}

.quest-card {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 15px;
  padding: 1.5rem;
  text-align: center;
  backdrop-filter: blur(10px);
}

.quest-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.progress-ring {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1rem auto;
  color: white;
  font-weight: bold;
}

.character-float {
  position: absolute;
  top: 50px;
  right: -50px;
  z-index: 3;
  animation: float 3s ease-in-out infinite;
}

.character {
  font-size: 4rem;
  text-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.magic-sparkles {
  position: absolute;
  top: -20px;
  left: -20px;
  right: -20px;
  bottom: -20px;
}

.magic-sparkles span {
  position: absolute;
  font-size: 1.5rem;
  animation: sparkle 2s infinite ease-in-out;
}

.magic-sparkles span:nth-child(1) {
  top: 0;
  left: 50%;
  animation-delay: 0s;
}

.magic-sparkles span:nth-child(2) {
  top: 50%;
  right: 0;
  animation-delay: 0.7s;
}

.magic-sparkles span:nth-child(3) {
  bottom: 0;
  left: 0;
  animation-delay: 1.4s;
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-20px);
  }
}

@keyframes sparkle {

  0%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }

  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

/* Floating Elements */
.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.float-item {
  position: absolute;
  font-size: 2rem;
  animation: floatElement 6s infinite ease-in-out;
  animation-delay: var(--delay);
  left: var(--x);
  top: var(--y);
}

@keyframes floatElement {

  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.5;
  }

  50% {
    transform: translateY(-30px) rotate(180deg);
    opacity: 1;
  }
}

/* Features Section */
.features-section {
  padding: 80px 0;
  background: rgba(0, 0, 0, 0.2);
}

.section-header {
  text-align: center;
  margin-bottom: 4rem;
}

.section-header h2 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.section-header p {
  color: rgba(255, 255, 255, 0.8);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 20px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1.5rem;
}

.feature-card h3 {
  color: white;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.feature-card p {
  color: rgba(255, 255, 255, 0.8);
}

/* Dashboard Section */
.dashboard-section {
  padding: 80px 0;
  background: rgba(0, 0, 0, 0.2);
}

.dashboard-header {
  text-align: center;
  margin-bottom: 4rem;
}

.dashboard-header h2 {
  font-size: 2.5rem;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.dashboard-header p {
  color: rgba(255, 255, 255, 0.8);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.dashboard-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 2.5rem;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.dashboard-card h3 {
  margin-bottom: 2rem;
  color: white;
  font-size: 1.3rem;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.action-btn {
  padding: 1.5rem;
  border: none;
  border-radius: 15px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.action-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.action-icon {
  font-size: 2rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: rgba(255, 255, 255, 0.8);
}

.stat-value {
  font-weight: bold;
  color: #ffa726;
}

/* Floating Gandalf Button */
.floating-gandalf {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #8b4513, #daa520);
  border-radius: 50%;
  width: 70px;
  height: 70px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 25px rgba(139, 69, 19, 0.4);
  transition: all 0.3s ease;
  border: 3px solid rgba(255, 255, 255, 0.3);
  z-index: 999;
}

.floating-gandalf:hover {
  transform: translateY(-5px) scale(1.1);
  box-shadow: 0 15px 35px rgba(139, 69, 19, 0.6);
}

.gandalf-icon {
  font-size: 2.5rem;
  animation: gandalfFloat 3s ease-in-out infinite;
}

@keyframes gandalfFloat {

  0%,
  100% {
    transform: rotate(-5deg);
  }

  50% {
    transform: rotate(5deg);
  }
}

.gandalf-sparkles {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 1.2rem;
  animation: sparkles 2s linear infinite;
}

@keyframes sparkles {
  0% {
    opacity: 0.5;
    transform: scale(0.8) rotate(0deg);
  }

  50% {
    opacity: 1;
    transform: scale(1.2) rotate(180deg);
  }

  100% {
    opacity: 0.5;
    transform: scale(0.8) rotate(360deg);
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-buttons {
    flex-direction: column;
  }

  .btn-quest {
    width: 100%;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .phone-mockup {
    width: 200px;
    height: 350px;
  }

  .character-float {
    position: relative;
    top: 0;
    right: 0;
    margin-top: 2rem;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 100px 0 60px;
  }

  .hero-title {
    font-size: 2rem;
  }

  .nav-links {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
