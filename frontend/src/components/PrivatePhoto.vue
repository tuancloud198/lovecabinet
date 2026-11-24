<script setup>
// A private photo, fetched with the login token (cached per session, see photos.js).
import { ref, watch } from 'vue'
import { photoSrc } from '@/photos.js'
const props = defineProps({ url: String, alt: { type: String, default: 'Ảnh kỷ niệm' } })
const src = ref('')
watch(() => props.url, async url => {
  src.value = ''
  const result = url ? await photoSrc(url) : ''
  if (url === props.url) src.value = result
}, { immediate: true })
</script>
<template><img v-if="src" :src="src" :alt="alt" decoding="async"><span v-else class="photo-placeholder">📷</span></template>
