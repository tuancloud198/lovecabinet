// Character art cropped from task/ui-source (Dog-Growth.png, Design system.png).
const files = import.meta.glob('/src/assets/characters/*.webp', { eager: true, import: 'default' })
export const art = Object.fromEntries(Object.entries(files).map(([path, url]) => [path.split('/').pop().replace('.webp', ''), url]))

/** 'female' (Cún Nón Lá) or 'male' (Cún Mũ Xanh) for a user, from their gender. */
export function characterOf(user) {
  if (user?.gender === 'Nam') return 'male'
  if (user?.gender === 'Nữ') return 'female'
  return (user?.id ?? 0) % 2 ? 'male' : 'female'
}

export const STAGES = [
  { label: 'Bé', levels: 'Cấp 1–3', min: 0 },
  { label: 'Lớn dần', levels: 'Cấp 4–6', min: 30 },
  { label: 'Trưởng thành', levels: 'Cấp 7+', min: 60 },
]
const MOODS = [
  { maxDays: 0, face: 'excited', text: 'Phấn khích! Hôm nay có kỷ niệm mới' },
  { maxDays: 2, face: 'happy', text: 'Vui vẻ, no nê yêu thương' },
  { maxDays: 6, face: 'shy', text: 'Hơi đói... hehe' },
  { maxDays: Infinity, face: 'neutral', text: 'Nhớ hai bạn quá, lưu kỷ niệm đi mà' },
]

/** Pet growth: one level per 10 memories; stages at 30 and 60 memories. */
export function petStatus(memories) {
  const count = memories.length
  const stageIndex = STAGES.findLastIndex(stage => count >= stage.min)
  const next = STAGES[stageIndex + 1]
  const latest = memories.reduce((max, m) => (m.created_at > max ? m.created_at : max), '')
  const days = latest ? Math.floor((Date.now() - new Date(latest)) / 86400000) : Infinity
  return {
    count,
    level: Math.floor(count / 10) + 1,
    stageIndex,
    stage: STAGES[stageIndex],
    next,
    target: next ? next.min : (Math.floor(count / 10) + 1) * 10,
    mood: MOODS.find(mood => days <= mood.maxDays),
  }
}

export const PET_SPECIES = [
  { key: 'dog', label: 'Cún', baby: 'Cún con' },
  { key: 'cat', label: 'Mèo', baby: 'Mèo con' },
  { key: 'capybara', label: 'Capybara', baby: 'Capy con' },
  { key: 'honey_badger', label: 'Lửng mật', baby: 'Lửng con' },
  { key: 'hamster', label: 'Hamster', baby: 'Hamster con' },
]

/** Stage name for a species: the first stage is 'Cún con' / 'Mèo con' / 'Capy con'. */
export function stageLabel(species, index) {
  return index === 0 ? (PET_SPECIES.find(s => s.key === species)?.baby ?? STAGES[0].label) : STAGES[index].label
}
