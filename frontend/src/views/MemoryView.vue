<script setup>
import { ref, computed } from 'vue'
import { Camera, Heart, ImagePlus, Play, Send, Trash2, X } from 'lucide-vue-next'
import { api, upload } from '@/api.js'
import { displayDate, timeAgo } from '@/format.js'
import { forgetPhoto, isVideo, mediaOf, uploadablePhoto } from '@/photos.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import PhotoViewer from '@/components/PhotoViewer.vue'
import PrivatePhoto from '@/components/PrivatePhoto.vue'
import UploadProgress from '@/components/UploadProgress.vue'

const props = defineProps({ id: Number })
const memory = computed(() => state.memories.find(m => m.id === props.id))
const media = computed(() => mediaOf(memory.value)) // oldest first: new items go to the end
const photo = ref(0)
const current = computed(() => Math.min(photo.value, Math.max(0, (media.value.length || 1) - 1)))
const item = computed(() => media.value[current.value])
// The full-screen viewer shows photos only; videos play in place with their own controls.
const images = computed(() => media.value.filter(p => !isVideo(p)))
const viewing = ref(false)
const progress = ref(null) // { done, total, part } while adding photos
const comment = ref('')
const member = id => state.couple.members.find(m => m.id === id)
const back = () => navigate('jar', { id: memory.value?.jar })

function react() {
  run(async () => { await api(`memories/${props.id}/react/`, { method: 'POST' }); await load() })
}
function send() {
  run(async () => {
    await api(`memories/${props.id}/comment/`, { method: 'POST', body: { text: comment.value } })
    comment.value = ''
    await load()
  })
}
function addPhotos(event) {
  const files = [...event.target.files]
  event.target.value = ''
  if (!files.length) return
  run(async () => {
    progress.value = { done: 0, total: files.length, part: 0 }
    try {
      for (const file of files) {
        const body = new FormData()
        body.append('memory', props.id)
        body.append('file', await uploadablePhoto(file))
        await upload('photos/', body, part => { progress.value.part = part })
        progress.value = { ...progress.value, done: progress.value.done + 1, part: 0 }
      }
      await new Promise(resolve => setTimeout(resolve, 700)) // let "5/5 · 100%" be seen
    } finally {
      await load() // show whatever was uploaded, even if a later photo failed
    }
    photo.value = media.value.length - 1 // show the newest item
    toast(`Đã thêm ${files.length} ảnh/video.`)
  })
}
function removePhoto(p) {
  if (!window.confirm(isVideo(p) ? 'Xóa video này?' : 'Xóa ảnh này?')) return
  run(async () => {
    await api(`photos/${p.id}/`, { method: 'DELETE' })
    await load()
    if (!isVideo(p)) forgetPhoto(p.url)
    toast(isVideo(p) ? 'Đã xóa video.' : 'Đã xóa ảnh.')
  })
}
function remove() {
  if (!window.confirm('Xóa kỷ niệm này?')) return
  run(async () => {
    const jar = memory.value.jar
    await api(`memories/${props.id}/`, { method: 'DELETE' })
    navigate('jar', { id: jar })
    await load()
    toast('Đã xóa kỷ niệm.')
  })
}
</script>

<template>
  <div v-if="memory" class="page">
    <AppHeader :title="displayDate(memory.date)" back @back="back">
      <button class="icon-button" aria-label="Xóa kỷ niệm" @click="remove"><Trash2 :size="20" /></button>
    </AppHeader>
    <div class="photo-frame">
      <template v-if="item">
        <video v-if="isVideo(item)" :key="item.id" class="photo-video" :src="item.stream_url" controls playsinline preload="metadata"></video>
        <button v-else type="button" class="photo-open" aria-label="Xem ảnh toàn màn hình" @click="viewing = true">
          <PrivatePhoto :url="item.url" />
        </button>
        <button type="button" class="photo-delete" :aria-label="isVideo(item) ? 'Xóa video này' : 'Xóa ảnh này'" :disabled="state.busy" @click="removePhoto(item)"><Trash2 :size="18" /></button>
      </template>
      <span v-else class="photo-emoji">{{ memory.emoji }}</span>
    </div>
    <div class="thumb-strip">
      <span v-for="(p, i) in media" :key="p.id" class="thumb-wrap" :class="{ chosen: current === i }">
        <button type="button" :aria-label="isVideo(p) ? `Video ${i + 1}` : `Ảnh ${i + 1}`" @click="photo = i">
          <span v-if="isVideo(p)" class="thumb-video"><video :src="`${p.stream_url}#t=0.1`" muted playsinline preload="metadata"></video><Play :size="16" fill="currentColor" /></span>
          <PrivatePhoto v-else :url="p.url" alt="" />
        </button>
        <button type="button" class="thumb-remove" :aria-label="isVideo(p) ? 'Xóa video' : 'Xóa ảnh'" :disabled="state.busy" @click="removePhoto(p)"><X :size="12" /></button>
      </span>
      <label class="thumb-add" aria-label="Thêm ảnh hoặc video từ thư viện"><ImagePlus :size="20" /><input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif,video/mp4,video/quicktime,video/webm,.mp4,.mov,.webm" multiple :disabled="state.busy" @change="addPhotos" /></label>
      <label class="thumb-add" aria-label="Chụp thêm ảnh hoặc quay video"><Camera :size="20" /><input type="file" accept="image/*,video/*" capture="environment" :disabled="state.busy" @change="addPhotos" /></label>
    </div>
    <UploadProgress v-if="state.busy && progress" v-bind="progress" />
    <PhotoViewer v-if="viewing && images.length" :urls="images.map(p => p.url)" :start="Math.max(0, images.indexOf(item))" private @close="viewing = false" />
    <section class="sheet-section">
      <h2 class="memory-title">{{ memory.emoji }} {{ memory.title }}</h2>
      <p class="muted">{{ memory.author_name }} · {{ timeAgo(memory.created_at) }}</p>
      <p v-if="memory.story" class="story">{{ memory.story }}</p>
      <button class="chip like" :class="{ liked: memory.liked }" :disabled="state.busy" @click="react">
        <Heart :size="16" :fill="memory.liked ? 'currentColor' : 'none'" /> {{ memory.liked ? 'Đã thích' : 'Thích' }} · {{ memory.likes }}
      </button>
      <h3 class="subhead">Lời nhắn của chúng ta</h3>
      <p v-if="!memory.comments.length" class="muted">Chưa có lời nhắn nào.</p>
      <div v-for="c in memory.comments" :key="c.id" class="comment">
        <CharacterAvatar :user="member(c.author)" mood="happy" :size="40" />
        <div><strong>{{ c.author_name }}</strong> <small class="muted">{{ timeAgo(c.created_at) }}</small><p>{{ c.text }}</p></div>
      </div>
      <form class="comment-form" @submit.prevent="send">
        <input v-model="comment" required maxlength="1000" placeholder="Để lại một lời nhắn…" aria-label="Lời nhắn" />
        <button class="icon-button send" :disabled="state.busy" aria-label="Gửi"><Send :size="18" /></button>
      </form>
    </section>
  </div>
</template>
