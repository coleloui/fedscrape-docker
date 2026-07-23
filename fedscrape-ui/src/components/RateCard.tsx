import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDate, formatRate } from '@/lib/formatters'

export function RateCard({
  label,
  value,
  date,
}: {
  label: string
  value: string | null | undefined
  date: string
}) {
  return (
    <Card className='border-border bg-card'>
      <CardHeader className='pb-2'>
        <CardTitle className='text-sm font-normal text-muted-foreground'>
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className='font-mono text-2xl font-semibold text-foreground'>
          {formatRate(value)}
        </div>
        <div className='mt-1 text-xs text-muted-foreground'>
          {formatDate(date)}
        </div>
      </CardContent>
    </Card>
  )
}
