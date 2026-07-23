import { useMemo, useState } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { RateSeriesChart } from '@/components/charts/RateSeriesChart'
import { useRateSeries, useRateTypes } from '@/hooks/useRates'
import { formatRate, parseRateValue } from '@/lib/formatters'

const WINDOW_OPTIONS = [
  { label: 'Last 30 days', value: 30 },
  { label: 'Last 90 days', value: 90 },
  { label: 'Last 180 days', value: 180 },
  { label: 'Last year', value: 365 },
]

export function Explorer() {
  const [rateType, setRateType] = useState('federal_funds')
  const [days, setDays] = useState(90)

  const { data: rateTypes, isLoading: typesLoading } = useRateTypes()
  const { data: series, isLoading: seriesLoading } = useRateSeries(
    rateType,
    days,
  )

  const stats = useMemo(() => {
    if (!series) return null
    const values = series.data
      .map(point => parseRateValue(point.value))
      .filter((v): v is number => v != null)
    if (values.length === 0) return null
    return {
      min: Math.min(...values),
      max: Math.max(...values),
      avg: values.reduce((sum, v) => sum + v, 0) / values.length,
    }
  }, [series])

  return (
    <div className='flex flex-col gap-6'>
      <div className='flex flex-wrap gap-4'>
        <div className='min-w-48'>
          {typesLoading || !rateTypes ? (
            <Skeleton className='h-9 w-48' />
          ) : (
            <Select
              value={rateType}
              onValueChange={value => value && setRateType(value)}
            >
              <SelectTrigger>
                <SelectValue placeholder='Select a rate type' />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(rateTypes.rate_types).map(([slug, label]) => (
                  <SelectItem key={slug} value={slug}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        <Select
          value={String(days)}
          onValueChange={value => setDays(Number(value))}
        >
          <SelectTrigger className='w-40'>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {WINDOW_OPTIONS.map(opt => (
              <SelectItem key={opt.value} value={String(opt.value)}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className='grid grid-cols-3 gap-4'>
        <Card className='border-border bg-card'>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-normal text-muted-foreground'>
              Min
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='font-mono text-xl text-foreground'>
              {stats ? formatRate(stats.min) : '—'}
            </div>
          </CardContent>
        </Card>
        <Card className='border-border bg-card'>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-normal text-muted-foreground'>
              Max
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='font-mono text-xl text-foreground'>
              {stats ? formatRate(stats.max) : '—'}
            </div>
          </CardContent>
        </Card>
        <Card className='border-border bg-card'>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-normal text-muted-foreground'>
              Average
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='font-mono text-xl text-foreground'>
              {stats ? formatRate(stats.avg) : '—'}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className='border-border bg-card'>
        <CardContent className='pt-6'>
          {seriesLoading || !series ? (
            <Skeleton className='h-72 rounded-lg' />
          ) : (
            <RateSeriesChart data={series.data} />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
