import { reactive, computed } from 'vue'
import { api, getToken, setToken, TOKEN_KEY } from '@/api.js'
import { clearPhotos } from '@/photos.js'

const emptyInvites = () => ({ received: [], sent: [] })

export const state = reactive({
  token: getToken(),
  me: null,
  couple: null,
  cabinets: [],
  jars: [],
  memories: [],
  events: [],
  /** Couple quiz questions (both partners'), newest first. */
  quiz: [],
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
})

export const partner = computed(() => state.couple?.members.find(m => m.id !== state.me?.id) || null)

export function navigate(name, params = {}) {
  state.view = { name, params }
  window.scrollTo(0, 0)
  // These screens list jars/cabinets the partner may have just created on their phone.
  if (name === 'cabinet' || name === 'capture') refresh()
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
    ;[state.cabinets, state.jars, state.memories, state.events, state.quiz] = await Promise.all(['cabinets/', 'jars/', 'memories/', 'events/', 'quiz-questions/'].map(path => api(path)))
  } else {
    state.invites = await api('couple-invitations/')
  }
}

/**
 * Quietly re-fetch the couple's data so changes made by the partner show up without a reload.
 * Skipped while an action is running (its own load() follows) and never shows the busy state.
 */
let refreshing = false
export async function refresh() {
  if (!state.token || !state.me || !state.couple || state.busy || refreshing) return
  refreshing = true
  try {
    await load()
  } catch (error) {
    if (error.status === 401) signOutLocally()
  } finally {
    refreshing = false
  }
}

/**
 * Cheap check used while waiting to be paired: one request for the invitations, and a
 * full load() only when something changed that may mean we are now a couple.
 */
export async function refreshPairing() {
  const before = state.invites
  const invites = await api('couple-invitations/')
  const sentGone = before.sent.some(s => !invites.sent.some(i => i.id === s.id))
  state.invites = invites
  if (sentGone) await load() // our invitation was accepted (or declined/expired)
}

export async function signIn(token) {
  setToken(token)
  state.token = token
  await load()
}

function signOutLocally() {
  setToken('')
  clearPhotos()
  Object.assign(state, { token: '', me: null, couple: null, cabinets: [], jars: [], memories: [], events: [], quiz: [], invites: emptyInvites(), onboarding: '', justPaired: false, view: { name: 'cabinet', params: {} } })
}

// Signing out (or in as someone else) in another tab applies here too.
window.addEventListener('storage', event => {
  if (event.key !== TOKEN_KEY || event.newValue === state.token) return
  if (!event.newValue) signOutLocally()
  else window.location.reload()
})

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
