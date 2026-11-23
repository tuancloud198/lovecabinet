<script setup>
// A small, still map with one pin (memory page). Tapping is handled by the parent.
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { createMap, pinIcon } from '@/map.js'

const props = defineProps({ latitude: Number, longitude: Number })
const element = ref(null)
let map, marker

const STILL = { dragging: false, touchZoom: false, scrollWheelZoom: false, doubleClickZoom: false, boxZoom: false, keyboard: false, tap: false }
onMounted(async () => {
  try {
    const { L, map: created } = await createMap(element.value, STILL)
    map = created
    map.setView([props.latitude, props.longitude], 15)
    marker = L.marker([props.latitude, props.longitude], { icon: pinIcon(L), interactive: false }).addTo(map)
  } catch { /* offline: the place name is still shown */ }
})
watch(() => [props.latitude, props.longitude], at => { map?.setView(at, 15); marker?.setLatLng(at) })
onBeforeUnmount(() => map?.remove())
</script>

<template>
  <div ref="element" class="map mini-map" aria-hidden="true"></div>
</template>
