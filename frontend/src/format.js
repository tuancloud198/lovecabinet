const pad = n => String(n).padStart(2, '0')

/** Local date as YYYY-MM-DD (the API's date format). */
export function isoDate(date = new Date()) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
}
/** '2026-11-14' -> '14/11/2026' */
export function displayDate(iso) {
  const [y, m, d] = iso.split('-')
  return `${d}/${m}/${y}`
}
/** '2026-11-14' -> '14/11' */
export function shortDate(iso) {
  const [, m, d] = iso.split('-')
  return `${d}/${m}`
}
/** Whole days from today to an ISO date (negative when in the past). */
export function daysUntil(iso) {
  const [y, m, d] = iso.split('-').map(Number)
  const today = new Date(); today.setHours(0, 0, 0, 0)
  return Math.round((new Date(y, m - 1, d) - today) / 86400000)
}
export function timeAgo(timestamp) {
  const minutes = Math.floor((Date.now() - new Date(timestamp)) / 60000)
  if (minutes < 1) return 'vừa xong'
  if (minutes < 60) return `${minutes} phút trước`
  if (minutes < 1440) return `${Math.floor(minutes / 60)} giờ trước`
  return `${Math.floor(minutes / 1440)} ngày trước`
}
