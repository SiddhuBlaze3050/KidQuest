<template>
  <div class="container">
    <div class="header">
      <h1>🧠 Psychometric Test</h1>
      <p>Discover your learning style and personality traits!</p>
      <p>Explore your unique strengths and interests</p>
    </div>

    <div v-if="showStats" class="stats-bar">
      <div class="stat-item">
        <span class="stat-value">{{ currentQuestionNumber }}</span>
        <span class="stat-label">Question</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ currentAccuracy }}%</span>
        <span class="stat-label">Accuracy</span>
      </div>
    </div>


    <div v-if="showQuestion" class="question-container">
      <div class="question">
        <h3>{{ currentQuestion.question }}</h3>
      </div>
      <div class="options">
        <div
          v-for="(text, letter) in currentQuestion.options"
          :key="letter"
          class="option"
          :class="{ selected: selectedAnswer === letter }"
          @click="selectOption(letter)"
        >
          <div class="option-letter">{{ letter }}</div>
          <div>{{ text }}</div>
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>

    <div v-if="showResults" class="results">
      <h2>🎉 Test Complete!</h2>
      <div class="results-grid">
        <div class="result-card">
          <span class="result-value">{{ results.results?.learning_style || '-' }}</span>
          <span>Learning Style</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ results.results?.personality_type || '-' }}</span>
          <span>Personality Type</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ formatPercentage(results.results?.concentration_level) }}</span>
          <span>Concentration</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ formatPercentage(results.results?.memory_strength) }}</span>
          <span>Memory</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ results.total_correct || 0 }}</span>
          <span>Correct Answers</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ results.total_questions || 0 }}</span>
          <span>Total Questions</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ Math.round(results.accuracy || 0) }}%</span>
          <span>Final Accuracy</span>
        </div>
        <div class="result-card">
          <span class="result-value">{{ results.duration_seconds || 0 }}s</span>
          <span>Test Duration</span>
        </div>
      </div>
      
      <div v-if="results.results && results.results.detailed_scores" class="category-breakdown">
        <h4>Category Breakdown</h4>
        <ul>
          <li v-for="(data, category) in results.results.detailed_scores" :key="category">
            <b>{{ formatCategoryName(category) }}:</b> {{ data.percentage }}% ({{ data.score }}/{{ data.total }})
          </li>
        </ul>
      </div>
      
      <div v-if="results.results && results.results.feedback" class="feedback-section">
        <h3>Personalized Feedback:</h3>
        <div v-html="results.results.feedback"></div>
      </div>
    </div>

    <div class="buttons">
      <button v-if="!testStarted && !showResults" class="btn" @click="startTest">
        🚀 Start Test
      </button>
      <button 
        v-if="showQuestion" 
        class="btn" 
        @click="submitAnswer" 
        :disabled="!selectedAnswer || isLoading"
      >
        Submit Answer
      </button>
      <button v-if="showResults" class="btn btn-secondary" @click="restartTest">
        Start New Test
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PsychometricTestView',
  data() {
    return {
      // Test state
      testStarted: false,
      isLoading: false,
      loadingMessage: 'Starting the assessment...',
      
      // Question data
      currentQuestion: null,
      selectedAnswer: null,
      currentQuestionNumber: 1,
      totalQuestions: 0,
      
      // Progress tracking
      currentAccuracy: 0,
      progressPercentage: 0,
      
      // Results
      results: {},
      showResults: false,
      
      // API base URL - adjust this to match your Flask app
      apiBaseUrl: 'http://localhost:5000/api/psychometry'
    }
  },
  computed: {
    showStats() {
      return this.testStarted && !this.showResults && !this.isLoading;
    },
    showProgress() {
      return this.testStarted && !this.showResults;
    },
    showQuestion() {
      return this.testStarted && !this.showResults && !this.isLoading && this.currentQuestion;
    }
  },
  methods: {
    async startTest() {
      this.testStarted = true;
      this.isLoading = true;
      this.loadingMessage = 'Starting the assessment...';
      this.showResults = false;
      this.resetData();

      try {
        const response = await fetch(`${this.apiBaseUrl}/start`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json'
          },
          credentials: 'include' // Important for session management
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.displayQuestion(data);
        this.isLoading = false;
      } catch (error) {
        console.error('Error starting test:', error);
        this.isLoading = false;
        alert('Error starting test. Please try again.');
      }
    },

    async submitAnswer() {
      if (!this.selectedAnswer) return;
      
      this.isLoading = true;
      this.loadingMessage = 'Processing your answer...';

      try {
        const response = await fetch(`${this.apiBaseUrl}/submit`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify({
            answer: this.selectedAnswer
          })
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.isLoading = false;
        
        if (data.results) {
          // Test is complete
          this.showTestResults(data);
        } else {
          // Continue with next question
          this.displayQuestion(data);
          this.updateAccuracy();
        }
      } catch (error) {
        console.error('Error submitting answer:', error);
        this.isLoading = false;
        alert('Error submitting answer. Please try again.');
      }
    },

    displayQuestion(data) {
      this.currentQuestion = data;
      this.selectedAnswer = null;
      this.currentQuestionNumber = data.question_number || 1;
      this.totalQuestions = data.total_questions || 1;
      
      // Update progress
      this.progressPercentage = data.progress || 0;
    },

    selectOption(answer) {
      this.selectedAnswer = answer;
    },

    updateAccuracy() {
      // Calculate accuracy based on current progress
      // This is a simple implementation - you might want to track this differently
      if (this.currentQuestionNumber > 1) {
        // This is a placeholder - you might want to track correct answers separately
        this.currentAccuracy = Math.round(Math.random() * 100); // Replace with actual calculation
      }
    },

    showTestResults(data) {
      this.showResults = true;
      this.results = data;
      this.progressPercentage = 100;
      
      console.log('Test results:', data);
    },

    restartTest() {
      this.resetData();
      this.testStarted = false;
      this.showResults = false;
    },

    resetData() {
      this.currentQuestion = null;
      this.selectedAnswer = null;
      this.currentQuestionNumber = 1;
      this.totalQuestions = 0;
      this.currentAccuracy = 0;
      this.progressPercentage = 0;
      this.results = {};
    },

    formatPercentage(value) {
      return value !== undefined ? `${value}%` : '-';
    },

    formatCategoryName(category) {
      return category
        .replace(/_/g, ' ')
        .replace('personality ', 'Personality ')
        .replace(/\b\w/g, l => l.toUpperCase());
    }
  }
}
</script>

<style scoped>
* { 
  margin: 0; 
  padding: 0; 
  box-sizing: border-box; 
}

.container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.container > * {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  width: 100%;
  backdrop-filter: blur(10px);
  margin-bottom: 20px;
}

.container > .buttons {
  background: none;
  box-shadow: none;
  backdrop-filter: none;
  padding: 0;
}

.header { 
  text-align: center; 
  margin-bottom: 30px; 
}

.header h1 {
  color: #333;
  font-size: 2.5em;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header p { 
  color: #666; 
  font-size: 1.1em; 
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 15px;
  border-radius: 15px;
  margin-bottom: 0;
  color: white;
}

.stat-item { 
  text-align: center; 
}

.stat-value { 
  font-size: 1.8em; 
  font-weight: bold; 
  display: block; 
}

.stat-label { 
  font-size: 0.9em; 
  opacity: 0.9; 
}

.question-container {
  animation: fadeIn 0.5s ease-in;
}

.question {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 15px;
  margin-bottom: 25px;
  border-left: 5px solid #667eea;
}

.question h3 {
  color: #333;
  font-size: 1.3em;
  margin-bottom: 20px;
  line-height: 1.6;
}

.options { 
  display: grid; 
  gap: 15px; 
}

.option {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
}

.option:hover {
  border-color: #667eea;
  background: #f8f9ff;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
}

.option.selected {
  border-color: #667eea;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.option-letter {
  background: #667eea;
  color: white;
  width: 35px;
  height: 35px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.option.selected .option-letter {
  background: white;
  color: #667eea;
}

.buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 25px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.results {
  text-align: center;
  animation: fadeIn 0.5s ease-in;
}

.results h2 {
  color: #333;
  margin-bottom: 20px;
  font-size: 2em;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin: 30px 0;
}

.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  border-radius: 15px;
  text-align: center;
}

.result-value {
  font-size: 2.5em;
  font-weight: bold;
  display: block;
  margin-bottom: 10px;
}

.feedback-section {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 25px;
  margin-top: 20px;
  color: #333;
  text-align: left;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
  font-size: 1.1em;
  white-space: pre-line;
}

.loading {
  text-align: center;
  color: #667eea;
  font-size: 1.2em;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  margin-bottom: 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 0%;
  transition: width 0.3s ease;
}

.category-breakdown {
  margin-top: 20px;
  text-align: left;
  max-width: 700px;
  margin-left: auto;
  margin-right: auto;
}

.category-breakdown h4 {
  margin-bottom: 8px;
  color: #764ba2;
}

.category-breakdown ul {
  list-style: none;
  padding-left: 0;
}

.category-breakdown li {
  margin-bottom: 4px;
}
</style>