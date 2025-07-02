<template>
  <div class="container">
    <h2 class="section-title">
      <span class="title-icon">✅</span>
      KidQuest Health Tracker
    </h2>

    <div class="main-content">
      <!-- Left Side Tasks -->
      <div class="task-box">
        <p class="task-heading">Complete at least two tasks to maintain your streak!</p>
        <ul class="task-list">
          <li v-for="(task, index) in tasks" :key="index">
            <span>{{ task.name }}</span>
            <input type="checkbox" :checked="task.completed" @change="toggleTask(index)" />
          </li>
        </ul>
      </div>

      <!-- Right Side Panel -->
      <div class="right-panel">
        <!-- Top Right Streak -->
        <div class="streak-area">
          <h2 class="streak-label">Streak</h2>
          <div class="streak-counter">
            <span>{{ streak }} days</span>
            <span class="fire">🔥</span>
          </div>
        </div>

        <!-- Widgets: Water Counter + Graph -->
        <div class="widgets">
          <div class="widget water">
            <p>{{ waterCount }}</p>
            <p>Water Counter</p>
            <button class="add-glass-btn" @click="incrementWater">+ Add Glass</button>
          </div>
          <div class="graph-box">
            <canvas id="waterChart"></canvas>
          </div>
        </div>
      </div>
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
            backgroundColor: '#60a5fa',
            borderColor: '#2563eb',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              ticks: { precision: 0 }
            }
          }
        }
      });
    },
  }
};
</script>

<style scoped>
.container {
  padding: 20px;
  font-family: 'Poppins', sans-serif;
  background: linear-gradient(to bottom right, #dbeafe, #d1fae5);
  min-height: 100vh;
}

.section-title {
  font-size: 1.8rem;
  margin-bottom: 10px;
  font-weight: bold;
  display: flex;
  align-items: center;
}
.title-icon {
  margin-right: 10px;
}

.main-content {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  margin-top: 20px;
}

.task-box {
  background-color: #bbf7d0;
  padding: 20px;
  border-radius: 20px;
  flex: 1;
  min-width: 280px;
}
.task-heading {
  text-align: center;
  font-style: italic;
  font-weight: bold;
  margin-bottom: 20px;
}
.task-list li {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: white;
  border-radius: 10px;
  margin-bottom: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.right-panel {
  flex: 2;
  display: flex;
  flex-direction: column;
  min-width: 300px;
}

.streak-area {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
}
.streak-label {
  font-size: 1.5rem;
  font-weight: bold;
}
.streak-counter {
  background-color: #fde68a;
  padding: 10px 20px;
  border-radius: 30px;
  font-weight: bold;
  display: flex;
  gap: 10px;
  align-items: center;
}
.fire {
  color: red;
  font-size: 24px;
}

.widgets {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.widget {
  flex: 1;
  text-align: center;
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  cursor: pointer;
}
.widget.water {
  background-color: #7dd3fc;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;     
  justify-content: center; 
  gap: 10px;               
}
.graph-box {
  flex: 2;
  min-width: 300px;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.add-glass-btn {
  min-width: 120px;
  text-align: center;
}
.add-glass-btn:hover {
  background-color: #1e40af;
}

</style>
