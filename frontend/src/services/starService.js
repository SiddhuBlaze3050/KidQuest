/**
 * Star Calculation Service
 *
 * Handles star calculation logic for user progress
 */
export const calculateStars = (userStats) => {
  const {
    totalStars = 0, // Total stars from backend
    questsCompleted = 0, // Completed tasks
    skillsLearned = 0, // Completed modules
  } = userStats

  // Star calculation rules:
  // 1. Base stars from total stars (backend calculation)
  // 2. Bonus stars from quests completed (1 star per quest, max 10)
  // 3. Bonus stars from skills learned (10 stars per skill)

  // Calculate bonus stars from quests
  const questBonusStars = Math.min(questsCompleted, 10)

  // Calculate bonus stars from skills
  const skillBonusStars = skillsLearned * 10

  // Total stars calculation
  const calculatedStars = totalStars + questBonusStars + skillBonusStars

  // Determine current level
  const currentLevel = Math.max(1, Math.floor(calculatedStars / 50))

  // Stars needed for next level
  const starsForCurrentLevel = currentLevel * 50
  const starsForNextLevel = (currentLevel + 1) * 50
  const starsInCurrentLevel = calculatedStars - starsForCurrentLevel
  const starsNeededForNextLevel = starsForNextLevel - calculatedStars

  return {
    totalStars: calculatedStars,
    currentLevel,
    starsInLevel: starsInCurrentLevel,
    starsNeededForNextLevel,
    levelProgress: Math.round((starsInCurrentLevel / 50) * 100),
    levelTitle: getLevelTitle(currentLevel),
  }
}

// Level title mapping (similar to levelService)
export const getLevelTitle = (level) => {
  const levelTitles = {
    1: '🌱 Novice Adventurer',
    2: '🔍 Curious Explorer',
    3: '📚 Knowledge Seeker',
    4: '🏆 Skill Master',
    5: '🌟 Wisdom Warrior',
  }

  return levelTitles[level] || '🌱 Novice Adventurer'
}

// Optional: Export a function to check for level up
export const checkForLevelUp = (oldStats, newStats) => {
  const oldStarCalculation = calculateStars(oldStats)
  const newStarCalculation = calculateStars(newStats)

  return {
    leveledUp: newStarCalculation.currentLevel > oldStarCalculation.currentLevel,
    oldLevel: oldStarCalculation.currentLevel,
    newLevel: newStarCalculation.currentLevel,
  }
}
