# Retention Lab capacity explorer

A static React dashboard of the validated Phase 5/6 aggregates. Compare Random
expected, Business Rule, post-hoc Logistic Regression and validation-selected
HistGradientBoosting at exactly the same outreach capacity. No model executes
in the browser; no Python service or private data is needed.

**Status:** Ready for Netlify deployment — live verification pending.
No deployment has been performed. Phase 7 deployment remains pending; Phase 8
public presentation is in progress.

## Run locally

From the repository root, use Node 24 (`web/.nvmrc`) and npm:

```sh
cd web
npm ci
npm run dev
```

Open the local URL printed by Vite (normally `http://127.0.0.1:5173`).

```sh
npm run typecheck
npm test
npm run build
npm run check:build
npm run preview
```

The application has one page with hash anchors, so no SPA rewrite is needed.
Production output is `web/dist/`, ignored by Git. Dev and preview are local
verification servers, not required at deployment time.

## Data and metric contract

`src/main.tsx` dynamically imports only the original
`../../artifacts/capacity_comparison_v2.json` and `../../artifacts/robustness_v1.json`.
Vite bundles them into local static chunks. There are no maintained copies in
`public/`, no fetches to scoring APIs, and no external fonts/assets. Runtime
validation fails closed on missing/malformed records, duplicate capacities,
missing strategies, nonfinite/out-of-range metrics, inconsistent populations/K,
incorrect formulas, invalid nulls or mismatched bootstrap estimates/intervals.

- The 101 records are requested integer capacities 0–100%, **not every K**.
- K = floor(N × requested percentage / 100). The chart uses effective K/N on X;
  the slider chooses exact requested records. The UI shows requested capacity
  and exact K of N, with a floor-rounding note instead of unnecessary effective
  capacity decimals. Metrics still use the original full-precision values.
- Lines connect published points with straight segments, not smoothed curves.
  Tooltips and metrics use exact records; no metric interpolation occurs.
- At zero, Recall is 0; Precision and Lift are N/A. At full capacity Recall is
  100%. Random counts remain fractional and explicitly **expected**.
- Paired differences use full precision before formatting, in Recall percentage
  points and observed churner counts.
- Bootstrap intervals exist only at 5/10/20%. Recall intervals are fractions;
  difference intervals are already percentage points. These are conditional
  95% pointwise intervals, not production guarantees.
- HGB remains validation-selected. LR is a descriptive post-hoc addition.
  Identification does not establish prevention or intervention value.

`npm run check:build` compares both decoded shipped JSON chunks to the originals,
checks the comparison SHA-256 recorded by the robustness artifact, and enforces
a dist filename allowlist plus a focused private-data/secret-marker scan. This
is bounded integrity evidence, not a universal secret detector or a data license.
Publication terms remain in [data attribution](../docs/data_attribution.md).

## Architecture and checks

One React state value drives the control, chart markers, cards, table, differences
and bootstrap panel. Pure typed lookup/format/difference functions live in
`src/lib/data.ts`; small presentation components live in `src/components/`.
Recharts supplies responsive SVG, exact-point tooltips and keyboard chart
navigation; native range/buttons/details remain accessible without hover.
The selected-capacity table is the numeric alternative to the chart.

Vitest + Testing Library cover the real aggregate contract, tampering, 0/5/10/20/100%,
nulls, fractional expectations, differences and synchronized controls. Browser
tests run against the **production preview**, not mocked chart components:

```sh
npx playwright install chromium
npm run build
npm run test:browser
```

Linux may require Playwright's documented browser system libraries; do not treat
missing libraries as a passing browser check. Optional `PLAYWRIGHT_BROWSERS_PATH`
and `LD_LIBRARY_PATH` can select a locally provisioned browser/runtime. Browser
outputs go outside the worktree (`/tmp` by default). Chromium tests cover
1440px, 768px and 390px, keyboard range operation, four rendered curves/markers,
exact boundary metrics, bootstrap availability, console/network errors,
horizontal overflow, axe WCAG A/AA checks and fail-closed loading errors.
Automated accessibility does not replace screen-reader/user testing.

## Netlify preparation — not deployed

The root `netlify.toml` sets base `web`, command `npm ci && npm run build`,
publish directory `dist` relative to that base, and Node 24. The lockfile makes
installation reproducible. The full repository is checked out, so Vite can bundle
the two allowlisted JSON files outside `web/`. Only `web/dist` is published;
Python source, private data and local records are not served. Netlify installs
dependencies from the base directory; `requirements.txt` at repository root is
not a frontend dependency and no Python install/server is required.

These paths follow Netlify's [base and publish directory definitions](https://docs.netlify.com/build/configure-builds/monorepos/)
and [file-based configuration](https://docs.netlify.com/build/configure-builds/file-based-configuration/).
Keep base `web` and publish `dist` (not `web/dist` relative to base). No secrets, environment credentials, backend,
serverless functions or database are needed. No client-side router is used.

After separate deployment approval:
1. Connect this GitHub repository in Netlify and select the authorized branch.
2. Keep the checked-in build settings; do not publish the repository root.
3. Build and inspect the preview for asset paths, metrics, keyboard/mobile
   behavior and technical documentation links before publishing.

## UX refinement and scientific copy

The existing warm off-white/forest identity and four strategy colors are retained.
Body copy uses 15–16px, secondary/table text 13–15px, chart labels 13px, and small
labels normally at least 12px. Native controls have visible keyboard focus;
slider/buttons/disclosure headers provide a 44px interaction area.

- The control describes hypothetical selection, not an executed campaign. Equal K
  does not imply identical selected people. Requested capacity and K/N replace
  six-decimal effective percentages without changing calculations.
- Tooltip exploration is explicitly labeled **Hovered capacity** alongside
  **Selected capacity**. Moving over a different sample never changes the slider,
  selected markers, KPI cards or table. Straight segments join the 101 published
  samples; they are not every-K results.
- Metric cards show source-derived HGB examples and their denominators. Precision
  and Recall describe different populations; they are not complementary shares.
- Technical Evidence leads with paired-resampling facts, then three common-scale
  HGB−LR point/interval graphics. Exact 5/10/20 matches are highlighted. Other
  capacities show the published overview without inventing a selected interval.
  Marginal Recall and all three paired comparisons remain in expandable detail.
  The conditional, fixed-ranking intervals do not establish temporal performance.

Repository URLs are constructed centrally in `src/lib/links.ts` and point to
integrated documentation on `main`, including methodology. Unit and browser
tests verify stable destinations and preserve footer/Technical Evidence links.
At K = 0 the Precision card displays N/A and explains why precision is undefined,
rather than displaying a zero-over-zero fraction.

Before a separately authorized deployment, review the default page at 1440, 768
and 390px, then compare the 5/10/20% checkpoints, inspect a different hovered
capacity and navigate the slider/disclosures by keyboard. Automated axe and
Chromium checks do not certify all assistive technology or other browsers.
