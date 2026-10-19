# Retention Lab — Incremental Roadmap

> Status: Phase 3 DONE — reproducible cutoff-safe features; Phase 4 not started · Updated: 2026-10-19
> Follow `PROJECT.md` for scope and methodology, `AGENTS.md` for operating conventions, and `PROGRESS.md` for actual progress.

## Working method

Build **one small, testable increment at a time**. For each stage: clarify the scientific question → inspect evidence → implement only the agreed scope → verify acceptance criteria → document conclusions → update `PROGRESS.md` → stop. A phase is not complete merely because files exist.

**Budget:** approximately 30–45 hours of effective work, provisional. KKBOX access, size and temporal-label reconstruction are the highest-variance factors. If the feasibility gate fails, revise the plan before investing in model training or frontend work.

| Phase | Work | Indicative hours | Main deliverable |
|---|---|---:|---|
| 1 | Dataset feasibility and temporal protocol | 3–5 | Approved problem definition or documented pivot |
| 2 | Exploratory data analysis | 3–5 | Interpreted EDA notebook |
| 3 | Cutoff-safe feature engineering | 5–8 | Reproducible modeling table |
| 4 | Random/rule/ML baseline rankings | 4–6 | Comparable held-out scores |
| 5 | Capacity-constrained evaluation | 4–6 | Real three-curve chart and metrics |
| 6 | Robustness and verification | 3–5 | Tested and defensible results |
| 7 | React/Netlify demonstration | 5–7 | Interactive public-facing demo |
| 8 | Documentation and storytelling | 3–4 | GitHub/portfolio/interview package |

The phase-level estimates are rough and may total beyond the nominal range depending on overlap and rework. Scope reduction takes priority over rushing validation.

## Phase 1 — Data audit and prediction-time contract

**Goal:** determine whether a defensible KKBOX study is feasible.

**Closed: DONE — RESTRICTED GO (2026-10-19).** The developer accepted the
original February 2017 single-cohort retrospective benchmark in
`docs/problem_definition.md`, not an operational campaign simulation.
Feasibility investigations below are bounded by its documented limitations;
closure does not assert complete labeler reconstruction or verified arrival times.

**Tasks**
- [ ] Verify official dataset access, actual filenames, rules and local sizes.
- [ ] Inspect schemas, date ranges, missingness and label/cohort composition.
- [ ] Read and verify exact churn label semantics; investigate cancellations and renewals.
- [ ] Propose campaign cutoff(s), eligible population, feature cutoffs and outcome horizon.
- [ ] Determine *label maturity*, training label availability and separation of cohorts.
- [ ] Audit potential overlap and repeated subscriber observations.
- [ ] Identify leakage risks and feasible compute strategy; consider cutoff-safe sampling.
- [ ] Document distinction between retrospective research and an operationally faithful backtest.
- [ ] Record a go / restricted-go / no-go decision with supporting evidence.

**Deliverable:** `docs/problem_definition.md` with a timeline, data inventory, key assumptions, evaluation protocol and data-source decision.

**Acceptance gate:** explain for every row: who is eligible, what is known at prediction time, when churn is measured and when that result is known. No unresolved critical leak in the adopted evaluation protocol. **Do not train a model yet.**

## Phase 2 — EDA and hypothesis formation

**Goal:** understand the development population, target and signals before model training; do not inspect final holdout labels.

**Tasks**
- [x] Before EDA or final evaluation label access, materialize and verify the approved deterministic user partitions (SHA-256 of `retention-lab-feb2017-v1|` + ID, integer modulo 10: 0–5 train, 6–7 validation, 8–9 final); record counts, repeatability, disjointness and coverage without outcome values; isolate final labels from development.
- [x] Characterize churn prevalence, cohort size and available history.
- [x] Inspect nulls, duplicates, invalid dates, rare categories and outliers.
- [x] Compare relevant subscription/transaction signals by outcome without claiming causality.
- [x] Activity analysis not applicable: approved scope uses original transactions only.
- [x] Choose a plausible, cutoff-safe business baseline and document assumptions.
- [x] Write 3–5 interpreted charts and 2–3 testable hypotheses.

**Deliverable:** `notebooks/01_eda.ipynb` and concise notes in `docs/methodology.md`.

**Acceptance gate:** verified frozen user partitions and isolated final labels; development-only findings, data issues and a justified business-rule candidate; no post-cutoff inputs used as predictors.

**Verified 2026-10-19.** Two identical partition reconstructions, five interpreted
training-only charts, three exploratory hypotheses and documented-only rule;
22 tests and independent isolation/dependency verification. See `PROGRESS.md`
for observations and `docs/methodology.md` for limitations. No Phase 3 work.

## Phase 3 — Reproducible feature engineering

**Goal:** turn raw events into a model-ready **subscriber-at-cutoff** table.

**Tasks**
- [x] Implement input schema and parsing checks.
- [x] Reuse eligible subscribers; attach training labels and isolate validation labels; no final-label export.
- [x] Compute cutoff-safe subscription/payment features.
- [x] Activity aggregates not applicable: approved original-transactions-only scope.
- [x] Address missing values and document categorical encoding plans.
- [x] Check user/cohort uniqueness, date boundaries and source provenance.
- [x] Reuse and verify the deterministic subscriber partitions frozen before Phase 2 EDA; do not substitute chronological or cross-cohort partitions.
- [x] Keep processing in `src/retention_lab/`, not embedded only in a notebook.

**Deliverables:** `data.py`, `features.py`, tests and local processed tables (gitignored).

**Acceptance gate:** every column has meaning and an availability rule; no future events; reproducible output; integrity tests pass.

**Verified 2026-10-19:** 41 synthetic/structural tests, independent differential
and outcome-isolation probes, real frozen population and seven-column tables,
byte-identical cached outputs, four byte-identical rebuilt EDA artifacts and
unchanged two-kernel notebook reproduction. See `docs/features.md` and
`PROGRESS.md`. No Phase 4 work performed.

## Phase 4 — Baselines and first ML models

**Goal:** produce three comparable rankings on the same evaluation population.

**Tasks**
- [ ] Define deterministic expected random baseline or reproducible random draws.
- [ ] Implement and freeze the commercial rule, including ties.
- [ ] Train logistic regression with train-only preprocessing.
- [ ] Optionally compare one tree-based classifier using validation data.
- [ ] Generate out-of-sample risk scores / rankings without inspecting final labels to tune choices.
- [ ] Record training configuration, seed, metrics and limitations.

**Deliverables:** `baselines.py`, `train.py`, documented candidate selection and held-out scores.

**Acceptance gate:** all strategies evaluate the same eligible customers; predictions are reproducible and truly out of sample. ML is **not required** to win.

## Phase 5 — Capacity curves: the core research result

**Goal:** quantify the proportion of future churners identified at each outreach capacity.

**Tasks**
- [ ] Implement tested `Recall@K`, `Precision@K` and `Lift@K` definitions.
- [ ] Define the K rounding rule and tie handling; test K=0, K=N, no positives, and invalid inputs.
- [ ] Compute metrics for capacities from 0% to 100% with focus on 5%, 10%, 20%.
- [ ] Build the same-population curves: Random, Business Rule and ML.
- [ ] Compute ML-vs-rule and ML-vs-random differences at selected capacities.
- [ ] Export versioned, aggregated results with cohort metadata and no user identifiers.
- [ ] Document exactly what was measured and what is *not* inferred (no prevented churn).

**Deliverables:** `evaluate.py`, `export.py`, reproducible chart, metrics table and candidate JSON artifacts.

**Acceptance gate:** empirical metrics match hand-checkable samples; graph uses real evaluation results and answers the central research question.

## Phase 6 — Reliability, audit and limitations

**Goal:** make results defensible in a Data Scientist / ML Engineer interview.

**Tasks**
- [ ] Independently revisit the label-maturity, eligibility and feature-cutoff audit.
- [ ] Confirm no final-set-driven policy/model selection.
- [ ] Unit-test formulas and temporal invariants; inspect source-data assumptions.
- [ ] Compare ranking quality and model diagnostics (PR-AUC/ROC-AUC/calibration if feasible).
- [ ] Analyze stability / uncertainty (e.g., appropriate subscriber-level resampling) where feasible.
- [ ] Investigate counterintuitive or exceptionally strong performance.
- [ ] Record limits from dataset era, sampling, cohort coverage and retrospective design.
- [ ] Freeze evaluation artifacts used for the public site.

**Deliverables:** tests, `docs/results.md`, `docs/limitations.md`, validated aggregate artifacts.

**Acceptance gate:** reproducible evidence for every public claim and no known unresolved invalidating leakage.

## Phase 7 — Interactive static demo

**Goal:** help a business audience understand the trade-off in under a minute while preserving technical transparency.

**Tasks**
- [ ] Set up React + TypeScript + Vite under `web/`.
- [ ] Load **only validated aggregated** evaluation JSON.
- [ ] Implement an outreach-capacity slider, three-curve plot and selected-K metric cards.
- [ ] Explain in plain language the observed detection difference.
- [ ] Add a compact Technical Evidence panel with methodology, cohort and limits.
- [ ] Handle loading/error states, responsive layout and accessibility.
- [ ] Run frontend build and check displayed values against Python artifacts.
- [ ] Prepare/deploy the static site to Netlify with the developer's approval.

**Deliverable:** working interactive demo (no Python server and no per-customer data).

**Acceptance gate:** the capacity control changes correctly calculated historical results; business/technical meanings are unambiguous; build succeeds; no fabricated published outcomes.

## Phase 8 — GitHub and storytelling

**Goal:** turn the evidence into a portfolio case study for remote DS/ML roles.

**Tasks**
- [ ] Write a readable README with question, dataset constraints, method, graph and verified takeaway.
- [ ] Provide reproducibility commands, environment setup and lawful data download instructions.
- [ ] Add screenshots / short demo clip and Netlify URL.
- [ ] Summarize decisions, negative findings if any, and methodological limitations.
- [ ] Draft a short LinkedIn post **after** metrics are finalized.
- [ ] Prepare 2–3-minute interview walkthrough and likely technical Q&A.
- [ ] Create an accurate one-/two-line CV entry only for demonstrated skills.

**Deliverables:** README, demo link, portfolio text, LinkedIn draft, interview narrative.

**Acceptance gate:** a recruiter can understand value quickly; a technical reviewer can reproduce and challenge the findings; no unsupported impact claims.

## Milestones and control points

**Milestone A — Scientifically feasible (Phases 1–3):** dataset, temporal protocol and features are defensible. If not, pivot dataset or reduce scope **before** modeling.

**Milestone B — Answer obtained (Phases 4–6):** graph with real scores and critical validation; this alone is already a defensible technical study.

**Milestone C — Demonstrable product (Phases 7–8):** Netlify demo and portfolio story.

## Scope-control rules

- Every phase should end with verifiable evidence, not just generated files.
- Do not start frontend before empirical results are validated, except isolated temporary design mockups explicitly approved.
- Do not add SHAP, MLflow, cloud infrastructure, LLMs, CRM, production scoring or uplift analysis without a separate decision.
- If an issue blocks progress, document it in `PROGRESS.md` with options and a recommendation; do not silently redefine churn or evaluation.
