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
import { useRateSnapshot } from '@/hooks/useRates'
import { AXIS_STYLE, GRID_STYLE } from '@/lib/chartConfig'
import { parseRateValue } from '@/lib/formatters'
import type { RateResponse } from '@/types/rates'

const MATURITIES: { label: string; field: keyof RateResponse }[] = [
  { label: '1M', field: 'treasury_1m' },
  { label: '3M', field: 'treasury_3m' },
  { label: '6M', field: 'treasury_6m' },
  { label: '1Y', field: 'treasury_1y' },
  { label: '2Y', field: 'treasury_2y' },
  { label: '3Y', field: 'treasury_3y' },
  { label: '5Y', field: 'treasury_5y' },
  { label: '7Y', field: 'treasury_7y' },
  { label: '10Y', field: 'treasury_10y' },
  { label: '20Y', field: 'treasury_20y' },
  { label: '30Y', field: 'treasury_30y' },
]

interface Snapshot {
  seriesKey: 'today' | 'oneYearAgo' | 'twoYearsAgo'
  legendLabel: string
  color: string
  date: string
}

const SNAPSHOTS: Snapshot[] = [
  {
    seriesKey: 'today',
    legendLabel: 'Today',
    color: 'var(--chart-curve-short)',
    date: format(new Date(), 'yyyy-MM-dd'),
  },
  {
    seriesKey: 'oneYearAgo',
    legendLabel: '1 Year Ago',
    color: 'var(--chart-curve-1y-ago)',
    date: format(subYears(new Date(), 1), 'yyyy-MM-dd'),
  },
  {
    seriesKey: 'twoYearsAgo',
    legendLabel: '2 Years Ago',
    color: 'var(--text-secondary)', // zinc-400, same value used for "2 years ago"
    date: format(subYears(new Date(), 2), 'yyyy-MM-dd'),
  },
]

interface CurveRow {
  label: string
  today: number | null
  oneYearAgo: number | null
  twoYearsAgo: number | null
}

function CurveOverTimeTooltip({
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
    <div className='rounded-md border border-[var(--border-subtle)] bg-[var(--bg-elevated)] px-3 py-2 text-xs shadow-lg'>
      <div className='mb-1 text-[var(--text-secondary)]'>{label}</div>
      {payload.map(entry => {
        const snapshot = SNAPSHOTS.find(s => s.seriesKey === entry.dataKey)
        if (!snapshot || entry.value == null) return null
        return (
          <div key={entry.dataKey} className='flex items-center justify-between gap-4'>
            <span style={{ color: snapshot.color }}>{snapshot.legendLabel}</span>
            <span className='font-mono text-[var(--text-primary)]'>
              {entry.value.toFixed(2)}%
            </span>
          </div>
        )
      })}
    </div>
  )
}

export function YieldCurveOverTime() {
  const today = useRateSnapshot(SNAPSHOTS[0].date)
  const oneYearAgo = useRateSnapshot(SNAPSHOTS[1].date)
  const twoYearsAgo = useRateSnapshot(SNAPSHOTS[2].date)

  const snapshotData: Record<Snapshot['seriesKey'], RateResponse | undefined> = {
    today: today.data,
    oneYearAgo: oneYearAgo.data,
    twoYearsAgo: twoYearsAgo.data,
  }

  const data: CurveRow[] = MATURITIES.map(({ label, field }) => ({
    label,
    today: parseRateValue(snapshotData.today?.[field] as string | null | undefined),
    oneYearAgo: parseRateValue(
      snapshotData.oneYearAgo?.[field] as string | null | undefined,
    ),
    twoYearsAgo: parseRateValue(
      snapshotData.twoYearsAgo?.[field] as string | null | undefined,
    ),
  }))

  return (
    <section aria-labelledby='curve-over-time-heading' className='glass-panel p-4'>
      <h2
        id='curve-over-time-heading'
        className='mb-2 text-sm font-medium text-[var(--text-primary)]'
      >
        Yield Curve Over Time
      </h2>
      <ResponsiveContainer width='100%' height={260}>
        <LineChart
          data={data}
          margin={{ top: 8, right: 16, bottom: 0, left: 0 }}
          accessibilityLayer
        >
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey='label' {...AXIS_STYLE} />
          <YAxis tickFormatter={value => `${value}%`} {...AXIS_STYLE} />
          <Tooltip
            cursor={{ stroke: 'var(--chart-grid)' }}
            content={<CurveOverTimeTooltip />}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: 'var(--text-secondary)' }}
            formatter={(value: string) =>
              SNAPSHOTS.find(s => s.seriesKey === value)?.legendLabel ?? value
            }
          />
          {SNAPSHOTS.map(({ seriesKey, color }) => (
            <Line
              key={seriesKey}
              type='monotone'
              dataKey={seriesKey}
              stroke={color}
              strokeWidth={1.75}
              dot={false}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}
