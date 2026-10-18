# Retention Lab — Project Specification

> Status: **planned; dataset feasibility not yet validated**  
> Last updated: 2026-10-18  
> This document is the source of truth for the **what and why** of the project. See `ROADMAP.md` for phase deliverables and `PROGRESS.md` for actual work status. Working conventions belong in `AGENTS.md`.

## 1. Project in one sentence

**Retention Lab investigates how much a machine-learning churn risk ranking improves the detection of future subscription churners when a business can contact only X% of eligible subscribers.**

**Research question:** *How much additional future churn can an ML-based ranking identify compared with random selection and a simple business rule, at fixed outreach capacities?*

### Audience and use case

- **Primary user:** retention / customer-success manager at a digital subscription service.
- **Decision:** given a fixed outreach capacity, which subscribers should be reviewed first?
- **User experience:** interactive simulator comparing historical *churn identified* under three selection policies.
- **Business framing:** a periodic (conceptually monthly) retention campaign; the exact prediction date, eligible population and horizons must be validated against the data.
- **Professional goal:** demonstrate supervised ML, feature engineering, temporally honest evaluation, ranking metrics, clear communication and proportionate product engineering.

**Important boundary:** predicting or identifying a future churner does **not** prove that contacting them prevents churn. Retention Lab does not estimate incremental retention, treatment effects or realized revenue saved.

## 2. Core experimental design

For each eligible subscriber at a specified historical prediction cutoff:

1. Construct features using **only information available at that cutoff**.
2. Estimate churn risk or generate a rank using each strategy.
3. Evaluate on a **common, held-out, labeled evaluation population**.
4. Select the top K users where K corresponds to X% of that population (document rounding and tie-breaking).
5. Count how many selected users actually churned; repeat for capacities from 0% to 100%.

### Strategies

| Strategy | Definition | Constraints |
|---|---|---|
| Random selection | Expected random selection or reproducible random draws | Clearly distinguish theoretical expectation from realized draws |
| Simple business rule | Risk ranking based on a justified, cutoff-available signal (e.g., auto-renew status or recent decline in usage) | Choose and freeze rule without inspecting final evaluation labels; specify tie-breaking |
| Machine learning | Supervised classification score, initially logistic regression and optionally a tree-based estimator | Preprocessing and model selection use training/validation data only |

The system must be able to report a **negative or negligible ML advantage** honestly. Do not select the model or baseline by repeatedly optimizing against the final evaluation set.

### Primary metrics

Let N be the eligible evaluation population, P the number of observed churners, K the number selected and TP@K the observed churners among the top K:

- **Recall@K:** `TP@K / P` (undefined when `P = 0`).
- **Precision@K:** `TP@K / K` (undefined when `K = 0`).
- **Lift@K:** `Precision@K / (P / N)` (undefined when prevalence is zero).
- **Outreach capacity:** `K / N`, displayed as a percentage.

Additional evaluation, as justified: average precision / PR-AUC, ROC-AUC, calibration and Brier score, cohort sensitivity, and uncertainty intervals with explicit assumptions.

### Central visualization

**Title:** `Churn Captured vs. Outreach Capacity`

- X-axis: percentage of eligible subscribers selected for outreach.
- Y-axis: percentage of observed future churners included in that selection (**Recall@K**).
- Curves: `Random Selection`, `Rule-Based Selection`, `ML-Based Selection`.
- At a selected X%, show the corresponding K, observed churners identified, Recall@K, Precision@K, Lift@K and ML-vs-rule difference.
- Under an expected-random policy, expected Recall@K follows X%; actual random simulations may fluctuate.
- Use empirical stepwise values or properly calculated interpolation, not hand-drawn/smoothed results. Include (0,0) and (100,100) only when the evaluation population has positive cases and these points have defined interpretation.
- Always state the evaluated cohort, temporal cutoff, total eligible users and churn prevalence.

**No fabricated empirical numbers in the published demo.** Mock curves are permitted only for temporary UI development when explicitly labeled and removed before release.

## 3. Data source: KKBOX (candidate, not yet confirmed)

**WSDM — KKBOX Churn Prediction Challenge**  
https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data

Expected file families to investigate (verify what is actually available):

- `train.csv`, `train_v2.csv` — labeled subscribers / cohorts.
- `transactions.csv`, `transactions_v2.csv` — payments, plan amounts, expiration and auto-renewal signals.
- `user_logs.csv`, `user_logs_v2.csv` — historical daily listening activity.
- `members.csv` — membership metadata.

**Do not assume** file sizes, schemas, completeness, historical coverage or permitted redistribution until verified locally and against competition rules.

The competition's churn definition is associated with failure to renew within a period after subscription expiry (commonly described as 30 days); **verify exact label semantics, cutoff dates and exceptions from primary documentation** before using them in the project.

### Required feasibility gate (Phase 1)

Investigate and document:

1. Kaggle access, file availability, data terms and redistribution rules.
2. Actual columns, data types, sizes and historical coverage.
3. The event semantics of cancellation, renewal, plan changes and expiration.
4. Who could have been known to be **eligible** at each hypothetical campaign date.
5. What was knowable at the cutoff (both features and eligibility).
6. The churn outcome window and **when its label would have become known**.
7. Possible overlap of subscribers across cohorts; repeated observations must be handled explicitly.
8. Whether a genuinely forward-looking evaluation can be reconstructed without future information.
9. An affordable compute / sampling approach that preserves valid temporal and label structure.
10. Whether a retrospective evaluation must be distinguished from a fully operational historical backtest.

**Critical example:** labels for subscriptions expiring late in February may not be known at the start of March if the outcome window extends 30 days after expiration. Never train a simulated March deployment using such unavailable labels and claim operational realism.

**Gate outcome:** (a) approve a defensible protocol, (b) approve an explicitly limited retrospective comparison, or (c) propose a better dataset. Make the decision and limitations explicit before advancing.

## 4. Planned technical approach

- **Python core:** pandas, NumPy, scikit-learn; focus on simple readable functions and scripts.
- **Exploration:** notebooks for EDA and interpretation, not as the only source of reproducible logic.
- **Models:** logistic regression as a first interpretable model; optionally HistGradientBoosting or a similar tree-based model when justified.
- **Evaluation:** reproducible functions and tests for top-K metrics, temporal integrity and baseline rankings.
- **Frontend:** React + TypeScript + Vite, with a small charting library (e.g., Recharts).
- **Deployment:** static frontend on Netlify using **precomputed, validated, aggregated JSON artifacts**.
- **No live model backend** in the MVP. Moving the slider re-reads/previews evaluation results, not predictions for arbitrary real customers.

### Indicative repository layout

```text
retention-lab/
├── AGENTS.md
├── PROJECT.md
├── ROADMAP.md
├── PROGRESS.md
├── README.md
├── pyproject.toml
├── docs/
│   ├── problem_definition.md
│   ├── methodology.md
│   ├── results.md
│   └── limitations.md
├── notebooks/
│   ├── 01_eda.ipynb
│   └── 02_model_analysis.ipynb
├── src/retention_lab/
│   ├── data.py
│   ├── features.py
│   ├── baselines.py
│   ├── train.py
│   ├── evaluate.py
│   └── export.py
├── tests/
├── data/              # local, gitignored
├── artifacts/         # derived, review before publication
└── web/               # React/Vite application for Netlify
```

This is a target, **not** a mandate to scaffold everything immediately. Add only what a current phase needs.

## 5. Data privacy and reproducibility

- Raw competition files, customer-level records, secrets and large intermediates must not be committed.
- Confirm licensing/competition rules before publishing any derived dataset or evaluation artifacts.
- Export only the minimum aggregated evaluation data necessary for the public UI; never expose subscriber IDs.
- Document data acquisition separately so others know how to reproduce results legally.
- Record all assumptions, random seeds and evaluation cohort/cutoffs.
- Validate exported JSON against source Python results.

## 6. Explicit non-goals

The MVP does **not** include real-time inference, production CRM, outreach automation, uplift/causal inference, customers 'saved', realized financial savings, authentication, a Python serving API, Kubernetes, microservices, LLM agents, RAG or advanced MLOps infrastructure. Any addition requires an explicit rationale and approval.

## 7. Product narrative and portfolio positioning

**One-liner:** *Turning churn predictions into defensible customer prioritization decisions.*

**Narrative arc:**

1. **Problem:** a subscription team cannot contact everyone.
2. **Question:** is ML ranking meaningfully better than random selection or an inexpensive business rule when capacity is scarce?
3. **Method:** reconstruct cutoff-safe features, train a simple classifier, compare all policies on the same held-out subscriber cohort.
4. **Evidence:** show the `Churn Captured vs. Outreach Capacity` curves and quote actual Recall@K / Lift@K at business-relevant capacities.
5. **Product:** publish a simple Netlify demo with an outreach slider and a technical-evidence panel.
6. **Honest limits:** detection is not causal retention; historical KKBOX conditions are not necessarily current-market conditions.

### Demo structure

**Business View:** a plain-language question, capacity slider, three curves, a few numerical cards and a clearly stated interpretation of **historical identified churn**.

**Technical Evidence:** cohort and cutoff, label definition, feature provenance, baselines, evaluation design, metrics, reproducibility and limitations.

### LinkedIn story (only after verified results)

**Hook:** *What if a subscription business could reach only 10% of its customers? Would machine learning identify more future churners than a simple rule?*

Then: challenge → experiment → real graph → quantified result (including an honest null result if appropriate) → lessons on leakage and decision-focused ML → links to demo and repository.

### Interview story (2–3 minutes)

Explain business constraint, target and time cutoff, baseline design, ML choice, why Recall@K matters beyond ROC-AUC, actual findings at 5/10/20% capacity, validation limits, static demo architecture and what intervention data would be required to claim real retained customers.

**Target evidence for CV:** churn prediction, classification, temporal feature engineering, model evaluation, ranking metrics and decision support **only when implemented and demonstrated**.

## 8. Success and stop criteria

The MVP succeeds when:

- Churn, eligibility, prediction cutoff and label maturity are documented and defensible.
- A shared held-out evaluation cohort has cutoff-safe scores from all three strategies.
- Recall@K, Precision@K and Lift@K are tested and computed from actual labels.
- The central three-curve plot is reproducible.
- A static Netlify demo presents real results and a transparent technical explanation.
- README, reproduction instructions and limitations are complete.

**Success does not require ML to beat the simple rule.** An honest demonstration that a rule is equally effective can be a strong result.

See `ROADMAP.md` for phase-by-phase acceptance gates and `PROGRESS.md` for live status.
