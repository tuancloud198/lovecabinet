const TOKEN_KEY = 'token'

export function getToken() {
  return sessionStorage.getItem(TOKEN_KEY) || ''
}
export function setToken(token) {
  if (token) sessionStorage.setItem(TOKEN_KEY, token)
  else sessionStorage.removeItem(TOKEN_KEY)
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
