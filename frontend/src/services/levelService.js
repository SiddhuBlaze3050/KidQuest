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
 * Calculate total experience points
 * 1 star = 1 XP, 1 completed skill = 18 XP
 */
const calculateTotalXP = (userStats) => {
  const { starsEarned = 0, skillsMastered = 0 } = userStats
  return starsEarned + skillsMastered * 18
}

/**
 * Calculate level based on total XP
 * Level 1: 0-9 XP, Level 2: 10-19 XP, Level 3: 20-29 XP, etc.
 * Each level requires 10 more XP than the previous
 */
export const calculateSimpleLevel = (userStats) => {
  const totalXP = calculateTotalXP(userStats)

  // Each level requires 10 XP, starting from level 1
  return Math.max(1, Math.floor(totalXP / 10) + 1)
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
  const totalXP = calculateTotalXP(userStats)
  const currentLevel = calculateSimpleLevel(userStats)

  // Calculate XP needed for current level and next level
  const currentLevelMinXP = (currentLevel - 1) * 10
  const nextLevelMinXP = currentLevel * 10

  // XP progress within current level
  const xpInCurrentLevel = totalXP - currentLevelMinXP
  const xpNeededForNext = nextLevelMinXP - totalXP

  return {
    currentLevel,
    title: getLevelTitle(currentLevel),
    starsInLevel: xpInCurrentLevel,
    starsNeeded: xpNeededForNext,
    progressPercentage: (xpInCurrentLevel / 10) * 100,
    totalStars: starsEarned,
    skillsMastered,
    totalXP,
    xpFromStars: starsEarned,
    xpFromSkills: skillsMastered * 18,
  }
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
