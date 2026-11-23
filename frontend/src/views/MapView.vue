<script setup>
// Every pinned memory on a map. Memories at the same spot share one marker (their latest photo);
// nearby markers cluster when zoomed out. Tapping a marker lists the memories at that place (within
// NEAR_KM), tapping a cluster lists everything in it; both with "Xem lại ở đây".
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Play, ZoomIn } from 'lucide-vue-next'
import { displayDate } from '@/format.js'
import { distanceKm, hasLocation, NEAR_KM, placeLabel, VIETNAM } from '@/location.js'
import { createMap, escapeHtml } from '@/map.js'
import { coverPhoto, photoSrc } from '@/photos.js'
import { state, navigate } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import ReplayPlayer from '@/components/ReplayPlayer.vue'

const props = defineProps({ focus: Number }) // a memory to center on (from its page)
const jar = ref(null) // filter: null = every jar
const pinned = computed(() => state.memories.filter(m => hasLocation(m) && (jar.value == null || m.jar === jar.value)))
const unpinned = computed(() => state.memories.length - state.memories.filter(hasLocation).length)
const jars = computed(() => state.jars.filter(j => state.memories.some(m => m.jar === j.id && hasLocation(m))))

// One marker per spot (~10 m): memories newest first.
const spots = computed(() => {
  const groups = new Map()
  for (const m of pinned.value) {
    const key = `${m.latitude.toFixed(4)},${m.longitude.toFixed(4)}`
    if (!groups.has(key)) groups.set(key, { key, latitude: m.latitude, longitude: m.longitude, memories: [] })
    groups.get(key).memories.push(m)
  }
  for (const g of groups.values()) g.memories.sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id)
  return [...groups.values()]
})
const selected = ref(null) // { title, memories (newest first), zoom? } for the sheet
const replaying = ref(null) // { title, memories }
const spotTitle = spot => spot.memories.find(m => m.place)?.place || 'Kỷ niệm ở đây'
const newestFirst = list => [...list].sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id)
function select(memories, zoom) {
  selected.value = { title: placeLabel(memories) || 'Kỷ niệm ở đây', memories: newestFirst(memories), zoom }
}
// A marker: every shown memory at the same place (within NEAR_KM of it).
const selectSpot = spot => select(pinned.value.filter(m => distanceKm(spot, m) <= NEAR_KM))

const element = ref(null)
const failed = ref(false)
let L, map, layer

function markerHtml(spot, src) {
  const cover = src ? `<img src="${escapeHtml(src)}" alt="">` : `<span>${escapeHtml(spot.memories[0].emoji)}</span>`
  const count = spot.memories.length > 1 ? `<b>${spot.memories.length}</b>` : ''
  return `<span class="map-photo">${cover}</span>${count}`
}
const spotIcon = (spot, src) => L.divIcon({ className: 'map-marker', html: markerHtml(spot, src), iconSize: [52, 52], iconAnchor: [26, 52] })

function draw(fit) {
  layer?.clearLayers()
  if (!layer) {
    layer = L.markerClusterGroup({
      showCoverageOnHover: false,
      zoomToBoundsOnClick: false, // a tap opens the list (with "Phóng to") instead
      maxClusterRadius: 56,
      iconCreateFunction: cluster => {
        const total = cluster.getAllChildMarkers().reduce((n, marker) => n + marker.options.count, 0)
        return L.divIcon({ className: 'map-cluster', html: `<span>${total}</span>`, iconSize: [44, 44] })
      },
    }).addTo(map)
    layer.on('clusterclick', event => {
      const cluster = event.layer
      select(cluster.getAllChildMarkers().flatMap(marker => marker.options.spot.memories), () => cluster.zoomToBounds({ padding: [48, 48] }))
    })
  }
  for (const spot of spots.value) {
    const marker = L.marker([spot.latitude, spot.longitude], { icon: spotIcon(spot), count: spot.memories.length, spot, title: spotTitle(spot) })
    marker.on('click', () => selectSpot(spot))
    layer.addLayer(marker)
    const cover = spot.memories.map(coverPhoto).find(Boolean)
    if (cover) photoSrc(cover.url).then(src => { if (src) marker.setIcon(spotIcon(spot, src)) })
  }
  if (!fit) return
  const focused = pinned.value.find(m => m.id === props.focus)
  if (focused) map.setView([focused.latitude, focused.longitude], 16)
  else if (spots.value.length) map.fitBounds(spots.value.map(s => [s.latitude, s.longitude]), { padding: [48, 48], maxZoom: 15 })
  else map.setView(VIETNAM.center, VIETNAM.zoom)
}
// Redraw when the filter changes (and re-fit) or the data changes (partner's edits, background refresh).
let drawnJar = null
watch(spots, () => {
  if (!map) return
  draw(jar.value !== drawnJar)
  drawnJar = jar.value
})

onMounted(async () => {
  try {
    ;({ L, map } = await createMap(element.value, { zoomControl: true }))
  } catch {
    failed.value = true
    return
  }
  draw(true)
})
onBeforeUnmount(() => map?.remove())

function open(memory) {
  selected.value = null
  navigate('memory', { id: memory.id })
}
function replayHere() {
  replaying.value = { title: `Kỷ niệm ở ${selected.value.title}`, memories: selected.value.memories }
  selected.value = null
}
function zoomIn() {
  const zoom = selected.value.zoom
  selected.value = null
  zoom()
}
const back = () => (props.focus ? navigate('memory', { id: props.focus }) : navigate('cabinet'))
</script>

<template>
  <div class="page map-page">
    <AppHeader title="Bản đồ kỷ niệm" back @back="back" />
    <div v-if="jars.length > 1" class="chips map-filter">
      <button class="chip" :class="jar == null ? 'chosen' : 'soft'" @click="jar = null">Tất cả</button>
      <button v-for="j in jars" :key="j.id" class="chip" :class="jar === j.id ? 'chosen' : 'soft'" @click="jar = j.id">{{ j.emoji }} {{ j.name }}</button>
    </div>

    <div ref="element" class="map full-map" aria-label="Bản đồ kỷ niệm"></div>
    <p v-if="failed" class="form-error" role="alert">Không tải được bản đồ, kiểm tra mạng nhé.</p>
    <p v-else-if="!state.memories.some(hasLocation)" class="muted center map-note">Chưa có kỷ niệm nào được ghim. Ảnh có vị trí sẽ tự ghim, hoặc thêm địa điểm trong từng kỷ niệm nhé.</p>
    <p v-else-if="unpinned" class="muted center map-note">{{ unpinned }} kỷ niệm chưa có địa điểm.</p>

    <BottomSheet v-if="selected" :title="selected.title" @close="selected = null">
      <div class="map-sheet-actions">
        <button class="btn primary block" @click="replayHere"><Play :size="18" fill="currentColor" /> Xem lại ở đây ({{ selected.memories.length }})</button>
        <button v-if="selected.zoom" class="btn outline block" @click="zoomIn"><ZoomIn :size="18" /> Phóng to</button>
      </div>
      <button v-for="m in selected.memories" :key="m.id" class="notification" @click="open(m)">
        <span class="row-icon">{{ m.emoji }}</span>
        <span class="row-text"><strong>{{ m.title }}</strong><small>{{ displayDate(m.date) }} · {{ m.place || m.author_name }}</small></span>
      </button>
    </BottomSheet>
    <ReplayPlayer v-if="replaying" :memories="replaying.memories" :title="replaying.title" @close="replaying = null" />
  </div>
</template>
