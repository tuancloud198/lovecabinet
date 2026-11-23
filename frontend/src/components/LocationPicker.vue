<script setup>
// Pick or change where a memory happened: tap the map or drag the pin, search a place, or use the
// phone's current location. The place name is looked up automatically and can be edited.
// Emits `save` with { latitude, longitude, place } or null (remove the location).
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { LocateFixed, Search } from 'lucide-vue-next'
import { currentLocation, hasLocation, placeName, searchPlaces, VIETNAM } from '@/location.js'
import { createMap, pinIcon } from '@/map.js'
import { state } from '@/store.js'
import BottomSheet from '@/components/BottomSheet.vue'

const props = defineProps({ location: Object }) // { latitude, longitude, place } or null
const emit = defineEmits(['save', 'close'])

const pin = ref(hasLocation(props.location) ? { latitude: props.location.latitude, longitude: props.location.longitude } : null)
const place = ref(props.location?.place || '')
const naming = ref(false)
const query = ref('')
const results = ref(null) // null = no search yet
const searching = ref(false)
const locating = ref(false)
const error = ref('')
const element = ref(null)
let L, map, marker

// Without a pin yet, start around the latest pinned memory (most likely the same area), else Vietnam.
function startView() {
  if (pin.value) return [[pin.value.latitude, pin.value.longitude], 16]
  const latest = [...state.memories].filter(hasLocation).sort((a, b) => b.date.localeCompare(a.date))[0]
  return latest ? [[latest.latitude, latest.longitude], 13] : [VIETNAM.center, VIETNAM.zoom]
}

let lookup = 0
async function setPin(coords, { name, zoom } = {}) {
  pin.value = coords
  error.value = ''
  const at = [coords.latitude, coords.longitude]
  if (marker) marker.setLatLng(at)
  else if (map) {
    marker = L.marker(at, { icon: pinIcon(L), draggable: true, autoPan: true }).addTo(map)
    marker.on('dragend', () => { const p = marker.getLatLng(); setPin(round(p)) })
  }
  if (zoom) map?.setView(at, zoom)
  if (name !== undefined) { place.value = name; return }
  const id = ++lookup
  naming.value = true
  const found = await placeName(coords)
  if (id !== lookup) return // the pin moved again meanwhile
  naming.value = false
  if (found) place.value = found
}
const round = ({ lat, lng }) => ({ latitude: Math.round(lat * 1e6) / 1e6, longitude: Math.round(lng * 1e6) / 1e6 })

async function useCurrent() {
  locating.value = true
  error.value = ''
  try {
    await setPin(await currentLocation(), { zoom: 16 })
  } catch (e) {
    error.value = e.message
  } finally {
    locating.value = false
  }
}
async function search() {
  if (!query.value.trim()) return
  searching.value = true
  error.value = ''
  try {
    results.value = await searchPlaces(query.value.trim())
  } catch {
    results.value = null
    error.value = 'Không tìm được, thử lại sau nhé.'
  } finally {
    searching.value = false
  }
}
function choose(result) {
  results.value = null
  setPin({ latitude: result.latitude, longitude: result.longitude }, { name: result.place, zoom: 16 })
}
function save() {
  emit('save', { ...pin.value, place: place.value.trim().slice(0, 120) })
}

onMounted(async () => {
  try {
    ;({ L, map } = await createMap(element.value))
  } catch {
    error.value = 'Không tải được bản đồ, kiểm tra mạng nhé.'
    return
  }
  map.setView(...startView())
  map.on('click', event => setPin(round(event.latlng)))
  if (pin.value) setPin(pin.value, { name: place.value })
  await nextTick()
  setTimeout(() => map?.invalidateSize(), 150) // the sheet finished laying out
})
onBeforeUnmount(() => map?.remove())
</script>

<template>
  <BottomSheet title="Địa điểm ♡" @close="emit('close')">
    <div class="stack">
      <form class="place-search" @submit.prevent="search">
        <input v-model="query" type="search" maxlength="120" placeholder="Tìm địa điểm: Hồ Gươm, Đà Lạt…" aria-label="Tìm địa điểm" />
        <button class="icon-button" :disabled="searching" aria-label="Tìm"><Search :size="18" /></button>
      </form>
      <div v-if="results" class="place-results">
        <p v-if="!results.length" class="muted">Không thấy địa điểm nào.</p>
        <button v-for="r in results" :key="`${r.latitude},${r.longitude}`" type="button" class="place-result" @click="choose(r)">
          <strong>{{ r.place }}</strong><small>{{ r.detail }}</small>
        </button>
      </div>

      <div ref="element" class="map picker-map" aria-label="Bản đồ: chạm để ghim vị trí"></div>
      <p class="muted map-hint">{{ pin ? 'Kéo ghim hoặc chạm chỗ khác để đổi vị trí.' : 'Chạm vào bản đồ để ghim vị trí.' }}</p>
      <button type="button" class="btn outline small" :disabled="locating" @click="useCurrent"><LocateFixed :size="16" /> {{ locating ? 'Đang lấy vị trí…' : 'Vị trí hiện tại' }}</button>

      <label class="field">Tên địa điểm
        <input v-model="place" maxlength="120" :placeholder="naming ? 'Đang tìm tên địa điểm…' : 'Ví dụ: Quán cà phê đầu tiên'" :disabled="!pin" />
      </label>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button type="button" class="btn primary block" :disabled="!pin" @click="save">Lưu vị trí</button>
      <button v-if="hasLocation(location)" type="button" class="btn tertiary block" @click="emit('save', null)">Bỏ vị trí</button>
    </div>
  </BottomSheet>
</template>
