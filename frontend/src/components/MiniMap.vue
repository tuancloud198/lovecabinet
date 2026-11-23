<script setup>
// A small, still map with a pin per place (memory page). Tapping is handled by the parent.
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { createMap, pinIcon } from '@/map.js'

const props = defineProps({ points: { type: Array, required: true } }) // [{ latitude, longitude }]
const element = ref(null)
let L, map, pins

function show() {
  pins.clearLayers()
  const at = props.points.map(p => [p.latitude, p.longitude])
  for (const latLng of at) L.marker(latLng, { icon: pinIcon(L), interactive: false }).addTo(pins)
  if (at.length === 1) map.setView(at[0], 15)
  else if (at.length) map.fitBounds(at, { padding: [28, 28], maxZoom: 15 })
}
const STILL = { dragging: false, touchZoom: false, scrollWheelZoom: false, doubleClickZoom: false, boxZoom: false, keyboard: false, tap: false }
onMounted(async () => {
  try {
    ;({ L, map } = await createMap(element.value, STILL))
    pins = L.layerGroup().addTo(map)
    show()
  } catch { /* offline: the place names are still shown */ }
})
watch(() => JSON.stringify(props.points), () => map && show())
onBeforeUnmount(() => map?.remove())
</script>

<template>
  <div ref="element" class="map mini-map" aria-hidden="true"></div>
</template>
