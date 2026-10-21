import { useState } from 'react';
import { CapacityControl } from './components/CapacityControl';
import { CapacityChart } from './components/CapacityChart';
import { StrategyComparison } from './components/StrategyComparison';
import { TechnicalEvidence, doc, repo } from './components/TechnicalEvidence';
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
        <p className="hero-description">Find more future churners with a limited outreach budget.</p>
        <p className="hero-context">How many future churners can we identify when outreach capacity is limited? Compare four strategies using validated historical results—not real-time predictions.</p>
        <div className="cohort-strip"><span><strong>{count(data.n)}</strong> evaluated subscribers</span><span><strong>{percent(data.prevalence)}</strong> observed churn</span><span>KKBOX · February 2017</span></div>
      </section>
      <div id="explorer" className="explorer-grid"><CapacityControl row={row} onChange={setCapacity} />
        <aside className="reading-guide"><p className="eyebrow">READ THE RESULT</p><h2>A smaller list.<br />A sharper ranking.</h2>
          <p>At {capacity}% capacity, each strategy selects the same {count(row.hgb.k)} subscribers. Better ranking places more observed churners in that limited group.</p>
          <a href="#results">Compare the exact numbers ↓</a></aside></div>
      <CapacityChart rows={data.curve} row={row} />
      <div id="results"><StrategyComparison row={row} /></div>
      <section className="explanations" aria-labelledby="metrics-title"><p className="eyebrow">A QUICK READING GUIDE</p><h2 id="metrics-title">Three ways to understand your list</h2>
        <div className="definition-grid"><article><h3>Recall@K <span>Coverage</span></h3><p>Of all customers who eventually churned, how many did we identify in our selected group?</p></article>
          <article><h3>Precision@K <span>Concentration</span></h3><p>Among the customers selected for outreach, how many eventually churned?</p></article>
          <article><h3>Lift@K <span>Over random</span></h3><p>How much more concentrated is churn in our selected group compared with random selection?</p></article></div>
      </section>
      <aside className="boundary"><span aria-hidden="true">↳</span><div><h2>Identifying churn does not mean preventing churn.</h2><p>These are observed churners identified in a historical evaluation—not customers saved. Contact effectiveness requires a separate intervention study.</p></div></aside>
      <div id="evidence"><TechnicalEvidence data={data} capacity={capacity} /></div>
    </main>
    <footer><div><a className="brand" href="#">Retention Lab</a><p>An independent educational project. Not affiliated with KKBOX or Kaggle.</p></div>
      <div><p>Source: <a href="https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge">WSDM 2018 KKBOX Churn Prediction Challenge ↗</a></p>
        <p>Public aggregates only. No subscriber records, scores or models.</p><a href={doc('docs/data_attribution.md')}>Attribution & publication boundary ↗</a></div></footer>
  </>;
}
