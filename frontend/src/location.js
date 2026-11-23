// Where a memory happened. Priority: the GPS in the photos' metadata (EXIF), then the phone's
// current location or a place picked by hand. Place names come from OpenStreetMap Nominatim
// (called from the browser; its policy allows ~1 request/s and no search-as-you-type).

const NOMINATIM = 'https://nominatim.openstreetmap.org'
export const TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
export const ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
export const VIETNAM = { center: [16.0, 106.5], zoom: 5 } // the map's start when nothing is pinned yet

const round = n => Math.round(n * 1e6) / 1e6
const valid = (lat, lng) => Number.isFinite(lat) && Number.isFinite(lng) && Math.abs(lat) <= 90 && Math.abs(lng) <= 180 && !(lat === 0 && lng === 0)
export const hasLocation = memory => memory?.latitude != null && memory?.longitude != null

/** { latitude, longitude } from a photo's EXIF GPS (JPEG, HEIC, PNG, WebP), or null. Must run before
 * uploadablePhoto(): the canvas re-encode drops all metadata. */
export async function photoLocation(file) {
  if (/^video\//.test(file.type)) return null
  try {
    const { default: exifr } = await import('exifr') // loaded only when photos are picked
    const gps = await exifr.gps(file)
    return gps && valid(gps.latitude, gps.longitude) ? { latitude: round(gps.latitude), longitude: round(gps.longitude) } : null
  } catch {
    return null
  }
}

/** The first location found in the files, checked in order. */
export async function firstPhotoLocation(files) {
  for (const file of files) {
    const location = await photoLocation(file)
    if (location) return location
  }
  return null
}

/** The phone's current position (asks for permission). Rejects with a Vietnamese message. */
export function currentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error('Trình duyệt không hỗ trợ lấy vị trí.'))
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => resolve({ latitude: round(coords.latitude), longitude: round(coords.longitude) }),
      error => reject(new Error(error.code === 1 ? 'Bạn chưa cho phép truy cập vị trí.' : 'Không lấy được vị trí, thử lại nhé.')),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 },
    )
  })
}

// "Hồ Xuân Hương, Đà Lạt": the place's own name (or road) plus its city/town.
function shortName(result) {
  const a = result.address || {}
  const area = a.city || a.town || a.village || a.county || a.state || ''
  const name = result.name || a.road || ''
  return [...new Set([name, area].filter(Boolean))].join(', ').slice(0, 120) || (result.display_name || '').split(',').slice(0, 2).join(',').trim()
}

async function nominatim(path, params) {
  const query = new URLSearchParams({ format: 'jsonv2', 'accept-language': 'vi', ...params })
  const response = await fetch(`${NOMINATIM}/${path}?${query}`, { signal: AbortSignal.timeout(10000) })
  if (!response.ok) throw new Error(String(response.status))
  return response.json()
}

const names = new Map()
/** Short place name for a point, or '' if it can't be looked up (offline, rate limited). */
export async function placeName({ latitude, longitude }) {
  const key = `${latitude.toFixed(4)},${longitude.toFixed(4)}`
  if (!names.has(key)) {
    names.set(key, nominatim('reverse', { lat: latitude, lon: longitude, zoom: 16 }).then(shortName).catch(() => { names.delete(key); return '' }))
  }
  return names.get(key)
}

/** Places matching a search (on submit only), as [{ place, latitude, longitude }]. */
export async function searchPlaces(text) {
  const results = await nominatim('search', { q: text, limit: 5, addressdetails: 1 })
  return results.map(r => ({ place: shortName(r), detail: r.display_name, latitude: round(Number(r.lat)), longitude: round(Number(r.lon)) }))
}

// ---- "Same place": memories within NEAR_KM of each other (GPS from photos of one place varies) ----
export const NEAR_KM = 1
/** Distance between two { latitude, longitude } in km (haversine). */
export function distanceKm(a, b) {
  const rad = d => (d * Math.PI) / 180
  const dLat = rad(b.latitude - a.latitude)
  const dLng = rad(b.longitude - a.longitude)
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a.latitude)) * Math.cos(rad(b.latitude)) * Math.sin(dLng / 2) ** 2
  return 6371 * 2 * Math.asin(Math.sqrt(h))
}
/** The most used place name among memories; a tie goes to the oldest memory's ('' if none has one). */
export function placeLabel(memories) {
  const counts = new Map() // insertion order = oldest first, and sort() is stable
  for (const m of [...memories].sort((a, b) => a.date.localeCompare(b.date) || a.id - b.id)) if (m.place) counts.set(m.place, (counts.get(m.place) || 0) + 1)
  return [...counts].sort((a, b) => b[1] - a[1])[0]?.[0] || ''
}
/** Pinned memories grouped by place (each within NEAR_KM of the group's first memory), biggest first:
 * [{ key, label, latitude, longitude, memories }]. */
export function placeGroups(memories) {
  const groups = []
  for (const m of memories.filter(hasLocation).sort((a, b) => a.date.localeCompare(b.date) || a.id - b.id)) {
    const group = groups.find(g => distanceKm(g, m) <= NEAR_KM)
    if (group) group.memories.push(m)
    else groups.push({ key: `${m.latitude},${m.longitude}`, latitude: m.latitude, longitude: m.longitude, memories: [m] })
  }
  for (const g of groups) g.label = placeLabel(g.memories) || 'Địa điểm chưa đặt tên'
  return groups.sort((a, b) => b.memories.length - a.memories.length || a.label.localeCompare(b.label))
}
