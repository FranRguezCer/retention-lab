# Retention Lab — Progress Log

> Last updated: 2026-10-18  
> **State: planning complete; implementation not started.**  
> This file records *actual progress*, not intentions. `PROJECT.md` is the scope reference and `ROADMAP.md` contains acceptance gates.

## Current focus

**Phase 1 — KKBOX feasibility audit and prediction-time contract**  
Status: `NOT STARTED`  
Next objective: verify the dataset and determine whether a leakage-free historical campaign evaluation is feasible.

## Phase tracker

| Phase | Status | Evidence / blocker |
|---|---|---|
| 1. Dataset feasibility | NOT STARTED | Official files have not been downloaded or audited |
| 2. EDA | NOT STARTED | Depends on Phase 1 |
| 3. Feature engineering | NOT STARTED | Depends on approved temporal contract |
| 4. Baselines + models | NOT STARTED | No scores or models trained |
| 5. Capacity evaluation | NOT STARTED | No empirical ranking curves calculated |
| 6. Validation + tests | NOT STARTED | No tests executed |
| 7. React demo | NOT STARTED | No frontend created or deployed |
| 8. Portfolio + storytelling | NOT STARTED | No empirical results or public claims |

## Decisions already made (project design, not implementation)

- Name: **Retention Lab**.
- Audience: subscription-retention / customer-success manager.
- Core question: how many future churners can be identified when outreach capacity is limited to X%?
- Campaign concept: periodic/monthly prioritization of eligible digital subscribers.
- Three policies: random selection, simple business rule, supervised ML score.
- Main chart: **Churn Captured vs. Outreach Capacity**.
- Main metrics: Recall@K, Precision@K, Lift@K.
- Data candidate: WSDM KKBOX Churn Prediction Challenge; **not yet validated**.
- Engineering direction: notebooks for exploration, Python modules for reproducible processing/evaluation, React/Vite static app on Netlify, precomputed aggregate JSON.
- Public interpretation: *future churners identified*, **not** customers saved or actual impact of interventions.
- Scope: small MVP; no online inference, CRM or causal uplift estimates.

## Completed work

- [x] Project goal, audience and research question defined in planning.
- [x] Proposed stack, repository structure and incremental phases specified.
- [x] Portfolio/LinkedIn/interview narrative outlined at a conceptual level.
- [ ] Dataset downloaded and inspected.
- [ ] Valid empirical evaluation protocol established.
- [ ] Any code, test, model, graph or deployment verified.

## Pending validations and open questions

1. Can KKBOX files be accessed and processed locally under acceptable resource and usage constraints?
2. What are the exact files, schemas, date ranges and label rules?
3. Who is eligible at a proposed campaign cutoff using only information then available?
4. When do the churn labels become mature/known relative to training and simulated decision dates?
5. Do the February/March cohorts permit a defensible retrospective comparison or only a restricted one?
6. Is a different historical subscription dataset preferable if honest evaluation becomes too complex?
7. What should the final business-rule baseline be, after inspecting available cutoff-safe variables?

## Risks / blockers

- **Methodological risk (open):** future transactions, future eligibility or immature churn labels could inflate performance.
- **Dataset risk (open):** large files, access terms and data coverage have not been verified firsthand.
- **Scope risk (managed):** frontend or infrastructure work could distract from validating the ML comparison.

No blocker is confirmed until relevant evidence has been inspected.

## Immediate next task for Codex

**Only begin Phase 1.**

1. Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `PROGRESS.md`.
2. Inspect the repo and any already available KKBOX files; do not assume they exist.
3. Verify official dataset documentation and actual file schemas where accessible.
4. Propose and critically test the prediction cutoff, eligible population, label window and label availability.
5. Create `docs/problem_definition.md` with a concrete temporal example, evidence and unresolved risks.
6. Recommend `GO`, `RESTRICTED GO` or `PIVOT`, explaining the evidence.
7. Update this log with what was truly checked and the next bounded task.

**Do not** train models, scaffold the full frontend or mark Phase 1 complete without satisfying its acceptance gate.

## Verification record

| Date | Check | Result | Evidence |
|---|---|---|---|
| 2026-10-18 | Planning documents authored | COMPLETE | `PROJECT.md`, `ROADMAP.md`, `PROGRESS.md` |
| — | KKBOX data access | NOT RUN | — |
| — | Dataset schema / cutoff audit | NOT RUN | — |
| — | Unit tests / model evaluation | NOT RUN | — |
| — | Frontend build / Netlify deployment | NOT RUN | — |

## Session log

### 2026-10-18 — Initial handoff

- Established project scope, staged roadmap and initial progress baseline.
- No implementation, dataset download, model evaluation or deployment was performed.

### Template for future sessions

**Date:** YYYY-MM-DD  
**Phase / task:** ...  
**Changed files:** ...  
**Evidence / checks run:** ...  
**Decisions:** ...  
**Blockers / unknowns:** ...  
**Next small task:** ...

---

**Progress rule:** Never mark a phase `DONE` based solely on a generated file. Link its acceptance evidence and note which checks actually ran.
