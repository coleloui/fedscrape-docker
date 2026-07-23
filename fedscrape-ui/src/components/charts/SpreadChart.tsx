import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  ReferenceLine,
} from 'recharts'
import { formatDate } from '@/lib/formatters'

type SpreadPoint = {
  date: string
  spread: number | null
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
  const value = payload[0].value
  return (
    <div className='rounded-md border border-border bg-card px-3 py-2 text-sm shadow-lg'>
      <div className='text-muted-foreground'>
        {label ? formatDate(label) : ''}
      </div>
      <div
        className={`font-mono ${value < 0 ? 'text-chart-negative' : 'text-chart-positive'}`}
      >
        {value >= 0 ? '+' : ''}
        {value.toFixed(2)}%
      </div>
    </div>
  )
}

export function SpreadChart({ data }: { data: SpreadPoint[] }) {
  return (
    <ResponsiveContainer width='100%' height={300}>
      <AreaChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id='spreadPositive' x1='0' y1='0' x2='0' y2='1'>
            <stop
              offset='5%'
              stopColor='var(--color-chart-positive)'
              stopOpacity={0.4}
            />
            <stop
              offset='95%'
              stopColor='var(--color-chart-positive)'
              stopOpacity={0}
            />
          </linearGradient>
        </defs>
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
          tickFormatter={value => `${value}%`}
        />
        <ReferenceLine y={0} stroke='var(--color-chart-reference)' />
        <Tooltip content={<TooltipContent />} />
        <Area
          type='monotone'
          dataKey='spread'
          stroke='var(--color-chart-line)'
          strokeWidth={2}
          fill='url(#spreadPositive)'
          connectNulls={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
