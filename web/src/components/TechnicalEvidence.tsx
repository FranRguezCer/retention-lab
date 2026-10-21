import { count, empirical, labels, pairs, percent, signed, type Data } from '../lib/data';
import { doc } from '../lib/links';
export { repo, doc } from '../lib/links';

export function TechnicalEvidence({ data, capacity }: { data: Data; capacity: number }) {
  const interval = data.bootstrap.capacities.find(r => r.requested_percent === capacity);
  // A common zero-based scale makes the three published intervals comparable.
  const comparisonMax = Math.max(...data.bootstrap.capacities.map(row =>
    row.differences_pp.hgb_minus_logistic.interval_95[1])) * 1.1;
  return <section className="evidence-panel" aria-labelledby="evidence-title">
    <p className="eyebrow">BEHIND THE NUMBERS</p><h2 id="evidence-title">Technical Evidence</h2>
    <p>One frozen historical cohort. Transparent assumptions. No live predictions.</p>
    <section className="evidence-overview" aria-labelledby="robustness-title">
      <h3 id="robustness-title">Robustness at a glance</h3>
      <div className="robustness-grid">
        <article className="robustness-fact"><strong>{count(data.bootstrap.replicates)}</strong><span>paired bootstrap replicates</span><p>The same resampled subscribers are used for every strategy.</p></article>
        <article className="robustness-fact"><strong>One cohort</strong><span>shared comparison population</span><p>All rankings are evaluated on the same eligible subscribers.</p></article>
        <article className="robustness-fact"><strong>Conditional</strong><span>uncertainty within this cohort</span><p>Frozen rankings; no retraining or model reselection.</p></article>
        <article className="robustness-fact"><strong>No temporal validation</strong><span>historical evidence only</span><p>These intervals do not establish performance in another period.</p></article>
      </div>
    </section>
    <section className="model-uncertainty" aria-labelledby="uncertainty-title">
      <h3 id="uncertainty-title">Model comparison uncertainty</h3>
      <p>HGB − Logistic Regression in Recall@K, in percentage points. Dots show observed differences; whiskers show 95% pointwise paired bootstrap percentile intervals.</p>
      <div className="uncertainty-grid">{data.bootstrap.capacities.map(row => {
        const estimate = row.differences_pp.hgb_minus_logistic;
        const [lo, hi] = estimate.interval_95;
        const position = (value: number) => 10 + value / comparisonMax * 280;
        return <article className="uncertainty-card" key={row.requested_percent}
          data-testid={`comparison-interval-${row.requested_percent}`} data-selected={row.requested_percent === capacity}>
          <div className="interval-card-heading"><h4>{row.requested_percent}% capacity</h4>{row.requested_percent === capacity && <span className="selected-evidence">Selected capacity</span>}</div>
          <strong className="interval-estimate">{signed(estimate.estimate)} pp</strong>
          <svg className="interval-whisker" viewBox="0 0 300 38" aria-hidden="true" focusable="false">
            <line className="interval-baseline" x1="10" x2="290" y1="19" y2="19" />
            <line className="interval-range" x1={position(lo)} x2={position(hi)} y1="19" y2="19" />
            {[lo, hi].map((value, i) => <line className="interval-range" key={i} x1={position(value)} x2={position(value)} y1="12" y2="26" />)}
            <circle className="interval-dot" cx={position(estimate.estimate)} cy="19" r="5" />
          </svg>
          <p className="interval-bounds">95% interval: {lo.toFixed(2)} to {hi.toFixed(2)} pp</p>
        </article>;
      })}</div>
      <p className="muted">Common scale from zero. Conditional on this cohort and frozen rankings, not guarantees of future performance.</p>
      {!interval && <p className="notice">Uncertainty intervals are available at 5%, 10% and 20% outreach capacity.</p>}
      <p className="muted">Use the capacity control above to explore these published checkpoints. No interval interpolation.</p>
      <details><summary>Full interval detail{interval ? ` · ${capacity}% capacity` : ''}</summary>
        {interval ? <div data-testid="bootstrap-intervals">
          <p>Recall@K intervals for each empirical strategy</p>
          <ul className="interval-list">{empirical.map(key => <li key={key}><span>{labels[key]} Recall</span><strong>{interval.recall[key].interval_95.map(v => percent(v)).join(' – ')}</strong></li>)}</ul>
          <p>Paired differences in Recall@K (percentage points)</p>
          <ul className="interval-list">{pairs.map(([a, b]) => <li key={`${a}-${b}`}><span>{a === 'hgb' ? 'HGB' : 'LR'} − {b === 'business' ? 'Rule' : 'LR'}</span><strong>{interval.differences_pp[`${a}_minus_${b}`].interval_95.map(v => v.toFixed(2)).join(' – ')} pp</strong></li>)}</ul>
        </div> : <p>Select 5%, 10% or 20% above to inspect all paired comparisons and marginal Recall@K intervals.</p>}
      </details>
    </section>
    <h3 className="methodology-title">Methodology &amp; limitations</h3>
    <details><summary>Cohort & evaluation protocol</summary><dl className="facts">
      <div><dt>Dataset</dt><dd>KKBOX · original February 2017 labeled cohort</dd></div>
      <div><dt>Feature cutoff</dt><dd>January 31, 2017 ({data.cutoff})</dd></div>
      <div><dt>Held-out evaluation</dt><dd>{count(data.n)} eligible subscribers · {count(data.positives)} observed churners</dd></div>
      <div><dt>Prevalence</dt><dd>{percent(data.prevalence)}</dd></div>
      <div><dt>Predictors</dt><dd>Seven approved transaction-derived features; preprocessing fit on training only</dd></div>
      <div><dt>Strategies</dt><dd>Random expected, renewal-off-first Business Rule, Logistic Regression and HistGradientBoosting</dd></div>
    </dl><p>HGB was selected on validation Recall@10% (at least +1 pp, with no decrease at 5% or 20%), then frozen before the original final evaluation. It was not selected using these test results.</p>
      <p>LR was added later using its original frozen ranking: a post-hoc descriptive comparison, not an independent confirmation. This is a retrospective evaluation, not a historical deployment simulation.</p>
      <p>ROC-AUC and Average Precision are global ranking diagnostics, not metrics at a selected outreach capacity.</p>
    </details>
    <details><summary>What this evidence cannot establish</summary><p>One 2017 company/cohort; no out-of-time or external validation. Source arrival timestamps and exact label adjudication remain unverified. Eligibility is conditioned on supplied competition labels. No causal retention effect, campaign ROI or production guarantee is estimated.</p></details>
    <nav className="evidence-links" aria-label="Technical documentation"><a href={doc('docs/methodology.md')}>Methodology ↗</a><a href={doc('docs/results.md')}>Results ↗</a><a href={doc('docs/robustness.md')}>Bootstrap audit ↗</a><a href={doc('docs/limitations.md')}>Limitations ↗</a><a href={doc('docs/data_attribution.md')}>Data attribution ↗</a></nav>
  </section>;
}
