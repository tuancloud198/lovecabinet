<script setup>
import { ref, computed } from 'vue'
import { ChevronLeft, ChevronRight, Plus, X } from 'lucide-vue-next'
import { api } from '@/api.js'
import { daysUntil, isoDate, shortDate } from '@/format.js'
import { state, run, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import EmojiPicker from '@/components/EmojiPicker.vue'

const WEEKDAYS = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
const today = isoDate()
const month = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const eventsByDay = computed(() => state.events.reduce((byDay, e) => ((byDay[e.date] ||= []).push(e), byDay), {}))
const memoryDays = computed(() => new Set(state.memories.map(m => m.date)))
const cells = computed(() => {
  const first = month.value
  const offset = (first.getDay() + 6) % 7 // Monday-first
  const days = new Date(first.getFullYear(), first.getMonth() + 1, 0).getDate()
  return [...Array(offset).fill(null), ...Array.from({ length: days }, (_, i) => isoDate(new Date(first.getFullYear(), first.getMonth(), i + 1)))]
})
const upcoming = computed(() => state.events.filter(e => e.date >= today).sort((a, b) => a.date.localeCompare(b.date)))
const shift = n => { month.value = new Date(month.value.getFullYear(), month.value.getMonth() + n, 1) }

const adding = ref(false)
const form = ref({})
function startEvent(date = today) {
  form.value = { title: '', date, emoji: '🎂' }
  state.error = ''
  adding.value = true
}
function saveEvent() {
  run(async () => {
    state.events.push(await api('events/', { method: 'POST', body: form.value }))
    adding.value = false
    toast('Đã thêm sự kiện!')
  })
}
function removeEvent(event) {
  if (!window.confirm(`Xóa sự kiện "${event.title}"?`)) return
  run(async () => {
    await api(`events/${event.id}/`, { method: 'DELETE' })
    state.events = state.events.filter(e => e.id !== event.id)
  })
}
const countdown = d => { const n = daysUntil(d); return n === 0 ? 'Hôm nay' : `Còn ${n} ngày` }
</script>

<template>
  <div class="page">
    <AppHeader title="Lịch của chúng ta"><template #title-suffix><span class="heart">♡</span></template></AppHeader>
    <section class="calendar card">
      <div class="month-nav">
        <button class="icon-button" aria-label="Tháng trước" @click="shift(-1)"><ChevronLeft :size="20" /></button>
        <strong>Tháng {{ month.getMonth() + 1 }}, {{ month.getFullYear() }}</strong>
        <button class="icon-button" aria-label="Tháng sau" @click="shift(1)"><ChevronRight :size="20" /></button>
      </div>
      <div class="month-grid">
        <span v-for="w in WEEKDAYS" :key="w" class="weekday" :class="{ sunday: w === 'CN' }">{{ w }}</span>
        <template v-for="(day, i) in cells" :key="i">
          <span v-if="!day"></span>
          <button v-else class="day" :class="{ today: day === today, event: eventsByDay[day], sunday: i % 7 === 6 }" :aria-label="`Ngày ${Number(day.slice(8))}${eventsByDay[day] ? ', có sự kiện' : ''}`" @click="startEvent(day)">
            <span class="num">{{ Number(day.slice(8)) }}</span>
            <span v-if="eventsByDay[day]" class="day-emoji">{{ eventsByDay[day][0].emoji }}</span>
            <span v-else-if="memoryDays.has(day)" class="day-dot"></span>
          </button>
        </template>
      </div>
    </section>

    <section class="sheet-section">
      <h2 class="section-title">Sự kiện sắp tới</h2>
      <p v-if="!upcoming.length" class="muted">Chưa có sự kiện sắp tới. Lên lịch một buổi hẹn nhé!</p>
      <div v-for="e in upcoming" :key="e.id" class="event-row card">
        <span class="date-chip">{{ shortDate(e.date) }}</span>
        <span class="row-text"><strong>{{ e.title }} {{ e.emoji }}</strong></span>
        <span class="chip green">{{ countdown(e.date) }}</span>
        <button class="icon-button" :aria-label="`Xóa ${e.title}`" @click="removeEvent(e)"><X :size="16" /></button>
      </div>
    </section>

    <button class="fab" aria-label="Thêm sự kiện" @click="startEvent()"><Plus :size="26" /></button>

    <BottomSheet v-if="adding" title="Một ngày đặc biệt ♡" @close="adding = false">
      <form class="stack" @submit.prevent="saveEvent">
        <label class="field">Tên sự kiện<input v-model="form.title" required maxlength="150" placeholder="Kỷ niệm ngày yêu nhau" /></label>
        <label class="field">Ngày<input v-model="form.date" type="date" required /></label>
        <div class="field"><span>Biểu tượng</span><EmojiPicker v-model="form.emoji" /></div>
        <p v-if="state.error" class="form-error" role="alert">{{ state.error }}</p>
        <button class="btn primary block" :disabled="state.busy">Thêm vào lịch</button>
      </form>
    </BottomSheet>
  </div>
</template>
