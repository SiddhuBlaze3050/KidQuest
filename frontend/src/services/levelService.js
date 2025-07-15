import Swal from 'sweetalert2'

// Simple level titles based on progression
const LEVEL_TITLES = {
  1: '🌱 New Adventurer',
  2: '⭐ Star Collector',
  3: '🎯 Quest Seeker',
  4: '📚 Book Explorer',
  5: '🧠 Smart Learner',
  6: '💫 Rising Star',
  7: '🔥 Knowledge Hunter',
  8: '🏃 Fast Learner',
  9: '🎨 Creative Mind',
  10: '🌟 Bright Scholar',
  12: '🚀 Super Student',
  14: '🧙 Wisdom Seeker',
  16: '⚡ Lightning Learner',
  18: '🏆 Achievement Master',
  20: '👑 Learning Champion',
  25: '💎 Diamond Scholar',
  30: '🌈 Rainbow Achiever',
  35: '🔮 Master Explorer',
  40: '🎭 Grand Adventurer',
  50: '🌟 Legendary Learner',
}

// Level rewards for motivation
const LEVEL_REWARDS = {
  5: '🎨 Unlocked: Advanced Drawing Tools',
  10: '🎮 Unlocked: Memory Game Hard Mode',
  15: '📚 Unlocked: Story Builder Pro',
  20: '🏆 Unlocked: Champion Badge',
  25: '🌟 Unlocked: Master Challenges',
  30: '👑 Unlocked: Elite Status',
  40: '🎭 Unlocked: Grand Master Title',
  50: '🌟 Unlocked: Legendary Status',
}

/**
 * Calculate simple level based on stars and skills
 * 10 stars = 1 level, each skill mastered = +2 levels
 */
export const calculateSimpleLevel = (userStats) => {
  const { starsEarned = 0, skillsMastered = 0 } = userStats

  // Base level from stars (every 10 stars = 1 level)
  const starLevels = Math.floor(starsEarned / 10)

  // Bonus levels from skills mastered (each 100% module = +2 levels)
  const skillBonusLevels = skillsMastered * 2

  // Total level (minimum level 1)
  return Math.max(1, starLevels + skillBonusLevels)
}

/**
 * Get level title based on current level
 */
export const getLevelTitle = (level) => {
  // Find the highest title that doesn't exceed the level
  const availableLevels = Object.keys(LEVEL_TITLES)
    .map(Number)
    .sort((a, b) => b - a)

  for (const titleLevel of availableLevels) {
    if (level >= titleLevel) {
      return LEVEL_TITLES[titleLevel]
    }
  }
  return LEVEL_TITLES[1] // Default to first title
}

/**
 * Get detailed level progress information
 */
export const getLevelProgress = (userStats) => {
  const { starsEarned = 0, skillsMastered = 0 } = userStats
  const currentLevel = calculateSimpleLevel(userStats)

  // Progress within current star level (0-9 stars to next level)
  const starsInCurrentLevel = starsEarned % 10
  const starsToNextLevel = 10 - starsInCurrentLevel

  return {
    currentLevel,
    title: getLevelTitle(currentLevel),
    starsInLevel: starsInCurrentLevel,
    starsNeeded: starsToNextLevel,
    progressPercentage: (starsInCurrentLevel / 10) * 100,
    totalStars: starsEarned,
    skillsMastered,
  }
}

/**
 * Check if user leveled up and show celebration
 */
export const checkForLevelUp = async (oldStats, newStats) => {
  const oldLevel = calculateSimpleLevel(oldStats)
  const newLevel = calculateSimpleLevel(newStats)

  if (newLevel > oldLevel) {
    const newTitle = getLevelTitle(newLevel)
    const reward = LEVEL_REWARDS[newLevel]

    await Swal.fire({
      title: '🎉 LEVEL UP! 🎉',
      html: `
        <div style="text-align: center; line-height: 1.8;">
          <div style="font-size: 3rem; margin: 1rem 0; color: #FFD700;">
            Level ${oldLevel} → Level ${newLevel}
          </div>
          <h3 style="color: #4a5568; margin: 1rem 0; font-size: 1.3rem;">
            ${newTitle}
          </h3>
          <p style="color: #718096; font-size: 1.1rem;">
            Amazing progress! Keep collecting those stars! ⭐
          </p>
          ${
            reward
              ? `
            <div style="background: rgba(255, 215, 0, 0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
              <h4 style="color: #FFD700; margin: 0.5rem 0;">🎁 New Reward!</h4>
              <p style="color: #4a5568; margin: 0;">${reward}</p>
            </div>
          `
              : ''
          }
          <div style="font-size: 2rem; margin: 1rem 0;">🌟✨🌟</div>
        </div>
      `,
      background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
      color: 'white',
      timer: 5000,
      timerProgressBar: true,
      showConfirmButton: true,
      confirmButtonText: '🚀 Continue Adventure!',
    })

    return true
  }
  return false
}

/**
 * Get reward for reaching a specific level
 */
export const getLevelReward = (level) => {
  return LEVEL_REWARDS[level] || null
}

/**
 * Get next milestone level and reward
 */
export const getNextMilestone = (currentLevel) => {
  const milestones = Object.keys(LEVEL_REWARDS)
    .map(Number)
    .sort((a, b) => a - b)
  const nextMilestone = milestones.find((level) => level > currentLevel)

  if (nextMilestone) {
    return {
      level: nextMilestone,
      reward: LEVEL_REWARDS[nextMilestone],
      levelsToGo: nextMilestone - currentLevel,
    }
  }

  return null
}
