export const TOKEN_KEY = 'token'

// The token lives in localStorage so the user stays signed in after closing the browser,
// until they sign out (which also revokes it on the server). Storage can be unavailable
// (private mode, blocked site data), in which case the session simply isn't remembered.
function storage(kind) {
  try { return window[kind] } catch { return null }
}

export function getToken() {
  try {
    const saved = storage('localStorage')?.getItem(TOKEN_KEY)
    if (saved) return saved
    // Sessions from before "stay signed in" were kept in sessionStorage: carry them over.
    const old = storage('sessionStorage')?.getItem(TOKEN_KEY)
    if (old) setToken(old)
    return old || ''
  } catch {
    return ''
  }
}
export function setToken(token) {
  try {
    storage('sessionStorage')?.removeItem(TOKEN_KEY)
    if (token) storage('localStorage')?.setItem(TOKEN_KEY, token)
    else storage('localStorage')?.removeItem(TOKEN_KEY)
  } catch { /* not remembered; the in-memory session still works */ }
}

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status }
}

function describe(data) {
  if (typeof data === 'string') return data
  if (Array.isArray(data)) return data.join(' ') // DRF ValidationError('...') responds with ["..."]
  return Object.entries(data)
    .map(([key, value]) => `${key === 'detail' || key === 'non_field_errors' ? '' : key + ': '}${Array.isArray(value) ? value.join(' ') : value}`)
    .join(' ')
}

export async function api(path, { method = 'GET', body } = {}) {
  const isForm = body instanceof FormData
  const headers = {}
  if (!isForm && body !== undefined) headers['Content-Type'] = 'application/json'
  const token = getToken()
  if (token) headers.Authorization = `Token ${token}`
  const response = await fetch(`/api/${path}`, { method, headers, body: body === undefined ? undefined : isForm ? body : JSON.stringify(body) })
  if (response.status === 204) return null
  const data = await response.json().catch(() => ({ detail: `Lỗi máy chủ (${response.status}).` }))
  if (!response.ok) throw new ApiError(describe(data), response.status)
  return data
}

// POST a FormData with upload progress (fetch can't report it). onProgress gets 0..1.
export function upload(path, body, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', `/api/${path}`)
    const token = getToken()
    if (token) xhr.setRequestHeader('Authorization', `Token ${token}`)
    xhr.upload.onprogress = event => { if (event.lengthComputable) onProgress?.(event.loaded / event.total) }
    xhr.onload = () => {
      let data
      try { data = JSON.parse(xhr.responseText) } catch { data = { detail: `Lỗi máy chủ (${xhr.status}).` } }
      if (xhr.status >= 200 && xhr.status < 300) resolve(data)
      else reject(new ApiError(describe(data), xhr.status))
    }
    xhr.onerror = () => reject(new ApiError('Mất kết nối mạng, vui lòng thử lại.', 0))
    xhr.send(body)
  })
}
