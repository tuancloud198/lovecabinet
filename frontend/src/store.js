import { reactive, computed } from 'vue'
import { api, getToken, setToken } from '@/api.js'

const emptyInvites = () => ({ received: [], sent: [] })

export const state = reactive({
  token: getToken(),
  me: null,
  couple: null,
  cabinets: [],
  jars: [],
  memories: [],
  events: [],
  invites: emptyInvites(),
  busy: false,
  error: '',
  toast: '',
  /** 'profile' right after registration, until the profile step is done or skipped. */
  onboarding: '',
  /** Show the "paired" celebration before entering the cabinet. */
  justPaired: false,
  /** Main app screen: { name, params }. */
  view: { name: 'cabinet', params: {} },
  /** Cabinet filters: whose memories ('me' | 'partner') and which year. */
  owner: 'me',
  year: new Date().getFullYear(),
})

export const partner = computed(() => state.couple?.members.find(m => m.id !== state.me?.id) || null)

export function navigate(name, params = {}) {
  state.view = { name, params }
  window.scrollTo(0, 0)
}

let toastTimer
export function toast(message) {
  state.toast = message
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { state.toast = '' }, 2200)
}

/** Run an action with the shared busy/error state. Returns true on success. */
export async function run(action) {
  if (state.busy) return false
  state.busy = true
  state.error = ''
  try {
    await action()
    return true
  } catch (error) {
    if (error.status === 401) signOutLocally()
    state.error = error.message
    return false
  } finally {
    state.busy = false
  }
}

export async function load() {
  state.me = await api('users/me/')
  const couples = await api('couples/')
  state.couple = couples[0] || null
  if (state.couple) {
    ;[state.cabinets, state.jars, state.memories, state.events] = await Promise.all(['cabinets/', 'jars/', 'memories/', 'events/'].map(path => api(path)))
  } else {
    state.invites = await api('couple-invitations/')
  }
}

export async function signIn(token) {
  setToken(token)
  state.token = token
  await load()
}

function signOutLocally() {
  setToken('')
  Object.assign(state, { token: '', me: null, couple: null, cabinets: [], jars: [], memories: [], events: [], invites: emptyInvites(), onboarding: '', justPaired: false, owner: 'me', view: { name: 'cabinet', params: {} } })
}

export async function signOut() {
  await run(async () => {
    await api('auth/logout/', { method: 'POST' })
    signOutLocally()
  })
}

/** The cabinet for a year, created on first use. */
export async function cabinetForYear(year) {
  let cabinet = state.cabinets.find(c => c.year === year)
  if (!cabinet) {
    cabinet = await api('cabinets/', { method: 'POST', body: { name: 'Tủ thương', year } })
    state.cabinets.push(cabinet)
  }
  return cabinet
}
