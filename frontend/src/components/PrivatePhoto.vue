<script setup>
// A private photo, fetched with the login token (cached per session, see photos.js).
import { ref, watch } from 'vue'
import { photoSrc } from '@/photos.js'
import PetLoader from '@/components/PetLoader.vue'
const props = defineProps({ url: String, alt: { type: String, default: 'Ảnh kỷ niệm' } })
const src = ref('')
const failed = ref(false)
watch(() => props.url, async url => {
  src.value = ''
  failed.value = false
  const result = url ? await photoSrc(url) : ''
  if (url !== props.url) return
  src.value = result
  failed.value = !result
}, { immediate: true })
</script>
<template><img v-if="src" :src="src" :alt="alt" decoding="async"><PetLoader v-else :still="failed" /></template>
