import { useQuery } from '@tanstack/react-query'
import {
  latestRatesRatesLatestGet,
  listRateTypesRatesTypesGet,
  rateAverageRatesRateTypeAverageGet,
  rateSeriesRatesRateTypeGet,
  yieldSpreadRatesSpreadGet,
} from '@/api/generated'
import { queryKeys } from '@/lib/queryKeys'

const RATES_STALE_TIME = 5 * 60 * 1000

export function useLatestRates() {
  return useQuery({
    queryKey: queryKeys.latestRates,
    queryFn: async () => (await latestRatesRatesLatestGet()).data,
    staleTime: RATES_STALE_TIME,
  })
}

export function useRateTypes() {
  return useQuery({
    queryKey: queryKeys.rateTypes,
    queryFn: async () => (await listRateTypesRatesTypesGet()).data,
    staleTime: RATES_STALE_TIME,
  })
}

export function useRateSeries(rateType: string, limit: number = 30) {
  return useQuery({
    queryKey: queryKeys.rateSeries(rateType, limit),
    queryFn: async () =>
      (
        await rateSeriesRatesRateTypeGet({
          path: { rate_type: rateType },
          query: { limit },
        })
      ).data,
    staleTime: RATES_STALE_TIME,
    enabled: Boolean(rateType),
  })
}

export function useRateAverage(rateType: string, days: number = 30) {
  return useQuery({
    queryKey: queryKeys.rateAverage(rateType, days),
    queryFn: async () =>
      (
        await rateAverageRatesRateTypeAverageGet({
          path: { rate_type: rateType },
          query: { days },
        })
      ).data,
    staleTime: RATES_STALE_TIME,
    enabled: Boolean(rateType),
  })
}

export function useSpread(rateA: string, rateB: string) {
  return useQuery({
    queryKey: queryKeys.spread(rateA, rateB),
    queryFn: async () =>
      (
        await yieldSpreadRatesSpreadGet({
          query: { rate_a: rateA, rate_b: rateB },
        })
      ).data,
    staleTime: RATES_STALE_TIME,
    enabled: Boolean(rateA) && Boolean(rateB),
  })
}
