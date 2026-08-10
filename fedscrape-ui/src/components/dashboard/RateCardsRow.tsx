import { Area, AreaChart, ResponsiveContainer } from 'recharts'
import { useLatestRates, useRateSeries } from '@/hooks/useRates'
import { formatDate, formatRate, parseRateValue } from '@/lib/formatters'
import { computeSpread, type RateDataPoint } from '@/lib/rateUtils'
import type { RateSeriesEntry } from '@/types/rates'

function toSparklineData(data: RateSeriesEntry[] | undefined): RateDataPoint[] {
  if (!data) return []
  return data
    .map(({ date, value }) => ({ date, value: parseRateValue(value) }))
    .sort((a, b) => a.date.localeCompare(b.date))
}

function MiniSparkline({ data }: { data: RateDataPoint[] }) {
  if (data.length === 0) return <div className='h-10' />
  return (
    <div className='h-10'>
      <ResponsiveContainer width='100%' height='100%'>
        <AreaChart data={data} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
          <Area
            type='monotone'
            dataKey='value'
            stroke='var(--accent-blue)'
            strokeWidth={1.5}
            fill='var(--accent-blue)'
            fillOpacity={0.15}
            connectNulls
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

function RateCard({
  label,
  value,
  date,
  sparkline,
  badge,
}: {
  label: string
  value: number | null
  date: string | undefined
  sparkline: RateDataPoint[]
  badge?: { text: string; positive: boolean }
}) {
  return (
    <div className='glass-panel flex flex-col gap-2 p-4'>
      <div className='flex items-center justify-between gap-2'>
        <span className='text-xs text-[var(--text-secondary)]'>{label}</span>
        {badge && (
          <span
            className='rounded-full px-2 py-0.5 text-[10px] font-medium'
            style={{
              color: badge.positive ? 'var(--accent-green)' : 'var(--accent-red)',
              backgroundColor: badge.positive
                ? 'rgba(34, 197, 94, 0.12)'
                : 'rgba(239, 68, 68, 0.12)',
            }}
          >
            {badge.text}
          </span>
        )}
      </div>
      <div className='font-mono text-2xl font-semibold text-[var(--text-primary)]'>
        {formatRate(value)}
      </div>
      <div className='text-xs text-[var(--text-muted)]'>
        {date ? formatDate(date) : '—'}
      </div>
      <MiniSparkline data={sparkline} />
    </div>
  )
}

const SPARKLINE_LIMIT = 30

export function RateCardsRow() {
  const { data: latest } = useLatestRates()

  const ffr = useRateSeries('federal_funds', SPARKLINE_LIMIT)
  const y2 = useRateSeries('treasury_2y', SPARKLINE_LIMIT)
  const y10 = useRateSeries('treasury_10y', SPARKLINE_LIMIT)
  const y30 = useRateSeries('treasury_30y', SPARKLINE_LIMIT)
  const prime = useRateSeries('bank_prime_loan', SPARKLINE_LIMIT)

  const spreadSparkline = computeSpread(
    toSparklineData(y10.data?.data),
    toSparklineData(y2.data?.data),
  )

  const spreadValue =
    latest?.treasury_10y != null && latest?.treasury_2y != null
      ? (parseRateValue(latest.treasury_10y) ?? 0) -
        (parseRateValue(latest.treasury_2y) ?? 0)
      : null

  return (
    <div className='grid grid-cols-2 gap-3 lg:grid-cols-6'>
      <RateCard
        label='Federal Funds Rate'
        value={parseRateValue(latest?.federal_funds)}
        date={latest?.date}
        sparkline={toSparklineData(ffr.data?.data)}
      />
      <RateCard
        label='2-Year Treasury'
        value={parseRateValue(latest?.treasury_2y)}
        date={latest?.date}
        sparkline={toSparklineData(y2.data?.data)}
      />
      <RateCard
        label='10-Year Treasury'
        value={parseRateValue(latest?.treasury_10y)}
        date={latest?.date}
        sparkline={toSparklineData(y10.data?.data)}
      />
      <RateCard
        label='30-Year Treasury'
        value={parseRateValue(latest?.treasury_30y)}
        date={latest?.date}
        sparkline={toSparklineData(y30.data?.data)}
      />
      <RateCard
        label='Bank Prime Loan'
        value={parseRateValue(latest?.bank_prime_loan)}
        date={latest?.date}
        sparkline={toSparklineData(prime.data?.data)}
      />
      <RateCard
        label='10Y-2Y Spread'
        value={spreadValue}
        date={latest?.date}
        sparkline={spreadSparkline}
        badge={
          spreadValue != null
            ? {
                text: spreadValue >= 0 ? 'Normal' : 'Inverted',
                positive: spreadValue >= 0,
              }
            : undefined
        }
      />
    </div>
  )
}
