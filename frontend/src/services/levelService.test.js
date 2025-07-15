import { calculateSimpleLevel, getLevelTitle, getLevelProgress } from './levelService.js'

// Test cases to demonstrate the level system
console.log('🧪 Testing Simple Level System')
console.log('================================')

// Test Case 1: New user (0 stars, 0 skills)
const newUser = { starsEarned: 0, skillsMastered: 0 }
console.log('👶 New User:', getLevelProgress(newUser))

// Test Case 2: User with some stars (15 stars, 0 skills)
const starCollector = { starsEarned: 15, skillsMastered: 0 }
console.log('⭐ Star Collector:', getLevelProgress(starCollector))

// Test Case 3: User with 1 skill mastered (5 stars, 1 skill)
const skillLearner = { starsEarned: 5, skillsMastered: 1 }
console.log('🧠 Skill Learner:', getLevelProgress(skillLearner))

// Test Case 4: Advanced user (25 stars, 2 skills)
const advancedUser = { starsEarned: 25, skillsMastered: 2 }
console.log('🚀 Advanced User:', getLevelProgress(advancedUser))

// Test Case 5: Master user (50 stars, 3 skills)
const masterUser = { starsEarned: 50, skillsMastered: 3 }
console.log('👑 Master User:', getLevelProgress(masterUser))

console.log('================================')
console.log('Level System Rules:')
console.log('• Every 10 stars = +1 level')
console.log('• Each skill mastered = +2 levels')
console.log('• Progress bar shows stars in current level (0-9)')
