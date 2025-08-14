<template>
    <div class="enhanced-chatbot" @click="closeModal">
        <div class="chatbot-container" @click.stop>
            <!-- Header with session controls -->
            <div class="chat-header">
                <div class="bot-info">
                    <h3>{{ botCharacter.name }}</h3>
                    <p>{{ botCharacter.description }}</p>
                    <div class="emotion-indicator">
                        <span class="emotion-label">Mood:</span>
                        <span class="emotion-value" :class="`emotion-${currentEmotion}`">
                            {{ getEmotionLabel(currentEmotion) }} {{ getEmotionEmoji(currentEmotion) }}
                        </span>
                    </div>
                </div>
                
                <!-- Session Controls -->
                <div class="session-controls">
                    <button @click="toggleSessionHistory" class="session-btn" title="Chat History">
                        📚
                    </button>
                    <button @click="startNewSession" class="session-btn" title="New Chat">
                        ➕
                    </button>
                    <button @click="$emit('close')" class="close-btn">&times;</button>
                </div>
            </div>

            <!-- Session History Sidebar -->
            <div v-if="showSessionHistory" class="session-sidebar">
                <div class="session-header">
                    <h4>Chat History</h4>
                    <button @click="showSessionHistory = false" class="close-sidebar">×</button>
                </div>
                <div class="session-list">
                    <div v-for="session in sessions" :key="session.id" 
                         @click="loadSession(session.id)" 
                         class="session-item"
                         :class="{ active: session.id === currentSessionId }">
                        <div class="session-date">{{ formatSessionDate(session.updated_at) }}</div>
                        <div class="session-preview">{{ session.last_message_preview }}</div>
                        <div class="session-meta">
                            <span class="interaction-count">{{ session.interaction_count }} msgs</span>
                            <span v-if="session.mood_tag" class="mood-tag">{{ session.mood_tag }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Chat Messages Area -->
            <div class="chat-messages" ref="messagesContainer" :class="{ 'with-sidebar': showSessionHistory }">
                <!-- Welcome Message -->
                <div class="welcome-message">
                    <div class="message-bubble bot-message">
                        <div class="message-avatar">
                            <div class="mini-bot">🧙‍♂️</div>
                        </div>
                        <div class="message-content">
                            <p>{{ botCharacter.welcomeMessage }}</p>
                            <div class="message-time">{{ getCurrentTime() }}</div>
                        </div>
                    </div>
                </div>

                <!-- Chat History -->
                <div v-for="message in messages" :key="message.id" class="message-wrapper"
                    :class="{ 'user-wrapper': message.sender === 'user' }">
                    <div class="message-bubble" :class="{
                        'user-message': message.sender === 'user',
                        'bot-message': message.sender === 'assistant'
                    }">
                        <div v-if="message.sender === 'assistant'" class="message-avatar">
                            <div class="mini-bot" :class="`emotion-${getMessageEmotion(message.message)}`">
                                {{ getEmotionEmoji(getMessageEmotion(message.message)) }}
                            </div>
                        </div>
                        <div class="message-content">
                            <p>{{ message.message }}</p>
                            <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                        </div>
                    </div>
                </div>

                <!-- Typing Indicator -->
                <div v-if="isTyping" class="message-wrapper">
                    <div class="message-bubble bot-message typing">
                        <div class="message-avatar">
                            <div class="mini-bot thinking">🤔</div>
                        </div>
                        <div class="typing-content">
                            <div class="typing-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                            <div class="typing-text">{{ botCharacter.name }} is thinking deeply...</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Input Area -->
            <div class="chat-input">
                <form @submit.prevent="sendMessage" class="input-form">
                    <div class="input-wrapper">
                        <input v-model="newMessage" type="text" :placeholder="inputPlaceholder" class="message-input"
                            :disabled="isTyping" ref="messageInput" @focus="onInputFocus" @blur="onInputBlur" />
                        <div class="input-suggestions" v-if="showSuggestions && suggestions.length > 0">
                            <button v-for="suggestion in suggestions" :key="suggestion"
                                @click="selectSuggestion(suggestion)" class="suggestion-btn" type="button">
                                {{ suggestion }}
                            </button>
                        </div>
                    </div>
                    <button type="submit" class="send-btn" :disabled="!newMessage.trim() || isTyping">
                        <span class="send-icon">🚀</span>
                    </button>
                </form>

                <!-- Quick Actions -->
                <div class="quick-actions">
                    <button v-for="action in quickActions" :key="action.id" @click="sendQuickMessage(action.message)"
                        class="quick-action-btn" :disabled="isTyping">
                        <span class="action-icon">{{ action.icon }}</span>
                        <span class="action-label">{{ action.label }}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { apiService } from '@/services/api'
import { getEmotionFromKeywords } from '@/utils/emotionDetection'
import Swal from 'sweetalert2'

export default {
    name: 'EnhancedChatBot',
    props: {
        user: {
            type: Object,
            default: () => ({ id: 1, username: 'Adventurer' })
        }
    },
    emits: ['close'],
    setup(props, { emit }) {
        // Reactive data
        const messages = ref([])
        const newMessage = ref('')
        const isTyping = ref(false)
        const currentEmotion = ref('neutral')
        const showSuggestions = ref(false)
        const messagesContainer = ref(null)
        const messageInput = ref(null)
        
        // Session management
        const currentSessionId = ref(null)
        const sessions = ref([])
        const showSessionHistory = ref(false)

        // Bot configuration
        const botCharacterData = {
            name: 'Gandalf the Wise',
            description: 'Your magical guide through life skills adventures',
            welcomeMessage: `Greetings, ${props.user.username}! I am Gandalf, your wise companion on this quest to master life's essential skills. What knowledge do you seek today? 🧙‍♂️✨`
        }

        // Input suggestions
        const suggestions = ref([
            'How can I manage my time better?',
            'Tips for staying organized',
            'Help with homework planning',
            'How to build good habits?'
        ])

        // Quick actions
        const quickActions = [
            { id: 1, icon: '⏰', label: 'Time Tips', message: 'Give me some time management tips' },
            { id: 2, icon: '📚', label: 'Study Help', message: 'How can I study more effectively?' },
            { id: 3, icon: '💧', label: 'Health', message: 'Remind me about healthy habits' },
            { id: 4, icon: '😊', label: 'Mood', message: 'I want to talk about my feelings' }
        ]

        // Computed properties
        const inputPlaceholder = computed(() => {
            const placeholders = {
                happy: 'Share your excitement with me! 🌟',
                sad: 'Tell me what\'s on your mind... 💙',
                angry: 'Let\'s talk through what\'s bothering you... 🔥',
                fear: 'Share your concerns, I\'m here to help... 🛡️',
                surprise: 'Tell me what amazed you! ⚡',
                love: 'Share what makes your heart happy... 💖',
                excited: 'What adventure shall we explore? 🚀',
                disgusted: 'Let\'s work through what\'s troubling you... 🌿',
                thinking: 'Let\'s ponder together... 🤔',
                confident: 'Share your victories and strengths! 💪',
                tired: 'Rest your thoughts with me... 😴',
                neutral: 'Share your quest for knowledge with me... ✨'
            }
            return placeholders[currentEmotion.value] || placeholders.neutral
        })

        // Emotion detection and mapping
        const emotionKeywords = {
            happy: ['happy', 'great', 'awesome', 'amazing', 'wonderful', 'excited', 'joy', 'smile', 'laugh', 'cheerful', 'delighted', 'pleased', 'glad', 'thrilled'],
            sad: ['sad', 'upset', 'down', 'depressed', 'cry', 'hurt', 'lonely', 'worried', 'anxious', 'disappointed', 'heartbroken', 'miserable', 'gloomy', 'melancholy'],
            angry: ['angry', 'mad', 'furious', 'rage', 'hate', 'annoyed', 'irritated', 'frustrated', 'pissed', 'outraged', 'livid', 'enraged', 'bitter', 'resentful', 'hostile'],
            fear: ['scared', 'afraid', 'terrified', 'frightened', 'nervous', 'worried', 'anxious', 'panic', 'terror', 'fearful', 'petrified', 'alarmed', 'apprehensive'],
            surprise: ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'confused', 'unexpected', 'wow', 'omg', 'unbelievable', 'incredible'],
            love: ['love', 'adore', 'cherish', 'affection', 'romantic', 'crush', 'heart', 'valentine', 'care', 'devoted', 'passionate', 'tender', 'fond'],
            excited: ['excited', 'pump', 'energy', 'amazing', 'fantastic', 'incredible', 'enthusiastic', 'eager', 'hyped', 'pumped', 'stoked', 'thrilled'],
            disgusted: ['disgusted', 'gross', 'yuck', 'eww', 'sick', 'revolting', 'nasty', 'repulsive', 'awful', 'terrible', 'horrible'],
            thinking: ['think', 'wonder', 'question', 'curious', 'understand', 'learn', 'study', 'ponder', 'contemplate', 'reflect', 'consider', 'analyze'],
            confident: ['confident', 'sure', 'certain', 'positive', 'determined', 'brave', 'bold', 'strong', 'powerful', 'capable', 'skilled', 'accomplished'],
            tired: ['tired', 'exhausted', 'sleepy', 'weary', 'drained', 'fatigued', 'worn out', 'drowsy', 'sluggish', 'lethargic'],
            neutral: ['okay', 'fine', 'normal', 'regular', 'usual', 'alright', 'average', 'moderate']
        }

        // Methods
        const getMessageEmotion = (message) => {
            return getEmotionFromKeywords(message.toLowerCase(), emotionKeywords)
        }

        const getEmotionLabel = (emotion) => {
            const labels = {
                happy: 'Joyful',
                sad: 'Thoughtful',
                angry: 'Fiery',
                fear: 'Cautious',
                surprise: 'Amazed',
                love: 'Loving',
                excited: 'Energetic',
                disgusted: 'Disturbed',
                thinking: 'Pondering',
                confident: 'Bold',
                tired: 'Weary',
                neutral: 'Balanced'
            }
            return labels[emotion] || 'Balanced'
        }

        const getEmotionEmoji = (emotion) => {
            const emojis = {
                happy: '😊',
                sad: '😢',
                angry: '😠',
                fear: '😨',
                surprise: '😲',
                love: '😍',
                excited: '🤩',
                disgusted: '🤢',
                thinking: '🤔',
                confident: '😎',
                tired: '😴',
                neutral: '😌'
            }
            return emojis[emotion] || '😌'
        }

        // Session management methods
        const loadChatHistory = async () => {
            try {
                const response = await apiService.getChatHistory(props.user?.id || 1)
                if (response.success) {
                    messages.value = response.messages.map((msg, index) => ({
                        ...msg,
                        id: msg.id || index + 1
                    }))
                    
                    // Set current session ID from latest message
                    if (messages.value.length > 0) {
                        const latestMessage = messages.value[messages.value.length - 1]
                        currentSessionId.value = latestMessage.session_id
                        
                        // Update emotion based on latest message
                        if (latestMessage.mood) {
                            currentEmotion.value = latestMessage.mood
                        } else if (latestMessage.sender === 'user') {
                            // Detect emotion from user's latest message
                            const detectedEmotion = getMessageEmotion(latestMessage.message)
                            currentEmotion.value = detectedEmotion
                        }
                        console.log('Updated emotion from chat history:', currentEmotion.value)
                    }
                }
            } catch (error) {
                console.error('Failed to load chat history:', error)
            }
        }

        const loadChatSessions = async () => {
            try {
                const response = await apiService.getChatSessions(props.user?.id || 1)
                if (response.success) {
                    sessions.value = response.sessions
                }
            } catch (error) {
                console.error('Failed to load chat sessions:', error)
            }
        }

        const loadSession = async (sessionId) => {
            try {
                const response = await apiService.getSession(sessionId)
                if (response.success) {
                    messages.value = response.session.messages.map((msg, index) => ({
                        ...msg,
                        id: msg.id || index + 1
                    }))
                    currentSessionId.value = sessionId
                    showSessionHistory.value = false
                    
                    // Update emotion based on latest message in session
                    if (messages.value.length > 0) {
                        const latestMessage = messages.value[messages.value.length - 1]
                        if (latestMessage.mood) {
                            currentEmotion.value = latestMessage.mood
                        } else if (latestMessage.sender === 'user') {
                            // Detect emotion from user's latest message
                            const detectedEmotion = getMessageEmotion(latestMessage.message)
                            currentEmotion.value = detectedEmotion
                        }
                        console.log('Updated emotion from session:', currentEmotion.value)
                    }
                    
                    scrollToBottom()
                }
            } catch (error) {
                console.error('Failed to load session:', error)
            }
        }

        const startNewSession = () => {
            messages.value = []
            currentSessionId.value = null // This will force creation of new session
            showSessionHistory.value = false
            newMessage.value = ''
            currentEmotion.value = 'neutral'
        }

        const toggleSessionHistory = () => {
            showSessionHistory.value = !showSessionHistory.value
            if (showSessionHistory.value) {
                loadChatSessions()
            }
        }

        const formatSessionDate = (dateString) => {
            return new Date(dateString).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            })
        }

        // Core chat methods
        const sendMessage = async () => {
            if (!newMessage.value.trim() || isTyping.value) return

            const userMessage = newMessage.value.trim()
            
            // Immediately detect emotion from user message
            const detectedEmotion = getMessageEmotion(userMessage)
            currentEmotion.value = detectedEmotion
            console.log('Immediate emotion detection:', detectedEmotion)
            
            newMessage.value = ''
            showSuggestions.value = false

            // Add user message to local state immediately
            const tempUserMsg = {
                id: Date.now(),
                message: userMessage,
                sender: 'user',
                timestamp: new Date().toISOString(),
                session_id: currentSessionId.value
            }
            messages.value.push(tempUserMsg)

            scrollToBottom()
            isTyping.value = true

            try {
                const response = await apiService.sendMessage(
                    userMessage, 
                    props.user?.id || 1, 
                    currentSessionId.value
                )

                if (response.success) {
                    // Update session ID for future messages
                    if (response.session_id) {
                        currentSessionId.value = response.session_id
                    }

                    // Use mood detected by LLM instead of client-side detection
                    if (response.mood) {
                        currentEmotion.value = response.mood
                        console.log('LLM detected mood:', response.mood)
                    } else {
                        // Fallback: detect emotion from user's message if LLM didn't provide mood
                        const detectedEmotion = getMessageEmotion(userMessage)
                        currentEmotion.value = detectedEmotion
                        console.log('Client-side detected emotion:', detectedEmotion)
                    }

                    // Add bot response
                    messages.value.push({
                        id: Date.now() + 1,
                        message: response.response,
                        sender: 'assistant',
                        timestamp: response.timestamp,
                        session_id: currentSessionId.value,
                        mood: response.mood
                    })
                }
            } catch (error) {
                console.error('Failed to send message:', error)

                await Swal.fire({
                    icon: 'error',
                    title: 'Connection Troubled! 🌫️',
                    text: 'The magical pathways seem clouded. Let\'s try again!',
                    timer: 2000,
                    showConfirmButton: false,
                    background: 'linear-gradient(135deg, #ff6b6b, #ffa726)',
                    color: 'white'
                })

                // Add fallback message
                messages.value.push({
                    id: Date.now() + 1,
                    message: "My apologies, young friend. The paths between realms seem troubled. Perhaps we might try again? Even wisdom faces challenges on its journey. 🧙‍♂️✨",
                    sender: 'assistant',
                    timestamp: new Date().toISOString(),
                    session_id: currentSessionId.value
                })

                currentEmotion.value = 'thinking'
            } finally {
                isTyping.value = false
                scrollToBottom()
            }
        }

        const sendQuickMessage = (message) => {
            newMessage.value = message
            sendMessage()
        }

        const selectSuggestion = (suggestion) => {
            newMessage.value = suggestion
            showSuggestions.value = false
            // Automatically send the suggestion
            nextTick(() => {
                sendMessage()
            })
        }

        const scrollToBottom = () => {
            nextTick(() => {
                if (messagesContainer.value) {
                    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
                }
            })
        }

        const onInputFocus = () => {
            showSuggestions.value = !newMessage.value.trim()
        }

        const onInputBlur = () => {
            // Delay to allow suggestion clicks
            setTimeout(() => {
                showSuggestions.value = false
            }, 200)
        }

        const closeModal = () => {
            emit('close')
        }

        const getCurrentTime = () => {
            return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }

        const formatTime = (timestamp) => {
            return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }

        // Watchers
        watch(messages, (newMessages, oldMessages) => {
            scrollToBottom()
            
            // Update emotion based on latest user message
            if (newMessages.length > oldMessages?.length) {
                const latestMessage = newMessages[newMessages.length - 1]
                if (latestMessage.sender === 'user') {
                    // Only detect emotion from user messages, not bot responses
                    const detectedEmotion = getMessageEmotion(latestMessage.message)
                    if (detectedEmotion !== currentEmotion.value) {
                        currentEmotion.value = detectedEmotion
                        console.log('Emotion updated from new user message:', detectedEmotion)
                    }
                }
                // If it's a bot message with mood, use that
                else if (latestMessage.sender === 'assistant' && latestMessage.mood) {
                    currentEmotion.value = latestMessage.mood
                    console.log('Emotion updated from bot response mood:', latestMessage.mood)
                }
            }
        }, { deep: true })

        watch(currentEmotion, (newEmotion) => {
            console.log('Emotion changed to:', newEmotion)
            // Update suggestions based on emotion
            updateSuggestions(newEmotion)
        })

        const updateSuggestions = (emotion) => {
            const emotionSuggestions = {
                happy: [
                    'Tell me about something that made you happy!',
                    'What are you excited about?',
                    'Share your good news with me!'
                ],
                sad: [
                    'What\'s been bothering you?',
                    'How can I help you feel better?',
                    'Want to talk about it?'
                ],
                angry: [
                    'What happened that upset you?',
                    'Tell me what\'s making you angry',
                    'How can we work through this frustration?'
                ],
                fear: [
                    'What are you worried about?',
                    'Tell me about your concerns',
                    'How can I help you feel safer?'
                ],
                surprise: [
                    'What surprised you today?',
                    'Tell me about this amazing thing!',
                    'What caught you off guard?'
                ],
                love: [
                    'Tell me about someone special',
                    'What do you love most?',
                    'Share something that makes you feel loved'
                ],
                excited: [
                    'What adventure are you planning?',
                    'Tell me about your goals!',
                    'What skills do you want to learn?'
                ],
                disgusted: [
                    'What\'s bothering you?',
                    'Tell me what seems wrong',
                    'How can we fix this situation?'
                ],
                thinking: [
                    'What\'s on your mind?',
                    'Help me understand something',
                    'I have a question about...'
                ],
                confident: [
                    'Tell me about your achievements!',
                    'What are you proud of?',
                    'Share your success story'
                ],
                tired: [
                    'How can I help you relax?',
                    'What\'s been exhausting you?',
                    'Want some rest and comfort tips?'
                ],
                neutral: [
                    'How can I help you today?',
                    'What would you like to learn?',
                    'Tell me about your day'
                ]
            }

            suggestions.value = emotionSuggestions[emotion] || emotionSuggestions.neutral
        }

        // Lifecycle
        onMounted(() => {
            loadChatHistory()
            loadChatSessions()

            nextTick(() => {
                if (messageInput.value) {
                    messageInput.value.focus()
                }
            })
        })

        return {
            // Refs
            messages,
            newMessage,
            isTyping,
            currentEmotion,
            showSuggestions,
            suggestions,
            messagesContainer,
            messageInput,
            
            // Session management
            currentSessionId,
            sessions,
            showSessionHistory,

            // Data
            botCharacter: botCharacterData,
            quickActions,

            // Computed
            inputPlaceholder,

            // Methods
            sendMessage,
            sendQuickMessage,
            selectSuggestion,
            onInputFocus,
            onInputBlur,
            closeModal,
            getCurrentTime,
            formatTime,
            getMessageEmotion,
            getEmotionLabel,
            getEmotionEmoji,
            
            // Session methods
            loadSession,
            startNewSession,
            toggleSessionHistory,
            formatSessionDate
        }
    }
}
</script>

<style scoped>
.enhanced-chatbot {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
    backdrop-filter: blur(10px);
}

.chatbot-container {
    background: linear-gradient(135deg, #2c1810, #8b4513);
    border-radius: 25px;
    width: 90%;
    max-width: 900px;
    height: 85vh;
    display: flex;
    flex-direction: column;
    animation: modalSlideIn 0.4s ease-out;
    border: 3px solid #daa520;
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
    overflow: hidden;
    position: relative;
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translateY(-50px) scale(0.9);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

/* Header */
.chat-header {
    background: linear-gradient(135deg, #8b4513, #daa520);
    color: white;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    position: relative;
    border-bottom: 2px solid #daa520;
}

.bot-info {
    flex: 1;
}

.bot-info h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-family: 'Times New Roman', serif;
}

.bot-info p {
    margin: 0 0 0.5rem 0;
    opacity: 0.9;
    font-size: 0.95rem;
}

.emotion-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
}

.emotion-label {
    opacity: 0.8;
}

.emotion-value {
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.2);
    font-weight: 600;
    transition: all 0.3s ease;
}

/* Emotion-specific colors */
.emotion-value.emotion-happy {
    background: rgba(255, 215, 0, 0.3);
    color: #fff200;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.2);
}

.emotion-value.emotion-sad {
    background: rgba(100, 149, 237, 0.3);
    color: #6495ed;
    box-shadow: 0 0 10px rgba(100, 149, 237, 0.2);
}

.emotion-value.emotion-angry {
    background: rgba(255, 69, 0, 0.3);
    color: #ff4500;
    box-shadow: 0 0 10px rgba(255, 69, 0, 0.2);
}

.emotion-value.emotion-fear {
    background: rgba(138, 43, 226, 0.3);
    color: #8a2be2;
    box-shadow: 0 0 10px rgba(138, 43, 226, 0.2);
}

.emotion-value.emotion-surprise {
    background: rgba(255, 20, 147, 0.3);
    color: #ff1493;
    box-shadow: 0 0 10px rgba(255, 20, 147, 0.2);
}

.emotion-value.emotion-love {
    background: rgba(255, 105, 180, 0.3);
    color: #ff69b4;
    box-shadow: 0 0 10px rgba(255, 105, 180, 0.2);
}

.emotion-value.emotion-excited {
    background: rgba(255, 165, 0, 0.3);
    color: #ffa500;
    box-shadow: 0 0 10px rgba(255, 165, 0, 0.2);
}

.emotion-value.emotion-disgusted {
    background: rgba(128, 128, 0, 0.3);
    color: #808000;
    box-shadow: 0 0 10px rgba(128, 128, 0, 0.2);
}

.emotion-value.emotion-thinking {
    background: rgba(70, 130, 180, 0.3);
    color: #4682b4;
    box-shadow: 0 0 10px rgba(70, 130, 180, 0.2);
}

.emotion-value.emotion-confident {
    background: rgba(50, 205, 50, 0.3);
    color: #32cd32;
    box-shadow: 0 0 10px rgba(50, 205, 50, 0.2);
}

.emotion-value.emotion-tired {
    background: rgba(105, 105, 105, 0.3);
    color: #696969;
    box-shadow: 0 0 10px rgba(105, 105, 105, 0.2);
}

.emotion-value.emotion-neutral {
    background: rgba(255, 255, 255, 0.2);
    color: white;
}

/* Session Controls */
.session-controls {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.session-btn {
    background: rgba(255, 255, 255, 0.2);
    border: none;
    color: white;
    width: 35px;
    height: 35px;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    z-index: 5;
}

.session-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.05);
}

.close-btn {
    background: none;
    border: none;
    font-size: 2rem;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 5;
}

.close-btn:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: rotate(90deg);
}

/* Session Sidebar */
.session-sidebar {
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    height: 100%;
    background: rgba(46, 38, 70, 0.98);
    border-left: 2px solid #daa520;
    z-index: 10;
    display: flex;
    flex-direction: column;
    animation: slideInRight 0.3s ease-out;
}

@keyframes slideInRight {
    from {
        transform: translateX(100%);
    }
    to {
        transform: translateX(0);
    }
}

.session-header {
    padding: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.session-header h4 {
    margin: 0;
    color: #daa520;
    font-size: 1.1rem;
}

.close-sidebar {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
}

.session-list {
    flex: 1;
    overflow-y: auto;
    padding: 0.5rem;
}

.session-item {
    padding: 1rem;
    margin-bottom: 0.5rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.session-item:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateX(5px);
}

.session-item.active {
    background: rgba(218, 165, 32, 0.3);
    border-color: #daa520;
}

.session-date {
    font-size: 0.8rem;
    color: #daa520;
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.session-preview {
    font-size: 0.9rem;
    color: white;
    margin-bottom: 0.5rem;
    line-height: 1.3;
}

.session-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.75rem;
}

.interaction-count {
    color: rgba(255, 255, 255, 0.7);
}

.mood-tag {
    background: rgba(218, 165, 32, 0.3);
    color: #daa520;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-weight: 600;
}

/* Chat Messages Area */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    min-height: 300px;
    transition: margin-right 0.3s ease;
}

.chat-messages.with-sidebar {
    margin-right: 300px;
}

.message-wrapper {
    margin-bottom: 1.5rem;
    display: flex;
}

.user-wrapper {
    justify-content: flex-end;
}

.message-bubble {
    max-width: 70%;
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.user-message {
    flex-direction: row-reverse;
}

.message-avatar {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #8b4513, #daa520);
    font-size: 1.2rem;
}

.mini-bot {
    font-size: 1.2rem;
    animation: float 2s ease-in-out infinite;
}

.mini-bot.thinking {
    animation: pulse 1s ease-in-out infinite;
}

@keyframes float {
    0%, 100% {
        transform: translateY(0);
    }
    50% {
        transform: translateY(-2px);
    }
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.1);
    }
}

.message-content {
    flex: 1;
    padding: 1rem 1.5rem;
    border-radius: 20px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
}

.bot-message .message-content {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(218, 165, 32, 0.1));
    color: #333;
    border-bottom-left-radius: 8px;
}

.user-message .message-content {
    background: linear-gradient(135deg, #8b4513, #daa520);
    color: white;
    border-bottom-right-radius: 8px;
}

.message-content p {
    margin: 0;
    line-height: 1.5;
    font-size: 0.95rem;
}

.message-time {
    font-size: 0.75rem;
    opacity: 0.7;
    margin-top: 0.5rem;
    text-align: right;
}

.bot-message .message-time {
    text-align: left;
}

.welcome-message {
    text-align: center;
    margin-bottom: 2rem;
}

.welcome-message .message-bubble {
    max-width: 100%;
    justify-content: center;
}

.welcome-message .message-content {
    background: linear-gradient(135deg, #8b4513, #daa520);
    color: white;
    border-radius: 15px;
    border: 2px solid rgba(255, 255, 255, 0.3);
}

/* Typing indicator */
.typing .message-content {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(218, 165, 32, 0.1)) !important;
    padding: 1rem 1.5rem !important;
}

.typing-content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.typing-dots {
    display: flex;
    gap: 0.5rem;
    align-items: center;
}

.typing-dots span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #daa520;
    animation: typingPulse 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) {
    animation-delay: -0.32s;
}

.typing-dots span:nth-child(2) {
    animation-delay: -0.16s;
}

@keyframes typingPulse {
    0%, 80%, 100% {
        opacity: 0.3;
        transform: scale(0.8);
    }
    40% {
        opacity: 1;
        transform: scale(1);
    }
}

.typing-text {
    font-size: 0.85rem;
    color: #8b4513;
    font-style: italic;
}

/* Input area */
.chat-input {
    padding: 1.5rem;
    background: linear-gradient(135deg, #2c1810, #8b4513);
    border-top: 2px solid #daa520;
}

.input-form {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
}

.input-wrapper {
    flex: 1;
    position: relative;
}

.message-input {
    width: 100%;
    padding: 1rem 1.5rem;
    border: 2px solid #daa520;
    border-radius: 25px;
    font-size: 1rem;
    outline: none;
    transition: all 0.3s ease;
    background: rgba(255, 255, 255, 0.95);
    color: #333;
    box-sizing: border-box;
}

.message-input:focus {
    border-color: #ffeda7;
    box-shadow: 0 0 15px rgba(218, 165, 32, 0.3);
    background: white;
}

.message-input:disabled {
    background: rgba(255, 255, 255, 0.7);
    opacity: 0.7;
}

.input-suggestions {
    position: absolute;
    bottom: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 2px solid #daa520;
    border-bottom: none;
    border-radius: 15px 15px 0 0;
    max-height: 150px;
    overflow-y: auto;
    z-index: 10;
}

.suggestion-btn {
    width: 100%;
    padding: 0.75rem 1rem;
    border: none;
    background: none;
    text-align: left;
    cursor: pointer;
    transition: background 0.2s ease;
    color: #333;
    font-size: 0.9rem;
}

.suggestion-btn:hover {
    background: rgba(218, 165, 32, 0.1);
}

.send-btn {
    width: 55px;
    height: 55px;
    border: none;
    border-radius: 50%;
    background: linear-gradient(135deg, #daa520, #ffeda7);
    color: #8b4513;
    font-size: 1.3rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    z-index: 5;
}

.send-btn:hover:not(:disabled) {
    transform: scale(1.1);
    box-shadow: 0 5px 20px rgba(218, 165, 32, 0.4);
}

.send-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Quick actions */
.quick-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    z-index: 5;
}

.quick-action-btn {
    padding: 0.5rem 1rem;
    border: 2px solid rgba(218, 165, 32, 0.3);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.1);
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    z-index: 5;
}

.quick-action-btn:hover:not(:disabled) {
    background: rgba(218, 165, 32, 0.2);
    border-color: #daa520;
    transform: translateY(-2px);
}

.quick-action-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .session-sidebar {
        width: 250px;
    }
    
    .chat-messages.with-sidebar {
        margin-right: 250px;
    }
    
    .chatbot-container {
        width: 95%;
        height: 90vh;
    }

    .chat-header {
        padding: 1rem;
        text-align: center;
    }

    .message-bubble {
        max-width: 85%;
    }

    .quick-actions {
        justify-content: center;
    }

    .quick-action-btn {
        flex: 1;
        justify-content: center;
        min-width: 0;
    }
}

@media (max-width: 600px) {
    .session-sidebar {
        width: 100%;
    }
    
    .chat-messages.with-sidebar {
        display: none;
    }
}

/* Custom scrollbar */
.chat-messages::-webkit-scrollbar {
    width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: #daa520;
    border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: #ffeda7;
}

.session-list::-webkit-scrollbar {
    width: 6px;
}

.session-list::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 5px;
}

.session-list::-webkit-scrollbar-thumb {
    background: #daa520;
    border-radius: 5px;
}
</style>