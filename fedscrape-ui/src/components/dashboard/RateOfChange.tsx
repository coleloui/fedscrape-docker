import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useRateSeries } from '@/hooks/useRates'
import { computeSpread } from '@/lib/rateUtils'
import { parseRateValue } from '@/lib/formatters'
import type { RateSeriesEntry } from '@/types/rates'

// Reuses the same limit=30 series queries RateCardsRow already fetches
// for sparklines — same query key, so React Query serves this from
// cache instead of firing a new request.
const CHANGE_WINDOW_LIMIT = 30

function toChangeSeries(data: RateSeriesEntry[] | undefined) {
  if (!data) return []
  return data
    .map(({ date, value }) => ({ date, value: parseRateValue(value) }))
    .sort((a, b) => a.date.localeCompare(b.date))
}

function thirtyDayChange(series: ReturnType<typeof toChangeSeries>): number | null {
  const withValues = series.filter(({ value }) => value != null)
  if (withValues.length < 2) return null
  const first = withValues[0].value
  const last = withValues[withValues.length - 1].value
  return first != null && last != null ? last - first : null
}

interface ChangeBar {
  label: string
  change: number | null
}

export function RateOfChange() {
  const ffr = useRateSeries('federal_funds', CHANGE_WINDOW_LIMIT)
  const y2 = useRateSeries('treasury_2y', CHANGE_WINDOW_LIMIT)
  const y10 = useRateSeries('treasury_10y', CHANGE_WINDOW_LIMIT)
  const y30 = useRateSeries('treasury_30y', CHANGE_WINDOW_LIMIT)
  const prime = useRateSeries('bank_prime_loan', CHANGE_WINDOW_LIMIT)

  const y2Series = toChangeSeries(y2.data?.data)
  const y10Series = toChangeSeries(y10.data?.data)
  const spreadSeries = computeSpread(y10Series, y2Series)

  const bars: ChangeBar[] = [
    { label: 'Fed Funds', change: thirtyDayChange(toChangeSeries(ffr.data?.data)) },
    { label: '2Y', change: thirtyDayChange(y2Series) },
    { label: '10Y', change: thirtyDayChange(y10Series) },
    { label: '30Y', change: thirtyDayChange(toChangeSeries(y30.data?.data)) },
    { label: 'Prime', change: thirtyDayChange(toChangeSeries(prime.data?.data)) },
    { label: '10Y-2Y Spread', change: thirtyDayChange(spreadSeries) },
  ]

  return (
    <section aria-labelledby='change-heading' className='glass-panel p-4'>
      <h2 id='change-heading' className='mb-2 text-sm font-medium text-[var(--text-primary)]'>
        30-Day Rate Change
      </h2>
      <ResponsiveContainer width='100%' height={220}>
        <BarChart
          data={bars}
          layout='vertical'
          margin={{ top: 8, right: 24, bottom: 8, left: 8 }}
          accessibilityLayer
        >
          <XAxis
            type='number'
            tick={{ fill: 'var(--chart-axis)', fontSize: 11 }}
            axisLine={{ stroke: 'var(--chart-grid)' }}
            tickLine={false}
            tickFormatter={value => `${value > 0 ? '+' : ''}${value}%`}
          />
          <YAxis
            type='category'
            dataKey='label'
            tick={{ fill: 'var(--text-secondary)', fontSize: 11 }}
            axisLine={{ stroke: 'var(--chart-grid)' }}
            tickLine={false}
            width={90}
          />
          <Tooltip
            cursor={false}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const { label, change } = payload[0].payload as ChangeBar
              return (
                <div className='rounded-md border border-[var(--border-subtle)] bg-[var(--bg-elevated)] px-3 py-2 text-xs shadow-lg'>
                  <div className='text-[var(--text-secondary)]'>{label}</div>
                  <div className='font-mono text-[var(--text-primary)]'>
                    {change == null
                      ? 'n/a'
                      : `${change > 0 ? '+' : ''}${change.toFixed(2)}%`}
                  </div>
                </div>
              )
            }}
          />
          <Bar dataKey='change' radius={3}>
            {bars.map(({ label, change }) => (
              <Cell
                key={label}
                fill={
                  change == null
                    ? 'var(--text-muted)'
                    : change > 0
                      ? 'var(--accent-green)'
                      : change < 0
                        ? 'var(--accent-red)'
                        : 'var(--text-muted)'
                }
              />
            ))}
            <LabelList
              dataKey='change'
              position='right'
              fill='var(--text-secondary)'
              fontSize={11}
              formatter={(value: unknown) => {
                const num = typeof value === 'number' ? value : null
                return num == null ? 'n/a' : `${num > 0 ? '+' : ''}${num.toFixed(2)}%`
              }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </section>
  )
}
