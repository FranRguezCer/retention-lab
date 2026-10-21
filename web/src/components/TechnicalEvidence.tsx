import { count, empirical, labels, pairs, percent, type Data } from '../lib/data';
export const repo = 'https://github.com/FranRguezCer/retention-lab';
export const doc = (path: string) => `${repo}/blob/feat/retention-interactive-demo/${path}`;

export function TechnicalEvidence({ data, capacity }: { data: Data; capacity: number }) {
  const interval = data.bootstrap.capacities.find(r => r.requested_percent === capacity);
  return <section className="evidence-panel" aria-labelledby="evidence-title">
    <p className="eyebrow">BEHIND THE NUMBERS</p><h2 id="evidence-title">Technical Evidence</h2>
    <p>One frozen historical cohort. Transparent assumptions. No live predictions.</p>
    <details open><summary>Uncertainty at {capacity}% capacity</summary>
      <p>95% pointwise percentile intervals · {count(data.bootstrap.replicates)} paired subscriber bootstrap replicates.</p>
      {interval ? <div data-testid="bootstrap-intervals">
        <ul className="interval-list">{empirical.map(key => <li key={key}><span>{labels[key]} Recall</span><strong>{interval.recall[key].interval_95.map(v => percent(v)).join(' – ')}</strong></li>)}</ul>
        <ul className="interval-list">{pairs.map(([a, b]) => <li key={`${a}-${b}`}><span>{a === 'hgb' ? 'HGB' : 'LR'} − {b === 'business' ? 'Rule' : 'LR'}</span><strong>{interval.differences_pp[`${a}_minus_${b}`].interval_95.map(v => v.toFixed(2)).join(' – ')} pp</strong></li>)}</ul>
      </div> : <p className="notice">Uncertainty intervals are available at 5%, 10% and 20% outreach capacity.</p>}
      <p className="muted">Conditional on this cohort and frozen rankings, not guarantees of future performance. No interval interpolation; no retraining or reselection.</p>
    </details>
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
    <nav className="evidence-links" aria-label="Technical documentation"><a href={doc('docs/methodology.md')}>Methodology ↗</a><a href={doc('docs/results.md')}>Results ↗</a><a href={doc('docs/robustness.md')}>Bootstrap audit ↗</a><a href={doc('docs/limitations.md')}>Limitations ↗</a></nav>
  </section>;
}
