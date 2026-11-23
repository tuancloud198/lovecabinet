<script setup>
// "Ngày này năm xưa": memories from this same date 1 week ago, 1 month ago and 1, 2, 3… years ago.
// A date that doesn't exist that month/year (31/02, 29/02) is skipped. Hidden when nothing matches.
import { ref, computed } from 'vue'
import { Play } from 'lucide-vue-next'
import { displayDate, isoDate } from '@/format.js'
import { coverPhoto } from '@/photos.js'
import { state, navigate } from '@/store.js'
import PrivatePhoto from '@/components/PrivatePhoto.vue'
import ReplayPlayer from '@/components/ReplayPlayer.vue'

const now = new Date()
const [y, m, d] = [now.getFullYear(), now.getMonth(), now.getDate()]
/** ISO date for (year, month, day), or null when that day doesn't exist (e.g. 31/02). */
const exact = (year, month, day) => {
  const date = new Date(year, month, day)
  return date.getDate() === day ? isoDate(date) : null
}

const groups = computed(() => {
  const byDate = new Map()
  for (const memory of state.memories) {
    if (!byDate.has(memory.date)) byDate.set(memory.date, [])
    byDate.get(memory.date).push(memory)
  }
  const oldest = Math.min(...state.memories.map(memory => Number(memory.date.slice(0, 4))), y)
  const candidates = [
    { label: '1 tuần trước', date: isoDate(new Date(y, m, d - 7)) },
    { label: '1 tháng trước', date: exact(y, m - 1, d) },
    ...Array.from({ length: y - oldest }, (_, i) => ({ label: `${i + 1} năm trước`, date: exact(y - i - 1, m, d) })),
  ]
  return candidates
    .filter(c => c.date && byDate.has(c.date))
    .map(c => ({ ...c, memories: byDate.get(c.date).sort((a, b) => a.id - b.id) }))
})
const all = computed(() => groups.value.flatMap(g => g.memories))
const replaying = ref(false)
</script>

<template>
  <section v-if="groups.length" class="on-this-day" aria-label="Ngày này năm xưa">
    <header class="on-this-day-head">
      <h2>Ngày này năm xưa <span class="heart">♡</span></h2>
      <button class="chip" @click="replaying = true"><Play :size="12" fill="currentColor" /> Xem lại</button>
    </header>
    <div v-for="g in groups" :key="g.date" class="on-this-day-group">
      <p class="on-this-day-label"><strong>{{ g.label }}</strong> · {{ displayDate(g.date) }}</p>
      <div class="on-this-day-strip">
        <button v-for="memory in g.memories" :key="memory.id" class="on-this-day-item" @click="navigate('memory', { id: memory.id })">
          <span class="on-this-day-thumb">
            <PrivatePhoto v-if="coverPhoto(memory)" :url="coverPhoto(memory).url" alt="" />
            <span v-else>{{ memory.emoji }}</span>
          </span>
          <span class="on-this-day-title">{{ memory.title }}</span>
        </button>
      </div>
    </div>
    <ReplayPlayer v-if="replaying" :memories="all" title="Ngày này năm xưa" @close="replaying = false" />
  </section>
</template>
