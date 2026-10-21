import { CartesianGrid, Line, LineChart, ReferenceDot, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { colors, count, dashes, labels, percent, strategies, type CapacityRow } from '../lib/data';

/** Present one published sample independently of the dashboard selection. */
export function CapacityTooltip({ hovered, selected }: { hovered: CapacityRow; selected: CapacityRow }) {
  return <div className="chart-tooltip">
    <strong>Hovered capacity: {hovered.requested_percent}%</strong>
    <p className="tooltip-selection">Selected capacity: {selected.requested_percent}%</p>
    <p className="tooltip-population">{count(hovered.hgb.k)} of {count(hovered.hgb.n)} subscribers selected</p>
    <p className="tooltip-metric">Observed churners identified (Recall@K)</p>
    {strategies.map(key => <p className="tooltip-strategy" data-testid={`tooltip-${key}`} key={key}>
      <span><svg width="20" height="12" aria-hidden="true"><line x1="0" y1="6" x2="20" y2="6"
        stroke={colors[key]} strokeWidth="3" strokeDasharray={dashes[key]} /></svg>{labels[key]}</span>
      <b>{percent(hovered[key].recall)}</b>
    </p>)}
    <p className="tooltip-note">Random expected is a mathematical expectation.</p>
  </div>;
}

export function CapacityChart({ rows, row }: { rows: CapacityRow[]; row: CapacityRow }) {
  const points = rows.map(r => ({ x: r.hgb.capacity * 100,
    requested: r.requested_percent,
    ...Object.fromEntries(strategies.map(key => [key, r[key].recall * 100])),
  }));
  return <section className="chart-panel" aria-labelledby="chart-title">
    <div className="section-heading"><div><p className="eyebrow">THE CAPACITY TRADE-OFF</p>
      <h2 id="chart-title">Churn Captured vs. Outreach Capacity</h2></div><span className="badge">Historical evaluation</span></div>
    <p id="chart-description" className="muted">Higher means more observed churners identified. Lines connect the 101 published integer-capacity samples (0–100%), not every possible K. Tooltip values come from those samples only.</p>
    <ul className="legend" aria-label="Strategy line styles">{strategies.map(key => <li key={key}>
      <svg width="26" height="12" aria-hidden="true"><line x1="0" y1="6" x2="26" y2="6" stroke={colors[key]} strokeWidth="3" strokeDasharray={dashes[key]} /></svg>
      {labels[key]}{key === 'logistic' ? ' · post-hoc' : key === 'hgb' ? ' · validation-selected' : ''}
    </li>)}</ul>
    <p className="axis-caption">Observed churners identified (Recall@K, %)</p>
    <div className="chart" role="group" aria-label="Four-strategy recall curves" aria-describedby="chart-description chart-selection">
      <ResponsiveContainer width="100%" height="100%" minWidth={0}>
        <LineChart data={points} margin={{ top: 14, right: 18, bottom: 8, left: -12 }} accessibilityLayer>
          <CartesianGrid stroke="#cbd3cd" strokeDasharray="3 5" vertical={false} />
          <XAxis type="number" dataKey="x" domain={[0, 100]} ticks={[0, 20, 40, 60, 80, 100]} tickLine={false} tick={{ fontSize: 13, fill: '#4b5e55' }} />
          <YAxis domain={[0, 100]} ticks={[0, 20, 40, 60, 80, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 13, fill: '#4b5e55' }} />
          <Tooltip content={({ active, payload }) => {
            const point = active ? payload?.[0]?.payload as { requested: number } | undefined : undefined;
            if (!point) return null;
            const hovered = rows.find(r => r.requested_percent === point.requested);
            return hovered ? <CapacityTooltip hovered={hovered} selected={row} /> : null;
          }} />
          {strategies.map(key => <Line key={key} type="linear" dataKey={key} name={labels[key]}
            stroke={colors[key]} strokeWidth={key === 'hgb' ? 3 : 2} strokeDasharray={dashes[key]}
            dot={false} isAnimationActive={false} />)}
          <ReferenceLine x={row.hgb.capacity * 100} stroke="#263d35" strokeWidth={2} strokeDasharray="4 4" />
          {strategies.map(key => <ReferenceDot key={key} x={row.hgb.capacity * 100} y={row[key].recall * 100}
            r={6} fill={colors[key]} stroke="white" strokeWidth={2} />)}
        </LineChart>
      </ResponsiveContainer>
    </div>
    <p className="x-axis-caption">Subscribers selected (%)</p>
    <p id="chart-selection" data-testid="chart-selection" className="chart-selection">Selected capacity: {row.requested_percent}% outreach capacity · {count(row.hgb.k)} of {count(row.hgb.n)} subscribers selected. Exact selected values appear in the table below.</p>
  </section>;
}
