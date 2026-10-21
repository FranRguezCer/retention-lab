import { useState } from 'react';
import { CapacityControl } from './components/CapacityControl';
import { CapacityChart } from './components/CapacityChart';
import { StrategyComparison } from './components/StrategyComparison';
import { TechnicalEvidence } from './components/TechnicalEvidence';
import { doc, repo } from './lib/links';
import { capacityAt, count, percent, type Data } from './lib/data';

export default function App({ data }: { data: Data }) {
  const [capacity, setCapacity] = useState(10);
  const row = capacityAt(data, capacity);
  return <>
    <a href="#explorer" className="skip-link">Skip to capacity explorer</a>
    <header className="site-header"><a className="brand" href="#"><span className="brand-mark" aria-hidden="true">R<span>↗</span></span>Retention Lab</a>
      <nav aria-label="Main navigation"><a href="#evidence">Evidence</a><a href={repo}>GitHub ↗</a></nav></header>
    <main>
      <section className="hero"><p className="eyebrow"><span className="status-dot" /> A HISTORICAL CHURN PRIORITIZATION STUDY</p>
        <h1>Limited outreach.<br /><span>More informed priorities.</span></h1>
        <p className="hero-description">Compare historical churn rankings at a fixed outreach capacity.</p>
        <p className="hero-context">Explore one held-out February 2017 cohort. These retrospective results show observed churners identified—not live predictions or a real contact campaign.</p>
        <div className="cohort-strip"><span><strong>{count(data.n)}</strong> evaluated subscribers</span><span><strong>{percent(data.prevalence)}</strong> observed churn</span><span>KKBOX · February 2017</span></div>
      </section>
      <div id="explorer" className="explorer-grid"><CapacityControl row={row} onChange={setCapacity} />
        <aside className="reading-guide"><p className="eyebrow">READ THE RESULT</p><h2>A smaller list.<br />A sharper ranking.</h2>
          <p>At {capacity}% capacity, each strategy prioritizes the same number of subscribers ({count(row.hgb.k)}), but not necessarily the same people. Better ranking places more observed churners in that limited group.</p>
          <a href="#results">Compare the exact numbers ↓</a></aside></div>
      <CapacityChart rows={data.curve} row={row} />
      <div id="results"><StrategyComparison row={row} /></div>
      <section className="explanations" aria-labelledby="metrics-title"><p className="eyebrow">A QUICK READING GUIDE</p><h2 id="metrics-title">Three ways to understand your list</h2>
        <p className="muted">For validation-selected HGB at {capacity}% capacity. Each metric answers a different question.</p>
        <div className="definition-grid">
          <article><h3>Recall@K <span>Coverage</span></h3><strong className="definition-value">{percent(row.hgb.recall)}</strong><p>What share of all observed churners is in the selected list?</p><div className="formula">{count(row.hgb.captured)} / {count(data.positives)}</div><p className="denominator">Denominator: all observed churners</p></article>
          <article><h3>Precision@K <span>Concentration</span></h3><strong className="definition-value">{percent(row.hgb.precision)}</strong><p>What share of the selected subscribers was observed to churn?</p><div className="formula">{row.hgb.k === 0 ? 'Precision is undefined because no subscribers are selected.' : `${count(row.hgb.captured)} / ${count(row.hgb.k)}`}</div><p className="denominator">Denominator: subscribers selected (K){row.hgb.k === 0 ? ' · undefined at K = 0' : ''}</p></article>
          <article><h3>Lift@K <span>Over random</span></h3><strong className="definition-value">{row.hgb.lift === null ? 'N/A' : `${row.hgb.lift.toFixed(2)}×`}</strong><p>How concentrated is observed churn compared with the whole cohort?</p><div className="formula">Precision@K / prevalence</div><p className="denominator">Baseline: {percent(data.prevalence)} cohort prevalence</p></article>
        </div>
      </section>
      <aside className="boundary"><span aria-hidden="true">↳</span><div><h2>Identifying churn does not mean preventing churn.</h2><p>These are observed churners identified in a historical evaluation—not customers saved. Contact effectiveness requires a separate intervention study.</p></div></aside>
      <div id="evidence"><TechnicalEvidence data={data} capacity={capacity} /></div>
    </main>
    <footer><div><a className="brand" href="#">Retention Lab</a><p>An independent educational project. Not affiliated with KKBOX or Kaggle.</p></div>
      <div><p>Source: <a href="https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge">WSDM 2018 KKBOX Churn Prediction Challenge ↗</a></p>
        <p>Public aggregates only. No subscriber records, scores or models.</p><a href={doc('docs/data_attribution.md')}>Attribution & publication boundary ↗</a></div></footer>
  </>;
}
