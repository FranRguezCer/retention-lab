import { count, difference, labels, lift, pairs, percent, signed, strategies, type CapacityRow } from '../lib/data';

export function StrategyComparison({ row }: { row: CapacityRow }) {
  return <section aria-labelledby="results-title" className="results-section">
    <div className="section-heading"><div><p className="eyebrow">Same capacity. Different priorities.</p>
      <h2 id="results-title">What your capacity finds</h2></div></div>
    <div className="metric-cards" aria-live="polite" aria-atomic="true">
      <article className="metric-card"><span>Subscribers selected · all strategies</span><strong data-testid="selected-count">{count(row.hgb.k)}</strong><small>of {count(row.hgb.n)} eligible subscribers</small></article>
      <article className="metric-card featured"><span>Observed churners identified · HGB</span><strong>{count(row.hgb.captured)}</strong><small>{percent(row.hgb.recall)} of all observed churners</small></article>
      <article className="metric-card"><span>Churn concentration · HGB</span><strong>{lift(row.hgb.lift)}</strong><small>{row.hgb.k ? 'compared with random selection' : 'Undefined when nobody is selected'}</small></article>
    </div>
    <div className="table-wrapper"><table className="strategy-table">
      <caption>Four strategies at {row.requested_percent}% outreach capacity</caption>
      <thead><tr><th scope="col">Strategy</th><th scope="col">Observed churners identified</th><th scope="col">Recall@K</th><th scope="col">Precision@K</th><th scope="col">Lift@K</th></tr></thead>
      <tbody>{strategies.map(key => <tr key={key} data-testid={`strategy-${key}`} className={key}>
        <th scope="row"><span className={`strategy-symbol ${key}`} aria-hidden="true">{key === 'random_expected' ? '○' : key === 'business' ? '◆' : key === 'logistic' ? '▲' : '●'}</span>{labels[key]}
          <small>{key === 'random_expected' ? 'Theoretical expectation' : key === 'logistic' ? 'Post-hoc descriptive comparison' : key === 'hgb' ? 'Validation-selected model' : 'Renewal-off-first ranking'}</small></th>
        <td data-label="Observed churners identified">{count(row[key].captured, key === 'random_expected')}</td>
        <td data-label="Recall@K">{percent(row[key].recall)}</td><td data-label="Precision@K">{percent(row[key].precision)}</td><td data-label="Lift@K">{lift(row[key].lift)}</td>
      </tr>)}</tbody></table></div>
    <p className="muted">Random counts are expected values, not actual identified people. N/A means undefined at K = 0. Empirical counts are original integers.</p>
    <p className="muted">Pairwise Recall@K differences · pp = percentage points. Differences are calculated before rounding.</p>
    <div className="differences">{pairs.map(([a, b]) => {
      const diff = difference(row, a, b);
      return <article key={`${a}-${b}`}><h3>{a === 'hgb' ? 'HGB' : 'Logistic Regression'} vs {b === 'business' ? 'Business Rule' : 'Logistic Regression'}</h3>
        <strong>{signed(diff.pp)} <span>pp Recall</span></strong><p>{signed(diff.captures, 0)} observed churners</p></article>;
    })}</div>
  </section>;
}
