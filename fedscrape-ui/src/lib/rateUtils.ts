export interface RateDataPoint {
  date: string
  value: number | null
}

export const computeSpread = (
  tenData: RateDataPoint[],
  twoData: RateDataPoint[],
): RateDataPoint[] => {
  if (tenData.length !== twoData.length) {
    console.warn(
      `computeSpread: array length mismatch — ` +
        `tenData=${tenData.length}, twoData=${twoData.length}. ` +
        `Truncating to shorter array.`,
    )
  }

  const length = Math.min(tenData.length, twoData.length)

  return Array.from({ length }, (_, i) => ({
    date: tenData[i].date,
    value:
      tenData[i].value != null && twoData[i].value != null
        ? tenData[i].value! - twoData[i].value!
        : null,
  }))
}
