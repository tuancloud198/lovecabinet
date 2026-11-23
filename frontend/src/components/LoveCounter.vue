<script setup>
// Tủ: "Bên nhau N ngày" with today's or the next anniversary. Asks for our dates until they're set.
import { ref, computed } from 'vue'
import { CalendarHeart } from 'lucide-vue-next'
import { daysTogether, upcomingAnniversaries } from '@/anniversaries.js'
import { daysUntil, displayDate, isoDate } from '@/format.js'
import { state } from '@/store.js'
import CoupleDatesSheet from '@/components/CoupleDatesSheet.vue'

const today = isoDate()
const days = computed(() => daysTogether(state.couple))
const upcoming = computed(() => upcomingAnniversaries(state.couple))
const todays = computed(() => upcoming.value.filter(a => a.date === today))
const next = computed(() => upcoming.value.find(a => a.date > today))
const editing = ref(false)
</script>

<template>
  <section v-if="days" class="love-counter">
    <button class="love-days" aria-label="Sửa ngày của chúng mình" @click="editing = true">
      <small>Bên nhau</small><strong>{{ days.toLocaleString('vi-VN') }}</strong><small>ngày <span class="heart">♡</span></small>
    </button>
    <p v-if="todays.length" class="love-today">🎉 Hôm nay: {{ todays.map(a => `${a.title} ${a.emoji}`).join(' · ') }}</p>
    <p v-else-if="next" class="love-next">Sắp tới: <strong>{{ next.emoji }} {{ next.title }}</strong> · còn {{ daysUntil(next.date) }} ngày ({{ displayDate(next.date) }})</p>
  </section>
  <section v-else class="love-counter empty">
    <p>Hai bạn gặp nhau và yêu nhau từ ngày nào? Thêm vào để đếm ngày bên nhau và nhắc các ngày kỷ niệm nhé.</p>
    <button class="btn primary small" @click="editing = true"><CalendarHeart :size="16" /> Thêm ngày của chúng mình</button>
  </section>
  <CoupleDatesSheet v-if="editing" @close="editing = false" />
</template>
