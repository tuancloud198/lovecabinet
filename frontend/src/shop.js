// Shop actions shared by the shop page and the preview bar.
import { api } from '@/api.js'
import { state, run, toast } from '@/store.js'

export const themeOf = item => item.id.replace(/^theme_/, '')

/** Try an item without buying: a theme is applied to the whole app until stopPreview() (not saved). */
export function startPreview(item) {
  if (item.kind === 'theme') state.preview = { item, theme: themeOf(item) }
}
export function stopPreview() {
  state.preview = null
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
    stopPreview()
    toast(`Đã mua "${item.name}"! ♡`)
    if (item.kind === 'theme') await useTheme(themeOf(item))
  })
}

export function applyTheme(theme) {
  run(async () => {
    stopPreview()
    await useTheme(theme)
    toast(theme ? 'Đã đổi giao diện!' : 'Đã dùng giao diện mặc định.')
  })
}
