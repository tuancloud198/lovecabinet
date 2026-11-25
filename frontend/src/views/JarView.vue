<script setup>
import { ref, computed } from 'vue'
import { ChevronRight, Camera, Play, Trash2, MapPin } from 'lucide-vue-next'
import { api } from '@/api.js'
import { displayDate, daysUntil, isoDate } from '@/format.js'
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

// ---- filters (date range and place, like the replay sheet) and day groups ----
const today = isoDate()
const now = new Date()
const first = computed(() => memories.value.at(-1)?.date ?? today)
const last = computed(() => (memories.value[0]?.date > today ? memories.value[0].date : today))
const daysAgo = n => isoDate(new Date(now.getFullYear(), now.getMonth(), now.getDate() - n))
const presets = computed(() => [
  { label: '7 ngày qua', from: daysAgo(6), to: today },
  { label: 'Tháng này', from: isoDate(new Date(now.getFullYear(), now.getMonth(), 1)), to: today },
  { label: 'Năm nay', from: `${now.getFullYear()}-01-01`, to: today },
  { label: 'Tất cả', from: '', to: '' },
])
const range = ref({ from: '', to: '' }) // '' = no limit on that side
const isPreset = p => p.from === range.value.from && p.to === range.value.to
// Place: typed text, matched against the names of the memory's place and its photos' places (accents and
// a leading "Đường"/"Phố" ignored). Names come from reverse geocoding, which names the same area several
// ways ("Đường Tràng An, …" / "Tràng An, …"), so suggestions list each name once, keyed the same way.
const fold = text => (text || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/gi, 'd').toLowerCase().trim().replace(/^(duong|pho)\s+/, '')
const placesOf = m => [m.place, ...m.photos.map(p => p.place)].filter(Boolean)
const placeNames = computed(() => {
  const byKey = new Map() // folded name -> { name (the shortest spelling), count (memories) }
  for (const m of memories.value) {
    for (const name of new Set(placesOf(m))) {
      const entry = byKey.get(fold(name))
      if (!entry) byKey.set(fold(name), { name, count: 1, seen: m.id })
      else {
        if (name.length < entry.name.length) entry.name = name
        if (entry.seen !== m.id) { entry.count++; entry.seen = m.id }
      }
    }
  }
  return [...byKey.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
})
const placeQuery = ref('')
const filtered = computed(() => {
  const { from, to } = range.value
  const q = fold(placeQuery.value)
  return memories.value.filter(m => (!from || m.date >= from) && (!to || m.date <= to) && (!q || placesOf(m).some(name => fold(name).includes(q))))
})
const filtering = computed(() => !!(range.value.from || range.value.to || fold(placeQuery.value)))
function clearFilters() { range.value = { from: '', to: '' }; placeQuery.value = '' }
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
      <div v-if="memories.length > 1" class="jar-filters stack">
        <div class="chips replay-presets">
          <button v-for="p in presets" :key="p.label" type="button" class="chip" :class="isPreset(p) ? 'chosen' : 'soft'" @click="range = { from: p.from, to: p.to }">{{ p.label }}</button>
        </div>
        <div class="range-fields">
          <label class="field">Từ ngày<input v-model="range.from" type="date" :min="first" :max="range.to || last" /></label>
          <label class="field">Đến ngày<input v-model="range.to" type="date" :min="range.from || first" :max="last" /></label>
        </div>
        <label v-if="placeNames.length" class="field">Địa điểm
          <input v-model="placeQuery" type="search" list="jar-places" placeholder="Mọi nơi · gõ để tìm, vd. Tràng An" autocomplete="off" enterkeyhint="search" />
          <datalist id="jar-places"><option v-for="p in placeNames" :key="p.name" :value="p.name">{{ p.count }} kỷ niệm</option></datalist>
        </label>
      </div>
      <div v-if="memories.length && !filtered.length" class="jar-no-match">
        <p>Không có kỷ niệm nào khớp bộ lọc.</p>
        <button class="btn small" @click="clearFilters">Xóa bộ lọc</button>
      </div>
      <template v-for="g in groups" :key="g.date">
        <h3 v-if="g.month" class="day-month">{{ g.month }}</h3>
        <div class="day-head"><strong>{{ g.label }}</strong></div>
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
