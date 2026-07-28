import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDate, formatRate } from '@/lib/formatters'

export function RateCard({
  label,
  value,
  date,
  isSelected = false,
  onClick,
}: {
  label: string
  value: string | null | undefined
  date: string
  isSelected?: boolean
  onClick?: () => void
}) {
  return (
    <Card
      onClick={onClick}
      className={[
        'cursor-pointer border transition-colors duration-200',
        isSelected
          ? 'border-primary bg-primary shadow-lg shadow-card-selected-shadow'
          : 'border-border bg-card hover:border-primary',
      ].join(' ')}
    >
      <CardHeader className='pb-2'>
        <CardTitle
          className={[
            'text-sm font-normal transition-colors duration-200',
            isSelected ? 'text-foreground' : 'text-muted-foreground',
          ].join(' ')}
        >
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className='font-mono text-2xl font-semibold text-foreground transition-colors duration-200'
        >
          {formatRate(value)}
        </div>
        <div
          className={[
            'mt-1 text-xs transition-colors duration-200',
            isSelected ? 'text-card-selected-muted' : 'text-muted-foreground',
          ].join(' ')}
        >
          {formatDate(date)}
        </div>
      </CardContent>
    </Card>
  )
}
