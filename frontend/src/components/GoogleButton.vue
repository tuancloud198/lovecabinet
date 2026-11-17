<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { api } from '@/api.js'

// "Continue with Google" via Google Identity Services. Renders nothing until the backend
// reports a GOOGLE_CLIENT_ID, so the button simply stays hidden when it isn't configured.
const emit = defineEmits(['credential'])
const el = ref(null)
const ready = ref(false)

let gis
function loadGis() {
  gis ||= new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.onload = () => resolve(window.google.accounts.id)
    script.onerror = () => { gis = null; reject(new Error('gsi')) }
    document.head.appendChild(script)
  })
  return gis
}

onMounted(async () => {
  try {
    const { google_client_id: clientId } = await api('auth/config/')
    if (!clientId) return
    const id = await loadGis()
    id.initialize({ client_id: clientId, callback: ({ credential }) => emit('credential', credential), ux_mode: 'popup' })
    ready.value = true
    await nextTick() // measure the width once visible
    id.renderButton(el.value, { theme: 'outline', size: 'large', shape: 'pill', text: 'continue_with', locale: 'vi', width: Math.min(el.value.clientWidth || 320, 400) })
  } catch { /* Google sign-in unavailable: username/password still works. */ }
})
</script>

<template>
  <div v-show="ready" class="google-signin">
    <span class="divider"><span>hoặc</span></span>
    <div ref="el" class="google-button"></div>
  </div>
</template>
