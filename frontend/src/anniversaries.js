// Our day count and anniversaries, computed from the couple's two dates:
//   dating_since: the day we started loving each other = day 1 of the count
//   met_on:       the day we first met
// Milestones: every 100 days up to 1000, then every 500; yearly anniversaries of both dates.
// Also both partners' birthdays (members' birth_date from their profiles).
import { isoDate } from '@/format.js'

const parse = iso => { const [y, m, d] = iso.split('-').map(Number); return new Date(y, m - 1, d) }
const addDays = (iso, n) => { const date = parse(iso); date.setDate(date.getDate() + n); return isoDate(date) }
// Same day `years` later; 29/02 falls on 28/02 in other years.
const addYears = (iso, years) => {
  const [y, m, d] = iso.split('-').map(Number)
  const date = new Date(y + years, m - 1, d)
  return isoDate(date.getDate() === d ? date : new Date(y + years, m, 0))
}
const DAY = 86400000

/** Days together, counting the first day as day 1 (null before it or when unset). */
export function daysTogether(couple, today = isoDate()) {
  if (!couple?.dating_since || couple.dating_since > today) return null
  return Math.round((parse(today) - parse(couple.dating_since)) / DAY) + 1
}

/** Anniversaries from `from` to `to` (ISO dates, inclusive), by date: [{ date, title, emoji, key }]. */
export function anniversaries(couple, from, to) {
  const items = []
  const add = (date, title, emoji) => { if (date >= from && date <= to) items.push({ date, title, emoji, key: `${date}-${title}` }) }
  const since = couple?.dating_since
  const met = couple?.met_on
  if (since) {
    add(since, 'Ngày đầu tiên yêu nhau', '💘')
    for (let n = 100; ; n += n < 1000 ? 100 : 500) {
      const date = addDays(since, n - 1)
      if (date > to) break
      add(date, `${n} ngày yêu nhau`, '💗')
    }
    for (let k = 1; addYears(since, k) <= to; k++) add(addYears(since, k), `Kỷ niệm ${k} năm yêu nhau`, '🎉')
  }
  if (met) {
    add(met, 'Ngày gặp nhau lần đầu', '👋')
    for (let k = 1; addYears(met, k) <= to; k++) add(addYears(met, k), `${k} năm ngày gặp nhau`, '🌷')
  }
  for (const member of couple?.members ?? []) {
    const born = member.birth_date
    if (!born) continue
    const first = Math.max(1, Number(from.slice(0, 4)) - Number(born.slice(0, 4))) // skip years before the range
    for (let k = first; addYears(born, k) <= to; k++) add(addYears(born, k), `Sinh nhật ${member.display_name} (${k} tuổi)`, '🎂')
  }
  return items.sort((a, b) => a.date.localeCompare(b.date))
}

/** Anniversaries and birthdays from today on (the next two years). */
export const upcomingAnniversaries = (couple, today = isoDate()) => anniversaries(couple, today, addYears(today, 2))
