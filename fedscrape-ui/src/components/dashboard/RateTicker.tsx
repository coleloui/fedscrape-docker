import { useLatestRates } from '@/hooks/useRates'
import { formatRate, parseRateValue } from '@/lib/formatters'

interface TickerItem {
  label: string
  value: number | null
  dotColor: string
}

export function RateTicker() {
  const { data: latest } = useLatestRates()
  if (!latest) return null

  const spread =
    latest.treasury_10y != null && latest.treasury_2y != null
      ? (parseRateValue(latest.treasury_10y) ?? 0) -
        (parseRateValue(latest.treasury_2y) ?? 0)
      : null

  const items: TickerItem[] = [
    {
      label: 'Fed Funds',
      value: parseRateValue(latest.federal_funds),
      dotColor: 'var(--accent-blue)',
    },
    {
      label: '2Y Treasury',
      value: parseRateValue(latest.treasury_2y),
      dotColor: 'var(--accent-blue)',
    },
    {
      label: '10Y Treasury',
      value: parseRateValue(latest.treasury_10y),
      dotColor: 'var(--accent-blue)',
    },
    {
      label: '30Y Treasury',
      value: parseRateValue(latest.treasury_30y),
      dotColor: 'var(--accent-blue)',
    },
    {
      label: 'Prime',
      value: parseRateValue(latest.bank_prime_loan),
      dotColor: 'var(--accent-blue)',
    },
    {
      label: '10Y-2Y Spread',
      value: spread,
      dotColor:
        spread != null && spread < 0 ? 'var(--accent-red)' : 'var(--accent-green)',
    },
  ]

  const track = (keyPrefix: string) => (
    <div className='flex shrink-0 items-center'>
      {items.map(({ label, value, dotColor }) => (
        <span
          key={`${keyPrefix}-${label}`}
          className='flex items-center gap-2 px-4 text-xs text-[var(--text-secondary)]'
        >
          <span
            className='inline-block size-1.5 rounded-full'
            style={{ backgroundColor: dotColor }}
          />
          {label}:{' '}
          <span className='font-mono text-[var(--text-primary)]'>
            {formatRate(value)}
          </span>
        </span>
      ))}
    </div>
  )

  return (
    // Decorative restatement of values already exposed accessibly in
    // RateCardsRow's <dl> — hidden from assistive tech so a screen reader
    // doesn't announce a constantly-scrolling duplicate of the same data.
    <div
      aria-hidden='true'
      className='fixed bottom-0 z-30 hidden h-9 w-full items-center overflow-hidden border-t border-[var(--border-subtle)] bg-[var(--bg-elevated)] lg:flex'
    >
      <div className='ticker-track flex w-max'>
        {track('a')}
        {track('b')}
      </div>
    </div>
  )
}
