// The two partners' characters, cropped from task/ui-source (Dog-Growth.png, Design system.png).
const files = import.meta.glob('/src/assets/characters/*.webp', { eager: true, import: 'default' })
export const art = Object.fromEntries(Object.entries(files).map(([path, url]) => [path.split('/').pop().replace('.webp', ''), url]))

// The couple's pet, by Couple.pet_type: a body per growth stage + a head per mood (assets/characters/<pet>/).
import dog from '@/assets/characters/dog/index.js'
import cat from '@/assets/characters/cat/index.js'
import ragdog from '@/assets/characters/ragdog/index.js'
export const PETS = { dog, cat, ragdog }

/** 'female' (Cún Nón Lá) or 'male' (Cún Mũ Xanh) for a user, from their gender. */
export function characterOf(user) {
  if (user?.gender === 'Nam') return 'male'
  if (user?.gender === 'Nữ') return 'female'
  return (user?.id ?? 0) % 2 ? 'male' : 'female'
}

// Pet points: each memory is worth MEMORY_POINTS, each answered quiz question QUIZ_POINTS. The server keeps
// the total on the couple (couple.points_earned); these are for the hints shown to the user.
export const MEMORY_POINTS = 10
export const QUIZ_POINTS = 2
const LEVEL_POINTS = 100
export const STAGES = [
  { label: 'Bé', levels: 'Cấp 1–3', min: 0 },
  { label: 'Lớn dần', levels: 'Cấp 4–6', min: 300 },
  { label: 'Trưởng thành', levels: 'Cấp 7+', min: 600 },
]
const MOODS = [
  { maxDays: 0, face: 'excited', text: 'Phấn khích! Hôm nay có kỷ niệm mới' },
  { maxDays: 2, face: 'happy', text: 'Vui vẻ, no nê yêu thương' },
  { maxDays: 6, face: 'shy', text: 'Hơi đói... hehe' },
  { maxDays: Infinity, face: 'neutral', text: 'Nhớ hai bạn quá, lưu kỷ niệm đi mà' },
]

/** Pet growth: one level per 100 points (10 memories); stages at 300 and 600 points. */
export function petStatus(memories, earned = 0) {
  const count = earned // couple.points_earned: memories and quiz answers (memories also set the mood below)
  const stageIndex = STAGES.findLastIndex(stage => count >= stage.min)
  const next = STAGES[stageIndex + 1]
  const latest = memories.reduce((max, m) => (m.created_at > max ? m.created_at : max), '')
  const days = latest ? Math.floor((Date.now() - new Date(latest)) / 86400000) : Infinity
  return {
    count,
    level: Math.floor(count / LEVEL_POINTS) + 1,
    stageIndex,
    stage: STAGES[stageIndex],
    next,
    target: next ? next.min : (Math.floor(count / LEVEL_POINTS) + 1) * LEVEL_POINTS,
    mood: MOODS.find(mood => days <= mood.maxDays),
  }
}

/** Stage name: the first stage is 'Cún con' (or 'Mèo con' for the cat). */
export function stageLabel(index, species = 'dog') {
  return index === 0 ? (species === 'cat' ? 'Mèo con' : 'Cún con') : STAGES[index].label
}
