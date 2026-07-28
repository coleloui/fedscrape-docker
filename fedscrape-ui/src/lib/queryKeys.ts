export const queryKeys = {
  latestRates: ['rates', 'latest'] as const,
  rateTypes: ['rates', 'types'] as const,
  rateSeries: (rateType: string, limit: number) =>
    ['rates', 'series', rateType, limit] as const,
  rateAverage: (rateType: string, days: number) =>
    ['rates', 'average', rateType, days] as const,
  spread: (rateA: string, rateB: string) =>
    ['rates', 'spread', rateA, rateB] as const,
}
