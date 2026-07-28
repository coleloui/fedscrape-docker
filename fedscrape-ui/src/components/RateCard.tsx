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
          ? 'border-blue-600 bg-blue-600 shadow-lg shadow-blue-500/50'
          : 'border-border bg-card hover:border-blue-500',
      ].join(' ')}
    >
      <CardHeader className='pb-2'>
        <CardTitle
          className={[
            'text-sm font-normal transition-colors duration-200',
            isSelected ? 'text-white' : 'text-muted-foreground',
          ].join(' ')}
        >
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div
          className={[
            'font-mono text-2xl font-semibold transition-colors duration-200',
            isSelected ? 'text-white' : 'text-foreground',
          ].join(' ')}
        >
          {formatRate(value)}
        </div>
        <div
          className={[
            'mt-1 text-xs transition-colors duration-200',
            isSelected ? 'text-blue-100' : 'text-muted-foreground',
          ].join(' ')}
        >
          {formatDate(date)}
        </div>
      </CardContent>
    </Card>
  )
}
