import { CartesianGrid, Line, LineChart, ReferenceDot, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { colors, dashes, labels, percent, strategies, type CapacityRow } from '../lib/data';

export function CapacityChart({ rows, row }: { rows: CapacityRow[]; row: CapacityRow }) {
  const points = rows.map(r => ({ x: r.hgb.capacity * 100,
    requested: r.requested_percent,
    ...Object.fromEntries(strategies.map(key => [key, r[key].recall * 100])),
  }));
  return <section className="chart-panel" aria-labelledby="chart-title">
    <div className="section-heading"><div><p className="eyebrow">THE CAPACITY TRADE-OFF</p>
      <h2 id="chart-title">Churn Captured vs. Outreach Capacity</h2></div><span className="badge">Historical evaluation</span></div>
    <p id="chart-description" className="muted">Higher means more observed churners identified. Lines connect published 1% capacity samples, not every possible K. No smoothed or interpolated metrics.</p>
    <ul className="legend" aria-label="Strategy line styles">{strategies.map(key => <li key={key}>
      <svg width="26" height="12" aria-hidden="true"><line x1="0" y1="6" x2="26" y2="6" stroke={colors[key]} strokeWidth="3" strokeDasharray={dashes[key]} /></svg>
      {labels[key]}{key === 'logistic' ? ' · post-hoc' : key === 'hgb' ? ' · selected' : ''}
    </li>)}</ul>
    <p className="axis-caption">Observed churners identified (Recall, %)</p>
    <div className="chart" role="group" aria-label="Four-strategy recall curves" aria-describedby="chart-description chart-selection">
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <LineChart data={points} margin={{ top: 14, right: 18, bottom: 8, left: -12 }} accessibilityLayer>
          <CartesianGrid stroke="#e2e6e2" strokeDasharray="3 5" vertical={false} />
          <XAxis type="number" dataKey="x" domain={[0, 100]} ticks={[0, 20, 40, 60, 80, 100]} tickLine={false} tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} ticks={[0, 20, 40, 60, 80, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 12 }} />
          <Tooltip content={({ active, payload }) => {
            const point = active ? payload?.[0]?.payload as { requested: number } | undefined : undefined;
            if (!point) return null;
            const r = rows[point.requested];
            return <div className="chart-tooltip"><strong>{r.requested_percent}% requested · {percent(r.hgb.capacity, 6)} effective</strong>
              {strategies.map(key => <p key={key}>{labels[key]}: <b>{percent(r[key].recall)}</b></p>)}
            </div>;
          }} />
          {strategies.map(key => <Line key={key} type="linear" dataKey={key} name={labels[key]}
            stroke={colors[key]} strokeWidth={key === 'hgb' ? 3 : 2} strokeDasharray={dashes[key]}
            dot={false} isAnimationActive={false} />)}
          <ReferenceLine x={row.hgb.capacity * 100} stroke="#263d35" strokeDasharray="4 4" />
          {strategies.map(key => <ReferenceDot key={key} x={row.hgb.capacity * 100} y={row[key].recall * 100}
            r={5} fill={colors[key]} stroke="white" strokeWidth={2} />)}
        </LineChart>
      </ResponsiveContainer>
    </div>
    <p className="x-axis-caption">Subscribers selected (%)</p>
    <p id="chart-selection" data-testid="chart-selection" className="chart-selection">{row.requested_percent}% requested · {percent(row.hgb.capacity, 6)} effective. Exact selected values appear in the table below.</p>
  </section>;
}
