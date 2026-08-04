import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useLatestRates } from '@/hooks/useRates'
import { AXIS_STYLE, GRID_STYLE } from '@/lib/chartConfig'
import { formatDate, parseRateValue } from '@/lib/formatters'
import type { RateResponse } from '@/types/rates'

interface Maturity {
  label: string
  field: keyof RateResponse
}

const MATURITIES: Maturity[] = [
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

const INVERTED_COLOR = '#f87171' // red-400
const SHORT_END_COLOR = [96, 165, 250] as const // blue-400
const LONG_END_COLOR = [34, 211, 238] as const // cyan-400

function lerpColor(from: readonly number[], to: readonly number[], t: number): string {
  const [r, g, b] = from.map((channel, i) => Math.round(channel + (to[i] - channel) * t))
  return `rgb(${r}, ${g}, ${b})`
}

export function YieldCurveSnapshot() {
  const { data: latest } = useLatestRates()

  const points = MATURITIES.map(({ label, field }) => ({
    label,
    yield: parseRateValue(latest?.[field] as string | null | undefined),
  })).filter((point): point is { label: string; yield: number } => point.yield != null)

  const threeMonth = parseRateValue(latest?.treasury_3m)
  const tenYear = parseRateValue(latest?.treasury_10y)
  const isInverted = threeMonth != null && tenYear != null && threeMonth > tenYear

  return (
    <section aria-labelledby='yield-curve-heading' className='glass-panel p-4'>
      <h2 id='yield-curve-heading' className='mb-2 text-sm font-medium text-[var(--text-primary)]'>
        Yield Curve{latest ? ` — ${formatDate(latest.date)}` : ''}
      </h2>
      <ResponsiveContainer width='100%' height={260}>
        <BarChart
          data={points}
          margin={{ top: 8, right: 8, bottom: 0, left: 0 }}
          accessibilityLayer
        >
          <CartesianGrid {...GRID_STYLE} />
          <XAxis dataKey='label' {...AXIS_STYLE} />
          <YAxis tickFormatter={value => `${value}%`} {...AXIS_STYLE} />
          <Tooltip
            cursor={false}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const { label, yield: yieldValue } = payload[0].payload as {
                label: string
                yield: number
              }
              return (
                <div className='rounded-md border border-white/10 bg-zinc-900 px-3 py-2 text-xs shadow-lg'>
                  <div className='text-[var(--text-secondary)]'>{label}</div>
                  <div className='font-mono text-[var(--text-primary)]'>
                    {yieldValue.toFixed(2)}%
                  </div>
                </div>
              )
            }}
          />
          <Bar dataKey='yield' radius={[3, 3, 0, 0]}>
            {points.map(({ label }, i) => (
              <Cell
                key={label}
                fill={
                  isInverted
                    ? INVERTED_COLOR
                    : lerpColor(
                        SHORT_END_COLOR,
                        LONG_END_COLOR,
                        points.length > 1 ? i / (points.length - 1) : 0,
                      )
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {isInverted && (
        <p className='mt-2 text-xs text-[var(--accent-red)]'>
          Inverted: the 3-month yield is higher than the 10-year yield.
        </p>
      )}
    </section>
  )
}
