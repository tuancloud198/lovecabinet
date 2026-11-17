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

// HEIC/HEIF (iPhone): browsers that can decode it (Safari) convert it to JPEG before
// upload, so the server never has to. Elsewhere the original is sent and the server converts.
const MAX_PIXELS = 16_000_000 // iOS Safari refuses larger canvases
export async function uploadablePhoto(file) {
  if (!/^image\/hei[cf]/i.test(file.type) && !/\.hei[cf]$/i.test(file.name)) return file
  const url = URL.createObjectURL(file)
  try {
    const img = new Image()
    img.src = url
    await img.decode() // rejects when the browser can't read HEIF
    const scale = Math.min(1, Math.sqrt(MAX_PIXELS / (img.naturalWidth * img.naturalHeight)))
    const canvas = document.createElement('canvas')
    canvas.width = Math.round(img.naturalWidth * scale)
    canvas.height = Math.round(img.naturalHeight * scale)
    canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height)
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9))
    return blob ? new File([blob], file.name.replace(/\.[^.]*$/, '') + '.jpg', { type: 'image/jpeg' }) : file
  } catch {
    return file
  } finally {
    URL.revokeObjectURL(url)
  }
}
