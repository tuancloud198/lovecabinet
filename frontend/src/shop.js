// Shop actions shared by the shop page and the preview bar.
import { api } from '@/api.js'
import { state, navigate, run, toast } from '@/store.js'

export const themeOf = item => item.id.replace(/^theme_/, '')

// Try an item without buying: the whole app switches to it in look-only mode (tabs and scrolling work,
// nothing inside the pages can be tapped) for PREVIEW_SECONDS, then you're back in the shop. Not saved.
export const PREVIEW_SECONDS = 60
export function startPreview(item) {
  if (item.kind === 'theme') state.preview = { item, theme: themeOf(item), endsAt: Date.now() + PREVIEW_SECONDS * 1000 }
}
/** End the preview; `back` returns to the shop (after ✕ or when time is up, not after buying). */
export function stopPreview(back = true) {
  if (!state.preview) return
  state.preview = null
  if (back) navigate('shop')
}

async function useTheme(theme) {
  state.me = await api('users/me/', { method: 'PATCH', body: { theme } })
  const member = state.couple.members.find(m => m.id === state.me.id)
  if (member) Object.assign(member, state.me)
}

export function buy(item) {
  if (!window.confirm(`Mua "${item.name}" với ${item.price} điểm?`)) return
  run(async () => {
    state.shop = await api(`shop/${item.id}/buy/`, { method: 'POST' })
    stopPreview(false) // stay on the page you're looking at, now in the bought theme
    toast(`Đã mua "${item.name}"! ♡`)
    if (item.kind === 'theme') await useTheme(themeOf(item))
  })
}

export function applyTheme(theme) {
  run(async () => {
    stopPreview(false)
    await useTheme(theme)
    toast(theme ? 'Đã đổi giao diện!' : 'Đã dùng giao diện mặc định.')
  })
}
