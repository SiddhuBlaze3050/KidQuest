<template>
  <div class="parent-dashboard">
    <!-- Transactions Modal (add here, at the top, so it overlays everything) -->
    <div v-if="modalComponent === 'transactions-modal'" class="transactions-modal modal-overlay" @click="closeModal">
      <div class="transactions-popup" @click.stop>
        <div class="popup-header">
          <span>Recent Transactions</span>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="popup-body">
          <div class="transaction-list">
            <div v-if="financeStats.recent.length === 0" class="no-transactions">No transactions yet.</div>
            <div v-for="t in financeStats.recent" :key="t.id" class="transaction-item" :class="t.type">
              <div class="transaction-date">{{ t.date }}</div>
              <div class="transaction-desc">{{ t.description }}</div>
              <div class="transaction-amount">
                {{ t.type === 'income' ? '+' : '-' }}₹{{ t.amount }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Transactions Modal -->

    <!-- Health Modal -->
    <div v-if="modalComponent === 'health-modal'" class="health-modal modal-overlay" @click="closeModal">
      <div class="transactions-popup" @click.stop>
        <div class="popup-header">
          <span>Water Intake - History</span>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <!-- Header Row -->
        <div class="history-header">
          <span class="col-intake">Intake</span>
          <span class="col-day">Day</span>
          <span class="col-target">Target</span>
          <span class="col-trend">Trend</span>
        </div>

        <div class="pill-container" v-if="healthStats.waterlog.length">
          <div class="pill" v-for="(entry, index) in healthStats.waterlog" :key="entry.date">
            <!-- Intake -->
            <div class="pill-count col-intake">{{ entry.count }}</div>

            <!-- Date / Day -->
            <div class="pill-date col-day">{{ entry.date }}</div>

            <!-- Target vs Actual -->
            <div class="pill-target col-target">
              Target: {{ healthStats.dailyTarget }}
              <span :class="entry.count >= healthStats.dailyTarget ? 'target-met' : 'target-missed'">
                ({{ entry.count >= healthStats.dailyTarget ? 'Met' : 'Missed' }})
              </span>
            </div>

            <!-- Trend Indicator -->
            <div class="pill-trend col-trend" v-if="index < healthStats.waterlog.length - 1">
              <span v-if="entry.count > healthStats.waterlog[index + 1].count" class="trend-up">⬆ Up</span>
              <span v-else-if="entry.count < healthStats.waterlog[index + 1].count" class="trend-down">⬇ Down</span>
              <span v-else class="trend-same">→ Same</span>
            </div>
            <!-- Fallback when no next day -->
            <div class="pill-trend col-trend" v-else>—</div>
          </div>
        </div>

        <div v-else class="no-data">
          No water intake data available.
        </div>
      </div>
    </div>

    <!-- Psychometric Modal Component -->
    <div v-if="modalComponent === 'psychometric-modal'" class="psychometric-modal modal-overlay" @click="closeModal">
      <div class="transactions-popup" @click.stop>
        <div class="popup-header">
          <span>Psychometric Test Results</span>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="psychometric-detailed popup-body scrollable-section">
          <div class="psycho-stats-grid highlight-style">
            <div class="psycho-stat-card learning-style-card">
              <div class="stat-icon">📚</div>
              <div class="stat-info">
                <h4>Learning Style</h4>
                <div class="stat-value highlight-badge">{{ modalData.learning_style || 'Balanced' }}</div>
              </div>
            </div>
            <div class="psycho-stat-card personality-card">
              <div class="stat-icon">👤</div>
              <div class="stat-info">
                <h4>Personality Type</h4>
                <div class="stat-value highlight-badge">{{ modalData.personality }}</div>
                <div class="personality-traits">
                  <span v-for="trait in modalData.traits" :key="trait" class="trait-tag">
                    {{ trait }}
                  </span>
                </div>
              </div>
            </div>
            <div class="psycho-stat-card interests-card">
              <div class="stat-icon">🎯</div>
              <div class="stat-info">
                <h4>Primary Interests</h4>
                <div class="stat-value highlight-badge">{{ modalData.interests }}</div>
              </div>
            </div>
            <div class="psycho-stat-card concentration-card">
              <div class="stat-icon">🎯</div>
              <div class="stat-info">
                <h4>Concentration Level</h4>
                <div class="stat-value highlight-badge">{{ modalData.concentration }}/100</div>
              </div>
            </div>
            <div class="psycho-stat-card memory-card">
              <div class="stat-icon">🧠</div>
              <div class="stat-info">
                <h4>Memory Strength</h4>
                <div class="stat-value highlight-badge">{{ modalData.memory }}/100</div>
                <div class="memory-types">
                  <div v-for="type in modalData.memoryTypes" :key="type.name" class="memory-type">
                    <span class="memory-emoji">{{ type.emoji }}</span>
                    <span class="memory-name">{{ type.name }}</span>
                    <span class="memory-score">{{ type.score }}/100</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="psycho-extra-info" style="margin-top:2rem;">
            <div><strong>Taken At:</strong> {{ modalData.taken_at }}</div>
            <div><strong>Duration:</strong> {{ modalData.duration_seconds }} seconds</div>
            <div v-if="modalData.feedback"><strong>Feedback:</strong> {{ modalData.feedback }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Tasks Modal Component -->
    <div v-if="modalComponent === 'recent-tasks-modal'" class="recent-tasks-modal modal-overlay" @click="closeModal">
      <div class="transactions-popup" @click.stop>
        <div class="popup-header">
          <span>Recent Tasks</span>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="popup-body">
          <div v-if="!modalData.allTasks || modalData.allTasks.length === 0" class="no-transactions">
            No recent tasks.
          </div>
          <div v-for="task in modalData.allTasks" :key="task.id" class="transaction-item">
            <div class="transaction-date">{{ task.due_date }}</div>
            <div class="transaction-desc">{{ task.title }} ({{ task.subject }})</div>
            <div class="transaction-amount">{{ task.status }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Emotional Modal Component -->
    <div v-if="modalComponent === 'emotional-modal'" class="emotional-modal modal-overlay" @click="closeModal">
      <div class="transactions-popup" @click.stop>
        <div class="popup-header">
          <div>Emotional Insight</div>
          <button class="close-btn" @click="closeModal">×</button>
        </div>

        <div class="popup-body scrollable-section">
          <!-- Today's Mood Section -->
          <div class="section-header">
            <h3>📅 Today's Mood Summary</h3>
          </div>

          <div v-if="modalData.weeklyMoods && modalData.weeklyMoods.length > 0" class="mood-section">
            <div v-for="mood in modalData.weeklyMoods" :key="mood.date + mood.feeling"
              class="transaction-item mood-item">
              <div class="transaction-date mood-date">
                <span class="date-text">{{ mood.date }}</span>
                <small v-if="mood.messageCount" class="message-count">{{ mood.messageCount }} messages</small>
              </div>
              <div class="transaction-desc mood-desc">
                <strong>{{ mood.feeling }}</strong>
                <p class="mood-notes">{{ mood.notes }}</p>
              </div>
              <div class="transaction-amount mood-emoji">{{ mood.emoji }}</div>
            </div>
          </div>

          <div v-else class="no-data-message">
            <p>🤔 No mood data available for today</p>
          </div>

          <!-- Conversation Analysis Section -->
          <div class="section-header">
            <h3>💭 Conversations & Messages</h3>
          </div>

          <div v-if="modalData.conversationTopics && modalData.conversationTopics.length > 0" class="topics-section">
            <div v-for="topic in modalData.conversationTopics" :key="topic.id" class="transaction-item topic-item">
              <div class="transaction-date sentiment-badge" :class="getSentimentClass(topic.sentiment)"
                style="max-width:0px;">
                <!--     <span class="sentiment-text">{{ getSentimentDisplay(topic.sentiment) }}</span>-->
              </div>
              <div class="transaction-desc topic-desc">
                <strong>{{ topic.title }}</strong>
                <p class="topic-summary">{{ topic.summary }}</p>

                <!-- User Messages Section -->
                <div v-if="topic.messages && topic.messages.length > 0" class="user-messages">
                  <div class="messages-header">
                    <span class="messages-label">💬 What your child said:</span>
                  </div>
                  <div v-for="(message, index) in topic.messages" :key="index" class="user-message-item">
                    <div class="message-content">
                      <span class="message-text">"{{ message.text }}"</span>
                      <div class="message-meta">
                        <span class="message-mood">{{ moodToEmoji(message.mood) }} {{ message.mood }}</span>
                        <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
              <div class="transaction-amount keywords-section">
                <div class="keywords-container">
                  <span v-for="keyword in topic.keywords" :key="keyword" class="keyword-tag">
                    {{ keyword }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="no-data-message">
            <p>💬 No conversation analysis available</p>
          </div>

          <!-- Tips Section -->
          <div class="section-header">
            <h3>💡 Insights</h3>
          </div>

          <div class="insights-section">
            <div class="insight-card">
              <p v-if="getMainSentiment() === 'positive'" class="insight-text positive">
                🌟 Your child seems to be in a positive mood today! Keep encouraging open communication.
              </p>
              <p v-else-if="getMainSentiment() === 'negative'" class="insight-text negative">
                🤗 Your child might need some extra support today. Consider having a gentle check-in conversation.
              </p>
              <p v-else class="insight-text neutral">
                😊 Your child's mood appears balanced today. Regular check-ins help maintain emotional well-being.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Header -->
    <header class="dashboard-header">
      <div class="container">
        <div class="header-content">
          <div class="parent-logo">
            <span class="logo-icon">👨‍👩‍👧‍👦</span>
            <div class="logo-text">
              <h1>Parent Dashboard</h1>
              <span class="subtitle" v-if="childName">Monitoring {{ childName }}'s Progress</span>
              <span class="subtitle" v-else>Progress Monitor</span>
            </div>
          </div>
          <div class="header-actions">
            <div class="child-info" v-if="childName">
              <span class="child-label">👶</span>
              <span class="child-name">{{ childName }}</span>
            </div>
            <button @click="logout" class="logout-btn">
              <span class="btn-icon">🚪</span>
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="dashboard-main">
      <div class="container">
        <!-- Overview Cards Row -->
        <div class="overview-grid">
          <div class="overview-card progress-card" @click="showProgressModal">
            <div class="card-icon">📊</div>
            <div class="card-content">
              <h3>Overall Progress</h3>
              <div class="progress-circle" :style="{ '--progress': overallProgress }">
                <span class="progress-text">{{ overallProgress }}%</span>
              </div>
              <p>{{ overallProgress }}% tasks completed</p>
            </div>
          </div>

          <div class="overview-card screentime-card" @click="showScreenTimeModal">
            <div class="card-icon">📱</div>
            <div class="card-content">
              <h3>Screen Time</h3>
              <div class="screentime-value">{{ screenTimeData.total }}</div>
              <p>{{ screenTimeData.status }}</p>
            </div>
          </div>

          <div class="overview-card achievement-card" @click="showAchievementModal">
            <div class="card-icon">⚡</div>
            <div class="card-content">
              <h3>Today's Achievement</h3>
              <div class="achievement-text">{{ todayAchievement.text }}</div>
              <div class="achievement-amount">{{ todayAchievement.amount }}</div>
            </div>
          </div>

          <div class="overview-card money-card" @click="showFinanceModal">
            <div class="card-icon">💰</div>
            <div class="card-content">
              <h3>Money Saved</h3>
              <div class="money-value">₹{{ financeStats.savings }}</div>
              <p>{{ financeStats.recent.length }} recent transactions</p>
            </div>
          </div>
        </div>

        <!-- Main Features Grid -->
        <div class="main-features-grid">
          <!-- Health Tracker -->
          <div class="feature-card health-card" @click="showHealthModal">
            <div class="card-header">
              <div class="card-icon">❤️</div>
              <h3>Health Tracker</h3>
            </div>
            <div class="card-content">
              <div class="health-grid">
                <div class="health-item">
                  <div class="health-emoji">✅</div>
                  <div class="health-label">Tasks Done</div>
                  <div class="health-value">{{ healthStats.tasks_completed }}/5</div>
                </div>
                <div class="health-item">
                  <div class="health-emoji">💪</div>
                  <div class="health-label">Completed Tasks</div>
                  <div class="health-value stacked-tasks">
                    <span v-for="(task, idx) in healthStats.completedTaskNames" :key="idx" class="completed-task-name">
                      {{ task }}
                    </span>
                  </div>
                </div>
                <div class="health-item">
                  <div class="health-emoji">💧</div>
                  <div class="health-label">Water</div>
                  <div class="health-value">{{ healthStats.water_today }}/8</div>
                </div>
                <div class="health-item streak-item">
                  <div class="health-emoji">🔥</div>
                  <div class="health-label">Streak</div>
                  <div class="health-value streak-number">{{ healthStats.streak }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Psychometric Test -->
          <div class="feature-card psychometric-card" @click="showPsychometricModal">
            <div class="card-header">
              <div class="card-icon">🧠</div>
              <h3>Psychometric Test</h3>
            </div>
            <div class="card-content">
              <div class="psychometric-grid">
                <div class="psycho-item">
                  <div class="psycho-emoji">👤</div>
                  <div class="psycho-label">Personality</div>
                  <div class="psycho-value">{{ psychometricData.personality }}</div>
                </div>
                <div class="psycho-item">
                  <div class="psycho-emoji">🎯</div>
                  <div class="psycho-label">Interests</div>
                  <div class="psycho-value">{{ psychometricData.interests }}</div>
                </div>
                <div class="psycho-item">
                  <div class="psycho-emoji">🎯</div>
                  <div class="psycho-label">Concentration</div>
                  <div class="psycho-value">{{ psychometricData.concentration }}/100</div>
                </div>
                <div class="psycho-item">
                  <div class="psycho-emoji">🧠</div>
                  <div class="psycho-label">Memory</div>
                  <div class="psycho-value">{{ psychometricData.memory }}/100</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Doodling Sessions -->
          <div class="feature-card doodling-card" @click="showDoodlingModal">
            <div class="card-header">
              <div class="card-icon">🎨</div>
              <h3>Doodling Sessions</h3>
            </div>
            <div class="card-content">
              <div class="doodle-summary">
                <span class="doodle-count">{{ doodleStats.allDoodles?.length || 0 }} artworks</span>
              </div>
              <div class="doodle-grid">
                <div v-for="(doodle, idx) in doodleStats.doodles.slice(0, 4)" :key="idx" class="doodle-box"
                  @click.stop="viewDoodle(doodle)">
                  <div class="doodle-canvas" :style="{ backgroundColor: doodle.color }">
                    <div class="doodle-preview-content">
                      <img v-if="doodle.file_exists && doodle.file_path" :src="getDoodleImageUrl(doodle.file_path)"
                        alt="Doodle" style="max-width: 100%; max-height: 70px; border-radius: 8px;" />
                      <span v-else>{{ doodle.emoji || '🎨' }}</span>
                    </div>
                  </div>
                  <div class="doodle-footer">
                    <div class="doodle-name">{{ doodle.title }}</div>
                    <div class="doodle-date">{{ doodle.date }}</div>
                  </div>
                </div>
              </div>
              <div v-if="doodleStats.allDoodles?.length > 4" class="more-indicator">
                <span>+{{ doodleStats.allDoodles.length - 4 }} more artworks</span>
              </div>
            </div>
          </div>

          <!-- Task Tracker -->
          <div class="feature-card task-card">
            <div class="card-header">
              <div class="card-icon">🎯</div>
              <h3>Task Tracker</h3>
            </div>
            <div class="card-content">
              <div class="task-calendar">
                <div class="calendar-header">
                  <span class="calendar-month">{{ getCurrentMonth() }}</span>
                </div>
                <div class="calendar-grid">
                  <div v-for="day in taskStats.calendar || []" :key="day.date" class="calendar-day"
                    :class="{ 'today': day.isToday, 'has-tasks': day.taskCount > 0 }">
                    <div class="day-number">{{ day.day }}</div>
                    <div class="day-tasks" v-if="day.taskCount > 0">
                      {{ day.completedTasks }}/{{ day.taskCount }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="recent-tasks">
                <div v-for="task in taskStats.recent || []" :key="task.id" class="recent-task-item"
                  @click="showRecentTasksModal" style="cursor:pointer;">
                  <div class="task-name">{{ task.title }}</div>
                  <div class="task-session">{{ task.status }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Emotional Insights -->
          <!-- filepath: frontend/src/views/ParentDashboard.vue -->
          <!-- Emotional Insights -->
          <div class="feature-card emotional-card" @click="showEmotionalModal">
            <div class="card-header">
              <div class="card-icon">💭</div>
              <h3>Emotional Insights</h3>
            </div>
            <div class="card-content">
              <div class="mood-tracker">
                <div class="mood-chart">
                  <template v-if="emotionalInsights.moodTrends && emotionalInsights.moodTrends.length">
                    <div v-for="mood in emotionalInsights.moodTrends" :key="mood.date" class="mood-day">
                      <div class="mood-emoji" :title="mood.feeling">{{ mood.emoji }}</div>
                      <div class="mood-date">{{ mood.date }}</div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="mood-day">
                      <div class="mood-emoji" title="No data">🙂</div>
                      <div class="mood-date">No data</div>
                    </div>
                  </template>
                </div>
              </div>
              <div class="conversation-summary">
                <div class="summary-cards">
                  <template v-if="emotionalInsights.summaries && emotionalInsights.summaries.length">
                    <div v-for="summary in emotionalInsights.summaries" :key="summary.id" class="summary-card">
                      <div class="summary-topic">{{ summary.topic }}</div>
                      <div class="summary-text">{{ summary.text }}</div>
                      <div class="summary-sentiment"
                        :class="[summary.sentiment, { 'highlighted': summary.sentiment === 'positive' || summary.sentiment === 'neutral' }]">
                        {{ summary.sentiment }}
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="summary-card">
                      <div class="summary-topic">Overall Mood</div>
                      <div class="summary-text">No summary available.</div>
                      <div class="summary-sentiment neutral highlighted">neutral</div>
                    </div>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <!-- Skill Adventures -->
          <div class="feature-card skills-card" @click="showSkillsModal">
            <div class="card-header">
              <div class="card-icon">🚀</div>
              <h3>Skill Adventures</h3>
            </div>
            <div class="card-content">
              <div class="skills-grid">
                <div v-for="(skill, idx) in skillProgress" :key="idx" class="skill-box">
                  <div class="skill-icon">{{ skill.icon }}</div>
                  <div class="skill-info">
                    <div class="skill-name">{{ skill.name }}</div>
                    <div class="skill-progress-bar">
                      <div class="skill-progress-fill" :style="{ width: skill.progress + '%' }"></div>
                    </div>
                    <div class="skill-progress-text">{{ skill.progress }}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Floating Magic -->
        <div class="floating-magic">
          <div class="magic-element" style="--delay: 0s; --x: 10%; --y: 20%;">🌟</div>
          <div class="magic-element" style="--delay: 2s; --x: 90%; --y: 30%;">⭐</div>
          <div class="magic-element" style="--delay: 4s; --x: 15%; --y: 70%;">💫</div>
          <div class="magic-element" style="--delay: 6s; --x: 85%; --y: 80%;">✨</div>
        </div>
      </div>
    </main>

    <!-- Modals -->



    <!-- Doodling Modal Component -->
    <div v-if="modalComponent === 'doodling-modal'" class="doodling-modal modal-overlay" @click="closeModal">
      <div class="doodling-popup" @click.stop>
        <div class="popup-header">
          <span>Doodle Gallery ({{ modalData.allDoodles?.length || 0 }} items)</span>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="doodle-gallery-container">
          <div class="doodle-gallery">
            <div v-for="(doodle, idx) in modalData.allDoodles" :key="idx" class="doodle-gallery-item">
              <div class="doodle-canvas-large" :style="{ backgroundColor: doodle.color }">
                <div class="doodle-artwork">
                  <img v-if="doodle.file_exists && doodle.file_path" :src="getDoodleImageUrl(doodle.file_path)"
                    alt="Doodle" class="doodle-image" />
                  <span v-else class="doodle-emoji">{{ doodle.emoji || '🎨' }}</span>
                </div>
              </div>
              <div class="doodle-details">
                <h4>{{ doodle.title }}</h4>
                <p class="doodle-date">{{ doodle.date }}</p>
                <div class="doodle-tags">
                  <span v-for="tag in doodle.tags" :key="tag" class="doodle-tag">{{ tag }}</span>
                </div>
              </div>
            </div>
            <div v-if="!modalData.allDoodles || modalData.allDoodles.length === 0" class="no-doodles">
              <div class="no-doodles-icon">🎨</div>
              <p>No doodles to display</p>
              <small>Child hasn't created any doodles yet</small>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Task Modal Component -->
    <div v-if="modalComponent === 'task-modal'" class="task-modal">
      <div class="task-detailed">
        <div class="task-calendar-detailed">
          <div class="calendar-navigation">
            <button @click="previousMonth" class="nav-btn">←</button>
            <h3>{{ getCurrentMonthYear() }}</h3>
            <button @click="nextMonth" class="nav-btn">→</button>
          </div>
          <div class="calendar-grid-detailed">
            <div class="calendar-weekdays">
              <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" class="weekday">
                {{ day }}
              </div>
            </div>
            <div class="calendar-dates">
              <div v-for="date in getDetailedCalendarDays()" :key="date.date" class="calendar-date"
                :class="{ 'today': date.isToday, 'has-tasks': date.taskCount > 0 }">
                <div class="date-number">{{ date.day }}</div>
                <div class="date-tasks" v-if="date.taskCount > 0">
                  <div class="task-indicator" :class="{ 'completed': date.completedTasks === date.taskCount }">
                    {{ date.completedTasks }}/{{ date.taskCount }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="task-list-detailed">
          <h4>Recent Tasks</h4>
          <div class="task-items">
            <div v-for="task in modalData.allTasks" :key="task.id" class="task-item-detailed">
              <div class="task-status-icon" :class="task.status">
                {{ task.status === 'completed' ? '✅' : task.status === 'in-progress' ? '🔄' : '⏳' }}
              </div>
              <div class="task-info">
                <h5>{{ task.title }}</h5>
                <p class="task-description">{{ task.description }}</p>
                <div class="task-meta">
                  <span class="task-date">{{ task.date }}</span>
                  <span class="task-duration">{{ task.sessionTime }} min</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Skills Modal Component -->
    <div v-if="modalComponent === 'skills-modal'" class="skills-modal">
      <div class="skills-detailed">
        <div class="skills-overview">
          <h4>Skill Development Overview</h4>
          <div class="skills-grid-detailed">
            <div v-for="skill in modalData.allSkills" :key="skill.id" class="skill-card-detailed">
              <div class="skill-icon-large">{{ skill.icon }}</div>
              <div class="skill-info-detailed">
                <h5>{{ skill.name }}</h5>
                <div class="skill-level">Level {{ skill.level }}</div>
                <div class="skill-progress-detailed">
                  <div class="progress-bar-detailed">
                    <div class="progress-fill-detailed" :style="{ width: skill.progress + '%' }"></div>
                  </div>
                  <span class="progress-percentage">{{ skill.progress }}%</span>
                </div>
                <div class="skill-milestones">
                  <div v-for="milestone in skill.milestones" :key="milestone.id" class="milestone"
                    :class="{ 'completed': milestone.completed }">
                    <span class="milestone-icon">{{ milestone.completed ? '✅' : '⏳' }}</span>
                    <span class="milestone-text">{{ milestone.text }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userUtils } from '@/services/api'
import { apiService } from '@/services/api' // adjust path as needed

// Reactive State

const showModal = ref(false)
const modalTitle = ref('')
const modalComponent = ref('')
const modalData = ref({})

const overallProgress = ref(0)
const screenTimeData = ref({
  total: 'Loading...',
  status: 'Loading...'
})
const todayAchievement = ref({
  text: 'Login Streak',
  amount: '0 days'
})
const getCurrentMonth = () => 'July 2025'

const getCurrentMonthYear = () => 'July 2025'

const getCalendarDays = () => [
  { date: '2025-07-01', day: 1, isToday: false, taskCount: 2, completedTasks: 1 },
  { date: '2025-07-02', day: 2, isToday: true, taskCount: 1, completedTasks: 1 },
  // Add more dummy days as needed
]

const getDetailedCalendarDays = () => [
  { date: '2025-07-01', day: 1, isToday: false, taskCount: 2, completedTasks: 1 },
  { date: '2025-07-02', day: 2, isToday: true, taskCount: 1, completedTasks: 1 },
  // Add more dummy days as needed
]

const previousMonth = () => console.log('Previous Month')
const nextMonth = () => console.log('Next Month')
const getStreakDays = () => Array.from({ length: 10 }, (_, i) => i + 1)


const psychometricData = ref({
  personality: '',
  interests: '',
  concentration: 0,
  memory: 0,
  traits: [],
  interestsList: [],
  memoryTypes: []
})

const fetchPsychometricData = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.get(`/api/psychometry/results/${childId.value}`)
    if (res.success && res.result) {
      const r = res.result
      // Map backend fields to frontend structure
      psychometricData.value = {
        personality: r.personality_type || '',
        interests: r.top_interest || '',
        concentration: r.concentration_level || 0,
        memory: r.memory_strength || 0,
        traits: Array.isArray(r.personality_breakdown?.traits) ? r.personality_breakdown.traits : [],
        interestsList: Array.isArray(r.detailed_scores?.interests)
          ? r.detailed_scores.interests.map(i => ({
            name: i.name,
            emoji: i.emoji || '',
            level: i.level || 0
          }))
          : [],
        memoryTypes: Array.isArray(r.detailed_scores?.memory_types)
          ? r.detailed_scores.memory_types.map(m => ({
            name: m.name,
            emoji: m.emoji || '',
            score: m.score || 0
          }))
          : [],
        taken_at: r.taken_at || '',
        duration_seconds: r.duration_seconds || 0,
        feedback: r.feedback || ''
      }
    }
  } catch (e) {
    console.error('Failed to fetch psychometric data', e)
  }
}

const fetchDoodles = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.get(`/api/drawings/${childId.value}`)
    console.log('Doodle API response:', res)
    if (res.success && Array.isArray(res.drawings)) {
      doodleStats.value.doodles = res.drawings.map(d => ({
        id: d.id,
        title: d.description || 'Untitled',
        date: d.timestamp ? d.timestamp.slice(0, 10) : '',
        duration: d.time_taken ? Math.round(d.time_taken / 60) : 0,
        tags: d.ref_image_title ? [d.ref_image_title] : [],
        file_path: d.file_path,
        file_exists: d.file_exists,
        emoji: '🎨', // fallback if no image
        color: '#aaf'
      }))
      doodleStats.value.allDoodles = doodleStats.value.doodles
    }
  } catch (e) {
    console.error('Failed to fetch doodles', e)
  }
}

const fetchTaskStats = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.getTasksParent(childId.value)
    if (res.success && Array.isArray(res.tasks)) {
      // Prepare calendar stats for last 7 days
      const today = new Date()
      const calendarStats = []
      for (let i = 6; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        const dateStr = date.toISOString().slice(0, 10)
        // Filter tasks for this day
        const dayTasks = res.tasks.filter(t => t.due_date?.slice(0, 10) === dateStr)
        const completedTasks = dayTasks.filter(t => t.status === 'completed').length
        calendarStats.push({
          date: dateStr,
          day: date.getDate(),
          isToday: i === 0,
          taskCount: dayTasks.length,
          completedTasks: completedTasks
        })
      }

      // Get latest 3 pending/in-progress tasks
      const recentTasks = res.tasks
        .filter(t => t.status === 'pending' || t.status === 'in-progress')
        .sort((a, b) => new Date(b.due_date) - new Date(a.due_date))
        .slice(0, 3)
        .map(t => ({
          id: t.id,
          title: t.task,
          status: t.status,
          subject: t.subject,
          due_date: t.due_date
        }))

      taskStats.value = {
        recent: recentTasks,
        calendar: calendarStats
      }
    }
  } catch (e) {
    console.error('Failed to fetch task stats', e)
  }
}

const skillProgress = ref([
  { id: 1, name: 'Math Magic', icon: '🔢', progress: 0, level: 1, milestones: [] },
  { id: 2, name: 'Science Lab', icon: '🔬', progress: 0, level: 1, milestones: [] },
  { id: 3, name: 'Word Wizard', icon: '📚', progress: 0, level: 1, milestones: [] },
  { id: 4, name: 'Safety Measures', icon: '🛡️', progress: 0, level: 1, milestones: [] },
  { id: 5, name: 'Good Touch Bad Touch', icon: '👥', progress: 0, level: 1, milestones: [] },
  { id: 6, name: 'Psychometric Test', icon: '🧠', progress: 0, level: 1, milestones: [] }
])


const financeStats = ref({ savings: 0, recent: [] })
const childId = ref(null)
const childName = ref('')

// Get the childId for this parent from ParentChild table
const fetchChildId = async () => {
  try {
    console.log('fetchChildId called')
    const res = await apiService.get('/api/parentchild')
    console.log('apiService.get(/api/parentchild) result:', res)
    const parentId = userUtils.getCurrentUser()?.id
    console.log('Current parentId:', parentId)
    console.log('Links:', res.links)
    const link = Array.isArray(res.links) ? res.links.find(l => l.parent_id === parentId) : null
    if (link) {
      childId.value = link.child_id
      console.log('Setting childId to:', childId.value)
      // Fetch child's name after getting the ID
      await fetchChildName()
    } else {
      console.error('No parent-child link found for parentId:', parentId)
    }
  } catch (e) {
    console.error('Failed to fetch childId', e)
  }
}

// Fetch child's name from user profile
const fetchChildName = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.get(`/api/user/profile/${childId.value}`)
    if (res.success && res.user) {
      childName.value = res.user.username || res.user.name || 'Child'
      console.log('Child name fetched:', childName.value)
    }
  } catch (e) {
    console.error('Failed to fetch child name', e)
    childName.value = 'Child' // Fallback name
  }
}

// Fetch transactions and calculate savings
const fetchFinanceStats = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.getTransactions(childId.value)
    if (res.success) {
      financeStats.value.recent = res.transactions.slice(0, 5)
      financeStats.value.savings = res.transactions.reduce((sum, t) => {
        return sum + (t.type === 'income' ? t.amount : -t.amount)
      }, 0)
    }
  } catch (e) {
    console.error('Failed to fetch transactions', e)
  }
}

// Fetch screen time data from API
const fetchScreenTimeData = async () => {
  if (!childId.value) return
  console.log('fetchScreenTimeData called with childId:', childId.value)
  try {
    const res = await apiService.getScreenTime(childId.value)
    console.log('Screen time API response:', res)
    if (res.success && res.screen_time) {
      screenTimeData.value = {
        total: res.screen_time.today_display,
        status: res.screen_time.status,
        week_average: res.screen_time.week_average_display
      }
      console.log('Screen time data fetched:', screenTimeData.value)
    } else {
      console.error('Screen time API returned unsuccessful or missing data:', res)
    }
  } catch (e) {
    console.error('Failed to fetch screen time data', e)
    // Provide fallback data on error
    screenTimeData.value = {
      total: 'No data',
      status: 'Unable to load',
      week_average: 'No data'
    }
  }
}

// Fetch overall progress from API
const fetchOverallProgress = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.getChildProgress(childId.value)
    if (res.success && res.progress) {
      overallProgress.value = res.progress.overall_percentage
      console.log('Overall progress fetched:', overallProgress.value + '%')
    }
  } catch (e) {
    console.error('Failed to fetch overall progress', e)
    // Provide fallback data on error
    overallProgress.value = 0
  }
}

// Fetch skill progress from API
const fetchSkillProgress = async () => {
  if (!childId.value) return
  console.log('fetchSkillProgress called with childId:', childId.value)
  try {
    const res = await apiService.getChildSkillProgress(childId.value)
    console.log('Skill progress API response:', res)
    if (res.success && res.skill_progress) {
      const skillData = res.skill_progress

      // Convert skill data to array format with all modules
      skillProgress.value = Object.keys(skillData).map((skillName, index) => ({
        id: index + 1,
        name: skillName,
        icon: skillData[skillName].icon || '🎯',
        progress: Math.round(skillData[skillName].progress || 0),
        level: Math.floor((skillData[skillName].progress || 0) / 50) + 1,
        milestones: []
      }))

      console.log('Skill progress fetched:', skillProgress.value)
    } else {
      console.error('Skill progress API returned unsuccessful or missing data:', res)
    }
  } catch (e) {
    console.error('Failed to fetch skill progress', e)
    // Keep default skill data on error - the skillProgress is already initialized with default values
  }
}

onMounted(async () => {
  await fetchChildId()
  if (childId.value) {
    await fetchFinanceStats()
    await fetchHealthStats()
    await fetchPsychometricData()
    await fetchTaskStats()
    await fetchEmotionalInsights()
    await fetchDoodles()
    await fetchScreenTimeData()  // Add screen time fetch
    await fetchOverallProgress()  // Add progress fetch
    await fetchSkillProgress()  // Add skill progress fetch
    await fetchLoginStreak()  // Add login streak fetch for achievement card
  }
})

const healthStats = ref({
  streak: 0,
  water_today: 0,
  tasks_completed: 0,
  completedTaskNames: [],
  waterlog: [],
  dailyTarget: 8, // glasses per day

})

const fetchHealthStats = async () => {
  if (!childId.value) return;

  try {
    const tasks = await apiService.getHealthTasks(childId.value);
    const completed = tasks.filter(t => t.completed);
    healthStats.value.tasks_completed = completed.length;
    healthStats.value.completedTaskNames = completed.map(t => t.name);

    healthStats.value.water_today = await apiService.getWaterCount(childId.value);
    healthStats.value.streak = await apiService.getHealthStreak(childId.value);
    healthStats.value.waterlog = await apiService.getWaterLog(childId.value);
  } catch (e) {
    console.error('Failed to fetch health stats', e);
  }
};

// Fetch login streak for achievement card
const fetchLoginStreak = async () => {
  if (!childId.value) return;

  try {
    const res = await apiService.get(`/api/login-streak/${childId.value}`)
    if (res.success) {
      const streakCount = res.current_streak || 0
      todayAchievement.value = {
        text: 'Login Streak',
        amount: `${streakCount} ${streakCount === 1 ? 'day' : 'days'}`
      }
      console.log('Login streak fetched:', streakCount)
    }
  } catch (e) {
    console.error('Failed to fetch login streak', e)
    // Keep default values on error
  }
}



// Helper function to format message timestamps
const formatMessageTime = (timestamp) => {
  if (!timestamp) return 'Unknown time'

  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = Math.floor((now - date) / (1000 * 60))

  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`

  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours}h ago`

  const options = { hour: '2-digit', minute: '2-digit', hour12: true }
  return date.toLocaleTimeString('en-US', options)
}


// Helper methods for the template
const getSentimentClass = (sentiment) => {
  return sentiment ? sentiment.toLowerCase() : 'neutral'
}

const getSentimentDisplay = (sentiment) => {
  const sentimentMap = {
    positive: '😊 Positive',
    negative: '😔 Needs Attention',
    neutral: '😐 Neutral'
  }
  return sentimentMap[sentiment] || '😐 Neutral'
}

const getMainSentiment = () => {
  if (!modalData.value.conversationTopics || modalData.value.conversationTopics.length === 0) {
    return 'neutral'
  }
  return modalData.value.conversationTopics[0].sentiment || 'neutral'
}

// Enhanced API error handling
const handleApiError = (error, context = 'emotional insights') => {
  console.error(`Error fetching ${context}:`, error)

  return {
    weeklyMoods: [
      {
        date: formatDate(new Date()),
        emoji: '',
        feeling: 'Could not load Details',
        notes: `Unable to load ${context}. Please try again.`,
        messageCount: 0
      }
    ],
    conversationTopics: [
      {
        id: 1,
        sentiment: 'neutral',
        title: 'Could not Load Details',
        summary: 'Please check your connection and try again',
        keywords: ['Retry'],
        messages: []
      }
    ]
  }
}
// Fetch emotional insights (mood summary) for the child
const fetchEmotionalInsights = async () => {
  if (!childId.value) return
  try {
    const res = await apiService.get(`/api/chat/mood-summary/${childId.value}`)
    if (res.success) {
      //new
      const moodEntries = []
      const conversationTopics = []

      if (res.mood_groups && Object.keys(res.mood_groups).length > 0) {
        // Create entries for each mood group
        Object.entries(res.mood_groups).forEach(([mood, messages], index) => {
          // Add mood summary entry
          moodEntries.push({
            date: formatDate(res.date),
            emoji: moodToEmoji(mood),
            feeling: mood,
            notes: res.overall_mood || 'Mood analysis based on conversations',
            messageCount: messages.length
          })

          // Add conversation topic for each mood with associated messages
          conversationTopics.push({
            id: index + 1,
            sentiment: moodToSentiment(mood),
            title: `${mood.charAt(0).toUpperCase() + mood.slice(1)} Conversations`,
            summary: `${messages.length} message${messages.length > 1 ? 's' : ''} showing ${mood} mood`,
            keywords: [mood],
            messages: messages.slice(0, 3).map(msg => ({
              text: msg.user_message,
              timestamp: msg.timestamp,
              mood: msg.mood_tag
            })) // Show up to 3 messages per mood
          })
        })
      } else if (res.latest_mood) {
        // Fallback: show latest mood info
        moodEntries.push({
          date: formatDate(res.date),
          emoji: moodToEmoji(res.latest_mood),
          feeling: res.latest_mood,
          notes: res.overall_mood || 'Latest mood detected',
          messageCount: res.total_messages || 0
        })

        if (res.latest_message) {
          conversationTopics.push({
            id: 1,
            sentiment: moodToSentiment(res.latest_mood),
            title: 'Recent Conversation',
            summary: res.overall_mood || 'Latest conversation analysis',
            keywords: [res.latest_mood],
            messages: [{
              text: res.latest_message,
              timestamp: new Date().toISOString(),
              mood: res.latest_mood
            }]
          })
        }
      }
      // Example: Map backend response to frontend structure
      emotionalInsights.value = {
        // Weekly Moods data for the modal
        weeklyMoods: moodEntries.length > 0 ? moodEntries : [
          {
            date: formatDate(res.date),
            emoji: '🤔',
            feeling: 'No mood recorded',
            notes: res.overall_mood || 'No conversations detected today',
            messageCount: 0
          }
        ],
        // Conversation Topics data for the modal
        conversationTopics: conversationTopics.length > 0 ? conversationTopics : [
          {
            id: 1,
            sentiment: 'neutral',
            title: 'Getting Started',
            summary: 'Start chatting to see emotional insights and mood analysis',
            keywords: ['No data'],
            messages: []
          }
        ],
        moodTrends: [
          {
            date: res.date,
            emoji: res.latest_mood ? moodToEmoji(res.latest_mood) : '🙂',
            feeling: res.latest_mood || 'Unknown'
          }
        ],
        summaries: [
          {
            id: 1,
            topic: 'Overall Mood',
            text: res.overall_mood || 'No summary available.',
            sentiment: moodToSentiment(res.latest_mood)
          }
        ]
      }
    } else {
      // Handle empty or failed response
      emotionalInsights.value = {
        weeklyMoods: [
          {
            date: formatDate(new Date()),
            emoji: '🤔',
            feeling: 'No data',
            notes: 'No emotional data available for today'
          }
        ],
        conversationTopics: [
          {
            id: 1,
            sentiment: 'neutral',
            title: 'No Analysis Available',
            summary: 'Start a conversation to see emotional insights',
            keywords: ['No data']
          }
        ],
        moodTrends: [],
        summaries: []
      }
    }
  } catch (e) {
    console.error('Failed to fetch emotional insights', e)
    // Handle error state
    emotionalInsights.value = {
      weeklyMoods: [
        {
          date: formatDate(new Date()),
          emoji: '',
          feeling: 'Could not load Details',
          notes: 'Sorry, could not load emotional insights, please try again.'
        }
      ],
      conversationTopics: [
        {
          id: 1,
          sentiment: 'neutral',
          title: 'Could not Load Details',
          summary: 'Please try again',
          keywords: ['Retry']
        }
      ],
      moodTrends: [],
      summaries: []
    }
  }
}

// Helper function to format date
function formatDate(dateStr) {
  const date = new Date(dateStr)
  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    weekday: 'short'
  }
  return date.toLocaleDateString('en-US', options)
}


// Helper functions to map mood to emoji/sentiment
function moodToEmoji(mood) {
  if (!mood) return '🙂'
  const map = {
    happy: '😊',
    sad: '😢',
    angry: '😠',
    excited: '🤩',
    anxious: '😰',
    calm: '😌',
    // Add more as needed
  }
  return map[mood.toLowerCase()] || '🙂'
}

function moodToSentiment(mood) {
  if (!mood) return 'neutral'
  const positive = ['happy', 'excited', 'calm']
  const negative = ['sad', 'angry', 'anxious']
  if (positive.includes(mood.toLowerCase())) return 'positive'
  if (negative.includes(mood.toLowerCase())) return 'negative'
  return 'neutral'
}

function getDoodleImageUrl(filePath) {
  if (!filePath) return ''
  // Remove 'static/' if present, then prepend '/static/'
  const relPath = filePath.replace(/^static[\\/]/, '')
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  return `${API_BASE_URL}/static/${relPath}`
}

const doodleStats = ref({
  doodles: [
    { title: 'My Cat', date: '2025-07-03', duration: 10, tags: ['fun'], color: '#aaf', emoji: '🐱' }
  ],
  allDoodles: []
})

const taskStats = ref({
  recent: [],
  calendar: []
})

const emotionalInsights = ref({
  moodTrends: [],
  summaries: []
})

// Methods
const openModal = (title, component, data) => {
  modalTitle.value = title
  modalComponent.value = component
  modalData.value = data
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  modalComponent.value = ''
}

const showProgressModal = () => openModal('Overall Progress', 'progress-modal', { progress: overallProgress.value })
const showScreenTimeModal = () => openModal('Screen Time', 'screentime-modal', screenTimeData.value)
const showAchievementModal = () => openModal('Achievement', 'achievement-modal', todayAchievement.value)
const showFinanceModal = () => openModal('Recent Transactions', 'transactions-modal', financeStats.value)
const showHealthModal = () => openModal('Health', 'health-modal', { ...healthStats.value, completedTaskNames: healthStats.value.completedTaskNames });
const showPsychometricModal = () => openModal('Psychometric', 'psychometric-modal', psychometricData.value)
const showDoodlingModal = () => openModal('Doodling', 'doodling-modal', doodleStats.value)
const showTaskModal = () => openModal('Tasks', 'task-modal', taskStats.value)
const showEmotionalModal = () => openModal('Emotions', 'emotional-modal', emotionalInsights.value)
const showSkillsModal = () => openModal('Skills', 'skills-modal', skillProgress.value)
const viewDoodle = (doodle) => openModal('Doodle View', 'doodling-modal', { allDoodles: [doodle] })
const showRecentTasksModal = () => {
  openModal('Recent Tasks', 'recent-tasks-modal', { allTasks: taskStats.value.recent })
}

const logout = () => {
  userUtils.logout()
  console.log('Logged out')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.parent-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #31417A 0%, #667eea 100%);
  position: relative;
  font-family: 'Merriweather', serif;
}

/* Header */
.dashboard-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 1rem 0;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.parent-logo {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-icon {
  font-size: 2.5rem;
  animation: sparkle 3s infinite ease-in-out;
}

@keyframes sparkle {

  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.1);
  }
}

.logo-text h1 {
  font-size: 1.8rem;
  color: #333;
  font-weight: 700;
  margin: 0;
}

.subtitle {
  font-size: 0.9rem;
  color: #666;
  font-weight: 400;
}

/* =========================
   HEADER SECTION
   ========================= */
.dashboard-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.parent-logo {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 2.5rem;
  background: linear-gradient(135deg, #ff6b6b, #ffd93d);
  border-radius: 50%;
  padding: 10px;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.logo-text h1 {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin-bottom: 5px;
}

.subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.child-info {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 8px 16px;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.child-label {
  font-size: 1.2rem;
}

.child-name {
  color: white;
  font-weight: 600;
  font-size: 0.95rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.date-selector select {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 10px 15px;
  border-radius: 10px;
  font-size: 0.9rem;
  cursor: pointer;
  backdrop-filter: blur(5px);
}

.date-selector select:focus {
  outline: none;
  border-color: #ffd93d;
}

.export-btn,
.logout-btn {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 12px 18px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
}

.export-btn:hover,
.logout-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.1));
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.export-btn {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.2), rgba(0, 123, 255, 0.1));
  border-color: rgba(0, 123, 255, 0.3);
}

.export-btn:hover {
  background: linear-gradient(135deg, rgba(0, 123, 255, 0.3), rgba(0, 123, 255, 0.15));
  border-color: rgba(0, 123, 255, 0.4);
}

.logout-btn {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 107, 107, 0.1));
  border-color: rgba(255, 107, 107, 0.3);
}

.logout-btn:hover {
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.3), rgba(255, 107, 107, 0.15));
  border-color: rgba(255, 107, 107, 0.4);
}

.btn-icon {
  font-size: 1.1rem;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.export-btn::before,
.logout-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.6s ease;
}

.export-btn:hover::before,
.logout-btn:hover::before {
  left: 100%;
}

/* =========================
   MAIN DASHBOARD
   ========================= */
.dashboard-main {
  padding: 30px 0;
}

/* =========================
   OVERVIEW GRID - WARM COMPLEMENTARY COLORS
   ========================= */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
}

.overview-card {
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.overview-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.overview-card:nth-child(1) {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.overview-card:nth-child(2) {
  background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
}

.overview-card:nth-child(3) {
  background: linear-gradient(135deg, #FFD93D 0%, #FFA726 100%);
}

.overview-card:nth-child(4) {
  background: linear-gradient(135deg, #A8E6CF 0%, #7FCDCD 100%);
}

.overview-card .card-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
  display: block;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.overview-card h3 {
  color: white;
  font-size: 1.2rem;
  margin-bottom: 15px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.overview-card p {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  margin-top: 10px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Progress Card Specific */
.progress-card .progress-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(white 0deg, white calc(var(--progress) * 3.6deg), rgba(255, 255, 255, 0.3) calc(var(--progress) * 3.6deg));
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 15px 0;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.progress-text {
  color: #333;
  font-weight: 700;
  font-size: 1.1rem;
}

/* Screen Time Card */
.screentime-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Achievement Card */
.achievement-text {
  font-size: 1.1rem;
  color: white;
  margin: 10px 0;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.achievement-amount {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* Money Card */
.money-value {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 10px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

/* =========================
   MAIN FEATURES GRID - VIBRANT COMPLEMENTARY COLORS
   ========================= */
.main-features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.feature-card {
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 300px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.feature-card:nth-child(1) {
  background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
}

.feature-card:nth-child(2) {
  background: linear-gradient(135deg, #A8EDEA 0%, #FED6E3 100%);
}

.feature-card:nth-child(3) {
  background: linear-gradient(135deg, #FFECD2 0%, #FCB69F 100%);
}

.feature-card:nth-child(4) {
  background: linear-gradient(135deg, #C3ECE0 0%, #E6F3FF 100%);
}

.feature-card:nth-child(5) {
  background: linear-gradient(135deg, #FFB7B7 0%, #FFDFDF 100%);
}

.feature-card:nth-child(6) {
  background: linear-gradient(135deg, #B8E6B8 0%, #DCEDC8 100%);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.3);
}

.card-header .card-icon {
  font-size: 2rem;
  background: linear-gradient(135deg, #333 0%, #555 100%);
  border-radius: 50%;
  padding: 10px;
  min-width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.card-header h3 {
  color: #333;
  font-size: 1.3rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.card-content {
  flex: 1;
}

/* Health Card Specific */
.health-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.health-item {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.health-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.health-emoji {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.health-label {
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 5px;
  display: block;
  font-weight: 500;
}

.health-value {
  color: #333;
  font-weight: 700;
  font-size: 1.1rem;
}

.streak-item {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

.streak-item .health-label {
  color: rgba(255, 255, 255, 0.9);
}

.streak-item .health-value {
  color: white;
}

.streak-number {
  font-size: 1.8rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.completed-task-name {
  background-color: rgba(255, 255, 255, 0.2);
  color: #2c2c2c;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  margin: 2px 4px 0 0;
  display: inline-block;
  white-space: nowrap;
}

.stacked-tasks {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 100%;
}

/* Psychometric Card */
.psychometric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.psycho-item {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.psycho-item:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: scale(1.05);
}

.psycho-emoji {
  font-size: 2rem;
  margin-bottom: 10px;
  display: block;
}

.psycho-label {
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 5px;
  display: block;
  font-weight: 500;
}

.psycho-value {
  color: #333;
  font-weight: 700;
  font-size: 1rem;
}

/* Doodling Card */
.doodle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.doodle-summary {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px 0;
}

.doodle-count {
  font-size: 0.9rem;
  color: #667eea;
  font-weight: 600;
}

.more-indicator {
  text-align: center;
  margin-top: 15px;
  padding: 8px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  color: #667eea;
  font-size: 0.85rem;
  font-weight: 500;
}

.doodle-box {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.doodle-box:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.doodling-popup {
  background: #fff;
  border-radius: 18px;
  max-width: 800px;
  width: 90vw;
  max-height: 85vh;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  padding: 0;
  position: relative;
  animation: fadeIn 0.2s;
  display: flex;
  flex-direction: column;
}

.doodling-modal.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

/* Doodle Gallery Container with Scroll */
.doodle-gallery-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px 20px;
  scrollbar-width: thin;
  scrollbar-color: #667eea transparent;
}

.doodle-gallery-container::-webkit-scrollbar {
  width: 6px;
}

.doodle-gallery-container::-webkit-scrollbar-track {
  background: transparent;
}

.doodle-gallery-container::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 3px;
}

.doodle-gallery-container::-webkit-scrollbar-thumb:hover {
  background: #5a67d8;
}

.doodle-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px 0;
}

.doodle-gallery-item {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.doodle-gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.doodle-canvas-large {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.doodle-artwork {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.doodle-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.doodle-emoji {
  font-size: 3rem;
  color: white;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* No Doodles State */
.no-doodles {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  grid-column: 1 / -1;
}

.no-doodles-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

.no-doodles p {
  font-size: 1.2rem;
  margin: 0 0 10px 0;
  color: #4a5568;
}

.no-doodles small {
  color: #a0aec0;
  font-size: 0.9rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .doodling-popup {
    max-width: 95vw;
    max-height: 90vh;
  }

  .doodle-gallery {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .doodle-gallery-container {
    padding: 0 15px 15px 15px;
  }

  .doodle-canvas-large {
    height: 150px;
  }
}

.doodle-details {
  padding: 1.2rem 1.5rem 1.5rem 1.5rem;
  font-family: 'Merriweather', serif;
  color: #31417A;
}

.doodle-details h4 {
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0 0 0.3rem 0;
  color: #31417A;
  letter-spacing: 0.5px;
}

.doodle-date {
  font-size: 0.95rem;
  color: #666;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.doodle-tags {
  margin-top: 0.5rem;
}

.doodle-tag {
  display: inline-block;
  background: #f7f8fa;
  color: #31417A;
  border-radius: 12px;
  padding: 3px 10px;
  font-size: 0.85rem;
  font-weight: 500;
  margin-right: 0.5rem;
  margin-bottom: 0.2rem;
  border: 1px solid #e0e0e0;
}

.doodle-canvas {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 15px 15px 0 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.doodle-preview-content {
  font-size: 2rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.doodle-footer {
  padding: 10px 15px;
  background: rgba(255, 255, 255, 0.6);
}

.doodle-name {
  color: #333;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.doodle-date {
  color: #666;
  font-size: 0.8rem;
}

/* Task Card */
.task-calendar {
  margin-bottom: 20px;
}

.calendar-header {
  text-align: center;
  margin-bottom: 15px;
}

.calendar-month {
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.5);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
}

.calendar-day {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  padding: 10px;
  text-align: center;
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.calendar-day:hover {
  background: rgba(255, 255, 255, 0.6);
}

.calendar-day.today {
  background: linear-gradient(135deg, #4ecdc4, #45b7d1);
}

.calendar-day.has-tasks {
  border: 2px solid #FF6B6B;
}

.day-number {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.calendar-day.today .day-number {
  color: white;
}

.day-tasks {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 5px;
  padding: 2px 5px;
  font-size: 0.7rem;
  color: #333;
  font-weight: 500;
}

.recent-tasks {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  padding: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.recent-task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-name {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
}

.task-session {
  color: #666;
  font-size: 0.8rem;
  background: rgba(255, 255, 255, 0.6);
  padding: 5px 10px;
  border-radius: 10px;
  font-weight: 500;
}

/* Emotional Card */
.mood-chart {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.mood-day {
  text-align: center;
  flex: 1;
}

.mood-emoji {
  font-size: 2rem;
  margin-bottom: 5px;
  display: block;
}

.mood-date {
  color: #666;
  font-size: 0.7rem;
  font-weight: 500;
}

.summary-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.summary-card {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.summary-topic {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.summary-text {
  color: #555;
  font-size: 0.8rem;
  margin-bottom: 8px;
}

.summary-sentiment {
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.summary-sentiment.positive {
  background: rgba(76, 175, 80, 0.8);
  color: white;
}

.summary-sentiment.neutral {
  background: rgba(255, 193, 61, 0.8);
  color: white;
}

.summary-sentiment.negative {
  background: rgba(244, 67, 54, 0.8);
  color: white;
}

.summary-sentiment.highlighted {
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.transactions-modal.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.health-modal.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.psychometric-modal.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-tasks-modal.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.emotional-modal.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(30, 30, 30, 0.5);
  z-index: 9999;
  display: flex;

  align-items: center;
  justify-content: center;
}

.transactions-popup {
  background: #fff;
  border-radius: 18px;
  max-width: 700px;
  max-height: 700px;
  width: 100vw;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  padding: 0;
  position: relative;
  animation: fadeIn 0.2s;
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 1.5rem 0.5rem 1.5rem;
  font-size: 1.2rem;
  font-weight: bold;
  color: #31417A;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.7rem;
  color: #31417A;
  cursor: pointer;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #ff5252;
}

.popup-body {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

.transaction-list {
  max-height: 300px;
  overflow-y: auto;
}

.transaction-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 1rem;
  padding: 1rem 0;
  border-radius: 10px;
  margin-bottom: 0.5rem;
  border-left: 3px solid transparent;
  background: #f7f8fa;
  color: #31417A;
}

.transaction-item.income {
  background: rgba(76, 175, 80, 0.08);
  color: #388e3c;
  border-left-color: #4CAF50;
}

.transaction-item.expense {
  background: rgba(255, 82, 82, 0.08);
  color: #c62828;
  border-left-color: #ff5252;
}

.transaction-date {
  opacity: 0.8;
  font-size: 0.9rem;
}

.transaction-desc {
  font-weight: bold;
}

.transaction-amount {
  font-weight: bold;
  font-size: 1.1rem;
}

.no-transactions {
  color: #888;
  text-align: center;
  padding: 1.5rem 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }

  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Skills Card */
.skills-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 5px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.skills-grid::-webkit-scrollbar {
  width: 6px;
}

.skills-grid::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.skills-grid::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.skills-grid::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.skill-box {
  background: rgba(255, 255, 255, 0.4);
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  min-height: 60px;
}

.skill-box:hover {
  background: rgba(255, 255, 255, 0.6);
  transform: translateX(3px);
}

.skill-icon {
  font-size: 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 50%;
  padding: 8px;
  min-width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.skill-info {
  flex: 1;
}

.skill-name {
  color: #333;
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 6px;
}

.skill-progress-bar {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  height: 6px;
  overflow: hidden;
  margin-bottom: 4px;
}

.skill-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4ecdc4, #45b7d1);
  border-radius: 8px;
  transition: width 0.3s ease;
}

.skill-progress-text {
  color: #666;
  font-size: 0.75rem;
  font-weight: 600;
}

/* =========================
   FLOATING MAGIC ANIMATION
   ========================= */
.floating-magic {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.magic-element {
  position: absolute;
  font-size: 1.5rem;
  opacity: 0.6;
  animation: float 8s ease-in-out infinite;
  animation-delay: var(--delay);
  left: var(--x);
  top: var(--y);
}

@keyframes float {

  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }

  25% {
    transform: translateY(-20px) rotate(90deg);
  }

  50% {
    transform: translateY(-10px) rotate(180deg);
  }

  75% {
    transform: translateY(-15px) rotate(270deg);
  }
}

/* =========================
   RESPONSIVE DESIGN
   ========================= */
@media (max-width: 1200px) {
  .main-features-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }

  .header-actions {
    flex-wrap: wrap;
    justify-content: center;
  }

  .export-btn,
  .logout-btn {
    padding: 10px 16px;
    font-size: 0.85rem;
    min-width: 120px;
    justify-content: center;
  }

  .child-info {
    order: -1;
    margin-bottom: 10px;
    padding: 10px 20px;
    border-radius: 25px;
  }

  .child-name {
    font-size: 1rem;
    font-weight: 700;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .main-features-grid {
    grid-template-columns: 1fr;
  }

  .health-grid,
  .psychometric-grid,
  .doodle-grid {
    grid-template-columns: 1fr;
  }

  .calendar-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .mood-chart {
    flex-wrap: wrap;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 15px;
  }

  .feature-card {
    min-height: auto;
    padding: 20px;
  }

  .logo-text h1 {
    font-size: 1.5rem;
  }

  .header-actions {
    flex-direction: column;
    gap: 10px;
  }

  .export-btn,
  .logout-btn {
    width: 100%;
    max-width: 200px;
    padding: 12px 16px;
    justify-content: center;
  }

  .date-selector {
    order: -1;
  }
}

.emotional-popup {
  max-width: 80%;
  max-height: 80vh;
  overflow-y: auto;
}

.section-header {
  margin: 20px 0 10px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e1e5e9;
}

.psycho-stats-grid.highlight-style {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
}

.psycho-stat-card {
  background: linear-gradient(135deg, #f8fafc 60%, #e0e7ff 100%);
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(80, 80, 180, 0.10);
  padding: 1.5rem 1.2rem;
  min-width: 220px;
  max-width: 270px;
  margin: 0.5rem;
  text-align: center;
  transition: box-shadow 0.2s;
}

.psycho-stat-card .stat-icon {
  font-size: 2.2rem;
  margin-bottom: 0.5rem;
}

.stat-value.highlight-badge {
  display: inline-block;
  background: linear-gradient(90deg, #6366f1 60%, #a5b4fc 100%);
  color: #fff;
  font-weight: 700;
  font-size: 1.2rem;
  border-radius: 12px;
  padding: 0.3em 1em;
  margin: 0.5em 0;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.10);
}

.trait-tag.highlight-tag {
  background: #fbbf24;
  color: #fff;
  border-radius: 8px;
  padding: 0.2em 0.7em;
  margin: 0.2em;
  font-size: 0.95em;
  font-weight: 600;
  display: inline-block;
}

.progress-bar {
  background: #e5e7eb;
  border-radius: 8px;
  height: 8px;
  margin: 0.5em 0;
  width: 80%;
  margin-left: auto;
  margin-right: auto;
  overflow: hidden;
}

.progress-fill {
  background: linear-gradient(90deg, #34d399, #60a5fa);
  height: 100%;
  border-radius: 8px;
  transition: width 0.4s;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.mood-section,
.topics-section {
  margin-bottom: 20px;
}

.scrollable-section {
  max-height: 650px;
  /* Adjust as needed for your modal size */
  overflow-y: auto;
  padding-right: 8px;
  /* Optional: for scrollbar spacing */
}


.mood-item {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #4CAF50;
}

.mood-date .date-text {
  font-weight: 600;
  color: #495057;
}

.message-count {
  display: block;
  color: #6c757d;
  font-size: 10px;
  margin-top: 2px;
}

.mood-desc {
  flex-grow: 1;
}

.mood-desc strong {
  color: #2c3e50;
  font-size: 14px;
}

.mood-notes {
  margin: 5px 0 0 0;
  font-size: 13px;
  color: #6c757d;
  line-height: 1.4;
}

.mood-emoji {
  font-size: 24px;
  min-width: 40px;
  text-align: center;
}

.topic-item {
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border-left: 4px solid #007bff;
}

.sentiment-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  min-width: 70px;
  text-align: center;
}

.sentiment-badge.positive {
  background-color: #d4edda;
  color: #155724;
}

.sentiment-badge.negative {
  background-color: #f8d7da;
  color: #721c24;
}

.sentiment-badge.neutral {
  background-color: #e2e3e5;
  color: #495057;
}

.topic-desc strong {
  color: #2c3e50;
  font-size: 14px;
}

.topic-summary {
  margin: 5px 0 0 0;
  font-size: 13px;
  color: #6c757d;
  line-height: 1.4;
}

/* User Messages Styling */
.user-messages {
  margin-top: 15px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
}

.messages-header {
  margin-bottom: 10px;
}

.messages-label {
  font-size: 12px;
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
  padding: 4px 8px;
  border-radius: 12px;
}

.user-message-item {
  margin-bottom: 10px;
  background: linear-gradient(135deg, #fff3cd 0%, #fef7e3 100%);
  border: 1px solid #ffeaa7;
  border-radius: 8px;
  padding: 10px;
}

.user-message-item:last-child {
  margin-bottom: 0;
}

.message-content {
  width: 100%;
}

.message-text {
  font-style: italic;
  color: #495057;
  font-size: 13px;
  line-height: 1.4;
  display: block;
  margin-bottom: 6px;
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #6c757d;
}

.message-mood {
  font-weight: 600;
  color: #495057;
}

.message-time {
  font-size: 10px;
  color: #868e96;
}

.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: flex-end;
}

.keyword-tag {
  background-color: #e3f2fd;
  color: #1565c0;
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.no-data-message {
  text-align: center;
  padding: 20px;
  color: #6c757d;
  font-style: italic;
}

.insights-section {
  margin-top: 15px;
}

.insight-card {
  background: linear-gradient(135deg, #f1f3f4 0%, #e8eaf6 100%);
  padding: 15px;
  border-radius: 8px;
  border-left: 4px solid #9c27b0;
}

.insight-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
}

.insight-text.positive {
  color: #2e7d32;
}

.insight-text.negative {
  color: #c62828;
}

.insight-text.neutral {
  color: #5e35b1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .emotional-popup {
    margin: 10px;
    max-width: calc(100vw - 20px);
  }

  .keywords-container {
    justify-content: flex-start;
  }

  .transaction-item {
    flex-direction: column;
    gap: 10px;
  }

  .mood-emoji {
    text-align: left;
  }
}

/* Pills container */
.pill-container {
  padding: 10px 0;
  max-height: 300px;
  overflow-y: auto;
}

/* Pill style */
.pill {
  display: grid;
  grid-template-columns: 100px 1fr 1.2fr 0.8fr;
  /* 👈 Matches header */
  gap: 12px;
  align-items: center;
  background: #f8f9fa;
  margin: 6px 12px;
  padding: 10px 12px;
  border-radius: 12px;
  transition: background 0.2s ease-in-out;
  cursor: default;
}

.pill:hover {
  background: #eef3f7;
}

/* Explicit Column Mapping */
.col-intake {
  grid-column: 1;
}

.col-day {
  grid-column: 2;
}

.col-target {
  grid-column: 3;
}

.col-trend {
  grid-column: 4;
  text-align: right;
}

.pill-count {
  font-size: 1rem;
  font-weight: bold;
  background: #4facfe;
  color: white;
  padding: 6px 10px;
  border-radius: 50%;
  min-width: 28px;
  text-align: center;
  justify-self: start;
}

.pill-date {
  font-size: 0.95rem;
  color: #333;
  font-weight: 500;
}

/* No data style */
.no-data {
  padding: 16px;
  text-align: center;
  color: #777;
}

.pill-target {
  font-size: 0.85rem;
  color: #555;
}

.history-header {
  display: grid;
  grid-template-columns: 100px 1fr 1.2fr 0.8fr;
  /* Ensures alignment */
  gap: 12px;
  background: #f0f4f8;
  padding: 8px 12px;
  font-weight: bold;
  font-size: 0.95rem;
  border-bottom: 2px solid #e0e0e0;
  color: #333;
}

/* Status Colors */
.target-met {
  color: green;
  font-weight: 600;
}

.target-missed {
  color: red;
  font-weight: 600;
}

/* Trend Styles */
.pill-trend {
  font-size: 0.85rem;
}

.trend-up {
  color: green;
}

.trend-down {
  color: red;
}

.trend-same {
  color: gray;
}

.modal-content {
  width: 800px;
  /* or your desired width */
  max-width: 95vw;
  /* for responsiveness */
  background: #fff;
  /* or your modal background */
  border-radius: 12px;
  /* optional */
  padding: 2rem;
  /* optional */
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.2);
  /* optional */
}
</style>