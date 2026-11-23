<script setup>
// Pick what to replay: a date range (quick presets or custom from/to dates) and optionally one place
// (memories pinned within NEAR_KM of each other). Emits `start` with the matching memories.
import { ref, computed } from 'vue'
import { Play } from 'lucide-vue-next'
import { isoDate } from '@/format.js'
import { placeGroups } from '@/location.js'
import { state } from '@/store.js'
import BottomSheet from '@/components/BottomSheet.vue'

const props = defineProps({ from: String, to: String })
const emit = defineEmits(['start', 'close'])

const today = isoDate()
const now = new Date()
const dates = computed(() => state.memories.map(m => m.date).sort())
const first = computed(() => dates.value[0] ?? today)
const last = computed(() => (dates.value.at(-1) > today ? dates.value.at(-1) : today))
const daysAgo = n => isoDate(new Date(now.getFullYear(), now.getMonth(), now.getDate() - n))
const presets = computed(() => [
  { label: '7 ngày qua', from: daysAgo(6), to: today },
  { label: 'Tháng này', from: isoDate(new Date(now.getFullYear(), now.getMonth(), 1)), to: today },
  { label: 'Năm nay', from: `${now.getFullYear()}-01-01`, to: today },
  { label: 'Tất cả', from: first.value, to: last.value },
])
const range = ref({ from: props.from || first.value, to: props.to || last.value })
const valid = computed(() => range.value.from && range.value.to && range.value.from <= range.value.to)
const places = computed(() => placeGroups(state.memories))
const place = ref('') // a place group's key; '' = everywhere
const inPlace = computed(() => {
  const group = places.value.find(g => g.key === place.value)
  return group ? new Set(group.memories.map(m => m.id)) : null
})
const selected = computed(() => (valid.value ? state.memories.filter(m => m.date >= range.value.from && m.date <= range.value.to && (!inPlace.value || inPlace.value.has(m.id))) : []))
const isPreset = p => p.from === range.value.from && p.to === range.value.to
</script>

<template>
  <BottomSheet title="Xem lại kỷ niệm ♡" @close="emit('close')">
    <form class="stack" @submit.prevent="emit('start', selected)">
      <div class="chips replay-presets">
        <button v-for="p in presets" :key="p.label" type="button" class="chip" :class="isPreset(p) ? 'chosen' : 'soft'" @click="range = { from: p.from, to: p.to }">{{ p.label }}</button>
      </div>
      <div class="range-fields">
        <label class="field">Từ ngày<input v-model="range.from" type="date" required :max="range.to" /></label>
        <label class="field">Đến ngày<input v-model="range.to" type="date" required :min="range.from" /></label>
      </div>
      <label v-if="places.length" class="field">Địa điểm
        <select v-model="place">
          <option value="">Mọi nơi</option>
          <option v-for="g in places" :key="g.key" :value="g.key">📍 {{ g.label }} ({{ g.memories.length }})</option>
        </select>
      </label>
      <p class="muted range-count" role="status">
        {{ !valid ? 'Ngày bắt đầu phải trước ngày kết thúc.' : selected.length ? `${selected.length} kỷ niệm${place ? ' ở địa điểm này' : ''} trong khoảng này` : `Chưa có kỷ niệm nào${place ? ' ở địa điểm này' : ''} trong khoảng này.` }}
      </p>
      <button class="btn primary block" :disabled="!selected.length"><Play :size="18" fill="currentColor" /> Bắt đầu xem lại</button>
    </form>
  </BottomSheet>
</template>
