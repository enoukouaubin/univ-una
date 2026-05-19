import { DIFFICULTY, STREAK_BONUS } from '../constants/theme';

export function generateQuestion(difficulty) {
  const { min, max } = DIFFICULTY[difficulty];
  const a = Math.floor(Math.random() * (max - min + 1)) + min;
  const b = Math.floor(Math.random() * (max - min + 1)) + min;
  return { a, b, answer: a * b };
}

export function calcScore(isCorrect, timeLeft, maxTime, basePoints, streak) {
  if (!isCorrect) return 0;
  const speedBonus = Math.round((timeLeft / maxTime) * 5);
  const streakBonus = streak > 2 ? STREAK_BONUS : 0;
  return basePoints + speedBonus + streakBonus;
}

export function getStreakEmoji(streak) {
  if (streak >= 5) return '🔥🔥🔥';
  if (streak >= 3) return '🔥🔥';
  if (streak >= 2) return '🔥';
  return '';
}

export function getRankTitle(score) {
  if (score >= 250) return 'Génie des maths 🏆';
  if (score >= 180) return 'Expert 🥇';
  if (score >= 120) return 'Avancé 🥈';
  if (score >= 60)  return 'Débutant 🥉';
  return 'Novice 📚';
}
