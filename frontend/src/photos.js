import { getToken } from '@/api.js'

// Photos are private (token-protected), so they are fetched as blobs. Cache the
// resulting object URLs so a photo is downloaded once per session instead of on
// every view mount (jar list, memory page, thumbnails, full-screen viewer).
const cache = new Map() // url -> Promise<objectURL | ''>

export function photoSrc(url) {
  if (!cache.has(url)) {
    const request = fetch(url, { headers: { Authorization: `Token ${getToken()}` } })
      .then(response => (response.ok ? response.blob() : Promise.reject(new Error(String(response.status)))))
      .then(blob => URL.createObjectURL(blob))
      .catch(() => { cache.delete(url); return '' }) // allow a retry on the next mount
    cache.set(url, request)
  }
  return cache.get(url)
}

export function forgetPhoto(url) {
  const request = cache.get(url)
  cache.delete(url)
  request?.then(src => src && URL.revokeObjectURL(src))
}

export function clearPhotos() {
  for (const url of [...cache.keys()]) forgetPhoto(url)
}

// Before upload, convert HEIC/HEIF and large photos to a JPEG of at most MAX_SIDE px on
// the long edge, so phones send a few MB instead of 10-20 MB and the server rarely has
// to decode HEIF. If the browser can't decode the file (e.g. HEIF outside Safari), the
// original is sent and the server converts it.
const MAX_SIDE = 4096 // also keeps the canvas under iOS Safari's size limit
const SMALL_ENOUGH = 3 * 1024 * 1024
const isHeif = file => /^image\/hei[cf]/i.test(file.type) || /\.hei[cf]$/i.test(file.name)
export async function uploadablePhoto(file) {
  const heif = isHeif(file)
  if (!heif && (file.size <= SMALL_ENOUGH || !/^image\/(jpeg|png|webp)$/.test(file.type))) return file
  const url = URL.createObjectURL(file)
  try {
    const img = new Image()
    img.src = url
    await img.decode() // rejects when the browser can't read the format
    const scale = Math.min(1, MAX_SIDE / Math.max(img.naturalWidth, img.naturalHeight))
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(img.naturalWidth * scale)
    canvas.height = Math.round(img.naturalHeight * scale)
    const context = canvas.getContext('2d')
    context.fillStyle = '#fff' // JPEG has no transparency
    context.fillRect(0, 0, canvas.width, canvas.height)
    context.drawImage(img, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.88))
    if (!blob || (!heif && blob.size >= file.size)) return file
    return new File([blob], file.name.replace(/\.[^.]*$/, '') + '.jpg', { type: 'image/jpeg' })
  } catch {
    return file
  } finally {
    URL.revokeObjectURL(url)
  }
}

// Photo sizes: thumbnails (~400 px) in lists and strips, the display size (~1600 px) for the main photo
// and replay, the original in the full-screen viewer.
export const thumbOf = item => item?.thumb_url || item?.url
export const displayOf = item => item?.display_url || item?.url
/** Start downloading a photo in the background (e.g. the next one), so showing it is instant. */
export function preload(url) {
  if (url) photoSrc(url)
}

// Videos (MP4/MOV/WebM) are uploaded as they are and played from their signed `stream_url`.
export const isVideoFile = file => /^video\//.test(file.type) || /\.(mp4|mov|m4v|webm)$/i.test(file.name)
export const isVideo = item => item?.kind === 'video'
/** A memory's photos and videos in the order they were added (the API lists newest first). */
export const mediaOf = memory => [...(memory?.photos ?? [])].sort((a, b) => a.id - b.id)
/** The picture shown for a memory in lists: its first photo (videos can't be a thumbnail image). */
export const coverPhoto = memory => mediaOf(memory).find(p => !isVideo(p))
