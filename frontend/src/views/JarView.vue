<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, Camera, Play, Trash2, MapPin } from 'lucide-vue-next'
import { api } from '@/api.js'
import { displayDate, daysUntil, shortDate } from '@/format.js'
import { placeGroups } from '@/location.js'
import { state, navigate, run, load, toast } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import CharacterAvatar from '@/components/CharacterAvatar.vue'
import EmojiIcon from '@/components/EmojiIcon.vue'
import EmptyState from '@/components/EmptyState.vue'
import JarArt from '@/components/JarArt.vue'
import PrivatePhoto from '@/components/PrivatePhoto.vue'
import ReplayPlayer from '@/components/ReplayPlayer.vue'
import { coverPhoto, thumbOf } from '@/photos.js'

const props = defineProps({ id: Number })
const jar = computed(() => state.jars.find(j => j.id === props.id))
const member = id => state.couple.members.find(m => m.id === id)
const memories = computed(() => state.memories.filter(m => m.jar === props.id).sort((a, b) => b.date.localeCompare(a.date)))
const replaying = ref(false) // replay every memory in this jar (oldest first)

// ---- filters (month and place) and day groups ----
const month = ref(null) // 'YYYY-MM' or 'YYYY-MM-DD' (prefix of memory.date), or null = all
const placeKey = ref(null) // placeGroups key or null = all
// Date options: the months present, or the days when everything is in one month.
const monthList = computed(() => [...new Set(memories.value.map(m => m.date.slice(0, 7)))])
const months = computed(() => monthList.value.length > 1 ? monthList.value : [...new Set(memories.value.map(m => m.date))])
const places = computed(() => placeGroups(memories.value))
const showMonths = computed(() => months.value.length > 1)
const showPlaces = computed(() => places.value.length > 1 || (places.value.length === 1 && places.value[0].memories.length < memories.value.length))
const monthLabel = key => key.length > 7 ? shortDate(key) : `Th ${key.slice(5)}/${key.slice(0, 4)}`
const filtered = computed(() => {
  const ids = placeKey.value == null ? null : new Set(places.value.find(g => g.key === placeKey.value)?.memories.map(m => m.id) ?? [])
  return memories.value.filter(m => (month.value == null || m.date.startsWith(month.value)) && (!ids || ids.has(m.id)))
})
const filtering = computed(() => month.value != null || placeKey.value != null)
function clearFilters() { month.value = null; placeKey.value = null }
const WEEKDAYS = ['Chủ nhật', 'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy']
function dayLabel(iso) {
  const diff = daysUntil(iso)
  if (diff === 0) return 'Hôm nay'
  if (diff === -1) return 'Hôm qua'
  const [y, m, d] = iso.split('-').map(Number)
  return `${WEEKDAYS[new Date(y, m - 1, d).getDay()]}, ${displayDate(iso)}`
}
// [{ date, label, month (set on the first day of a new month when the list spans several), items }]
const groups = computed(() => {
  const out = []
  const spans = new Set(filtered.value.map(m => m.date.slice(0, 7))).size > 1
  for (const m of filtered.value) {
    let g = out[out.length - 1]
    if (g?.date !== m.date) {
      const ym = m.date.slice(0, 7)
      g = { date: m.date, label: dayLabel(m.date), month: spans && ym !== out[out.length - 1]?.ym ? `Tháng ${ym.slice(5)}/${ym.slice(0, 4)}` : '', ym, items: [] }
      out.push(g)
    }
    g.items.push(m)
  }
  return out
})
const placeOf = m => m.place || m.photos.find(p => p.place)?.place || ''

function removeJar() {
  if (!window.confirm(`Xóa hũ "${jar.value.name}" và tất cả kỷ niệm bên trong?`)) return
  run(async () => {
    await api(`jars/${props.id}/`, { method: 'DELETE' })
    navigate('cabinet')
    await load()
    toast('Đã xóa hũ.')
  })
}
</script>

<template>
  <div v-if="jar" class="page">
    <AppHeader :title="jar.name" :subtitle="`${memories.length} kỷ niệm`" back @back="navigate('cabinet')">
      <button class="icon-button" aria-label="Xóa hũ" @click="removeJar"><Trash2 :size="20" /></button>
    </AppHeader>
    <div class="jar-stage">
      <JarArt :color="jar.color" :emojis="memories.length ? memories.map(m => m.emoji) : [jar.emoji]" large />
    </div>
    <button v-if="memories.length" class="chip replay-chip jar-replay" @click="replaying = true"><Play :size="14" fill="currentColor" /> Xem lại cả hũ</button>
    <ReplayPlayer v-if="replaying" :memories="memories" :title="`Hũ ${jar.name}`" @close="replaying = false" />
    <section class="sheet-section">
      <div class="section-head"><h2>Các kỷ niệm trong hũ ({{ filtering ? `${filtered.length}/${memories.length}` : memories.length }})</h2><button class="btn small primary" @click="navigate('capture', { jarId: jar.id })"><Camera :size="16" /> Thêm</button></div>
      <EmptyState v-if="!memories.length" title="Chưa có kỷ niệm nào" text="Hãy chụp một bức ảnh để lưu giữ khoảnh khắc đầu tiên cùng nhau nhé! ♡">
        <button class="btn primary" @click="navigate('capture', { jarId: jar.id })"><Camera :size="18" /> Chụp ngay</button>
      </EmptyState>
      <template v-if="memories.length > 1 && (showMonths || showPlaces)">
        <div v-if="showMonths" class="chips jar-filter">
          <button class="chip" :class="month == null ? 'chosen' : 'soft'" @click="month = null">Tất cả</button>
          <button v-for="ym in months" :key="ym" class="chip" :class="month === ym ? 'chosen' : 'soft'" @click="month = month === ym ? null : ym">{{ monthLabel(ym) }}</button>
        </div>
        <div v-if="showPlaces" class="chips jar-filter">
          <button class="chip" :class="placeKey == null ? 'chosen' : 'soft'" @click="placeKey = null"><MapPin :size="13" /> Mọi nơi</button>
          <button v-for="g in places" :key="g.key" class="chip" :class="placeKey === g.key ? 'chosen' : 'soft'" @click="placeKey = placeKey === g.key ? null : g.key">{{ g.label }} · {{ g.memories.length }}</button>
        </div>
      </template>
      <div v-if="memories.length && !filtered.length" class="jar-no-match">
        <p>Không có kỷ niệm nào khớp bộ lọc.</p>
        <button class="btn small" @click="clearFilters">Xóa bộ lọc</button>
      </div>
      <template v-for="g in groups" :key="g.date">
        <h3 v-if="g.month" class="day-month">{{ g.month }}</h3>
        <div class="day-head"><strong>{{ g.label }}</strong><small>{{ g.items.length }} kỷ niệm</small></div>
        <button v-for="m in g.items" :key="m.id" class="memory-row card" @click="navigate('memory', { id: m.id })">
          <span class="thumb"><PrivatePhoto v-if="coverPhoto(m)" :url="thumbOf(coverPhoto(m))" /><EmojiIcon v-else :emoji="m.photos.length ? '🎬' : m.emoji" /></span>
          <span class="row-text"><small class="date"><EmojiIcon :emoji="m.emoji" /> <template v-if="placeOf(m)"><MapPin :size="11" /> {{ placeOf(m) }}</template></small><strong>{{ m.title }}</strong><small class="clamp">{{ m.story }}</small></span>
          <CharacterAvatar :user="member(m.author)" :size="32" :title="m.author_name" />
          <ChevronRight :size="20" />
        </button>
      </template>
    </section>
  </div>
</template>
