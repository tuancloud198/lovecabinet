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
