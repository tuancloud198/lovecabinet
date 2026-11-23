// Leaflet (OpenStreetMap) loaded on demand: the map code and CSS are only downloaded when a map
// is shown. leaflet.markercluster is a UMD build that extends the global `L`.
import { ATTRIBUTION, TILES } from '@/location.js'

let loading = null
export function loadLeaflet() {
  loading ??= (async () => {
    const [{ default: L }] = await Promise.all([import('leaflet'), import('leaflet/dist/leaflet.css')])
    window.L = L
    await Promise.all([import('leaflet.markercluster'), import('leaflet.markercluster/dist/MarkerCluster.css')])
    return L
  })().catch(error => { loading = null; throw error })
  return loading
}

/** A Leaflet map with OpenStreetMap tiles in `element`. */
export async function createMap(element, options = {}) {
  const L = await loadLeaflet()
  const map = L.map(element, { zoomControl: false, ...options })
  L.tileLayer(TILES, { attribution: ATTRIBUTION, maxZoom: 19 }).addTo(map)
  map.attributionControl.setPrefix(false)
  return { L, map }
}

export const pinIcon = L => L.divIcon({ className: 'map-pin', html: '<span></span>', iconSize: [30, 30], iconAnchor: [15, 30] })

const ENTITIES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }
/** For user text (emoji, names) put into marker HTML. */
export const escapeHtml = text => String(text ?? '').replace(/[&<>"']/g, c => ENTITIES[c])
