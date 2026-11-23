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

let lastRequest = 0
async function nominatim(path, params) {
  const wait = lastRequest + 1100 - Date.now() // usage policy: at most 1 request per second
  lastRequest = Date.now() + Math.max(0, wait)
  if (wait > 0) await new Promise(resolve => setTimeout(resolve, wait))
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
/** Every place where a memory has something: one point per photo/video, at its own GPS or else at the
 * memory's pin; a memory without media is one point at its pin. A memory can be at several places.
 * [{ memory, item (photo/video or null), latitude, longitude, place }] */
export function mediaPoints(memories) {
  const points = []
  for (const memory of memories) {
    const pinned = hasLocation(memory)
    const media = memory.photos ?? []
    if (!media.length && pinned) points.push({ memory, item: null, latitude: memory.latitude, longitude: memory.longitude, place: memory.place })
    for (const item of media) {
      if (hasLocation(item)) {
        // The memory's own place name (often edited by hand) wins when the photo is near its pin.
        const near = pinned && memory.place && distanceKm(item, memory) <= NEAR_KM
        points.push({ memory, item, latitude: item.latitude, longitude: item.longitude, place: near ? memory.place : item.place })
      } else if (pinned) {
        points.push({ memory, item, latitude: memory.latitude, longitude: memory.longitude, place: memory.place })
      }
    }
  }
  return points
}

const chronological = (a, b) => a.memory.date.localeCompare(b.memory.date) || a.memory.id - b.memory.id || (a.item?.id ?? 0) - (b.item?.id ?? 0)
/** The most used place name among points; a tie goes to the oldest one ('' if none has a name). */
export function placeLabel(points) {
  const counts = new Map() // insertion order = oldest first, and sort() is stable
  for (const p of [...points].sort(chronological)) if (p.place) counts.set(p.place, (counts.get(p.place) || 0) + 1)
  return [...counts].sort((a, b) => b[1] - a[1])[0]?.[0] || ''
}

/** What to show/replay for some points: the memories (newest first), the photo/video ids taken there
 * (`only`; a replay shows just those) and how many items each memory has there. */
export function summarize(points) {
  const memories = [...new Map(points.map(p => [p.memory.id, p.memory])).values()].sort((a, b) => b.date.localeCompare(a.date) || b.id - a.id)
  const only = new Set(points.filter(p => p.item).map(p => p.item.id))
  const itemsHere = Object.fromEntries(memories.map(m => [m.id, points.filter(p => p.memory.id === m.id && p.item).length]))
  return { label: placeLabel(points) || 'Địa điểm chưa đặt tên', memories, only, itemsHere }
}

/** Places across memories: points within NEAR_KM of a group's first point, biggest first:
 * [{ key, latitude, longitude, points, label, memories, only, itemsHere }]. */
export function placeGroups(memories) {
  const groups = []
  for (const point of mediaPoints(memories).sort(chronological)) {
    const group = groups.find(g => distanceKm(g, point) <= NEAR_KM)
    if (group) group.points.push(point)
    else groups.push({ key: `${point.latitude},${point.longitude}`, latitude: point.latitude, longitude: point.longitude, points: [point] })
  }
  return groups.map(g => ({ ...g, ...summarize(g.points) })).sort((a, b) => b.memories.length - a.memories.length || b.points.length - a.points.length || a.label.localeCompare(b.label))
}

/** Place names for photo locations (null = none), one lookup per NEAR_KM area. A location near the
 * memory's pin takes the memory's place name. */
export async function namePlaces(locations, memoryLocation) {
  const named = []
  const names = []
  for (const location of locations) {
    if (!location) { names.push(''); continue }
    let hit = named.find(n => distanceKm(n, location) <= NEAR_KM)
    if (!hit) {
      const nearPin = hasLocation(memoryLocation) && memoryLocation.place && distanceKm(memoryLocation, location) <= NEAR_KM
      hit = { ...location, place: nearPin ? memoryLocation.place : await placeName(location) }
      named.push(hit)
    }
    names.push(hit.place)
  }
  return names
}

/** Form fields for an upload's location. */
export function appendLocation(body, location, place) {
  if (!location) return
  body.append('latitude', location.latitude)
  body.append('longitude', location.longitude)
  body.append('place', (place || '').slice(0, 120))
}
