import { useMemo } from 'react'
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts'
import type { TooltipValueType } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { SpreadChart } from '@/components/charts/SpreadChart'
import { useLatestRates, useRateSeries, useSpread } from '@/hooks/useRates'
import { parseRateValue } from '@/lib/formatters'
import type { RateResponse } from '@/types/rates'

const MATURITIES: Array<{ key: keyof RateResponse; label: string }> = [
  { key: 'treasury_1m', label: '1M' },
  { key: 'treasury_3m', label: '3M' },
  { key: 'treasury_6m', label: '6M' },
  { key: 'treasury_1y', label: '1Y' },
  { key: 'treasury_2y', label: '2Y' },
  { key: 'treasury_3y', label: '3Y' },
  { key: 'treasury_5y', label: '5Y' },
  { key: 'treasury_7y', label: '7Y' },
  { key: 'treasury_10y', label: '10Y' },
  { key: 'treasury_20y', label: '20Y' },
  { key: 'treasury_30y', label: '30Y' },
]

function SpreadBadge() {
  const { data: spread, isLoading } = useSpread('treasury_10y', 'treasury_2y')

  if (isLoading || !spread) return <Skeleton className='h-8 w-40' />

  const isInverted = spread.spread < 0

  return (
    <div className='flex items-center gap-3'>
      <span className='text-sm text-muted-foreground'>10Y–2Y Spread</span>
      <Badge
        className={
          isInverted
            ? 'bg-chart-negative/20 text-chart-negative'
            : 'bg-chart-positive/20 text-chart-positive'
        }
      >
        {spread.spread >= 0 ? '+' : ''}
        {spread.spread.toFixed(2)}%
        {isInverted ? ' (inverted)' : ''}
      </Badge>
    </div>
  )
}

function CurveShapeChart() {
  // Yield curve shape at latest date. Historical slices (1yr/2yr ago) would
  // need a "value as of date X" lookup, which the API doesn't expose (only
  // trailing series from today), so this renders the latest curve only
  // rather than fabricating the other two slices from data the backend
  // can't actually provide yet. Reuses /rates/latest (same source the
  // Dashboard uses) instead of one series call per maturity.
  const { data: latest, isLoading } = useLatestRates()

  const data = useMemo(() => {
    if (!latest) return []
    return MATURITIES.map(m => ({
      maturity: m.label,
      value: parseRateValue(latest[m.key] as string | null | undefined),
    }))
  }, [latest])

  if (isLoading || !latest) return <Skeleton className='h-72 rounded-lg' />

  return (
    <ResponsiveContainer width='100%' height={300}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray='3 3' stroke='var(--color-chart-grid)' />
        <XAxis
          dataKey='maturity'
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
        <Tooltip
          contentStyle={{
            background: 'var(--color-card)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
          }}
          labelStyle={{ color: 'var(--color-muted-foreground)' }}
          formatter={(value?: TooltipValueType) => [
            typeof value === 'number' ? `${value.toFixed(2)}%` : 'n/a',
            'Yield',
          ]}
        />
        <Legend />
        <Line
          type='monotone'
          dataKey='value'
          name='Latest'
          stroke='var(--color-chart-line)'
          strokeWidth={2}
          connectNulls={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

// /rates/{rate_type} caps `limit` at 365 server-side, so "history" here
// covers the last year, not the 2 years frontend_prompt.md originally
// called for — the backend has no endpoint for a longer trailing window.
const SPREAD_HISTORY_DAYS = 365

function SpreadHistoryChart() {
  const { data: tenYear, isLoading: tenLoading } = useRateSeries(
    'treasury_10y',
    SPREAD_HISTORY_DAYS,
  )
  const { data: twoYear, isLoading: twoLoading } = useRateSeries(
    'treasury_2y',
    SPREAD_HISTORY_DAYS,
  )

  const data = useMemo(() => {
    if (!tenYear || !twoYear) return []
    const twoYearByDate = new Map(
      twoYear.data.map(point => [point.date, parseRateValue(point.value)]),
    )
    return tenYear.data
      .map(point => {
        const tenVal = parseRateValue(point.value)
        const twoVal = twoYearByDate.get(point.date)
        return {
          date: point.date,
          spread: tenVal != null && twoVal != null ? tenVal - twoVal : null,
        }
      })
      .reverse()
  }, [tenYear, twoYear])

  if (tenLoading || twoLoading) return <Skeleton className='h-72 rounded-lg' />

  return <SpreadChart data={data} />
}

export function YieldCurve() {
  return (
    <div className='flex flex-col gap-6'>
      <SpreadBadge />

      <Card className='border-border bg-card'>
        <CardHeader>
          <CardTitle className='text-base font-normal text-muted-foreground'>
            Yield Curve Shape
          </CardTitle>
        </CardHeader>
        <CardContent>
          <CurveShapeChart />
        </CardContent>
      </Card>

      <Card className='border-border bg-card'>
        <CardHeader>
          <CardTitle className='text-base font-normal text-muted-foreground'>
            10Y–2Y Spread History (1 Year)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SpreadHistoryChart />
        </CardContent>
      </Card>
    </div>
  )
}
