export const CHART_DEFAULTS = {
  margin: { top: 8, right: 8, bottom: 8, left: 8 },
  style: { background: 'transparent' },
}

export const AXIS_STYLE = {
  tick: { fill: 'var(--chart-axis)', fontSize: 11 },
  axisLine: { stroke: 'var(--chart-grid)' },
  tickLine: { stroke: 'transparent' },
}

export const GRID_STYLE = {
  strokeDasharray: '3 3',
  stroke: 'var(--chart-grid)',
  vertical: false,
}
