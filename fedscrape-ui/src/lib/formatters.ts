import { format, parseISO } from 'date-fns'

export function parseRateValue(
  value: string | null | undefined,
): number | null {
  if (value == null) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

export function formatRate(value: string | number | null | undefined): string {
  const num = typeof value === 'string' ? parseRateValue(value) : value
  if (num == null) return 'n/a'
  return `${num.toFixed(2)}%`
}

export function formatDate(dateStr: string): string {
  return format(parseISO(dateStr), 'MMM d, yyyy')
}
