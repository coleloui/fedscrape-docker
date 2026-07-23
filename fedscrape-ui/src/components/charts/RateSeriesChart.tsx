import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'
import { formatDate, parseRateValue } from '@/lib/formatters'
import type { RateSeriesEntry } from '@/types/rates'

type SeriesPoint = RateSeriesEntry

type ChartPoint = {
  date: string
  value: number | null
}

function TooltipContent({
  active,
  payload,
  label,
}: {
  active?: boolean
  payload?: Array<{ value: number | null }>
  label?: string
}) {
  if (!active || !payload?.length || payload[0].value == null) return null
  return (
    <div className='rounded-md border border-border bg-card px-3 py-2 text-sm shadow-lg'>
      <div className='text-muted-foreground'>
        {label ? formatDate(label) : ''}
      </div>
      <div className='font-mono text-foreground'>
        {payload[0].value.toFixed(2)}%
      </div>
    </div>
  )
}

export function RateSeriesChart({ data }: { data: SeriesPoint[] }) {
  const chartData: ChartPoint[] = data.map(point => ({
    date: point.date,
    value: parseRateValue(point.value),
  }))

  return (
    <ResponsiveContainer width='100%' height={300}>
      <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray='3 3' stroke='var(--color-chart-grid)' />
        <XAxis
          dataKey='date'
          tickFormatter={value => formatDate(value)}
          stroke='var(--color-chart-axis)'
          fontSize={12}
          tickLine={false}
        />
        <YAxis
          stroke='var(--color-chart-axis)'
          fontSize={12}
          tickLine={false}
          domain={['auto', 'auto']}
          tickFormatter={value => `${value}%`}
        />
        <Tooltip content={<TooltipContent />} />
        <Line
          type='monotone'
          dataKey='value'
          stroke='var(--color-chart-line)'
          strokeWidth={2}
          dot={false}
          connectNulls={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
