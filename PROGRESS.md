# Retention Lab — Progress Log

> Last updated: 2026-10-19
> **State: four-file audit passed; RESTRICTED GO proposed for a February retrospective benchmark; acceptance pending.**
> This file records *actual progress*, not intentions. `PROJECT.md` is the scope reference and `ROADMAP.md` contains acceptance gates.

## Current focus

**Phase 1 — KKBOX feasibility audit and prediction-time contract**  
Status: `RESTRICTED GO — pending developer acceptance; not DONE`
Next objective: accept or reject the explicit single-cohort retrospective contract in `docs/problem_definition.md`; no operational-backtest claim or Phase 2 execution.

## Phase tracker

| Phase | Status | Evidence / blocker |
|---|---|---|
| 1. Dataset feasibility | RESTRICTED GO proposed | Four sources audited; original-only February subset established; developer acceptance pending |
| 2. EDA | NOT STARTED | Depends on Phase 1 |
| 3. Feature engineering | NOT STARTED | Depends on approved temporal contract |
| 4. Baselines + models | NOT STARTED | No scores or models trained |
| 5. Capacity evaluation | NOT STARTED | No empirical ranking curves calculated |
| 6. Validation + tests | NOT STARTED | 14 Phase 1 audit tests pass; no model validation |
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
- [x] All four local CSVs structurally inspected, hashed and checked for row/ID overlap and cutoff coverage; official download authenticity not independently verified.
- [x] Restricted original-February retrospective contract specified with audited source/cutoff population.
- [ ] Developer accepts the restricted protocol; operational temporal reconstruction remains unapproved.
- [x] Legacy auditor preserved; four-file/population auditor and 14 synthetic tests verified. No model, graph or deployment.

## Pending validations and open questions

1. Does the developer accept the original-February single-cohort benchmark,
   rather than require a realistic historical deployment or temporal transfer?
2. Before EDA, freeze and record the documented subscriber partition counts;
   keep the final holdout inaccessible to development. Do not build features now.
3. Confirm permitted future publication of derived artifacts separately; the
   indexed official rules do not provide blanket redistribution permission.
4. If broader future work uses v2 labels: authenticate its full cohort/window
   specification and resolve source-vintage/event semantics first.
5. Historical logging completeness, event arrival, Scala labeler boundaries and
   older mature training cohorts remain unproved for an operational backtest.

## Risks / blockers

- **Scope acceptance (pending):** the restricted contract is recommended, not
  silently substituted for an approved operational simulation.
- **Operational risk (excluded claim):** February labels need March follow-up;
  they cannot be treated as available for February or March 1 deployment.
- **Release risk (controlled):** v2 adds backdated, nonidentical records and
  changes diagnostic states; chosen inputs use the original vintage only.
- **Population risk (explicit limit):** record-based eligible subset, not all
  subscribers or all official targets. Same-day selected-state ambiguity is
  excluded; supplied labels are not independently regenerated.
- **Publication risk (pending):** developer confirms applicable conditions before
  any raw/derived data publication; educational local audit is not a clearance.

## Immediate next task for Codex

**Wait for acceptance of the restricted contract. Do not start Phase 2 here.**

If accepted and Phase 2 explicitly authorized: freeze the documented subscriber
partitions, then create a bounded EDA notebook on development users only, with
3–5 interpreted charts, 2–3 hypotheses and a cutoff-safe rule candidate. Preserve
final holdout isolation; no model training or feature pipeline in this audit.

If the operational objective is retained instead, its original evidence gaps
remain blocking; do not turn this RESTRICTED GO into an operational GO.

## Verification record

| Date | Check | Result | Evidence |
|---|---|---|---|
| 2026-10-18 | Planning documents authored | COMPLETE | `PROJECT.md`, `ROADMAP.md`, `PROGRESS.md` |
| 2026-10-19 | Four targets / official access | PARTIAL | Four local CSVs; indexed host answers and rules readable; data catalog/full Scala not verified |
| 2026-10-19 | Structural / aggregate cutoff audit | PASS / RESTRICTED | Four-file integrity and original-only cutoff population; not operational proof |
| 2026-10-19 | Unit tests / model evaluation | 14 PASS / NOT RUN | `python3 -m unittest discover -s tests -v`; no model evaluation |
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

## 2026-10-19 — Minimal KKBOX audit increment

- Added `scripts/audit_kkbox.py`, a standard-library streaming CSV audit with
  aggregate validation, source hashes and deterministic create-or-compare reports.
- Added `tests/test_audit_kkbox.py` and `docs/problem_definition.md`; ignored
  local reports in `.gitignore`. Existing skill and `.atl/` changes preserved.
- Observed RED before implementation; `python3 -m unittest discover -s tests -v`
  then passed all seven synthetic tests. No empirical metrics were generated.
- `python3 scripts/audit_kkbox.py` exited 2: target files absent. Real two-run
  source/report hash verification remains NOT RUN.
- Official Kaggle data page exposed no readable catalog to the browser. Names,
  sizes, terms and label semantics remain unverified; no agreements accepted.
- Next bounded task: developer reviews conditions, provides official catalog,
  downloads only confirmed targets manually; then run real audit twice.
- Historical eligibility, cohort comparisons and backtest approval remain pending.
  Phase 1 is not complete. No commits, models, scaffold or deployment.

## 2026-10-19 — Local files now available

- Inspected both target CSVs: train 45,635,134 bytes / 970,960 rows;
  transactions 115,394,513 bytes / 1,431,009 rows.
- Ran the real auditor twice: both exited 0. SHA-256 of both originals stayed
  unchanged across runs; report SHA-256 also stayed unchanged.
- No missing fields, invalid labels or invalid calendar dates in implemented
  checks. Transaction range: 2015-01-01–2017-03-31; expiry range:
  2016-04-19–2036-10-15. Far-future expiry requires semantic investigation.
- `git check-ignore -v` confirms both CSVs ignored by existing `data/raw/**`;
  `git ls-files -- data/raw` is empty. No ignore change was necessary.
- Updated `docs/problem_definition.md` with aggregate evidence and hashes.
- Supersedes the earlier local-file blocker, not the unverified provenance,
  conditions, label maturity or historical eligibility. Phase 1 remains open.
- Next task: verify official source/terms and temporal semantics; no models,
  commits or deployment performed.

## 2026-10-19 — Methodological feasibility assessment

### Completed and observed

- Read all project instructions/specification/roadmap/progress and the auditor,
  tests and prior problem definition. Stayed on `feat/kkbox-minimal-audit`.
- Official WSDM call confirms the broad renewal-within-30-days target:
  https://www.wsdm-conference.org/2018/call-for-participants.html
- Kaggle data and rules pages returned no readable body. Exact cohort dates,
  label polarity/boundaries, official labeler and usage conditions remain
  unverified. Participant descriptions were treated as secondary leads only.
- Ran a bounded CSV/temporary-SQLite diagnostic on the existing local CSVs:
  1,069,822 March transactions; only 92,686 labeled users have a transaction
  through February 28, while 878,274 have none in this extract.
- Verified 970,960 unique labeled IDs, 1,197,050 transaction IDs, 142,240 users
  with multiple transactions, and 27,940 same-day conflicting-state groups.
  Cohort overlap is NOT measured: only one undated label file is available.
- At February 28, 2,158 labeled users have ambiguous latest-day states.
  Calendar-valid distant expiries (including one in 2036) must not be treated
  as definitive churn dates.
- Replaced `docs/problem_definition.md` with source/evidence distinctions,
  inventory/hashes, aggregate checks, conditional prediction contract, timeline,
  leakage register, missing data, decision and bounded next steps.
- Local `data/audit/temporal_feasibility.json` records aggregate evidence and
  unchanged source hashes; ignored. Temporary customer-level SQLite removed.

### Checks and limitations

- `python3 -m unittest discover -s tests -v`: seven tests passed.
- `python3 scripts/audit_kkbox.py`: exit 0 against the existing report.
- One-off temporal diagnostic: exit 0; raw hashes unchanged before/after.
- Executed the documented reproduction diagnostic separately: all aggregate
  assertions passed; source hashes unchanged.
- `git diff --check`: passed after documentation edits.
- Executed calendar arithmetic: Feb 28 + 30 days = Mar 30; Mar 31 + 30 = Apr 30;
  Jan 31 + 30 = Mar 2; Dec 31 + 30 = Jan 30. These are not label-release claims.
- Raw files and reports are ignored; no raw files tracked. No new dependencies,
  dataset downloads, EDA, features, models, frontend, commits or pushes.
- Engram tools unavailable: evidence is retained in repository documentation,
  not claimed as persisted memory.

### Decision and remaining gate

**NO-GO with current files/evidence; Phase 1 remains BLOCKED, not DONE.**
The proposed March 1 cutoff allows inputs through Feb 28 only, determines active
March-expiry eligibility from as-of state, and requires March outcomes through
April 30 plus lag. Earlier training/validation labels must already be mature at
March 1. Supplied files do not prove these conditions. Even original February
labels would not all be mature at March 1. This is not an automatic PIVOT or an
approved RESTRICTED GO.

Next task: obtain readable authoritative cohort/labeler/rules documentation,
then evaluate precisely which earlier history and mature labels are missing.
Only after a defensible protocol is accepted should Phase 2 be authorized;
its scoped notebook would inspect development data, document 3–5 interpreted
charts / 2–3 hypotheses and a cutoff-safe baseline without tuning on final labels.

## 2026-10-19 — Four-source feasibility reassessment

This entry supersedes the current-evidence conclusion of the earlier two-file
NO-GO; historical entries above remain unchanged as an audit trail.

### Actual evidence

- `train.csv`: 46,667,771 bytes, 992,931 unique labeled IDs.
- `transactions.csv`: 1,729,298,376 bytes, 21,547,746 rows; transaction range
  2015-01-01–2017-02-28, with 20,639,483 rows through January 31.
- Existing v2 files remain unchanged. All four expected headers, row widths,
  nonempty values, label/flag values and calendar dates pass implemented checks.
- Targets overlap in 881,701 IDs; 45,990 shared labels differ. Original-only
  111,230 IDs and v2-only 89,259 IDs are not interchangeable cohorts.
- Transactions overlap in 1,134,533 IDs but zero full-row SHA-256 identities.
  Original file has 3,339 repeated full rows, v2 zero. V2 contains 361,187
  backdated/pre-March rows; merging releases changes latest-state diagnostics.
- Source-isolated audit: 874,581 original-source candidates have unambiguous
  latest selected state through Jan 31, recorded February expiry and no
  cancellation flag on that state; 874,580 have an original supplied label.
  Targeted population audit confirms 826,393 non-churn and 48,187 churn labels,
  with one unlabeled candidate; it exited 0 in about 40 seconds and preserved
  original source hashes. Local evidence: `data/audit/february_population.json`.
- Search-indexed primary KKBOX-host answers establish original February expiry
  labels and the 30-day concept, including late renewals still being churn:
  https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/discussion/40316
  https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/discussion/43622
- Indexed official rules now readable (sections 7–8): permitted uses and data
  security restrictions documented, not blanket public-data authorization.
- Full official v2 file specification and authenticated Scala labeler remain
  unavailable. No Scala file downloaded into the repository or runtime added.

### Changes and checks

- Added `scripts/audit_kkbox_history.py` and `tests/test_audit_kkbox_history.py`;
  retained the legacy auditor/tests unchanged. Added a targeted population mode
  to check target-class viability without repeating the full row-hash scan.
- RED observed before new implementation; source-isolation and population-mode
  assertions also failed before their implementations. Focused tests pass;
  `python3 -m unittest discover -s tests -v`: 14 tests passed.
- Real four-file v1 audit: exit 0, approximately 201 seconds. Real v2 audit with
  original-only summaries: exit 0, approximately 211 seconds. Source hashes
  unchanged before/after both scans; no measured peak-RAM claim.
- Latest complete report `data/audit/history_sources.json` is local and ignored;
  synthetic rerun/report immutability verified. Real v2 full scan ran once.
- Parent reran the population-only command: exit 0, existing report identical,
  original source fingerprints unchanged. Both target classes are present.
- RDD mode checked: globally off; no native review or mode change.
- Rewrote `docs/problem_definition.md` with four-file measurements, sources,
  report hashes, observed/proposed distinctions and the restricted contract.
- `git diff --check` passes. All raw files/reports ignored; no identifiers or
  original rows exported. No EDA, predictive feature table, model, dependency,
  frontend, commit or push. Existing skill/registry changes preserved.
- Engram tools unavailable; no persistent-memory write is claimed.

### Decision and boundary

**RESTRICTED GO proposed: original February single-cohort retrospective benchmark.**
Prediction index February 1, original-source inputs through January 31, explicit
record-based population, supplied original labels and deterministic subscriber
train/validation/final split. Fits occur retrospectively after outcomes are known;
there is NO claim the model existed or the labels were mature at February 1.
All policies will use the same final population, with development-only selection.

This is not a February→March transfer evaluation: full v2 month specification,
release semantics and operational maturity remain unresolved. No Scala replay
or April outcome reconstruction is needed to use supplied February benchmark
labels, but independent operational truth is not claimed.

**Phase 1 is not marked DONE:** developer acceptance of this limited estimand is
pending. No Phase 2 execution. The next action is acceptance of this contract;
then explicit EDA authorization, with subscriber partitions frozen first.

## 2026-10-19 — Account for remaining workspace changes

- At the developer's request, included the pending leading-blank-line removal
  in `.agents/skills/retention-stage/SKILL.md`; skill semantics are unchanged.
- Added `.atl/` to `.gitignore`: generated registry/cache contains machine-local
  absolute paths and is reproducible with `gentle-ai skill-registry refresh`.
- Registry refresh reported cache-hit. Raw data and audit reports remain ignored.
- Checked skill frontmatter, ignore coverage and `git diff --check`; no runtime
  code changed, so unit tests were not rerun for this repository-hygiene change.
- Methodological decision and phase status unchanged; restricted-protocol
  acceptance remains the next task. No Phase 2 work performed.
