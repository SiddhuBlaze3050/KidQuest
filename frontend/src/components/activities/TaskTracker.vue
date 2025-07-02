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
                            </div>
                            <div class="task-actions">
                                <span class="task-status">{{ task.status }}</span>
                                <button v-if="task.status === 'pending' || task.status === 'in-progress'"
                                    @click="startPomodoro(task)" class="action-btn start">
                                    Start Focus
                                </button>
                                <button v-if="task.status !== 'completed'" @click="updateTaskStatus(task, 'completed')"
                                    class="action-btn complete">
                                    Mark Done
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="add-task-container">
                    <h3>Add a New Quest</h3>
                    <form @submit.prevent="addTask">
                        <div class="form-group">
                            <label for="task-title">Quest Title</label>
                            <input type="text" id="task-title" v-model="newTask.task" required>
                        </div>
                        <div class="form-group">
                            <label for="task-subject">Subject</label>
                            <input type="text" id="task-subject" v-model="newTask.subject">
                        </div>
                        <div class="form-group">
                            <label for="task-due-date">Due Date</label>
                            <input type="date" id="task-due-date" v-model="newTask.due_date">
                        </div>
                        <button type="submit" class="add-task-btn">Add Quest</button>
                    </form>
                </div>
            </div>
        </div>

        <PomodoroTimer v-if="showPomodoro" :task="selectedTask" @close="showPomodoro = false"
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

        const fetchTasks = async () => {
            try {
                const response = await apiService.getTasks(props.user.id);
                if (response.success) {
                    tasks.value = response.tasks;
                }
            } catch (error) {
                console.error('Error fetching tasks:', error);
            }
        };

        const addTask = async () => {
            try {
                const response = await apiService.createTask({
                    ...newTask.value,
                    user_id: props.user.id,
                });
                if (response.success) {
                    tasks.value.push(response.task);
                    newTask.value = { task: '', subject: '', due_date: '' }; // Reset form
                }
            } catch (error) {
                console.error('Error adding task:', error);
            }
        };

        const updateTaskStatus = async (task, status) => {
            try {
                await apiService.updateTaskStatus(task.id, status);
                task.status = status;
            } catch (error) {
                console.error('Error updating task status:', error);
            }
        };

        const startPomodoro = (task) => {
            selectedTask.value = task;
            showPomodoro.value = true;
        };

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
            startPomodoro,
            handleSessionComplete,
        };
    },
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&display=swap');

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
    align-items: center;
    gap: 1rem;
    flex-shrink: 0;
}

.task-status {
    font-style: italic;
    color: #b0b8c4;
    font-size: 0.9rem;
    text-transform: capitalize;
}

.action-btn,
.add-task-btn {
    padding: 0.6rem 1.2rem;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-weight: bold;
    font-family: 'Merriweather', serif;
    color: white;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.action-btn:hover,
.add-task-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.action-btn.start {
    background: linear-gradient(135deg, #667eea, #764ba2);
}

.action-btn.complete {
    background: linear-gradient(135deg, #43b581, #389e70);
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
</style>