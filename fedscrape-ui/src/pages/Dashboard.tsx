import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { TooltipValueType } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { RateCard } from '@/components/RateCard'
import { RateSeriesChart } from '@/components/charts/RateSeriesChart'
import { useLatestRates, useRateSeries } from '@/hooks/useRates'
import type { RateResponse } from '@/types/rates'

const KEY_RATES: Array<{ key: keyof RateResponse; label: string }> = [
  { key: 'federal_funds', label: 'Federal Funds Rate' },
  { key: 'treasury_2y', label: '2-Year Treasury' },
  { key: 'treasury_10y', label: '10-Year Treasury' },
  { key: 'treasury_30y', label: '30-Year Treasury' },
  { key: 'bank_prime_loan', label: 'Bank Prime Loan' },
]

const YIELD_CURVE_MATURITIES: Array<{ key: keyof RateResponse; label: string }> = [
  { key: 'tbill_3m', label: '3M' },
  { key: 'treasury_1y', label: '1Y' },
  { key: 'treasury_2y', label: '2Y' },
  { key: 'treasury_5y', label: '5Y' },
  { key: 'treasury_10y', label: '10Y' },
  { key: 'treasury_30y', label: '30Y' },
]

function parseValue(value: string | null | undefined): number | null {
  if (value == null) return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function YieldCurveSnapshot({ latest }: { latest: RateResponse }) {
  const shortEnd = parseValue(latest.tbill_3m)
  const longEnd = parseValue(latest.treasury_10y)
  const inverted = shortEnd != null && longEnd != null && shortEnd > longEnd

  const data = YIELD_CURVE_MATURITIES.map(m => ({
    maturity: m.label,
    value: parseValue(latest[m.key] as string | null | undefined),
  }))

  return (
    <Card className='border-border bg-card'>
      <CardHeader>
        <CardTitle className='text-base font-normal text-muted-foreground'>
          Yield Curve Snapshot
          {inverted && (
            <span className='ml-2 text-xs font-medium text-chart-negative'>
              (inverted)
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width='100%' height={240}>
          <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
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
            <Bar
              dataKey='value'
              fill={inverted ? 'var(--color-chart-negative)' : 'var(--color-chart-line)'}
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

export function Dashboard() {
  const { data: latest, isLoading: latestLoading } = useLatestRates()
  const { data: fedFundsSeries, isLoading: seriesLoading } = useRateSeries(
    'federal_funds',
    365,
  )

  return (
    <div className='flex flex-col gap-6'>
      <div className='grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5'>
        {latestLoading || !latest
          ? Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className='h-24 rounded-lg' />
            ))
          : KEY_RATES.map(rate => (
              <RateCard
                key={rate.key}
                label={rate.label}
                value={latest[rate.key] as string | null | undefined}
                date={latest.date}
              />
            ))}
      </div>

      {latestLoading || !latest ? (
        <Skeleton className='h-64 rounded-lg' />
      ) : (
        <YieldCurveSnapshot latest={latest} />
      )}

      <Card className='border-border bg-card'>
        <CardHeader>
          <CardTitle className='text-base font-normal text-muted-foreground'>
            Fed Funds Rate (1 Year)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {seriesLoading || !fedFundsSeries ? (
            <Skeleton className='h-72 rounded-lg' />
          ) : (
            <RateSeriesChart data={fedFundsSeries.data} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
