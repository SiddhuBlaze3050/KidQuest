/**
 * Emotion Detection Utility for KidQuest Chatbot
 * Detects emotions from text messages using keyword matching and basic sentiment analysis
 */

// Import sentiment analysis library
import Sentiment from 'sentiment'

const sentiment = new Sentiment()

/**
 * Emotion keywords mapping
 */
export const emotionKeywords = {
  happy: [
    // Positive feelings
    'happy',
    'glad',
    'joy',
    'joyful',
    'excited',
    'thrilled',
    'elated',
    'cheerful',
    'pleased',
    'delighted',
    'content',
    'satisfied',
    'grateful',

    // Positive actions/expressions
    'smile',
    'smiling',
    'laugh',
    'laughing',
    'giggle',
    'grin',
    'grinning',

    // Positive descriptors
    'awesome',
    'amazing',
    'wonderful',
    'fantastic',
    'great',
    'excellent',
    'brilliant',
    'perfect',
    'love',
    'loving',
    'adore',
    'enjoy',
    'enjoying',

    // Achievement emotions
    'proud',
    'accomplished',
    'successful',
    'victorious',
    'winning',

    // Energy
    'energetic',
    'enthusiastic',
    'pumped',
    'motivated',
    'inspired',
  ],

  sad: [
    // Negative feelings
    'sad',
    'upset',
    'down',
    'blue',
    'depressed',
    'melancholy',
    'gloomy',
    'disappointed',
    'discouraged',
    'dejected',
    'heartbroken',
    'hurt',

    // Negative actions/expressions
    'cry',
    'crying',
    'weep',
    'weeping',
    'sob',
    'sobbing',
    'frown',

    // Emotional pain
    'pain',
    'ache',
    'lonely',
    'isolated',
    'abandoned',
    'rejected',
    'hopeless',
    'helpless',
    'lost',
    'empty',
    'broken',

    // Worry/anxiety
    'worried',
    'anxious',
    'nervous',
    'scared',
    'afraid',
    'fearful',
    'stressed',
    'overwhelmed',
    'panicked',
    'terrified',

    // Negative descriptors
    'awful',
    'terrible',
    'horrible',
    'bad',
    'worst',
    'hate',
    'dislike',
  ],

  excited: [
    // High energy positive
    'excited',
    'thrilled',
    'pumped',
    'hyped',
    'energized',
    'electrified',
    'exhilarated',
    'euphoric',
    'ecstatic',
    'overjoyed',
    'buzzing',

    // Enthusiasm
    'enthusiastic',
    'passionate',
    'fired up',
    'psyched',
    'stoked',
    'amped',
    'charged',
    'motivated',
    'inspired',
    'driven',

    // Anticipation
    'anticipating',
    'eager',
    'ready',
    'prepared',
    "can't wait",

    // Exclamations
    'wow',
    'amazing',
    'incredible',
    'unbelievable',
    'fantastic',
    'spectacular',
    'extraordinary',
    'phenomenal',
    'outstanding',

    // Adventure/quest terms
    'adventure',
    'quest',
    'journey',
    'explore',
    'discover',
    'achieve',
  ],

  thinking: [
    // Cognitive processes
    'think',
    'thinking',
    'thought',
    'consider',
    'considering',
    'wonder',
    'wondering',
    'ponder',
    'pondering',
    'reflect',
    'reflecting',
    'contemplate',
    'contemplating',
    'analyze',
    'analyzing',

    // Questions/curiosity
    'question',
    'curious',
    'why',
    'how',
    'what',
    'when',
    'where',
    'understand',
    'comprehend',
    'figure out',
    'puzzle',
    'mystery',

    // Learning
    'learn',
    'learning',
    'study',
    'studying',
    'research',
    'investigate',
    'explore',
    'discover',
    'find out',
    'knowledge',
    'wisdom',

    // Decision making
    'decide',
    'deciding',
    'choice',
    'option',
    'evaluate',
    'weigh',
    'compare',
    'assess',
    'judge',
    'determine',

    // Uncertainty
    'confused',
    'puzzled',
    'uncertain',
    'unsure',
    'doubtful',
    'hesitant',
  ],

  neutral: [
    // Basic states
    'okay',
    'ok',
    'fine',
    'alright',
    'normal',
    'regular',
    'usual',
    'average',
    'typical',
    'standard',
    'ordinary',
    'common',

    // Casual responses
    'sure',
    'yes',
    'no',
    'maybe',
    'perhaps',
    'possibly',
    'probably',

    // Neutral descriptors
    'calm',
    'peaceful',
    'quiet',
    'still',
    'stable',
    'balanced',
    'steady',
    'consistent',
    'moderate',
    'mild',
  ],
}

/**
 * Emotion intensity weights
 */
const emotionWeights = {
  happy: 1.2,
  excited: 1.5,
  sad: 1.1,
  thinking: 1.0,
  neutral: 0.8,
}

/**
 * Detect emotion from text using keyword matching
 * @param {string} text - The text to analyze
 * @param {Object} keywords - Custom keyword mapping (optional)
 * @returns {string} - Detected emotion
 */
export function getEmotionFromKeywords(text, keywords = emotionKeywords) {
  const lowercaseText = text.toLowerCase()
  const emotionScores = {}

  // Initialize scores
  Object.keys(keywords).forEach((emotion) => {
    emotionScores[emotion] = 0
  })

  // Count keyword matches
  Object.entries(keywords).forEach(([emotion, words]) => {
    words.forEach((word) => {
      const regex = new RegExp(`\\b${word}\\b`, 'gi')
      const matches = lowercaseText.match(regex)
      if (matches) {
        emotionScores[emotion] += matches.length * (emotionWeights[emotion] || 1)
      }
    })
  })

  // Find emotion with highest score
  let maxEmotion = 'neutral'
  let maxScore = 0

  Object.entries(emotionScores).forEach(([emotion, score]) => {
    if (score > maxScore) {
      maxScore = score
      maxEmotion = emotion
    }
  })

  return maxEmotion
}

/**
 * Detect emotion using sentiment analysis
 * @param {string} text - The text to analyze
 * @returns {string} - Detected emotion based on sentiment
 */
export function getEmotionFromSentiment(text) {
  const result = sentiment.analyze(text)
  const score = result.score
  const comparative = result.comparative

  // Determine emotion based on sentiment score
  if (score >= 3 || comparative >= 0.5) {
    return comparative >= 1 ? 'excited' : 'happy'
  } else if (score <= -3 || comparative <= -0.5) {
    return 'sad'
  } else if (score === 0 && comparative === 0) {
    return 'neutral'
  } else {
    return 'thinking'
  }
}

/**
 * Advanced emotion detection combining keywords and sentiment
 * @param {string} text - The text to analyze
 * @param {Object} options - Configuration options
 * @returns {Object} - Emotion analysis result
 */
export function detectEmotion(text, options = {}) {
  const {
    useKeywords = true,
    useSentiment = true,
    keywordWeight = 0.7,
    sentimentWeight = 0.3,
    customKeywords = null,
  } = options

  const results = {
    text: text,
    emotions: {},
    primaryEmotion: 'neutral',
    confidence: 0,
    details: {
      keywordEmotion: null,
      sentimentEmotion: null,
      sentimentScore: null,
    },
  }

  let keywordEmotion = 'neutral'
  let sentimentEmotion = 'neutral'

  // Keyword-based detection
  if (useKeywords) {
    keywordEmotion = getEmotionFromKeywords(text, customKeywords || emotionKeywords)
    results.details.keywordEmotion = keywordEmotion
  }

  // Sentiment-based detection
  if (useSentiment) {
    const sentimentResult = sentiment.analyze(text)
    sentimentEmotion = getEmotionFromSentiment(text)
    results.details.sentimentEmotion = sentimentEmotion
    results.details.sentimentScore = sentimentResult.score
  }

  // Combine results with weights
  const emotionCounts = {}

  if (useKeywords) {
    emotionCounts[keywordEmotion] = (emotionCounts[keywordEmotion] || 0) + keywordWeight
  }

  if (useSentiment) {
    emotionCounts[sentimentEmotion] = (emotionCounts[sentimentEmotion] || 0) + sentimentWeight
  }

  // Find primary emotion
  let maxCount = 0
  Object.entries(emotionCounts).forEach(([emotion, count]) => {
    results.emotions[emotion] = count
    if (count > maxCount) {
      maxCount = count
      results.primaryEmotion = emotion
    }
  })

  // Calculate confidence
  const totalWeight = (useKeywords ? keywordWeight : 0) + (useSentiment ? sentimentWeight : 0)
  results.confidence = maxCount / totalWeight

  return results
}

/**
 * Get emotion emoji representation
 * @param {string} emotion - The emotion to get emoji for
 * @returns {string} - Emoji representation
 */
export function getEmotionEmoji(emotion) {
  const emojiMap = {
    happy: '😊',
    sad: '😢',
    excited: '🤩',
    thinking: '🤔',
    neutral: '😐',
    angry: '😠',
    surprised: '😲',
    confused: '😕',
    love: '😍',
    laughing: '😂',
  }

  return emojiMap[emotion] || '😐'
}

/**
 * Get emotion color representation
 * @param {string} emotion - The emotion to get color for
 * @returns {string} - Color hex code
 */
export function getEmotionColor(emotion) {
  const colorMap = {
    happy: '#4caf50', // Green
    sad: '#2196f3', // Blue
    excited: '#ff9800', // Orange
    thinking: '#9c27b0', // Purple
    neutral: '#607d8b', // Blue Grey
    angry: '#f44336', // Red
    surprised: '#ffeb3b', // Yellow
    confused: '#795548', // Brown
    love: '#e91e63', // Pink
    laughing: '#4caf50', // Green
  }

  return colorMap[emotion] || '#607d8b'
}

/**
 * Batch emotion detection for multiple texts
 * @param {Array} texts - Array of texts to analyze
 * @param {Object} options - Configuration options
 * @returns {Array} - Array of emotion analysis results
 */
export function detectEmotionBatch(texts, options = {}) {
  return texts.map((text) => detectEmotion(text, options))
}

/**
 * Get emotion statistics from a conversation
 * @param {Array} messages - Array of message objects with 'message' property
 * @returns {Object} - Emotion statistics
 */
export function getConversationEmotionStats(messages) {
  const emotions = messages.map((msg) => getEmotionFromKeywords(msg.message))
  const stats = {}

  emotions.forEach((emotion) => {
    stats[emotion] = (stats[emotion] || 0) + 1
  })

  const total = emotions.length
  const percentages = {}

  Object.entries(stats).forEach(([emotion, count]) => {
    percentages[emotion] = Math.round((count / total) * 100)
  })

  return {
    counts: stats,
    percentages: percentages,
    total: total,
    dominant: Object.keys(stats).reduce((a, b) => (stats[a] > stats[b] ? a : b), 'neutral'),
  }
}

/**
 * Suggest responses based on detected emotion
 * @param {string} emotion - The detected emotion
 * @returns {Array} - Array of suggested responses
 */
export function getSuggestedResponses(emotion) {
  const responses = {
    happy: [
      "That's wonderful to hear! 😊",
      "I'm so glad you're feeling great!",
      'Your happiness is contagious! ✨',
      'Keep spreading those positive vibes!',
    ],
    sad: [
      "I'm here to listen and help. 💙",
      "It's okay to feel this way sometimes.",
      "Would you like to talk about what's bothering you?",
      "Remember, difficult times don't last forever.",
    ],
    excited: [
      'Your enthusiasm is amazing! 🚀',
      'I can feel your energy from here!',
      'That sounds incredibly exciting!',
      "Tell me more about what's got you so pumped!",
    ],
    thinking: [
      "That's a great question to ponder! 🤔",
      'I love how thoughtful you are!',
      "Let's explore that idea together.",
      'Your curiosity is wonderful!',
    ],
    neutral: [
      "I'm here to help with whatever you need.",
      'What would you like to explore today?',
      'How can I assist you on your journey?',
      "Feel free to share what's on your mind.",
    ],
  }

  return responses[emotion] || responses.neutral
}

export default {
  getEmotionFromKeywords,
  getEmotionFromSentiment,
  detectEmotion,
  getEmotionEmoji,
  getEmotionColor,
  detectEmotionBatch,
  getConversationEmotionStats,
  getSuggestedResponses,
  emotionKeywords,
}
