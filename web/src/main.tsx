import { StrictMode, Suspense, lazy, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { validateData, type Data } from './lib/data';
import './styles/main.css';
const App = lazy(() => import('./App'));

export function Bootstrap() {
  const [state, setState] = useState<{ data?: Data; error?: string }>({});
  useEffect(() => {
    let active = true;
    // Explicit allowlist: imports resolve to the original committed public aggregates.
    Promise.all([
      import('../../artifacts/capacity_comparison_v2.json'),
      import('../../artifacts/robustness_v1.json'),
    ]).then(([comparison, robustness]) => {
      const data = validateData(comparison.default, robustness.default);
      if (active) setState({ data });
    }).catch(() => {
      if (active) setState({ error: 'The validated historical results could not be loaded. No metrics are displayed. Please reload the page.' });
    });
    return () => { active = false; };
  }, []);
  if (state.error) return <main className="load-state"><h1>Results unavailable</h1><p role="alert">{state.error}</p><button onClick={() => window.location.reload()}>Reload results</button></main>;
  if (!state.data) return <p role="status" className="load-state">Loading validated historical results…</p>;
  return <Suspense fallback={<p role="status" className="load-state">Loading the capacity explorer…</p>}><App data={state.data} /></Suspense>;
}
createRoot(document.getElementById('root')!).render(<StrictMode><Bootstrap /></StrictMode>);
