<template>
    <div class="task-tracker-modal">
        <div class="task-tracker-content">
            <div class="task-tracker-header">
                <h2>🎯 My Quests & Tasks</h2>
                <button @click="$emit('close')" class="close-btn">×</button>
            </div>

            <div class="task-tracker-body">
                <div class="task-list-container">
                    <h3>Today's Adventures</h3>
                    <div v-if="tasks.length === 0" class="empty-state">
                        <p>No quests for today. Add a new one!</p>
                    </div>
                    <div v-else class="task-list">
                        <div v-for="task in tasks" :key="task.id" class="task-item" :class="task.status">
                            <div class="task-info">
                                <span class="task-subject">{{ task.subject }}</span>
                                <p class="task-title">{{ task.task }}</p>
                                <div v-if="task.time_spent > 0" class="time-spent">
                                    <span>🕒 {{ task.time_spent }} min spent</span>
                                </div>
                                <!-- Enhanced time analytics -->
                                 <div v-if="task.session_stats" class="session-card">
                                    <div v-if="task.last_work_duration !== undefined" class="session-row">
                                        <span class="session-label">Sessions:</span>
                                        <span class="session-value">{{task.session_stats.total_sessions }}</span>
                                    </div>
                                    <div v-if="task.last_work_duration !== undefined" class="session-row">
                                        <span class="session-label">Work time:</span>
                                        <span class="session-value">{{ task.last_work_duration }} sec</span>
                                    </div>
                                    <div v-if="task.last_work_duration !== undefined" class="session-row">
                                        <span class="session-label">Break Time:</span>
                                        <span class="session-value">{{ task.last_break_duration }} sec</span>
                                    </div>
                                </div>

                                <!-- <div v-if="task.session_stats" class="session-analytics">
                                    <div class="analytics-grid">
                                        <div  v-if="task.last_work_duration !== undefined"  class="analytics-item">
                                            <span class="analytics-label">Sessions:</span>
                                            <span class="analytics-value">{{ task.session_stats.total_sessions }}</span>
                                        </div>
                                        <div v-if="task.last_work_duration !== undefined"  class="analytics-item">
                                            <span class="analytics-label">Work time:</span>
                                            <span class="analytics-value">{{ task.last_work_duration }}sec</span>
                                        </div>
                                        <div  v-if="task.last_work_duration !== undefined"  class="analytics-item">
                                            <span class="analytics-label">Break Time:</span>
                                             <span class="analytics-value">{{ task.last_break_duration }}sec</span>
                                        </div>
                                    </div>
                                </div> -->
                            </div>
                            <div class="task-actions">
                                <span class="task-status">{{ task.status }}</span>

                                <!-- Start Focus Button -->
                                <button v-if="task.status === 'pending' || task.status === 'in-progress'"
                                    @click="startPomodoro(task)" class="action-btn start">
                                    <i class="fas fa-play"></i> Start Focus
                                </button>

                                <!-- Mark In Progress Button -->
                                <button v-if="task.status === 'pending'" @click="updateTaskStatus(task, 'in-progress')"
                                    class="action-btn in-progress">
                                    <i class="fas fa-hourglass-start"></i> In Progress
                                </button>

                                <!-- Mark Done Button -->
                                <button v-if="task.status !== 'completed'" @click="updateTaskStatus(task, 'completed')"
                                    class="action-btn complete">
                                    <i class="fas fa-check"></i> Mark Done
                                </button>

                                <!-- Reset to Pending Button -->
                                <button v-if="task.status === 'in-progress'" @click="updateTaskStatus(task, 'pending')"
                                    class="action-btn reset">
                                    <i class="fas fa-undo"></i> Reset
                                </button>

                                <!-- Remove Task Button (only for student-created tasks) -->
                                <button v-if="!task.assigned_by_teacher" @click="removeTask(task)"
                                    class="action-btn remove">
                                    <i class="fas fa-trash"></i> Remove
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="add-task-container">
                    <h3>Add a New Quest</h3>
                    <form @submit.prevent="addTask">
                        <div class="form-group">
                            <label for="task-title">Quest Title *</label>
                            <input type="text" id="task-title" v-model="newTask.task" required
                                placeholder="Enter your quest title (required)">
                        </div>
                        <div class="form-group">
                            <label for="task-subject">Subject</label>
                            <input type="text" id="task-subject" v-model="newTask.subject"
                                placeholder="e.g., Math, Science, Reading (optional)">
                        </div>
                        <div class="form-group">
                            <label for="task-due-date">Due Date</label>
                            <input type="date" id="task-due-date" v-model="newTask.due_date"
                                :min="new Date().toISOString().split('T')[0]">
                        </div>
                        <button type="submit" class="add-task-btn" :disabled="!newTask.task.trim()">Add Quest</button>
                    </form>
                </div>
            </div>
        </div>

        <PomodoroTimer v-if="showPomodoro" :task="selectedTask" :userId="user.id" @close="showPomodoro = false"
            @session-complete="handleSessionComplete" />
    </div>
</template>

<script>
import { ref, onMounted, defineComponent } from 'vue';
import { apiService } from '@/services/api';
import PomodoroTimer from './PomodoroTimer.vue';

export default defineComponent({
    name: 'TaskTracker',
    components: { PomodoroTimer },
    emits: ['close', 'task-completed'],
    props: {
        user: {
            type: Object,
            required: true,
        },
    },
    setup(props, { emit }) {
        const tasks = ref([]);
        const showPomodoro = ref(false);
        const selectedTask = ref(null);
        const newTask = ref({
            task: '',
            subject: '',
            due_date: '',
        });
const lastSessionStats = ref({ workDuration: 0, breakDuration: 0 });

const fetchLastPomodoroSession = async (userId, homeworkId) => {
    try {
        const response = await apiService.getLastPomodoroSession(userId, homeworkId);
        if (response.success) {
            // Find and update the matching task
            console.log('📥 Last pomodoro session fetched:', response);
            const task = tasks.value.find(t => t.id === homeworkId);
            if (task) {
                task.last_work_duration = response.work_duration;
                task.last_break_duration = response.break_duration;
                console.log(`✅ Updated task ${task.id} with last session data:`, {
                    work_duration: task.last_work_duration,
                    break_duration: task.last_break_duration,
                });
            }
        } else {
            const task = tasks.value.find(t => t.id === homeworkId);
            if (task) {
                task.last_work_duration = 0;
                task.last_break_duration = 0;
            }
        }
    } catch (error) {
        const task = tasks.value.find(t => t.id === homeworkId);
        if (task) {
            task.last_work_duration = 0;
            task.last_break_duration = 0;
        }
        console.error('Error fetching last pomodoro session:', error);
    }
};

   const fetchTasks = async () => {
    try {
        console.log('🔄 Fetching tasks for user:', props.user.id);
        const response = await apiService.getTasks(props.user.id);

        if (response.success) {
            tasks.value = response.tasks;
            console.log('📥 Tasks fetched successfully:', tasks.value);
            // Fetch session stats for each task
            for (const task of tasks.value) {
                await fetchLastPomodoroSession(props.user.id, task.id);
            }

            console.log('✅ Tasks loaded successfully:', tasks.value.length, 'tasks');
        } else {
            console.error('❌ Failed to fetch tasks:', response.error);
            alert('Failed to load tasks: ' + (response.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('❌ Error fetching tasks:', error);
        // error handling same as before...
    }
};

        
        const addTask = async () => {
            try {
                // Validate required fields
                if (!newTask.value.task || !newTask.value.task.trim()) {
                    alert('Please enter a quest title! 📝');
                    return;
                }

                if (!props.user || !props.user.id) {
                    alert('User information is missing. Please try logging in again.');
                    return;
                }

                console.log('🔄 Adding new task...', newTask.value);

                // Filter out empty due_date before sending
                const taskData = {
                    ...newTask.value,
                    user_id: props.user.id,
                };

                // Remove due_date if it's empty
                if (!taskData.due_date || taskData.due_date.trim() === '') {
                    delete taskData.due_date;
                }

                console.log('📤 Sending task data:', taskData);

                const response = await apiService.createTask(taskData);
                console.log('📥 Response received:', response);

                if (response.success) {
                    tasks.value.push(response.task);
                    newTask.value = { task: '', subject: '', due_date: '' }; // Reset form
                    console.log('✅ Task added successfully!');

                } else {
                    console.error('❌ Task creation failed:', response.error);
                    alert('Failed to add quest: ' + (response.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('❌ Error adding task:', error);

                // Show detailed error message
                if (error.response) {
                    console.error('Response error:', error.response.data);
                    alert('Failed to add quest: ' + (error.response.data.error || error.response.data.message || 'Server error'));
                } else if (error.request) {
                    console.error('Request error:', error.request);
                    alert('Failed to add quest: Network error. Please check your connection.');
                } else {
                    console.error('General error:', error.message);
                    alert('Failed to add quest: ' + error.message);
                }
            }
        };

        const updateTaskStatus = async (task, status) => {
            try {
                await apiService.updateTaskStatus(task.id, status);
                task.status = status;
                console.log(`✅ Task ${task.id} status updated to: ${status}`);

                // If task was completed, trigger achievement refresh
                if (status === 'completed') {
                    console.log('🎯 Task completed, refreshing achievements...');
                    // Emit event to parent to refresh achievements
                    emit('task-completed');
                }
            } catch (error) {
                console.error('Error updating task status:', error);
                alert('Failed to update task status. Please try again.');
            }
        };

        const removeTask = async (task) => {
            try {
                // Confirm before removing
                const confirmRemove = confirm(`Are you sure you want to remove the quest "${task.task}"? This action cannot be undone.`);
                if (!confirmRemove) {
                    return;
                }

                console.log('🗑️ Removing task:', task.id);

                const response = await apiService.deleteTask(task.id);

                if (response.success) {
                    // Remove task from local array
                    const taskIndex = tasks.value.findIndex(t => t.id === task.id);
                    if (taskIndex > -1) {
                        tasks.value.splice(taskIndex, 1);
                    }
                    console.log('✅ Task removed successfully!');
                } else {
                    console.error('❌ Task removal failed:', response.error);
                    alert('Failed to remove quest: ' + (response.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('❌ Error removing task:', error);

                // Show detailed error message
                if (error.response) {
                    console.error('Response error:', error.response.data);
                    alert('Failed to remove quest: ' + (error.response.data.error || error.response.data.message || 'Server error'));
                } else if (error.request) {
                    console.error('Request error:', error.request);
                    alert('Failed to remove quest: Network error. Please check your connection.');
                } else {
                    console.error('General error:', error.message);
                    alert('Failed to remove quest: ' + error.message);
                }
            }
        };

        const startPomodoro = async (task) => {
            try {
                const userId = props.user.id
                const homeworkId = task.id

                console.log('✅ Sending to API from TaskTracker:', {
                    user_id: userId,
                    homework_id: homeworkId,
                })

                // Make API call
                //await apiService.startPomodoro(userId, homeworkId)

                // Open PomodoroTimer component
                selectedTask.value = task
                showPomodoro.value = true
            } catch (err) {
                console.error('❌ Failed to start pomodoro session:', err)
                alert('Could not start session. Please try again.')
            }
        }

        const handleSessionComplete = () => {
            fetchTasks();
        };

        onMounted(fetchTasks);

        return {
            tasks,
            showPomodoro,
            selectedTask,
            newTask,
            addTask,
            updateTaskStatus,
            removeTask,
            startPomodoro,
            handleSessionComplete,
        };
    },
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');
.session-card {
  padding: 1rem 1.5rem; /* Extra padding inside */
  margin-top: 1rem; /* Space above */
  margin-bottom: 1rem; /* Space below */
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05); /* Slight transparent background */
  display: flex;
  flex-direction: column;
  gap: 0.5rem; /* Space between rows */
}

.session-row {
  display: flex;
  justify-content: space-between; /* Push text apart */
  font-size: 1rem;
}

.session-label {
  font-weight: 500;
}

.session-value {
  font-weight: bold;
  color: #4da3ff; /* Accent color */
}


.task-tracker-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1001;
    font-family: 'Merriweather', serif;
}

.task-tracker-content {
    background: linear-gradient(145deg, rgba(40, 50, 100, 0.85), rgba(60, 45, 90, 0.9));
    color: white;
    border-radius: 20px;
    width: 90%;
    max-width: 1000px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.task-tracker-header {
    padding: 1.5rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 2.5rem;
    cursor: pointer;
    transition: transform 0.3s, color 0.3s;
}

.close-btn:hover {
    color: #ff6b6b;
    transform: rotate(90deg);
}

.task-tracker-body {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 2rem;
    padding: 2rem;
    overflow: hidden;
    flex: 1;
    min-height: 0;
}

.task-list-container,
.add-task-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.task-list-container h3,
.add-task-container h3 {
    margin-bottom: 1.5rem;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

.task-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    flex-grow: 1;
    overflow-y: auto;
    padding-right: 1rem;
}

/* Custom Scrollbar */
.task-list::-webkit-scrollbar {
    width: 8px;
}

.task-list::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 4px;
}

.task-list::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 4px;
}

.task-list::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
}


.task-item {
    background: rgba(255, 255, 255, 0.08);
    padding: 1rem 1.5rem;
    border-radius: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-left: 6px solid;
    transition: all 0.3s ease;
}

.task-item:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    background: rgba(255, 255, 255, 0.12);
}


.task-item.pending {
    border-left-color: #ffcc4d;
}

.task-item.in-progress {
    border-left-color: #76daff;
}

.task-item.completed {
    border-left-color: #4dff88;
    text-decoration: line-through;
    opacity: 0.7;
}

.task-item.completed .task-title {
    color: #aeb8c4;
}

.task-info {
    flex-grow: 1;
}

.task-subject {
    font-size: 0.8rem;
    color: #b0b8c4;
    text-transform: uppercase;
    font-weight: bold;
    letter-spacing: 0.5px;
}

.task-title {
    margin: 0.25rem 0;
    font-size: 1.1rem;
    font-weight: 600;
}

.time-spent {
    font-size: 0.8rem;
    color: #99aab5;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    margin-top: 0.5rem;
}

.task-actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.8rem;
    flex-shrink: 0;
    min-width: 200px;
}

.task-status {
    font-style: italic;
    color: #b0b8c4;
    font-size: 0.85rem;
    text-transform: capitalize;
    background: rgba(255, 255, 255, 0.1);
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 0.5rem;
}

.action-btn,
.add-task-btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    font-family: 'Merriweather', serif;
    color: white;
    transition: all 0.3s ease;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.2);
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    white-space: nowrap;
    min-width: 130px;
}

.action-btn:hover,
.add-task-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.add-task-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #ccc !important;
}

.add-task-btn:disabled:hover {
    transform: none;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.action-btn.start {
    background: linear-gradient(135deg, #667eea, #764ba2);
}

.action-btn.in-progress {
    background: linear-gradient(135deg, #76daff, #4facfe);
}

.action-btn.complete {
    background: linear-gradient(135deg, #43b581, #389e70);
}

.action-btn.reset {
    background: linear-gradient(135deg, #ffcc4d, #f39c12);
}

.action-btn.remove {
    background: linear-gradient(135deg, #ff6b6b, #ee5a52);
}

.action-btn.remove:hover {
    background: linear-gradient(135deg, #ff5252, #d32f2f);
}

.add-task-container {
    padding-left: 2rem;
    border-left: 1px solid rgba(255, 255, 255, 0.1);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
    opacity: 0.8;
}

.form-group input {
    width: 100%;
    padding: 0.8rem;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    background: rgba(0, 0, 0, 0.2);
    color: white;
    font-family: 'Merriweather', serif;
    transition: all 0.3s ease;
}

.form-group input:focus {
    outline: none;
    border-color: #76daff;
    box-shadow: 0 0 15px rgba(118, 218, 255, 0.3);
}

.add-task-btn {
    width: 100%;
    padding: 1rem;
    border-radius: 8px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    font-size: 1rem;
}

.empty-state {
    text-align: center;
    padding: 3rem;
    margin-top: 2rem;
    opacity: 0.7;
}

.empty-state p {
    font-size: 1.1rem;
}

.task-name {
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.task-description {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

/* Session Analytics Styles */
.session-analytics {
    margin-top: 0.8rem;
    padding: 0.8rem;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.analytics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
}

.analytics-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 0;
}

.analytics-label {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.7);
    padding: 0%;
}

.analytics-value {
    font-size: 0.9rem;
    font-weight: bold;
    color: #4facfe;
}

/* Responsive Design */
@media (max-width: 768px) {
    .task-tracker-body {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .analytics-grid {
        grid-template-columns: 1fr;
    }

    .task-item {
        flex-direction: column;
        align-items: stretch;
        gap: 1rem;
    }

    .task-actions {
        align-items: stretch;
        min-width: auto;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.5rem;
    }

    .action-btn {
        flex: 1;
        min-width: 120px;
        justify-content: center;
    }

    .task-status {
        order: -1;
        align-self: center;
        margin-bottom: 0.8rem;
    }
}
</style>