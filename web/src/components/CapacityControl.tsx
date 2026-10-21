import { count, type CapacityRow } from '../lib/data';

export function CapacityControl({ row, onChange }: { row: CapacityRow; onChange: (p: number) => void }) {
  const p = row.requested_percent;
  return <section className="capacity-panel" aria-labelledby="capacity-heading">
    <div className="control-top">
      <div><p className="eyebrow">YOUR CONSTRAINT</p><h2 id="capacity-heading"><label htmlFor="capacity">Outreach capacity</label></h2></div>
      <output htmlFor="capacity" className="capacity-value">{p}<span>%</span></output>
    </div>
    <input id="capacity" type="range" min="0" max="100" step="1" value={p}
      aria-describedby="capacity-detail" aria-valuetext={`${p}% outreach capacity; ${count(row.hgb.k)} subscribers selected`}
      onChange={e => onChange(Number(e.target.value))} />
    <div className="range-labels"><span>0% · Nobody</span><span>100% · Everybody</span></div>
    <div className="quick-controls"><span>Explore capacity</span>{[5, 10, 20].map(v =>
      <button key={v} aria-pressed={p === v} onClick={() => onChange(v)}>{v}%</button>)}</div>
    <p id="capacity-detail" className="muted">{count(row.hgb.k)} of {count(row.hgb.n)} subscribers selected. K is rounded down from the requested capacity; this is a hypothetical selection, not contacts made.</p>
  </section>;
}
