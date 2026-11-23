<script setup>
// Full-screen, story-style replay of memories: one slide per photo/video (a memory without media
// gets one card), in date order. Photos stay PHOTO_MS, videos play to the end. Each slide shows its
// memory's title, date, author and description on top. Tap left/right = previous/next, middle (or
// space) = pause; arrow keys and Esc work too.
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { Pause, Play, RotateCcw, Volume2, VolumeX, X } from 'lucide-vue-next'
import { displayDate } from '@/format.js'
import { isVideo, mediaOf, photoSrc } from '@/photos.js'
import { state } from '@/store.js'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import PrivatePhoto from '@/components/PrivatePhoto.vue'

const props = defineProps({ memories: { type: Array, required: true }, title: { type: String, default: 'Xem lại kỷ niệm' } })
const emit = defineEmits(['close'])
const PHOTO_MS = 5000
const CARD_MS = 4000 // a memory without photos or videos

const ordered = computed(() => [...props.memories].sort((a, b) => a.date.localeCompare(b.date) || a.id - b.id))
const slides = computed(() => ordered.value.flatMap((memory, m) => {
  const media = mediaOf(memory)
  return media.length ? media.map((item, i) => ({ memory, item, m, i, n: media.length })) : [{ memory, item: null, m, i: 0, n: 1 }]
}))
const index = ref(0)
const slide = computed(() => slides.value[index.value])
const finished = ref(false)
const paused = ref(false)
const muted = ref(false)
const progress = ref(0) // of the current slide, 0..1
const video = ref(null)
const member = id => state.couple?.members.find(m => m.id === id)
const barWidth = k => (k < slide.value.i ? 100 : k === slide.value.i ? progress.value * 100 : 0)

// Photo/card timer that can pause and resume where it left off.
let frame = null
let elapsed = 0
function stopTimer() { cancelAnimationFrame(frame); frame = null }
function runTimer() {
  stopTimer()
  const duration = slide.value.item ? PHOTO_MS : CARD_MS
  const startedAt = performance.now() - elapsed
  const tick = now => {
    elapsed = now - startedAt
    progress.value = Math.min(1, elapsed / duration)
    if (progress.value >= 1) next()
    else frame = requestAnimationFrame(tick)
  }
  frame = requestAnimationFrame(tick)
}
async function playVideo() {
  const v = video.value
  if (!v) return
  v.muted = muted.value
  try {
    await v.play()
  } catch {
    // Autoplay with sound was blocked: play muted instead (the speaker button turns sound on).
    muted.value = true
    v.muted = true
    try { await v.play() } catch { paused.value = true }
  }
}
async function show() {
  stopTimer()
  elapsed = 0
  progress.value = 0
  if (!slide.value) return
  const upcoming = slides.value[index.value + 1]?.item
  if (upcoming && !isVideo(upcoming)) photoSrc(upcoming.url) // preload the next photo
  if (paused.value) return
  if (isVideo(slide.value.item)) { await nextTick(); playVideo() } else runTimer()
}
watch(index, show)

function next() {
  if (index.value < slides.value.length - 1) index.value++
  else { stopTimer(); video.value?.pause(); finished.value = true }
}
function prev() {
  if (index.value > 0) index.value--
  else show()
}
function togglePause() {
  paused.value = !paused.value
  if (isVideo(slide.value?.item)) paused.value ? video.value?.pause() : playVideo()
  else if (paused.value) stopTimer()
  else runTimer()
}
function toggleMute() {
  muted.value = !muted.value
  if (video.value) video.value.muted = muted.value
}
function restart() {
  finished.value = false
  paused.value = false
  if (index.value === 0) show()
  else index.value = 0
}
function onVideoTime() {
  const v = video.value
  if (v?.duration) progress.value = v.currentTime / v.duration
}
function tap(event) {
  const x = event.clientX / window.innerWidth
  if (x < 0.3) prev()
  else if (x > 0.7) next()
  else togglePause()
}
function onKey(event) {
  if (event.key === 'Escape') emit('close')
  else if (finished.value) return
  else if (event.key === 'ArrowLeft') prev()
  else if (event.key === 'ArrowRight') next()
  else if (event.key === ' ') { event.preventDefault(); togglePause() }
}

let previousOverflow = ''
onMounted(() => {
  previousOverflow = document.body.style.overflow
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', onKey)
  show()
})
onBeforeUnmount(() => {
  stopTimer()
  document.body.style.overflow = previousOverflow
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div class="replay" role="dialog" aria-modal="true" :aria-label="title">
    <div v-if="!slides.length" class="replay-end">
      <p>Không có kỷ niệm nào trong khoảng này.</p>
      <button class="btn primary" @click="emit('close')">Đóng</button>
    </div>

    <template v-else-if="!finished">
      <div class="replay-stage" @click="tap">
        <video v-if="isVideo(slide.item)" ref="video" :key="slide.item.id" :src="slide.item.stream_url" playsinline preload="auto"
               @timeupdate="onVideoTime" @ended="next"></video>
        <PrivatePhoto v-else-if="slide.item" :key="slide.item.id" :url="slide.item.url" />
        <div v-else class="replay-card"><span>{{ slide.memory.emoji }}</span></div>
      </div>

      <!-- The memory's details, above every photo/video -->
      <header class="replay-top">
        <div class="replay-bars" aria-hidden="true">
          <span v-for="k in slide.n" :key="k" class="replay-bar"><span :style="{ width: `${barWidth(k - 1)}%` }"></span></span>
        </div>
        <div class="replay-head">
          <CharacterAvatar :user="member(slide.memory.author)" :size="36" />
          <div class="replay-meta">
            <strong>{{ slide.memory.emoji }} {{ slide.memory.title }}</strong>
            <small>{{ displayDate(slide.memory.date) }} · {{ slide.memory.author_name }} · {{ slide.m + 1 }}/{{ ordered.length }}</small>
          </div>
          <button class="replay-button" aria-label="Đóng" @click="emit('close')"><X :size="22" /></button>
        </div>
        <p v-if="slide.memory.story" class="replay-story">{{ slide.memory.story }}</p>
      </header>

      <footer class="replay-controls">
        <button class="replay-button" :aria-label="paused ? 'Tiếp tục' : 'Tạm dừng'" @click="togglePause">
          <Play v-if="paused" :size="20" fill="currentColor" /><Pause v-else :size="20" fill="currentColor" />
        </button>
        <button v-if="isVideo(slide.item)" class="replay-button" :aria-label="muted ? 'Bật tiếng' : 'Tắt tiếng'" @click="toggleMute">
          <VolumeX v-if="muted" :size="20" /><Volume2 v-else :size="20" />
        </button>
      </footer>
    </template>

    <div v-else class="replay-end">
      <p class="replay-end-title">Hết rồi ♡</p>
      <p>Đã xem lại {{ ordered.length }} kỷ niệm.</p>
      <div class="replay-end-actions">
        <button class="btn outline" @click="restart"><RotateCcw :size="18" /> Xem lại từ đầu</button>
        <button class="btn primary" @click="emit('close')">Đóng</button>
      </div>
    </div>
  </div>
</template>
