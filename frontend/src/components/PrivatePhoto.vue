<script setup>
import { ref, watch } from 'vue'
import { photoSrc } from '@/photos.js'
const props = defineProps({ url: String, alt: { type: String, default: 'Ảnh kỷ niệm' } })
const src = ref('')
watch(() => props.url, async url => {
  src.value = ''
  const result = await photoSrc(url)
  if (url === props.url) src.value = result
}, { immediate: true })
</script>
<template><img v-if="src" :src="src" :alt="alt"><span v-else class="photo-placeholder">📷</span></template>
