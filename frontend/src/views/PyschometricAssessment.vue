<template>
  <div class="psychometric-app">
    <!-- Header -->
    <header class="app-header">
      <div class="container">
        <div class="header-content">
          <div class="app-logo">
            <span class="logo-icon">🧠</span>
            <span class="logo-text">Psychometric Test</span>
          </div>
          <div class="header-subtitle">
            <p>Discover your learning style and personality traits!</p>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="app-main">
      <div class="container">
        <!-- Stats Bar -->
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

        <!-- Debug info - remove this after fixing -->
        <div v-if="debugMode && currentQuestion" class="debug-info">
          <h4>Debug Info:</h4>
          <p>Current Question Object: {{ JSON.stringify(currentQuestion, null, 2) }}</p>
          <p>Question Text: "{{ currentQuestion.question }}"</p>
          <p>Options: {{ JSON.stringify(currentQuestion.options, null, 2) }}</p>
        </div>

        <!-- Welcome Section -->
        <div v-if="!testStarted && !showResults" class="welcome-section">
          <div class="welcome-card">
            <h1>🧠 Psychometric Assessment</h1>
            <p>Explore your unique strengths and interests through our comprehensive assessment.</p>
            <p>This test will help you understand your learning style, personality traits, and cognitive abilities.</p>
            <button class="btn primary-btn" @click="startTest">
              🚀 Start Assessment
            </button>
          </div>
        </div>

        <!-- Question Section -->
        <div v-if="showQuestion" class="question-section">
          <div class="question-card">
            <div class="question-header">
              <h3 v-if="currentQuestion && currentQuestion.question">{{ currentQuestion.question }}</h3>
              <h3 v-else class="error-text">⚠️ Question not loaded properly</h3>
            </div>
            <div class="options-container" v-if="currentQuestion && currentQuestion.options">
              <div
                v-for="(text, letter) in currentQuestion.options"
                :key="letter"
                class="option"
                :class="{ selected: selectedAnswer === letter }"
                @click="selectOption(letter)"
              >
                <div class="option-letter">{{ letter }}</div>
                <div class="option-text">{{ text }}</div>
              </div>
            </div>
            <div v-else class="error-text">
              ⚠️ Options not loaded properly
            </div>
          </div>
        </div>

        <!-- Loading Section -->
        <div v-if="isLoading" class="loading-section">
          <div class="loading-card">
            <div class="spinner"></div>
            <p>{{ loadingMessage }}</p>
          </div>
        </div>

        <!-- Results Section -->
        <div v-if="showResults" class="results-section">
          <div class="results-card">
            <h2>🎉 Assessment Complete!</h2>
            <div class="results-grid">
              <div class="result-item">
                <span class="result-value">{{ results.results?.learning_style || '-' }}</span>
                <span class="result-label">Learning Style</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ results.results?.personality_type || '-' }}</span>
                <span class="result-label">Personality Type</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ formatPercentage(results.results?.concentration_level) }}</span>
                <span class="result-label">Concentration</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ formatPercentage(results.results?.memory_strength) }}</span>
                <span class="result-label">Memory</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ results.total_correct || 0 }}</span>
                <span class="result-label">Correct Answers</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ results.total_questions || 0 }}</span>
                <span class="result-label">Total Questions</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ Math.round(results.accuracy || 0) }}%</span>
                <span class="result-label">Final Accuracy</span>
              </div>
              <div class="result-item">
                <span class="result-value">{{ results.duration_seconds || 0 }}s</span>
                <span class="result-label">Test Duration</span>
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
        </div>

        <!-- Action Buttons -->
        <div v-if="showQuestion || showResults" class="action-buttons">
          <button 
            v-if="showQuestion" 
            class="btn primary-btn" 
            @click="submitAnswer" 
            :disabled="!selectedAnswer || isLoading"
          >
            Submit Answer
          </button>
          <button v-if="showResults" class="btn secondary-btn" @click="restartTest">
            Start New Test
          </button>
        </div>
      </div>
    </main>
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
      debugMode: false,
      
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
        console.log('Starting test, making API call to:', `${this.apiBaseUrl}/start`);
        
        const response = await fetch(`${this.apiBaseUrl}/start`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json'
          },
          credentials: 'include' // Important for session management
        });

        console.log('API Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('API Error Response:', errorText);
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('API Response data:', data);
        
        this.displayQuestion(data);
        this.isLoading = false;
      } catch (error) {
        console.error('Error starting test:', error);
        this.isLoading = false;
        alert(`Error starting test: ${error.message}. Please check the console for details.`);
      }
    },

    async submitAnswer() {
      if (!this.selectedAnswer) return;
      
      this.isLoading = true;
      this.loadingMessage = 'Processing your answer...';

      try {
        console.log('Submitting answer:', this.selectedAnswer);
        
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

        console.log('Submit response status:', response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error('Submit API Error Response:', errorText);
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Submit response data:', data);
        
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
        alert(`Error submitting answer: ${error.message}. Please check the console for details.`);
      }
    },

    displayQuestion(data) {
      console.log('displayQuestion called with:', data);
      
      // Ensure we have the question data
      if (!data || !data.question) {
        console.error('Invalid question data received:', data);
        this.currentQuestion = null;
        return;
      }
      
      // Set the current question - this should contain all the question data
      this.currentQuestion = {
        question: data.question,
        options: data.options || {},
        correct_answer: data.correct_answer,
        category: data.category
      };
      
      console.log('Current question set to:', this.currentQuestion);
      
      this.selectedAnswer = null;
      this.currentQuestionNumber = data.question_number || 1;
      this.totalQuestions = data.total_questions || 1;
      
      // Update progress
      this.progressPercentage = data.progress || 0;
    },

    selectOption(answer) {
      console.log('Option selected:', answer);
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
      console.log('Showing test results:', data);
      this.showResults = true;
      this.results = data;
      this.progressPercentage = 100;
    },

    restartTest() {
      this.resetData();
      this.testStarted = false;
      this.showResults = false;
      this.debugMode = false;
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

    toggleDebug() {
      this.debugMode = !this.debugMode;
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

.psychometric-app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 100vw;
  overflow-x: hidden;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.app-logo {
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

.header-subtitle {
  color: #666;
  font-size: 1rem;
}

.app-main {
  padding: 2rem 0;
  min-height: calc(100vh - 80px);
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
  width: 100%;
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.stat-item { 
  text-align: center; 
}

.stat-value { 
  font-size: 2rem; 
  font-weight: bold; 
  display: block;
  color: #667eea;
}

.stat-label { 
  font-size: 0.9rem; 
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.welcome-section,
.question-section,
.loading-section,
.results-section {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.welcome-card,
.question-card,
.loading-card,
.results-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
  text-align: center;
}

.welcome-card h1 {
  color: #333;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.welcome-card p {
  color: #666;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.question-header {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  border-left: 5px solid #667eea;
}

.question-header h3 {
  color: #333;
  font-size: 1.3rem;
  line-height: 1.6;
  text-align: left;
}

.options-container { 
  display: grid; 
  gap: 1rem; 
}

.option {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  text-align: left;
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

.option-text {
  flex: 1;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.result-item {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  border-radius: 15px;
  text-align: center;
}

.result-value {
  font-size: 2rem;
  font-weight: bold;
  display: block;
  margin-bottom: 0.5rem;
}

.result-label {
  font-size: 0.9rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.category-breakdown {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 2rem;
  margin-top: 2rem;
  text-align: left;
}

.category-breakdown h4 {
  margin-bottom: 1rem;
  color: #764ba2;
}

.category-breakdown ul {
  list-style: none;
  padding-left: 0;
}

.category-breakdown li {
  margin-bottom: 0.5rem;
  color: #333;
}

.feedback-section {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 2rem;
  margin-top: 2rem;
  color: #333;
  text-align: left;
  font-size: 1.1rem;
  line-height: 1.6;
}

.action-buttons {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.btn {
  padding: 1rem 2rem;
  border: none;
  border-radius: 25px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 200px;
  justify-content: center;
}

.primary-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.primary-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.secondary-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 5px 15px rgba(240, 147, 251, 0.3);
}

.secondary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(240, 147, 251, 0.4);
}

.loading-card {
  color: #667eea;
  font-size: 1.2rem;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.debug-info {
  background: #fffbf0;
  border: 2px solid #ff9800;
  border-radius: 10px;
  padding: 1rem;
  margin-bottom: 2rem;
  font-family: monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
  word-break: break-all;
}

.error-text {
  color: #d32f2f;
  background: #ffebee;
  padding: 1rem;
  border-radius: 10px;
  border: 2px solid #f44336;
}

@media (max-width: 768px) {
  .container {
    padding: 0 0.5rem;
  }
  
  .welcome-card,
  .question-card,
  .loading-card,
  .results-card {
    padding: 2rem 1rem;
  }
  
  .results-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  .result-item {
    padding: 1.5rem 1rem;
  }
  
  .result-value {
    font-size: 1.5rem;
  }
  
  .stats-bar {
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .welcome-card h1 {
    font-size: 2rem;
  }
  
  .btn {
    width: 100%;
    min-width: auto;
  }
}
</style>