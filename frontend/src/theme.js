import { ref } from 'vue'

// Season themes: autumn is the original look; the rest only swap CSS colour tokens
// (see style.css, :root[data-theme=…]). The choice is a per-device preference.
export const THEMES = [
  { key: 'spring', label: 'Xuân', icon: '🌸', color: '#F2B3BE', bg: '#F8E7E3' },
  { key: 'summer', label: 'Hạ', icon: '🌻', color: '#A9D18E', bg: '#F7EFD6' },
  { key: 'autumn', label: 'Thu', icon: '🍁', color: '#E8A07A', bg: '#F6E8DD' },
  { key: 'winter', label: 'Đông', icon: '❄️', color: '#D7A3B4', bg: '#F2ECE8' },
]
const KEY = 'theme'
const DEFAULT = 'autumn'

function saved() {
  try { return localStorage.getItem(KEY) } catch { return null }
}
export const theme = ref(THEMES.some(t => t.key === saved()) ? saved() : DEFAULT)

export function applyTheme(key = theme.value) {
  const chosen = THEMES.find(t => t.key === key) ?? THEMES.find(t => t.key === DEFAULT)
  theme.value = chosen.key
  document.documentElement.dataset.theme = chosen.key
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', chosen.bg)
  try { localStorage.setItem(KEY, chosen.key) } catch { /* not remembered on this device */ }
}
