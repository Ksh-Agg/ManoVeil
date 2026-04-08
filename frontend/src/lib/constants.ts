export const PERSONAS = {
  manomitra: { name: 'ManoMitra', color: '#FBBF24', bg: '#FFFBEB', text: '#92400E', ageRange: '5-12', description: 'A gentle companion for children' },
  manospark: { name: 'ManoSpark', color: '#F472B6', bg: '#FDF2F8', text: '#9D174D', ageRange: '13-17', description: 'A supportive friend for teens' },
  manoveil_core: { name: 'ManoVeil Core', color: '#34D399', bg: '#F0FDF4', text: '#065F46', ageRange: '18-24', description: 'A peer companion for college students' },
  manobalance: { name: 'ManoBalance', color: '#60A5FA', bg: '#EFF6FF', text: '#1E40AF', ageRange: '25-59', description: 'A thoughtful guide for adults' },
  manosaathi: { name: 'ManoSaathi', color: '#A78BFA', bg: '#F5F3FF', text: '#5B21B6', ageRange: '60+', description: 'A warm companion for seniors' },
  manoconnect: { name: 'ManoConnect', color: '#2DD4BF', bg: '#F0FDFA', text: '#134E4A', ageRange: 'Clinical', description: 'Clinical intelligence for therapists' },
} as const;

export const AGE_GROUPS = [
  { value: 'children_5_12', label: 'Children (5-12)', persona: 'manomitra' },
  { value: 'teenagers_13_17', label: 'Teenagers (13-17)', persona: 'manospark' },
  { value: 'college_18_24', label: 'College Students (18-24)', persona: 'manoveil_core' },
  { value: 'adults_25_59', label: 'Adults (25-59)', persona: 'manobalance' },
  { value: 'elderly_60_plus', label: 'Elderly (60+)', persona: 'manosaathi' },
] as const;

export const SCORE_CATEGORIES = {
  minimal: { label: 'Minimal', color: '#22c55e', range: '0 - 2.0' },
  mild: { label: 'Mild', color: '#84cc16', range: '2.1 - 4.5' },
  moderate: { label: 'Moderate', color: '#f59e0b', range: '4.6 - 7.0' },
  moderately_severe: { label: 'Moderately Severe', color: '#f97316', range: '7.1 - 8.9' },
  severe: { label: 'Severe', color: '#ef4444', range: '9.0 - 10.0' },
} as const;

export const MOOD_EMOJIS = [
  { level: 'very_bad', emoji: '😢', label: 'Very Bad', value: 1 },
  { level: 'bad', emoji: '😟', label: 'Bad', value: 2 },
  { level: 'neutral', emoji: '😐', label: 'Neutral', value: 3 },
  { level: 'good', emoji: '😊', label: 'Good', value: 4 },
  { level: 'very_good', emoji: '😄', label: 'Very Good', value: 5 },
] as const;
