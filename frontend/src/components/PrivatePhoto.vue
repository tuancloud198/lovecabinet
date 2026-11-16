<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { getToken } from '@/api.js'
const props = defineProps({ url: String })
const src = ref('')
let version = 0
watch(() => props.url, async url => {
  const current = ++version
  if (src.value) URL.revokeObjectURL(src.value)
  src.value = ''
  try {
    const response = await fetch(url, { headers: { Authorization: `Token ${getToken()}` } })
    if (!response.ok) return
    const blob = await response.blob()
    if (current === version) src.value = URL.createObjectURL(blob)
  } catch { /* A failed image leaves its accessible placeholder. */ }
}, { immediate: true })
onBeforeUnmount(() => { version++; if (src.value) URL.revokeObjectURL(src.value) })
</script>
<template><img v-if="src" :src="src" alt="Ảnh kỷ niệm"><span v-else class="photo-placeholder">📷</span></template>
