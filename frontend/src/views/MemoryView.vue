<script setup>
import { ref, computed } from 'vue'
import { Heart, Send, Trash2 } from 'lucide-vue-next'
import { api } from '@/api.js'
import { displayDate, timeAgo } from '@/format.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import PrivatePhoto from '@/components/PrivatePhoto.vue'

const props = defineProps({ id: Number })
const memory = computed(() => state.memories.find(m => m.id === props.id))
const photo = ref(0)
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
      <PrivatePhoto v-if="memory.photos.length" :key="memory.photos[photo]?.id" :url="memory.photos[Math.min(photo, memory.photos.length - 1)].url" />
      <span v-else class="photo-emoji">{{ memory.emoji }}</span>
    </div>
    <div v-if="memory.photos.length > 1" class="thumb-strip">
      <button v-for="(p, i) in memory.photos" :key="p.id" :class="{ chosen: photo === i }" :aria-label="`Ảnh ${i + 1}`" @click="photo = i"><PrivatePhoto :url="p.url" /></button>
    </div>
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
