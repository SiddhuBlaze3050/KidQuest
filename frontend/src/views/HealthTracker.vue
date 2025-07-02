<template>
  <div class="health-tracker">
    <!-- Header -->
    <header class="health-header">
      <h2 class="section-title">
        <span class="title-icon">❤️‍🩹</span>
        My Health Adventure
      </h2>
      <p class="subtitle">Keep your body strong and healthy on your magical journey!</p>
    </header>

    <div class="main-content">
      <!-- Left Side Tasks -->
      <div class="task-box">
        <div class="task-header">
          <h3>🎯 Daily Health Quests</h3>
          <p class="task-description">Complete at least two quests to maintain your magical health streak!</p>
        </div>
        <ul class="task-list">
          <li v-for="(task, index) in tasks" :key="index" :class="['task-item', { completed: task.completed }]">
            <div class="task-content">
              <span class="task-icon">{{ getTaskIcon(task.name) }}</span>
              <span class="task-name">{{ task.name }}</span>
            </div>
            <label class="magic-checkbox">
              <input type="checkbox" :checked="task.completed" @change="toggleTask(index)" />
              <span class="checkmark"></span>
            </label>
          </li>
        </ul>
      </div>

      <!-- Right Side Panel -->
      <div class="right-panel">
        <!-- Top Right Streak -->
        <div class="streak-card">
          <div class="streak-content">
            <h3 class="streak-label">🔥 Magic Streak</h3>
            <div class="streak-counter">
              <span class="streak-number">{{ streak }}</span>
              <span class="streak-text">days</span>
            </div>
            <div class="streak-sparkles">
              <span class="sparkle">✨</span>
              <span class="sparkle">⭐</span>
              <span class="sparkle">💫</span>
            </div>
          </div>
        </div>

        <!-- Widgets: Water Counter + Graph -->
        <div class="widgets-container">
          <div class="water-widget">
            <div class="widget-header">
              <h4>💧 Hydration Potion</h4>
            </div>
            <div class="water-content">
              <div class="water-count">
                <span class="count-number">{{ waterCount }}</span>
                <span class="count-label">glasses today</span>
              </div>
              <button class="add-glass-btn" @click="incrementWater">
                <span class="btn-icon">💧</span>
                Add Glass
              </button>
            </div>
            <div class="water-animation">
              <div class="water-drops">
                <span class="drop" v-for="i in 3" :key="i">💧</span>
              </div>
            </div>
          </div>

          <div class="graph-widget">
            <div class="widget-header">
              <h4>📊 Progress Chronicle</h4>
            </div>
            <div class="graph-content">
              <canvas id="waterChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Magic Elements -->
    <div class="floating-magic">
      <div class="magic-element" style="--delay: 0s; --x: 10%; --y: 20%;">🌟</div>
      <div class="magic-element" style="--delay: 2s; --x: 90%; --y: 30%;">💫</div>
      <div class="magic-element" style="--delay: 4s; --x: 15%; --y: 70%;">✨</div>
      <div class="magic-element" style="--delay: 6s; --x: 85%; --y: 80%;">⭐</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import Chart from 'chart.js/auto';
import { nextTick } from 'vue';

export default {
  name: 'HealthTracker',
  data() {
    return {
      tasks: [],
      streak: 0,
      waterCount: 0,
      waterLog: [],
      waterChart: null,
    };
  },
  computed: {
    userId() {
      return 1; // Replace with real user context
    }
  },
  created() {
    this.fetchTasks();
    this.fetchStreak();
    this.fetchWaterCount();
    this.fetchWaterChart();
  },
  methods: {
    getTaskIcon(taskName) {
      const icons = {
        'Exercise': '🏃‍♂️',
        'Drink Water': '💧',
        'Eat Vegetables': '🥕',
        'Sleep 8 Hours': '😴',
        'Brush Teeth': '🦷',
        'Take Vitamins': '💊',
        'Wash Hands': '🧼',
        'Stretch': '🧘‍♂️'
      };
      return icons[taskName] || '⚡';
    },
    async fetchTasks() {
      try {
        const { data } = await axios.get(`/api/health/tasks/${this.userId}`);
        this.tasks = data.tasks;
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    },
    async toggleTask(index) {
      const task = this.tasks[index];
      try {
        const { data } = await axios.post(`/api/health/tasks/${task.id}/toggle`);
        this.tasks[index].completed = data.completed;
        await this.evaluateStreak();
      } catch (error) {
        console.error('Error toggling task:', error);
      }
    },
    async evaluateStreak() {
      try {
        await axios.post(`/api/health/streak/${this.userId}/evaluate`);
        this.fetchStreak();
      } catch (error) {
        console.error('Error evaluating streak:', error);
      }
    },
    async fetchStreak() {
      try {
        const { data } = await axios.get(`/api/health/streak/${this.userId}`);
        this.streak = data.streak;
      } catch (error) {
        console.error('Error fetching streak:', error);
      }
    },
    async fetchWaterCount() {
      try {
        const { data } = await axios.get(`/api/health/water/${this.userId}`);
        this.waterCount = data.count;
      } catch (error) {
        console.error('Error fetching water count:', error);
      }
    },
    async incrementWater() {
      try {
        const { data } = await axios.post(`/api/health/water/${this.userId}`);
        this.waterCount = data.count;
        this.fetchWaterChart(); // Refresh graph
      } catch (error) {
        console.error('Error incrementing water count:', error);
      }
    },
    async fetchWaterChart() {
      try {
        const { data } = await axios.get(`/api/health/water/log/${this.userId}`);
        this.waterLog = data.log;
        await nextTick(); // wait for DOM
        this.renderWaterChart();
      } catch (error) {
        console.error('Error fetching water chart data:', error);
      }
    },
    renderWaterChart() {
      if (!this.waterLog.length) return;

      const ctx = document.getElementById('waterChart');

      if (this.waterChart) {
        this.waterChart.destroy();
      }

      this.waterChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.waterLog.map(entry => entry.date),
          datasets: [{
            label: 'Water Intake',
            data: this.waterLog.map(entry => entry.count),
            backgroundColor: 'rgba(76, 175, 80, 0.2)',
            borderColor: '#4CAF50',
            fill: true,
            tension: 0.4,
            borderWidth: 3,
            pointBackgroundColor: '#4CAF50',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6
          }]
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              labels: {
                color: '#333',
                font: {
                  family: 'Merriweather',
                  size: 12
                }
              }
            }
          },
          scales: {
            x: {
              ticks: {
                color: '#666',
                font: {
                  family: 'Merriweather'
                }
              },
              grid: {
                color: 'rgba(0,0,0,0.1)'
              }
            },
            y: {
              beginAtZero: true,
              ticks: {
                precision: 0,
                color: '#666',
                font: {
                  family: 'Merriweather'
                }
              },
              grid: {
                color: 'rgba(0,0,0,0.1)'
              }
            }
          }
        }
      });
    },
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

.health-tracker {
  background: linear-gradient(135deg, #31417A 0%, #667eea 100%);
  position: relative;
  overflow: hidden;
  font-family: 'Merriweather', serif;
  padding: 1rem;
  border-radius: 20px;
  min-height: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Header */
.health-header {
  text-align: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 0.3rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: white;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.title-icon {
  font-size: 1.8rem;
  animation: heartbeat 2s infinite;
}

@keyframes heartbeat {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

.subtitle {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  margin: 0;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

/* Main Content */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
  flex: 1;
  min-height: 0;
}

/* Task Box */
.task-box {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.task-header {
  text-align: center;
  margin-bottom: 1rem;
}

.task-header h3 {
  color: #333;
  font-size: 1.2rem;
  margin-bottom: 0.3rem;
}

.task-description {
  color: #666;
  font-style: italic;
  font-size: 0.9rem;
  margin: 0;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 10px;
  margin-bottom: 0.5rem;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.task-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.task-item.completed {
  background: linear-gradient(135deg, rgba(76, 175, 80, 0.1), rgba(129, 199, 132, 0.1));
  border-color: #4CAF50;
}

.task-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.task-icon {
  font-size: 1.2rem;
}

.task-name {
  font-weight: 500;
  color: #333;
  font-size: 0.9rem;
}

/* Magic Checkbox */
.magic-checkbox {
  position: relative;
  cursor: pointer;
}

.magic-checkbox input {
  opacity: 0;
  position: absolute;
}

.checkmark {
  width: 20px;
  height: 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.magic-checkbox input:checked+.checkmark::after {
  content: "✓";
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.magic-checkbox:hover .checkmark {
  transform: scale(1.1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.5);
}

/* Right Panel */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

/* Streak Card */
.streak-card {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  border-radius: 15px;
  padding: 1rem;
  color: white;
  box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
  position: relative;
  overflow: hidden;
}

.streak-content {
  text-align: center;
  position: relative;
  z-index: 2;
}

.streak-label {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.streak-counter {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
}

.streak-number {
  font-size: 2rem;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.streak-text {
  font-size: 0.8rem;
  opacity: 0.9;
}

.streak-sparkles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.sparkle {
  position: absolute;
  font-size: 1.2rem;
  animation: sparkleFloat 3s infinite ease-in-out;
}

.sparkle:nth-child(1) {
  top: 20%;
  left: 15%;
  animation-delay: 0s;
}

.sparkle:nth-child(2) {
  top: 30%;
  right: 20%;
  animation-delay: 1s;
}

.sparkle:nth-child(3) {
  bottom: 20%;
  left: 20%;
  animation-delay: 2s;
}

@keyframes sparkleFloat {

  0%,
  100% {
    transform: translateY(0) rotate(0deg);
    opacity: 0.7;
  }

  50% {
    transform: translateY(-10px) rotate(180deg);
    opacity: 1;
  }
}

/* Widgets Container */
.widgets-container {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 1rem;
  flex: 1;
  min-height: 0;
}

.water-widget,
.graph-widget {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 1rem;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
}

.widget-header {
  text-align: center;
  margin-bottom: 0.5rem;
}

.widget-header h4 {
  color: #333;
  font-size: 0.9rem;
  margin: 0;
}

/* Water Widget */
.water-content {
  text-align: center;
  position: relative;
  z-index: 2;
}

.water-count {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.count-number {
  font-size: 1.8rem;
  font-weight: bold;
  color: #4CAF50;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.count-label {
  font-size: 0.7rem;
  color: #666;
}

.add-glass-btn {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
  margin: 0 auto;
  font-size: 0.8rem;
}

.add-glass-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
}

.btn-icon {
  font-size: 1rem;
}

.water-animation {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.water-drops {
  position: relative;
  width: 100%;
  height: 100%;
}

.drop {
  position: absolute;
  font-size: 1.5rem;
  animation: dropFall 3s infinite ease-in-out;
}

.drop:nth-child(1) {
  left: 20%;
  animation-delay: 0s;
}

.drop:nth-child(2) {
  left: 50%;
  animation-delay: 1s;
}

.drop:nth-child(3) {
  left: 80%;
  animation-delay: 2s;
}

@keyframes dropFall {
  0% {
    top: -10%;
    opacity: 0;
  }

  20% {
    opacity: 1;
  }

  100% {
    top: 110%;
    opacity: 0;
  }
}

/* Graph Widget */
.graph-content {
  position: relative;
  height: 150px;
}

#waterChart {
  border-radius: 10px;
}

/* Floating Magic Elements */
.floating-magic {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.magic-element {
  position: absolute;
  font-size: 1.5rem;
  animation: floatMagic 8s infinite ease-in-out;
  animation-delay: var(--delay);
  left: var(--x);
  top: var(--y);
}

@keyframes floatMagic {

  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.6;
  }

  50% {
    transform: translateY(-30px) rotate(180deg);
    opacity: 1;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .widgets-container {
    grid-template-columns: 1fr;
  }

  .health-tracker {
    padding: 0.8rem;
  }

  .section-title {
    font-size: 1.5rem;
  }

  .health-header {
    margin-bottom: 0.8rem;
  }
}

@media (max-width: 480px) {
  .task-item {
    padding: 0.5rem;
  }

  .task-content {
    gap: 0.4rem;
  }

  .streak-number {
    font-size: 1.5rem;
  }

  .task-name {
    font-size: 0.8rem;
  }
}
</style>
