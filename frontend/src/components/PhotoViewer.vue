<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import PrivatePhoto from '@/components/PrivatePhoto.vue'

// Full-screen photo viewer. `urls` are either private API URLs (`private`) or local object URLs.
const props = defineProps({ urls: { type: Array, required: true }, start: { type: Number, default: 0 }, private: Boolean })
const emit = defineEmits(['close'])
const index = ref(Math.min(props.start, props.urls.length - 1))
const closeButton = ref(null)

const go = step => { index.value = (index.value + step + props.urls.length) % props.urls.length }
function onKey(event) {
  if (event.key === 'Escape') emit('close')
  else if (event.key === 'ArrowLeft' && props.urls.length > 1) go(-1)
  else if (event.key === 'ArrowRight' && props.urls.length > 1) go(1)
}
let touchX = null
const touchStart = event => { touchX = event.touches[0].clientX }
function touchEnd(event) {
  if (touchX === null || props.urls.length < 2) return
  const dx = event.changedTouches[0].clientX - touchX
  touchX = null
  if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1)
}

let previousOverflow = ''
onMounted(() => {
  previousOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', onKey)
  closeButton.value?.focus()
})
onBeforeUnmount(() => {
  document.body.style.overflow = previousOverflow
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div class="viewer" role="dialog" aria-modal="true" aria-label="Xem ảnh" @click.self="emit('close')" @touchstart.passive="touchStart" @touchend="touchEnd">
    <PrivatePhoto v-if="private" :key="urls[index]" :url="urls[index]" :alt="`Ảnh ${index + 1}`" />
    <img v-else :src="urls[index]" :alt="`Ảnh ${index + 1}`" />
    <button ref="closeButton" class="viewer-button viewer-close" aria-label="Đóng" @click="emit('close')"><X :size="22" /></button>
    <template v-if="urls.length > 1">
      <button class="viewer-button viewer-prev" aria-label="Ảnh trước" @click="go(-1)"><ChevronLeft :size="26" /></button>
      <button class="viewer-button viewer-next" aria-label="Ảnh sau" @click="go(1)"><ChevronRight :size="26" /></button>
      <span class="viewer-count">{{ index + 1 }} / {{ urls.length }}</span>
    </template>
  </div>
</template>
