<script setup>
import { ref, computed } from 'vue'
import { Bell, Heart, Map as MapIcon, MessageCircle, Play, Plus } from 'lucide-vue-next'
import { api } from '@/api.js'
import { timeAgo } from '@/format.js'
import { state, partner, navigate, run, cabinetForYear, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import EmojiPicker from '@/components/EmojiPicker.vue'
import EmptyState from '@/components/EmptyState.vue'
import JarArt from '@/components/JarArt.vue'
import ReplayPlayer from '@/components/ReplayPlayer.vue'
import ReplayRangeSheet from '@/components/ReplayRangeSheet.vue'

const JAR_COLORS = ['#F6C9C4', '#BFD7EA', '#F3D9A4', '#CFE3CF', '#E3D3EE']
// A couple has one cabinet (Tủ): show every jar in it.
const jars = computed(() => state.jars)
const memoriesIn = jar => state.memories.filter(m => m.jar === jar.id)
const emojisIn = jar => {
  const emojis = memoriesIn(jar).map(m => m.emoji)
  return emojis.length ? emojis : [jar.emoji]
}

// Notifications: what the partner added recently (memories and comments).
const SEEN_KEY = 'notifications-seen'
const readSeen = () => { try { return localStorage.getItem(SEEN_KEY) || '' } catch { return '' } }
const seen = ref(readSeen())
const notifications = computed(() => {
  const pid = partner.value?.id
  const items = []
  for (const m of state.memories) {
    if (m.author === pid) items.push({ key: 'm' + m.id, memory: m, at: m.created_at, title: 'Có kỷ niệm mới', text: `${m.author_name} vừa lưu "${m.title}".`, icon: Heart })
    for (const c of m.comments) if (c.author === pid) items.push({ key: 'c' + c.id, memory: m, at: c.created_at, title: 'Lời nhắn mới', text: `${c.author_name}: ${c.text}`, icon: MessageCircle })
  }
  return items.sort((a, b) => b.at.localeCompare(a.at)).slice(0, 20)
})
const unread = computed(() => notifications.value.some(n => n.at > seen.value))
const showNotifications = ref(false)
function openNotifications() {
  showNotifications.value = true
  seen.value = new Date().toISOString()
  try { localStorage.setItem(SEEN_KEY, seen.value) } catch { /* optional */ }
}

// Replay memories from a date range (defaults to all of them).
const choosingRange = ref(false)
const replaying = ref(null)
function replayRange(memories) {
  choosingRange.value = false
  replaying.value = memories
}

const addingJar = ref(false)
const form = ref({})
function startJar() {
  form.value = { name: '', emoji: '❤️', color: JAR_COLORS[0] }
  state.error = ''
  addingJar.value = true
}
function saveJar() {
  run(async () => {
    const cabinet = state.cabinets[0] ?? (await cabinetForYear(new Date().getFullYear()))
    state.jars.push(await api('jars/', { method: 'POST', body: { ...form.value, cabinet: cabinet.id } }))
    addingJar.value = false
    toast('Đã tạo hũ mới!')
  })
}
</script>

<template>
  <div class="page">
    <AppHeader title="Tủ thương">
      <button class="icon-button bell" aria-label="Thông báo" @click="openNotifications"><Bell :size="22" /><span v-if="unread" class="dot"></span></button>
    </AppHeader>

    <div class="couple-head">
      <CharacterAvatar :user="state.me" :size="56" />
      <span class="heart" aria-hidden="true">♡</span>
      <CharacterAvatar :user="partner" :size="56" />
      <span class="visually-hidden">Tủ chung của {{ state.me.display_name }} và {{ partner?.display_name }}</span>
    </div>
    <div v-if="state.memories.length" class="cabinet-actions">
      <button class="chip replay-chip" @click="choosingRange = true"><Play :size="14" fill="currentColor" /> Xem lại kỷ niệm</button>
      <button class="chip replay-chip" @click="navigate('map')"><MapIcon :size="14" /> Bản đồ</button>
    </div>
    <ReplayRangeSheet v-if="choosingRange" @start="replayRange" @close="choosingRange = false" />
    <ReplayPlayer v-if="replaying" :memories="replaying" @close="replaying = null" />

    <div class="cabinet">
      <div v-if="!jars.length" class="cabinet-empty">
        <EmptyState title="Chưa có hũ nào" text="Tạo một hũ nhỏ cho chuyến đi, ngày đặc biệt hay những buổi cà phê nhé!">
          <button class="btn primary" @click="startJar"><Plus :size="18" /> Tạo hũ</button>
        </EmptyState>
      </div>
      <div v-else class="shelf-grid">
        <button v-for="jar in jars" :key="jar.id" class="shelf-cell" @click="navigate('jar', { id: jar.id })">
          <JarArt :color="jar.color" :emojis="emojisIn(jar)" />
          <span class="jar-label"><strong>{{ jar.name }}</strong><small>{{ memoriesIn(jar).length }} kỷ niệm</small></span>
        </button>
        <button class="shelf-cell new-jar" @click="startJar">
          <span class="new-jar-slot"><Plus :size="28" /></span>
          <span class="jar-label"><strong>Hũ mới</strong><small>Cho những điều sắp tới</small></span>
        </button>
      </div>
    </div>

    <BottomSheet v-if="addingJar" title="Một hũ mới ♡" @close="addingJar = false">
      <form class="stack" @submit.prevent="saveJar">
        <div class="jar-preview"><JarArt :color="form.color" :emojis="[form.emoji]" /></div>
        <label class="field">Tên hũ<input v-model="form.name" required maxlength="100" placeholder="Ví dụ: Đà Lạt 2026" /></label>
        <div class="field"><span>Màu nơ</span>
          <div class="swatches"><button v-for="c in JAR_COLORS" :key="c" type="button" :style="{ background: c }" :class="{ chosen: form.color === c }" :aria-label="`Màu ${c}`" @click="form.color = c"></button></div>
        </div>
        <div class="field"><span>Biểu tượng</span><EmojiPicker v-model="form.emoji" /></div>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy">Đặt lên kệ</button>
      </form>
    </BottomSheet>

    <BottomSheet v-if="showNotifications" title="Thông báo" @close="showNotifications = false">
      <p v-if="!notifications.length" class="muted center">Chưa có gì mới từ người ấy.</p>
      <button v-for="n in notifications" :key="n.key" class="notification" @click="showNotifications = false; navigate('memory', { id: n.memory.id })">
        <span class="row-icon"><component :is="n.icon" :size="18" /></span>
        <span class="row-text"><strong>{{ n.title }}</strong><small>{{ n.text }}</small></span>
        <small class="muted">{{ timeAgo(n.at) }}</small>
      </button>
    </BottomSheet>
  </div>
</template>
