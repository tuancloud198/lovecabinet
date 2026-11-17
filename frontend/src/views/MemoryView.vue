<script setup>
import { ref, computed } from 'vue'
import { Camera, Heart, ImagePlus, Send, Trash2, X } from 'lucide-vue-next'
import { api } from '@/api.js'
import { displayDate, timeAgo } from '@/format.js'
import { forgetPhoto } from '@/photos.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import PhotoViewer from '@/components/PhotoViewer.vue'
import PrivatePhoto from '@/components/PrivatePhoto.vue'

const props = defineProps({ id: Number })
const memory = computed(() => state.memories.find(m => m.id === props.id))
const photo = ref(0)
const current = computed(() => Math.min(photo.value, Math.max(0, (memory.value?.photos.length || 1) - 1)))
const viewing = ref(false)
const mine = computed(() => memory.value?.author === state.me.id)
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
    try {
      for (const file of files) {
        const body = new FormData()
        body.append('memory', props.id)
        body.append('file', file)
        await api('photos/', { method: 'POST', body })
      }
    } finally {
      await load() // show whatever was uploaded, even if a later photo failed
    }
    photo.value = memory.value.photos.length - 1
    toast(files.length > 1 ? `Đã thêm ${files.length} ảnh.` : 'Đã thêm ảnh.')
  })
}
function removePhoto(p) {
  if (!window.confirm('Xóa ảnh này?')) return
  run(async () => {
    await api(`photos/${p.id}/`, { method: 'DELETE' })
    await load()
    forgetPhoto(p.url)
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
      <button v-if="memory.author === state.me.id" class="icon-button" aria-label="Xóa kỷ niệm" @click="remove"><Trash2 :size="20" /></button>
    </AppHeader>
    <div class="photo-frame">
      <button v-if="memory.photos.length" type="button" class="photo-open" aria-label="Xem ảnh toàn màn hình" @click="viewing = true">
        <PrivatePhoto :url="memory.photos[current].url" />
      </button>
      <span v-else class="photo-emoji">{{ memory.emoji }}</span>
    </div>
    <div v-if="memory.photos.length > 1 || mine" class="thumb-strip">
      <span v-for="(p, i) in memory.photos" :key="p.id" class="thumb-wrap" :class="{ chosen: current === i }">
        <button type="button" :aria-label="`Ảnh ${i + 1}`" @click="photo = i"><PrivatePhoto :url="p.url" alt="" /></button>
        <button v-if="mine" type="button" class="thumb-remove" aria-label="Xóa ảnh" :disabled="state.busy" @click="removePhoto(p)"><X :size="12" /></button>
      </span>
      <template v-if="mine">
        <label class="thumb-add" aria-label="Thêm ảnh từ thư viện"><ImagePlus :size="20" /><input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif,.heic,.heif" multiple :disabled="state.busy" @change="addPhotos" /></label>
        <label class="thumb-add" aria-label="Chụp thêm ảnh"><Camera :size="20" /><input type="file" accept="image/*" capture="environment" :disabled="state.busy" @change="addPhotos" /></label>
      </template>
    </div>
    <PhotoViewer v-if="viewing" :urls="memory.photos.map(p => p.url)" :start="current" private @close="viewing = false" />
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
