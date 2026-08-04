import { useState } from 'react'
import { format, subYears } from 'date-fns'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useRateSeries, useRateSeriesRange } from '@/hooks/useRates'
import { AXIS_STYLE, GRID_STYLE } from '@/lib/chartConfig'
import { formatDate, parseRateValue } from '@/lib/formatters'
import type { RateSeriesEntry } from '@/types/rates'

type RangeKey = 'Live' | '1M' | '1Y' | '5Y' | 'All'

const RANGE_TABS: RangeKey[] = ['Live', '1M', '1Y', '5Y', 'All']

const ALL_TIME_START = '2015-01-01'

interface RateLine {
  key: 'federal_funds' | 'treasury_2y' | 'treasury_10y' | 'treasury_30y' | 'bank_prime_loan'
  label: string
  color: string
}

const RATE_LINES: RateLine[] = [
  { key: 'federal_funds', label: 'Fed Funds', color: 'var(--chart-ffr)' },
  { key: 'treasury_2y', label: '2Y Treasury', color: 'var(--chart-2y)' },
  { key: 'treasury_10y', label: '10Y Treasury', color: 'var(--chart-10y)' },
  { key: 'treasury_30y', label: '30Y Treasury', color: 'var(--chart-30y)' },
  { key: 'bank_prime_loan', label: 'Prime Rate', color: 'var(--chart-prime)' },
]

function getRangeConfig(
  range: RangeKey,
): { mode: 'limit'; limit: number } | { mode: 'range'; start: string } {
  switch (range) {
    case '1Y':
      return { mode: 'limit', limit: 365 }
    case '5Y':
      return { mode: 'range', start: format(subYears(new Date(), 5), 'yyyy-MM-dd') }
    case 'All':
      return { mode: 'range', start: ALL_TIME_START }
    case 'Live':
    case '1M':
    default:
      return { mode: 'limit', limit: 30 }
  }
}

function useTimelineSeries(rateType: string, range: RangeKey): RateSeriesEntry[] | undefined {
  const config = getRangeConfig(range)
  const isRangeMode = config.mode === 'range'

  const limitQuery = useRateSeries(rateType, isRangeMode ? 30 : config.limit, {
    enabled: !isRangeMode,
  })
  const rangeQuery = useRateSeriesRange(rateType, isRangeMode ? config.start : '', undefined, {
    enabled: isRangeMode,
  })

  return (isRangeMode ? rangeQuery.data : limitQuery.data)?.data
}

interface TimelineRow {
  date: string
  federal_funds: number | null
  treasury_2y: number | null
  treasury_10y: number | null
  treasury_30y: number | null
  bank_prime_loan: number | null
}

// Each rate's series loads independently and can resolve at different
// times, so we merge by date into a lookup rather than assuming the
// arrays line up positionally.
function mergeSeriesByDate(seriesByKey: Record<RateLine['key'], RateSeriesEntry[] | undefined>) {
  const rows = new Map<string, TimelineRow>()

  for (const { key } of RATE_LINES) {
    for (const { date, value } of seriesByKey[key] ?? []) {
      const row =
        rows.get(date) ??
        ({
          date,
          federal_funds: null,
          treasury_2y: null,
          treasury_10y: null,
          treasury_30y: null,
          bank_prime_loan: null,
        } satisfies TimelineRow)
      row[key] = parseRateValue(value)
      rows.set(date, row)
    }
  }

  return Array.from(rows.values()).sort((a, b) => a.date.localeCompare(b.date))
}

function TimelineTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ dataKey: string; value: number | null; color: string }>
  label?: string
}) {
  if (!active || !payload?.length) return null
  return (
    <div className='rounded-md border border-white/10 bg-zinc-900 px-3 py-2 text-xs shadow-lg'>
      <div className='mb-1 text-[var(--text-secondary)]'>
        {label ? formatDate(label) : ''}
      </div>
      {payload.map(entry => {
        const line = RATE_LINES.find(l => l.key === entry.dataKey)
        if (!line || entry.value == null) return null
        return (
          <div key={entry.dataKey} className='flex items-center justify-between gap-4'>
            <span style={{ color: entry.color }}>{line.label}</span>
            <span className='font-mono text-[var(--text-primary)]'>
              {entry.value.toFixed(2)}%
            </span>
          </div>
        )
      })}
    </div>
  )
}

export function HistoricalTimeline() {
  const [range, setRange] = useState<RangeKey>('Live')

  const ffr = useTimelineSeries('federal_funds', range)
  const y2 = useTimelineSeries('treasury_2y', range)
  const y10 = useTimelineSeries('treasury_10y', range)
  const y30 = useTimelineSeries('treasury_30y', range)
  const prime = useTimelineSeries('bank_prime_loan', range)

  const data = mergeSeriesByDate({
    federal_funds: ffr,
    treasury_2y: y2,
    treasury_10y: y10,
    treasury_30y: y30,
    bank_prime_loan: prime,
  })

  return (
    <div className='glass-panel p-4'>
      <div className='mb-2 flex flex-wrap items-center justify-between gap-2'>
        <h2 className='text-sm font-medium text-[var(--text-primary)]'>
          Historical Timeline
        </h2>
        <div className='flex gap-1'>
          {RANGE_TABS.map(tab => (
            <button
              key={tab}
              onClick={() => setRange(tab)}
              className={`rounded-full px-3 py-1 text-xs transition-colors duration-200 ${
                range === tab
                  ? 'bg-[var(--accent-blue-dim)] text-[var(--accent-blue)]'
                  : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width='100%' height={320}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey='date' tickFormatter={formatDate} {...AXIS_STYLE} />
          <YAxis tickFormatter={value => `${value}%`} {...AXIS_STYLE} />
          <Tooltip content={<TimelineTooltip />} cursor={{ stroke: 'var(--chart-grid)' }} />
          <Legend
            wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }}
            formatter={(value: string) =>
              RATE_LINES.find(l => l.key === value)?.label ?? value
            }
          />
          {RATE_LINES.map(({ key, color }) => (
            <Line
              key={key}
              type='monotone'
              dataKey={key}
              stroke={color}
              strokeWidth={1.75}
              dot={false}
              connectNulls={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
