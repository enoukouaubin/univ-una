export const COLORS = {
  background: '#1a1a2e',
  player1: '#e94560',
  player2: '#0f3460',
  player1Light: '#ff6b8a',
  player2Light: '#4a90d9',
  player1Dark: '#b02040',
  player2Dark: '#082540',
  gold: '#ffd700',
  silver: '#c0c0c0',
  correct: '#4caf50',
  wrong: '#f44336',
  white: '#ffffff',
  lightGray: '#cccccc',
  divider: '#ffffff',
  keyBg: 'rgba(255,255,255,0.15)',
  keyBgActive: 'rgba(255,255,255,0.35)',
};

export const DIFFICULTY = {
  easy:   { label: 'Facile',  min: 1, max: 5,  time: 15, points: 10 },
  medium: { label: 'Moyen',   min: 1, max: 10, time: 12, points: 15 },
  hard:   { label: 'Difficile', min: 1, max: 12, time: 10, points: 20 },
  expert: { label: 'Expert',  min: 5, max: 20, time: 8,  points: 30 },
};

export const TOTAL_ROUNDS = 10;
export const STREAK_BONUS = 5;
