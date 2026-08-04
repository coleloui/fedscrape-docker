export const queryKeys = {
  latestRates: ['rates', 'latest'] as const,
  rateTypes: ['rates', 'types'] as const,
  rateSeries: (rateType: string, limit: number) =>
    ['rates', 'series', rateType, limit] as const,
  rateSeriesRange: (rateType: string, start: string, end?: string) =>
    ['rates', 'series', rateType, start, end] as const,
  rateAverage: (rateType: string, days: number) =>
    ['rates', 'average', rateType, days] as const,
  spread: (rateA: string, rateB: string) =>
    ['rates', 'spread', rateA, rateB] as const,
  rateSnapshot: (date: string) => ['rates', 'snapshot', date] as const,
}
