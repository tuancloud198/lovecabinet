<script setup>
// Every place we've been on a map. Each photo/video is at its own GPS (else its memory's pin), so a
// memory can show up at several places. One marker per spot (~10 m) with a photo taken there; nearby
// markers cluster when zoomed out. Tapping a marker lists the memories with photos within NEAR_KM,
// tapping a cluster everything in it; "Xem lại ở đây" replays only the photos/videos taken there.
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { Play, ZoomIn } from 'lucide-vue-next'
import { displayDate } from '@/format.js'
import { distanceKm, mediaPoints, NEAR_KM, summarize, VIETNAM } from '@/location.js'
import { createMap, escapeHtml } from '@/map.js'
import { isVideo, photoSrc, thumbOf } from '@/photos.js'
import { state, navigate } from '@/store.js'
import AppHeader from '@/components/AppHeader.vue'
import BottomSheet from '@/components/BottomSheet.vue'
import ReplayPlayer from '@/components/ReplayPlayer.vue'

const props = defineProps({ focus: Number }) // a memory to center on (from its page)
const jar = ref(null) // filter: null = every jar
const allPoints = computed(() => mediaPoints(state.memories))
const points = computed(() => allPoints.value.filter(p => jar.value == null || p.memory.jar === jar.value))
const unpinned = computed(() => state.memories.length - new Set(allPoints.value.map(p => p.memory.id)).size)
const jars = computed(() => state.jars.filter(j => allPoints.value.some(p => p.memory.jar === j.id)))

// One marker per spot (~10 m).
const spots = computed(() => {
  const groups = new Map()
  for (const p of points.value) {
    const key = `${p.latitude.toFixed(4)},${p.longitude.toFixed(4)}`
    if (!groups.has(key)) groups.set(key, { key, latitude: p.latitude, longitude: p.longitude, points: [] })
    groups.get(key).points.push(p)
  }
  return [...groups.values()].map(spot => {
    const newest = [...spot.points].sort((a, b) => b.memory.date.localeCompare(a.memory.date) || b.memory.id - a.memory.id)
    return {
      ...spot,
      memoryIds: [...new Set(spot.points.map(p => p.memory.id))],
      cover: newest.find(p => p.item && !isVideo(p.item))?.item, // a photo taken at this spot
      emoji: newest[0].memory.emoji,
    }
  })
})

const selected = ref(null) // summarize(points) + zoom? for the sheet
const replaying = ref(null) // { title, memories, only }
const select = (pointsHere, zoom) => { selected.value = { ...summarize(pointsHere), zoom } }
// A marker: everything shown within NEAR_KM of it (photos of one place have slightly different GPS).
const selectSpot = spot => select(points.value.filter(p => distanceKm(spot, p) <= NEAR_KM))

const element = ref(null)
const failed = ref(false)
let L, map, layer

function markerHtml(spot, src) {
  const cover = src ? `<img src="${escapeHtml(src)}" alt="">` : `<span>${escapeHtml(spot.emoji)}</span>`
  const count = spot.memoryIds.length > 1 ? `<b>${spot.memoryIds.length}</b>` : ''
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
        const memories = new Set(cluster.getAllChildMarkers().flatMap(marker => marker.options.spot.memoryIds))
        return L.divIcon({ className: 'map-cluster', html: `<span>${memories.size}</span>`, iconSize: [44, 44] })
      },
    }).addTo(map)
    layer.on('clusterclick', event => {
      const cluster = event.layer
      select(cluster.getAllChildMarkers().flatMap(marker => marker.options.spot.points), () => cluster.zoomToBounds({ padding: [48, 48] }))
    })
  }
  for (const spot of spots.value) {
    const marker = L.marker([spot.latitude, spot.longitude], { icon: spotIcon(spot), spot, title: summarize(spot.points).label })
    marker.on('click', () => selectSpot(spot))
    layer.addLayer(marker)
    if (spot.cover) photoSrc(thumbOf(spot.cover)).then(src => { if (src) marker.setIcon(spotIcon(spot, src)) }) // the photo needs the token
  }
  if (!fit) return
  const focused = points.value.filter(p => p.memory.id === props.focus).map(p => [p.latitude, p.longitude])
  const all = focused.length ? focused : spots.value.map(s => [s.latitude, s.longitude])
  if (all.length) map.fitBounds(all, { padding: [48, 48], maxZoom: focused.length ? 16 : 15 })
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
  const { label, memories, only } = selected.value
  replaying.value = { title: `Kỷ niệm ở ${label}`, memories, only }
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
    <p v-else-if="!allPoints.length" class="muted center map-note">Chưa có kỷ niệm nào được ghim. Ảnh có vị trí sẽ tự ghim, hoặc thêm địa điểm trong từng kỷ niệm nhé.</p>
    <p v-else-if="unpinned" class="muted center map-note">{{ unpinned }} kỷ niệm chưa có địa điểm.</p>

    <BottomSheet v-if="selected" :title="selected.label" @close="selected = null">
      <div class="map-sheet-actions">
        <button class="btn primary block" @click="replayHere"><Play :size="18" fill="currentColor" /> Xem lại ở đây ({{ selected.memories.length }})</button>
        <button v-if="selected.zoom" class="btn outline block" @click="zoomIn"><ZoomIn :size="18" /> Phóng to</button>
      </div>
      <button v-for="m in selected.memories" :key="m.id" class="notification" @click="open(m)">
        <span class="row-icon">{{ m.emoji }}</span>
        <span class="row-text">
          <strong>{{ m.title }}</strong>
          <small>{{ displayDate(m.date) }}<template v-if="selected.itemsHere[m.id]"> · {{ selected.itemsHere[m.id] }}/{{ m.photos.length }} ảnh/video ở đây</template></small>
        </span>
      </button>
    </BottomSheet>
    <ReplayPlayer v-if="replaying" :memories="replaying.memories" :only="replaying.only" :title="replaying.title" @close="replaying = null" />
  </div>
</template>
