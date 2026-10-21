# Retention Lab — Progress Log

> Last updated: 2026-10-21
> **State: Phases 1–5 DONE (Phase 1 RESTRICTED GO); Phase 6 DONE; Phase 7 implemented / deployment pending; Phase 8 NOT STARTED.**
> This file records *actual progress*, not intentions. `PROJECT.md` is the scope reference and `ROADMAP.md` contains acceptance gates.

## Current focus

Phase 7 static dashboard implementation is locally verified on
`feat/retention-interactive-demo`, based on fetched `origin/main`
`787534281c9d53914bb72b17b1935f385db844cc`. See the dated entry below for
checks and delivery. No main merge, PR, Netlify deployment or Phase 8 work.
Historical models/rankings, evaluation and robustness artifacts remain unchanged.

## Phase tracker

| Phase | Status | Evidence / blocker |
|---|---|---|
| 1. Dataset feasibility | DONE — RESTRICTED GO | Four-source audit and restricted contract: `docs/problem_definition.md` §§2–7; explicit developer acceptance below |
| 2. EDA | DONE | Frozen verified partitions, five interpreted training-only charts and independent isolation/dependency verification |
| 3. Feature engineering | DONE | Seven predictors; exact real frozen population, cache repeatability and byte-identical EDA reconstruction |
| 4. Baselines and ML models | DONE | LR preserved; HGB selected on validation, private rankings/models anchored in pre-test commit; docs/models.md |
| 5. Capacity evaluation | DONE | Original evaluation preserved; post-hoc LR, sampled aggregates, four-curve PNG, conditions review and independent checks passed |
| 6. Reliability and robustness | DONE | `docs/robustness.md`, `docs/limitations.md`, fixed reproducible bootstrap, independent probes and 84/84 full-suite PASS |
| 7. React demo | IMPLEMENTED — deployment pending | `web/`, validated aggregates, frontend checks; no Netlify deployment |
| 8. Portfolio + storytelling | NOT STARTED | Final portfolio narrative pending; training-only EDA aggregates available |

## Decisions already made (project design, not implementation)

- Name: **Retention Lab**.
- Audience: subscription-retention / customer-success manager.
- Core question: how many future churners can be identified when outreach capacity is limited to X%?
- Campaign concept: periodic/monthly prioritization of eligible digital subscribers.
- Three strategy families: Random, Business Rule and ML; four public curves:
  Random expected, Business Rule, Logistic Regression and selected HGB.
- Main chart: **Churn Captured vs. Outreach Capacity**.
- Main metrics: Recall@K, Precision@K, Lift@K.
- Data source: WSDM KKBOX; original February cohort approved only for the restricted retrospective benchmark.
- Engineering direction: notebooks for exploration, Python modules for reproducible processing/evaluation, React/Vite static app on Netlify, precomputed aggregate JSON.
- Public interpretation: *future churners identified*, **not** customers saved or actual impact of interventions.
- Scope: small MVP; no online inference, CRM or causal uplift estimates.

## Completed work

- [x] Project goal, audience and research question defined in planning.
- [x] Proposed stack, repository structure and incremental phases specified.
- [x] Portfolio/LinkedIn/interview narrative outlined at a conceptual level.
- [x] All four local CSVs structurally inspected, hashed and checked for row/ID overlap and cutoff coverage; official download authenticity not independently verified.
- [x] Restricted original-February retrospective contract specified with audited source/cutoff population.
- [x] Developer explicitly accepted the restricted protocol on 2026-10-19; operational temporal reconstruction remains unapproved.
- [x] Initial audit increment: legacy auditor preserved; four-file/population
  auditor and 14 synthetic tests verified. No model/graph existed at that stage.
- [x] Subsequent Phases 2–5: EDA, seven-feature tables, both ML candidates,
  validation-selected HGB and public four-strategy post-hoc comparison completed.
  Phase 6 robustness audit and Phase 7 static demo are also implemented; Netlify
  deployment remains pending. Phase 8 has not started.

## Pending validations and open questions

1. Phase 6 full suite and independent verification passed; publication evidence is
   finalized in the delivery report (remote SHA and clean worktree).
2. Final access is consumed: no raw-label reopening, retraining or reselection.
3. Arrival times, source authenticity and exact label adjudication remain unverified;
   no temporal generalization or causal retention claim is supported.
4. Aggregate-only publication follows the existing owner authorization/attribution
   boundary, not an express derivative-data license.

## Risks / blockers

- **Scope accepted (restricted):** retrospective single-cohort comparison only;
  no operational simulation or temporal validation between cohorts.
- **Operational risk (excluded claim):** February labels need March follow-up;
  they cannot be treated as available for February or March 1 deployment.
- **Release risk (controlled):** v2 adds backdated, nonidentical records and
  changes diagnostic states; chosen inputs use the original vintage only.
- **Population risk (explicit limit):** record-based eligible subset, not all
  subscribers or all official targets. Same-day selected-state ambiguity is
  excluded; supplied labels are not independently regenerated.
- **Publication boundary:** current limited owner authorization and official-terms
  review permit only the described aggregate release; no raw/individual data or
  express derivative license. Stop affected publication if incompatible terms emerge.

## Next suggested task

Review the refined Phase 7 dashboard visually, then separately authorize Netlify
deployment and live-site checks. Do not begin Phase 8 or merge automatically.

## How to read the historical record

The dated entries below preserve the decisions and restrictions in force at
each stage. References to old branches, pending publication, unstarted phases,
"no merge" or "do not change main" are historical work boundaries, superseded
only by later explicit authorizations recorded here. The current status above
and the latest dated entry are the live handoff. Historical test counts are
not new executions; new checks are recorded separately when actually run.

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

## 2026-10-19 — Phase 1 formal closure

**DONE — RESTRICTED GO.** Developer acceptance (verbatim):

> He revisado y **acepto expresamente el contrato RESTRICTED GO** de la Fase 1 de Retention Lab: benchmark retrospectivo de la cohorte original de febrero de 2017.

### Acceptance evidence

| Phase 1 criterion | Evidence and restricted interpretation |
|---|---|
| Who is eligible | `docs/problem_definition.md` §§4–5: original-source pre-cutoff state, February recorded expiry, non-cancelled/unambiguous state; 874,581 candidates, 874,580 supplied labels |
| What is known at index | Original transactions dated through January 31 for February 1 index; event date is a proxy, not verified arrival time; no v2 inputs |
| When churn is measured / known | Supplied original February labels; follow-up through March 30, conservatively March 31 plus lag; actual release unknown; fitting is retrospective only |
| No unresolved critical leak in adopted protocol | User-disjoint deterministic split specified before EDA/final-label access; development-only selection and same final population for all policies; implementation checks remain future gates, not claimed complete |
| Explicit scope acceptance | Developer statement above accepts the limited estimand; broader operational and cross-cohort claims remain excluded |

Coverage, missing labels, ambiguous events, unverified labeler/arrival semantics,
source provenance and lack of temporal validation between cohorts remain limits,
not resolved facts. Publication permissions remain a separate pending decision.
Prior log entries are historical; this entry supersedes acceptance-pending status.

Updated `PROJECT.md`, `ROADMAP.md`, `PROGRESS.md` and status/next-step wording in
`docs/problem_definition.md`. Roadmap changes only remove contradictions with
the accepted scope and partition ordering. No new scientific results are claimed.

Verification: documentary acceptance/consistency readback and `git diff --check`
passed. Existing audit suite: `python3 -m unittest discover -s tests -v` —
14 passed. Raw-data audits were not rerun for this documentation-only closure;
prior measured evidence is cited above, not represented as newly reproduced.
No data downloads, EDA, features, training, frontend, split materialization,
commit or push. Engram unavailable; no memory save or session summary claimed.

Next small task: after separate Phase 2 authorization, materialize and verify
the frozen subscriber partitions and holdout isolation, without EDA or model work.


## 2026-10-19 — Isolated Phase 2 implementation

### Scope and implementation

- User authorized the supplied Phase 2 plan, including aggregate publication,
  existing SSH for fetch/push, `feat/kkbox-eda`, and the completion commit only
  after all checks. No PR, Phase 3, model, baseline implementation or deployment.
- Fetch confirmed `main` = `origin/main` = `ec3e456`; feature branch absent locally
  and remotely before creation. Main remains untouched. RDD globally off, unchanged.
- Added `src/retention_lab/eda_prepare.py` and preparation CLI: streaming original
  transactions, exact all-field SQLite deduplication, latest-day eligibility,
  deterministic SHA-256 partitions and private create-once artifacts. Existing
  auditors remain untouched and were not rerun on real data.
- Manifest/assignments are verified before interpreting only training label values.
  Label-source fingerprint hashes sorted identifiers only; transaction fingerprint
  hashes full bytes. Training artifact has a separate byte fingerprint. This
  deliberately makes non-training outcome changes irrelevant to preparation.
- Added training-only aggregate/plot logic, five interpreted notebook figures,
  `artifacts/eda_summary.json`, methodology, pinned direct/full dependency files
  and a two-clean-kernel execution/privacy-check command. No raw rows or IDs published.
- Python 3.12.3 environment is `.venv-eda`; existing Python 3.15 `.venv` preserved.
  Direct versions: pandas 2.2.3, matplotlib 3.9.4, nbformat 5.10.4,
  nbclient 0.10.2, ipykernel 6.29.5. Full environment pinned and pip check passed.
  Sandbox PyPI DNS and kernel socket attempts failed; authorized out-of-sandbox
  installation/local execution succeeded. No failed execution outputs were published.
- Local generated `.codegraph/` and `.venv-eda/` are ignored. Engram unavailable;
  no memory mirror, save or session summary is claimed.

### Real partition and training-only evidence

- Preparation executed twice, exiting 0 in 238 and 244 seconds. Both reconstructed
  874,581 candidates, 874,580 labeled identifiers and one unlabeled exclusion.
- Train **523,998 (59.9142%)**; validation **175,651 (20.0840%)**;
  final **174,931 (20.0017%)**. No validation/final label prevalence calculated.
- All four private artifact hashes matched byte-for-byte; parent rechecked them.
  Assignment SHA-256: `9bacf5cf7c279c40c98dd96df0bd842f5ce59592f4443a912929638095d87edd`.
- Training: **29,015 churners / 523,998 users (5.5372%)**. History contains
  7,792,865 exact distinct transactions and 1,452 duplicate copies. No missing
  selected latest fields or missing numeric raw values among these training records.
- Historical training diagnostics: 3,907 ambiguous auto-renew subscriber-days;
  31,458 distinct transactions with recorded expiry before event date; zero
  recorded expiry beyond the diagnostic February 1, 2018 threshold. These are
  descriptions, not invalidity adjudications. Validated calendar dates fail closed
  if malformed; future recorded expiry is not excluded simply for being future.

### Observed findings and hypotheses

| Training-only comparison | Observed churn | Interpretation |
|---|---|---|
| Auto-renew off vs on | 19,294/63,335 = 30.46%; 9,721/460,663 = 2.11% | Descriptive direction supports hypothesis 1; no intervention effect |
| Shortest vs longest observed-history quartile | 9,583/131,260 = 7.30%; 4,287/130,002 = 3.30% | Supports hypothesis 2 descriptively; not actual tenure |
| January transactions: 0–1 vs >1 | 28,739/520,925 = 5.52%; 276/3,073 = 8.98% | Tied marginal quartiles collapse; transaction count is not payment success |
| Latest duration <=30 vs >30 | 22,707/510,754 = 4.45%; 6,308/13,244 = 47.63% | Plan/renewal/channel mix can confound this association |
| Latest amount <=99; >99–149; >149 | 2.09% (231,723); 5.13% (231,813); 20.29% (60,462) | Recorded amounts, not verified revenue or price elasticity |
| Observed on-to-off vs always on | 1,879/13,586 = 13.83%; 8,660/428,138 = 2.02% | Supports hypothesis 3 descriptively; ambiguous days break transition chains |

Numeric groups use training marginal quartiles, never label-optimized cutpoints.
Every chart includes all training users with explicit unknown treatment and group
denominators. The three hypotheses are exploratory, not significance tests.
Candidate rule is documented only: renewal off first, ascending split digest then
ID for ties. It has not been implemented or tuned on any held-out outcome.

### Verification and limits

- Synthetic preparation RED: four missing-CLI failures; GREEN: four passed,
  including exact hash, ordering, duplicate/conflict eligibility, cutoff and
  non-training-label poisoning. Aggregate RED: missing module; GREEN: two passed.
- Full suite initially 20 passed. A structural notebook regression test then
  exposed removed required display-output metadata; retained empty metadata,
  added pre-publication nbformat validation, and reran the suite.
- Two-kernel execution matched aggregate text and all five PNGs exactly before
  and after numeric interval ordering/observed interpretations. Final `--check`
  and independent verifier results remain pending below; Phase 2 is not DONE yet.
- The official Kaggle data-page body was unreadable. Methodology links the canonical
  reference and uses conservative recorded-field semantics; no new unverified
  currency, revenue or successful-payment claim. Existing labeler/arrival and
  single-cohort limitations remain. Historical Phase 1 label exposure cannot be undone.
- Pipeline isolation is not an OS filesystem sandbox. No actual process-level
  restriction against manually opening raw labels is claimed.
- No completion commit or push yet. Next: finish independent verification and
  privacy/diff checks, then perform only the authorized commit and push.


### Final acceptance and delivery preparation

- Full final suite: `.venv-eda/bin/python -m unittest discover -s tests -v` —
  **22 passed**, including committed regression coverage for the independent
  verifier's ambiguous-day, multiline non-training label and rejected-artifact
  immutability probes. No tests read git history or real raw outcomes.
- `.venv-eda/bin/python scripts/run_eda_notebook.py --check` — **passed**:
  two fresh kernels matched each other and the published aggregate text and five
  PNGs exactly. Notebook schema validates; required empty display metadata retained.
  Aggregate SHA-256: `bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf`.
- Independent scratch verification: baseline 14 tests and candidate 21 tests at
  review time passed; extra public-interface probes passed; three original auditor
  CLI differentials (stdout/stderr/exit/report bytes) matched the baseline.
  Subsequent change only adds the probe regression test; final suite is 22 tests.
- Independent checks verified isolation, all-field deduplication, temporal limits,
  unknown agreement and unchanged artifacts after rejected commands. Notebook five
  PNGs/denominators and installed lock versions validated; 68 active dependency
  constraints satisfied. `.venv/bin/pip --python .venv-eda check` passed. The venv
  lacks pip intentionally, so invoking that environment's `python -m pip check`
  is unavailable; the documented external-pip interpreter option was verified.
- No reproducible blockers. Official-page unreadability remains an explicit
  source-semantic limitation, not evidence of independently verified meanings.
- **Phase 2 DONE** on its analytical acceptance gate. Requested completion commit
  and push follow final staged privacy/diff review; their exact SHA and remote
  confirmation belong in the delivery report, not a self-referential commit hash.
  No PR creation or advancement to Phase 3. Next suggested task: review the EDA
  findings and authorize a small cutoff-safe feature-engineering task separately.
- Final staged publication scan passed: 19 files / 280,275 bytes before this
  evidence note; no subscriber IDs, raw records, private paths, credential markers
  or raw/processed data in the index. Five aggregate PNGs and notebook schema valid;
  staged diff whitespace check passed. A broad path-pattern scan first matched
  the runner's intentional generic rejection pattern, not a private path; the
  concrete-path/identifier scan passed. Local `git write-tree` required the same
  Git-metadata sandbox escalation as branch creation/staging; no code check failed.


## 2026-10-19 — Clean-environment reproducibility audit

- User requested current documentation, complete dependency declarations and
  commit/push of justified corrections. Baseline `b7e70b8` was already published
  on `origin/feat/kkbox-eda`; this follow-up does not advance Phase 3.
- Found missing root README, two directly used dependencies only declared
  transitively (`jupyter-client`, `matplotlib-inline`), and direct requirements
  resolving without the verified full constraints. These were reproducibility
  gaps even though the existing development environment worked.
- Added README with supported target, data-free install/tests and links to full
  reproduction/results. Updated methodology with explicit ensurepip/external-pip
  setup, private-data prerequisites, temporary disk/kernel permissions, read-only
  notebook verification and intentional output-regeneration instructions.
- Declared all seven direct packages and constrained `requirements-eda.txt` using
  `-c requirements-eda.lock`. No package versions, modeling dependencies, analysis
  code, source data, notebook or aggregate outputs changed. The full 48-package
  lock remains byte-identical to the original verified Phase 2 commit.
- Added regression checks for direct/static/runtime imports, locked-version
  alignment, constraint inclusion and README links. Observed RED (two failures,
  one missing-README error), then GREEN (three tests pass).
- Created an empty, isolated CPython 3.12.3 environment outside the checkout;
  confirmed pandas absent, then installed the full lock from PyPI. All **48 exact
  pinned packages** installed with no extras. External pip 26.2.1 used the
  documented `--python` option because system Python lacks ensurepip; the existing
  analysis environment was not reused or modified. `pip check` passed and a
  no-index dry run of the direct requirements was already fully satisfied.
- Fresh-environment full suite: **25 tests passed**. Fresh-environment notebook
  `--check`: **two clean kernels reproduced all published text and five figures**;
  aggregate SHA-256 unchanged:
  `bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf`.
- Independent verification passed in a separate scratch checkout **without raw
  or processed data**: three focused tests, 25 full tests, 48 package/version
  checks, 68 active dependency constraints, relative documentation links and
  byte-identical analysis code/notebook/outputs. No real auditors or data
  preparation were rerun; no validation/final outcome inspection occurred.
- Supported proof is **Linux x86_64 / CPython 3.12.3**. Package pins are not
  distribution-byte hashes or an offline bundle; other operating systems and
  cross-machine PNG identity remain unverified. Private input acquisition and
  local kernel socket permissions remain explicit prerequisites, not bundled
  capabilities. RDD remains globally off. Engram unavailable; no memory claim.
- Next: requested documentation/dependency correction commit and push on the
  existing feature branch; review the EDA before any separate Phase 3 approval.


## 2026-10-19 — Authorized Phase 3 implementation

- Started from clean `main` = `origin/main` = `abf493e` after `git fetch origin`;
  created `feat/kkbox-feature-engineering`. Git metadata required sandbox
  escalation; no direct main modification, reset or previous local work lost.
- Extracted the existing deterministic event/state/assignment preparation and
  history calculation to `data.py`, preserving EDA helper imports and CLI.
  Added seven-feature export with separate technical keys and train/validation
  labels; no final-label artifact, feature decisions from validation, fitted
  preprocessing, model, additional dependency or new notebook.
- `docs/features.md` records source fields, computation, cutoff safety, unknowns,
  ambiguity, exceptional records, private file schemas and future train-only
  preprocessing contract. Output directory is owner-only; raw/processed data
  remain ignored. Cache checks hashes and coverage instead of deduplicating
  transactions again. A cold build still requires original events: the existing
  EDA has no validation/final histories.
- New public-interface feature tests observed RED (five missing-CLI failures),
  then GREEN. Intermediate extraction errors (indentation and moved-local
  references) were fixed before full verification; not represented as successful
  tests. Final synthetic/structural suite at this point: **41 passed**.
- Independent data-free scratch verification: **41 passed**, exact baseline
  `abf493e`/candidate EDA stdout/stderr/exit and all four artifact bytes matched;
  explicit feature/coverage, ambiguity/missing/duplicates, cold/cached final-label
  poisoning, separate validation changes, rejected-command immutability and
  0700 output probes all passed. No reproducible implementation blockers.
- Real EDA notebook `--check` initially failed at sandbox-denied localhost
  sockets. Authorized out-of-sandbox rerun passed: two clean kernels reproduced
  text and five figures; aggregate SHA-256 remains
  `bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf`.
- RDD status is globally off, unchanged; no native review started. Optional native
  assessment refused untracked inventory before staging (not a functional test);
  named risk still requires and received independent verification.
- Real feature generation/cache rerun and full private EDA reconstruction are
  pending. Phase 3 is **not DONE** until their evidence and staged privacy checks
  are recorded. No completion commit/push yet.
- Engram is unavailable; repository task log is retained, memory mirror and
  session summary unavailable, not claimed.

### Phase 3 final acceptance evidence

- **Real build PASS:** original-source preparation exited 0 in **251.70 s**;
  reconstructed 874,581 candidates, 874,580 eligible labeled IDs, one exclusion,
  **523,998 train / 175,651 validation / 174,931 final**. No new eligibility or
  partition rule. Each matrix has exactly seven predictors, separate aligned
  technical keys, and no target/ID predictor. All training feature values and
  permitted labels match the frozen EDA internally.
- **Real cache PASS:** 7.64 s after explicit owner-only directory adjustment;
  parent reran the same CLI successfully in 8.82 s. Every output hash is identical.
  The first in-flight build had imported the pre-permission-check implementation;
  its directory was 0755, so the updated cache conservatively refused (exit 2,
  0.02 s). Tightened only that newly created private directory to **0700**;
  all artifact bytes remained unchanged. Final cold-build permission behavior
  is separately covered by synthetic tests and independent probes.
- **Real EDA compatibility PASS:** full reconstruction with shared code to an
  external temporary directory exited 0 in **232.05 s**. `cmp` matched all four
  manifest/assignment/training/quality artifacts byte for byte; preexisting EDA
  hashes also remained unchanged. Phase 1 global-label auditors were not run.
- Feature-matrix SHA-256: train
  `30a59e243fa153883a4c568c3e2904ea4b667515c64988752414466a313fbf46`,
  validation `d7923848f2e48ebd24ba4bfde04316d39887f6b22442166f4d9223aeac702407`,
  final `870a894cc53c54667fadfecdb61c77184f0432a04c484d3fa3d7f61f4a6f174a`.
  Private completion-manifest SHA-256:
  `95853404439592bcd91c64866cc3a134f76be32218cefae7be97b1b9fee87bbd`.
- **Final synthetic suite PASS: 41 tests**, including repeated inherited EDA
  compatibility cases, not 41 independent new rules. Parent independently reran
  the verifier's complete differential/invariant probe in fresh scratch: PASS.
  The first attempt to rerun its one-shot fixture script in already-used scratch
  stopped at `FileExistsError`; fresh scratch resolved this harness-state issue,
  without source changes. No functional assertion failed.
- **Reproducibility:** identical-source reruns verify byte identity; independent
  cold synthetic rebuilds and source-row/future-event invariance pass. The real
  feature matrix was cold-built once, then cache-verified repeatedly, not falsely
  claimed as two independent real cold builds. Real EDA was fully rebuilt once
  and compared against previously verified artifacts. Notebook two-kernel proof
  is recorded above and unchanged.
- **Privacy/leakage:** separate train/validation label artifacts only; no final
  labels converted, validated, hashed or exported and no final prevalence or
  metrics calculated. CSV parsing necessarily transports the second field;
  isolation is data-flow, not OS denial or a claim that raw bytes are unread.
  All private outputs are ignored; output directory is 0700. Only source,
  synthetic tests, schema/configuration and aggregate verification evidence
  belong in the completion commit. Final staged scan follows below.
- **Phase 3 DONE** on all analytical/engineering acceptance criteria. No model,
  learned imputation/scaling/encoding, Phase 4, PR, merge or deployment. Existing
  source authenticity/arrival/labeler, left-truncated history, record-based
  population and single-cohort limits remain. Counts are records, not successful
  payments; identified churn is not retention causality.
- Delivery: the requested single completion commit/push follows final staged
  checks; exact local/remote SHA is reported in the delivery response rather
  than embedded self-referentially. RDD remains globally off, unchanged.
- Final staged privacy scan passed: 12 UTF-8 text files, 142,167 bytes before
  this note; no matching frozen subscriber IDs, credential signatures, absolute
  home paths, private data paths or binary files. `git diff --cached --check`
  passed; all private feature outputs are ignored. Main/origin-main remained
  `abf493e0f1b823415d865aaff1152912b1ee5984`.
- Informative native assessment initially required staged inventory and then
  sandbox-denied temporary Git-index access. Authorized assessment rerun passed
  with risk **high**, explicitly escalated item 3 (shared EDA contract). The
  independent verifier above supplies functional proof; globally disabled RDD
  remains disabled/unmanaged, with no review transaction or fabricated receipt.
- Temporary verification copies, synthetic fixtures and duplicated private EDA
  reconstruction were removed by the parent after checks; canonical ignored
  feature outputs and prior EDA remain available. Suggested next action: human
  branch review, then separately authorize Phase 4 if accepted.

## 2026-10-20 — Phase 3 pre-merge readiness review

- Independent read-only review found no confirmed implementation blocker. Checked
  shared EDA extraction, cutoff/eligibility, final-outcome membership gating,
  key/feature alignment, cache provenance and immutable output conflicts.
- Fresh full suite: `.venv-eda/bin/python -m unittest discover -s tests -v`:
  **41 passed** (parent and independent reviewer). These are synthetic/structural
  checks, not a new real cold reconstruction.
- Real `.venv-eda/bin/python scripts/prepare_kkbox_features.py
  --verify-real-population`: **PASS**, verified existing cache and original-source
  identity; 523,998 train / 175,651 validation / 174,931 final.
- `.venv-eda/bin/python scripts/run_eda_notebook.py --check`: **PASS**, two clean
  kernels reproduced aggregate text and figures; aggregate SHA-256 unchanged:
  `bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf`.
  Initial sandbox execution could not create Jupyter sockets; the authorized
  expanded-permission execution passed.
- Corrected a stale Phase 3 authorization statement in the problem definition.
  No feature algorithm, frozen artifact, dependency or final outcome was changed.
- Developer authorized merge/push of verified Phase 3 and a new Phase 4 branch.
  Local untracked `aclaraciones.md` remains untouched and excluded from commits.
  Receipt-driven review remains globally disabled, unchanged.
- Existing retrospective/source-availability/labeler limitations remain. This
  verification does not demonstrate operational deployment or causal retention.

## 2026-10-20 — Consolidate the local Python environment

- Added root-only `/aclaraciones.md` to `.gitignore`; preserved the local notes
  unchanged and excluded them from staging.
- Replaced `requirements-eda.txt` and `requirements-eda.lock` with one
  `requirements.txt`. All **48 package/version pairs are unchanged**, including
  transitive dependencies; no ML dependency or Phase 4 behavior was introduced.
- Recreated `.venv` with **CPython 3.12.3** using the documented external-pip
  fallback. The previous `.venv` used Python 3.15 and contained no application
  packages. Did not relocate `.venv-eda`: console scripts embed interpreter paths.
  Removed both superseded environments only after successful replacement checks.
- Updated README, methodology and feature reproduction commands to `.venv` and
  the single manifest. Earlier session commands remain historical evidence.
- New manifest/navigation tests observed RED before consolidation, then GREEN.
  Fresh full suite in `.venv`: **42 passed**. External-pip dependency check:
  **no broken requirements**. Installed inventory exactly matches all 48 pins.
- Real feature-cache verification passed with unchanged population:
  **523,998 train / 175,651 validation / 174,931 final**. This was a cache/source
  integrity check, not a new cold reconstruction or final-label evaluation.
- `.venv/bin/python scripts/run_eda_notebook.py --check`: **PASS**, two clean
  kernels produced identical aggregate text and figures; aggregate SHA-256 remains
  `bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf`.
- Initial package installation lacked sandbox DNS access; expanded-permission
  installation succeeded. Notebook execution required authorized localhost sockets.
  This host lacks Python 3.12 ensurepip; use the documented external-pip commands.
- Independent verification: **PASS**, fresh scratch copy ran all **42 tests**;
  baseline pins, new manifest and installed inventory matched exactly. Confirmed
  one environment, ignored notes, current documentation and dependency health.
  No production Python or notebook bytes changed.
- Risk: item 5 (dependency manifest and environment setup). No production CLI behavior changed, so a CLI
  differential probe is not applicable; unchanged pins and real EDA outputs
  provide the relevant compatibility evidence.
- Next task remains the separately authorized Phase 4 implementation. No merge
  to main, PR, model training or Phase 5 work is part of this environment cleanup.


## 2026-10-20 — Authorized Phase 4 implementation (in progress)

- Clean fetch/ancestry verified Phase 3 reference in origin/main; main, origin/main
  and existing model branch matched `7efdd4f`. Developer explicitly authorized
  reuse of the existing branch without rewriting history. No main changes.
- Implemented purpose-separated hash rankings: equal-priority random, renewal-off
  first business rule, and a single train-only logistic pipeline with seven inputs.
  No final-label input or generic serialized-model loading is supported.
- Synthetic RED observed before modules/CLI; interim full suite: **53 passed**.
  Real training, reproducibility, EDA reproduction, independent verification and
  final privacy checks are still pending; Phase 4 is **not DONE** at this point.
- Added four pinned ML packages; original environment pins retained. Initial pip
  attempt failed sandbox DNS; authorized PyPI installation succeeded and
  dependency health passed. RDD globally off, unchanged. Engram unavailable;
  local task document retained and memory mirror/summary pending.

### Phase 4 real checks (final acceptance still pending)

- Real CLI training/scoring passed three times, including independent output
  reconstruction: 10.01s, 12.22s and 11.98s. Every one of 13 private output files
  matched byte-for-byte. All strategies cover **523,998 train / 175,651 validation
  / 174,931 final** with separate exact Phase 3 keys and complete permutations.
- Logistic Regression converged in **21/1000 iterations**, no warning. One
  candidate, no search/second model, no final-label inspection. Train AP
  **0.347491**, ROC-AUC **0.820125**, log loss **0.159503**; validation AP
  **0.335492**, ROC-AUC **0.812455**, log loss **0.160784**. Business validation
  AP **0.212767**, ROC-AUC **0.780569**. Retain logistic for valid convergence
  and useful validation discrimination; no claim of final or top-K superiority.
- Private model SHA-256:
  `93dba88b049c39c650872f49a08fe588ba27978ae5f6f0deb66cc1e012df431d`.
  Private manifest SHA-256:
  `ec29560960b8513261790d9ef2504f85967afebe943f07ae3f3db42963d25d1c`.
  Final rankings SHA-256 (all three policies, no labels):
  `e2ed3d83b4c30535aa139e6a98daa8c8993877819a0ff9a3d1e771b23d827773`.
- Real EDA `--check` passed in **24.33s** after authorized socket escalation:
  two kernels reproduced all aggregate text/figures; aggregate SHA-256 remains
  `bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf`.
  This is notebook reproduction, not a new cold raw-data reconstruction.
- Environment: **52 installed distributions / 52 exact pins**, no extras or
  broken requirements. The original 48 pins are unchanged. No generic serialized
  model ingestion or remote experiment tracking. Engram unavailable.
- Still pending: independent scratch verification, final privacy/diff checks and
  requested completion commit/push. Phase 5 and final outcomes remain untouched.

### Phase 4 final acceptance

- Independent fresh scratch verification **PASS**: candidate 53 tests, baseline
  42 tests; five prior CLI help comparisons identical; EDA/feature preparation
  stdout/stderr/status and every synthetic artifact byte identical to baseline.
  Additional semantic/provenance, train-only fitting, positive-class scoring,
  unknown/required values, alignment and rejected-output immutability probes
  passed. Validation feature/outcome changes did not change model/train/final
  predictions. Guarded access and absent synthetic raw files confirm no raw/final
  outcome dependency. These are synthetic proofs, not real final-label analysis.
- Integrated independent semantic probes into reusable regression tests, without
  hard-coded Git history or scratch paths. Model tests: **9 passed**. Parent
  independently reran real training successfully with the same manifest/model
  identity and reran the full 53-test candidate before adding those probes.
  Final full-suite and staged publication evidence follows below.
- **Phase 4 DONE** on analytical/engineering acceptance. No final outcome values,
  final prevalence, final predictive metrics or capacity curves were read or
  calculated; partitions and Phase 3 files are unchanged. All individual outputs
  and model remain private/ignored. Only aggregate train/validation diagnostics
  are published in `artifacts/model_validation.json`.
- Retain Logistic Regression; validation AP/ROC-AUC exceed the rule's diagnostic
  scores, but no final/top-K superiority, calibration, operational deployment or
  retention causality is claimed. Existing source authenticity/arrival/labeler,
  left-truncated history, single-cohort and platform limitations remain.
- Risk: item 5 (ML dependency/environment additions); item 3 (explicit import to
  distribution audit mapping). Independent verification passed. RDD remains
  globally disabled/unmanaged; no review transaction, PR, merge or Phase 5.
- Next: human branch review before any merge; only subsequently authorize Phase 5.
  Requested completion commit/push follows final tests and staged privacy checks.
  Engram is unavailable; persistent memory mirror/session summary not claimed.

- **Final suite PASS: 54 tests** in 28.395s, including committed independent
  semantic-rejection probes. `git diff --check` passed. Parent publication scan
  passed over 16 UTF-8 text files: no frozen subscriber IDs, credential markers,
  absolute home paths, raw/processed files or binaries. All 13 private outputs
  are ignored; every private output hash and frozen implementation/CLI/dependency
  hash still matches the real training manifest.
- An initial privacy wrapper completed its assertions then failed at an unused
  package import without `src` on the Python path. Corrected invocation reran
  all checks successfully; no privacy assertion or artifact check failed.
- Parent removed only the two worker-reported external scratch directories after
  retaining their verification evidence here. Canonical private model/features
  and local notes remain untouched. No completion SHA is embedded in its own
  commit; local/remote confirmation belongs in the delivery report.


## 2026-10-20 — Phase 4 extension: second candidate and pre-test freeze

- Clean local/remote model branch at `471525b` verified before writes. User
  authorized exactly HGB as the second and last candidate, then one final
  capacity evaluation only after a separate committed freeze. No main change.
- Added `selection.py`, pure `evaluate.py` and a separate CLI; original Phase4
  training/baseline/feature/data code and all original artifacts are unchanged.
  Original LR is reused after checksum/provenance and prediction verification;
  serialized bytes preserved. Re-pickling equivalent objects can change alias
  encoding, so cross-API reproducibility tests use predictions as well as exact
  same-context artifact checks. No HGB parameter search or technical retuning.
- Capacity floor and practical selection threshold fixed before results. HGB
  passed that validation-only criterion and is selected. New empirical values
  are documented in private `kkbox-selection-v1/validation.json`, not published.
- Pure metric tests observed RED missing module, then GREEN3; comparison tests
  observed RED missing functionality, then GREEN5. Independent data-free final
  candidate suite **62 passed**; baseline **54 passed**; six prior CLI help
  stdout/stderr/status identical. Rehashed ranking corruption refused.
- Three real comparison runs, including independent output reconstruction,
  produced all nine artifacts byte-identically. Both candidates use exactly
  seven features; HGB native missingness, no scaling/early stopping/external
  validation fitting. Original LR predictions match validation/final scores.
- Real two-kernel EDA reproduction passed after authorized socket escalation;
  existing aggregate hash unchanged. Parent reran real freeze relationship and
  174,931-user coverage checks. No raw/final outcomes opened at this point.
- Public `artifacts/model_freeze.json` anchors decision/configuration and private
  manifest/model/key/score/ranking/report hashes. The final evaluator must verify
  this anchor in an explicit ancestor commit AND actual artifact relationships.
- **Publication blocker:** indexed official KKBOX rules sections7–8 checked
  again; educational/research use and restricted data sharing do not establish
  clearance for new project aggregates. Keep all new real metrics/plots private.
  Existing aggregates are untouched; not treated as permission for new releases.
- Phase4 extension analytically verified; pre-test commit follows privacy scan.
  Phase5 is not executed yet. Its public completion/push remains blocked by
  unresolved publication rights. RDD remains globally disabled/unmanaged.
  Engram unavailable; local task log retained, memory mirror pending.


### Phase 5 — Single private final evaluation and publication blocker

- Freeze commit **`7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8`** was created
  at **2026-10-20 17:44:26 UTC**. Actual artifact/model/prediction/ranking/commit
  relationships passed before outcome access. Final evaluation started at
  **17:53:34.786995 UTC**, completed at **17:53:37.195000 UTC**. This is local
  Git/log evidence, not an externally trusted timestamp or an OS security boundary.
- Independent PRE-OUTCOME review **PASS**: fresh data-free suite **68 passed**;
  semantic tampering with recalculated hashes/anchor, exact source/final joins,
  opaque nonfinal-label poisoning, manual metrics and one-shot/cached behavior
  probes passed. Two simultaneous attempts caused one outcome-file read; fsync
  preceded opening. Parent focused6 passed before the real pass. No power-loss
  simulation was performed; an interrupted consumed attempt fails closed.
- The real final CLI ran exactly once, using the committed HGB and three frozen
  policies on the same **174,931** keys. Only final-key outcome values were
  interpreted/hashed; original identifiers verified; no nonfinal outcome values
  interpreted. No new training, model choice, tie or parameter changes followed.
- Private `data/processed/kkbox-evaluation-v1/`: `results.json`,
  `capacity_curve.png`, `curve_counts.npz` and completion `manifest.json`. The
  every-K arrays can reconstruct ordered outcomes and must never be published.
  New outcome counts, prevalence, capacity table and measured curves remain private.
- Parent verified all output hashes and evaluator/source identity, reproduced
  the PNG byte-for-byte from cached counts without labels, and verified cached
  CLI readback with a nonexistent raw-label path. This was NOT another evaluation.
  Model freeze/source files and original LR artifacts remain unchanged.
- Private completion-manifest SHA-256:
  `b405bd78a3ececf8cfe33a2f0dd6788c4e9c821da8d3aec7f6483025467ae8e7`.
  Sampled aggregate JSON SHA-256:
  `2ec7d9d4866dbefe709b7d1565ff25fd54219620cacdefd641e31b85d71a9243`.
  PNG SHA-256:
  `ad23622d688018ccfa669b8dac5583b0ce50526d4792a68c76945d4ea939dce0`.
- **Phase5 NOT DONE:** computation/engineering completed privately, but no
  documented right to publish these derived results is established. The
  conditional second results commit/push is not performed. Preserve B edits
  locally and A commit locally; do not present private execution as a public
  completed release. No PR/merge/Phase6/frontend. RDD remains off.
- Next: obtain documented aggregate-publication clearance; then review/export
  only approved sampled aggregates and PNG from verified cache, without
  reopening labels or changing model/policies. Engram unavailable; memory
  summary/mirror pending, not claimed. Final tests/privacy evidence follows.

- **Final checks PASS:** fresh data-free full suite **71 tests**, including
  duplicate/missing original-ID and concurrent-start regressions. A source/anchor
  and B evaluator/CLI bytes remain identical to their verified snapshots. All
  private selection/evaluation hashes, start marker and directory permissions
  passed independent postchecks. No raw labels were reopened by those checks.
- Source/dependency/EDA compatibility evidence above remains valid; no new raw
  cold reconstruction or temporal-generalization test is claimed. Publication
  scan and remote-state confirmation follow as read-only handoff checks.

- Final read-only remote confirmation: branch still at
  `471525b34afdef2783350a734c4c2cfdd8366749`; main still at
  `7efdd4fd138005c451d5be5e4840df947be1d7b7`. A freeze commit remains local.
  Nine B source/test/doc files remain intentionally uncommitted; no push was
  attempted under the failed publication condition. Final candidate privacy and
  whitespace scans passed; no new empirical aggregates in public candidate files.
- Parent removed only reported verification/rebuild/plot scratch copies after
  retaining evidence in canonical private manifests and this log. All canonical
  raw/features/original LR/selection/evaluation outputs and local notes preserved.


## 2026-10-20 — Explicit authorization to publish the current code state

- Developer requested: "comitea y pushea el estado actual en esta rama al remoto".
  This authorizes the pending evaluator/tests/documentation commit and push of
  both local work units on `feat/kkbox-model-baselines`, not publication of
  private empirical outputs or clearance of the Phase5 publication blocker.
- Prior observed full suite: **71 passed**; no production source or tests changed
  since that verification. Evaluator/CLI hashes still match the one-shot real
  evaluation manifest. Do not rerun final labels.
- Commit/push proceeds after exact staged privacy/whitespace review. Models,
  keys, scores, outcomes, new metrics/plots and every-K arrays remain ignored.
  No PR/merge/main changes. Phase5 remains blocked for empirical publication.
- Engram tools remain unavailable; this local log preserves the handoff. Exact
  new commit and remote confirmation belong in the user-facing delivery report.


## 2026-10-20 — Four-strategy descriptive extension

- User authorized implementation, completion commit and push on the current
  branch, not PR/merge/Phase6. See `odd/tasks/four-strategy-comparison.md`.
- Original LR SHA-256 `93dba88b049c39c650872f49a08fe588ba27978ae5f6f0deb66cc1e012df431d`;
  original final ranking `e2ed3d83b4c30535aa139e6a98daa8c8993877819a0ff9a3d1e771b23d827773`.
  All original model, freeze, evaluation outputs/manifests and consumed marker
  retain their exact fingerprints. Model/ranking manifest identity anchored in
  pre-test `471525b`; HGB freeze `7f21d9b`; original evaluator `ec3e58e`.
- Read-only independent preflight verified all outputs, exact same 174931 keys,
  seven features, unchanged baseline orders/scores and 9527 outcomes reconstructed
  from all three private cached arrays. Canonical outcome digest matches original.
  No original CSV opened, model loaded/fitted/scored or selection rerun.
- Separate `posthoc.py` and CLI reverify historical identities before metrics,
  recover outcomes in memory, require whole-original-results equivalence and
  add only original LR order. No changes to previous Python/CLI/dependencies.
- New JSON exports only integer-percentage budgets plus 5/10/20 tables; private
  every-K arrays used solely in memory for the unsmoothed raster visualization.
  Original image and original results stay private and untouched.
- New official rules review and owner authorization supersede the earlier local
  publication hold only for global aggregates/visualizations: no express
  aggregate prohibition identified in retrievable indexed official text, no
  express derivative license claimed. See `docs/data_attribution.md`.
- RED observed: five missing-module errors before implementation. Focused GREEN:
  six synthetic tests pass, including public-interface manual values, hash
  corruption, historical rehash rejection, no raw/training/selection/score path,
  original equality/immutability, byte-identical PNG and CLI conflict retention.
  Warnings from existing pinned matplotlib/pyparsing packages are nonfatal.
- Real extension succeeded using only verified private evidence. At 5/10/20%,
  LR captures 3876/5845/6793; HGB 3993/5968/7410; rule 2664/5327/6612.
  HGB minus LR recall: 1.23/1.29/6.48 percentage points (display-rounded).
  HGB remains selected; these results cannot reopen the validation decision.
- Pending: complete suite, independent verification, public privacy scan,
  commit/push/remote/cleanliness. Phase5 not DONE until those checks pass.
- Risk: item 2 (privacy boundary when recovering outcomes and exporting public
  aggregates). Independent verification required. RDD globally off, unchanged.
  Engram memory/mirror/session summary unavailable; local handoff retained.


### Final local acceptance and authorized delivery

- Independent corrected fresh scratch full suite: **77/77 PASS**, 63.360s,
  `.venv/bin/python -m unittest discover -s tests -v`. Earlier scratch-copy
  omission of `.gitignore` caused one setup error; corrected full rerun passed,
  not merely a selective test waiver. Parent final focused spot-check: **6/6 PASS**.
- Independent verification found no blockers: all101 budgets/five differences
  validated independently, eight original CLI help outputs/exit statuses
  equivalent, all existing Python source/scripts/tests unchanged from `ec3e58e`.
  No new dependencies, no empirical training or new dataset evaluation in tests.
- Real guarded cached export reproduced JSON/table/PNG exactly with raw CSV,
  training, scoring, selection and original evaluator entry points blocked.
  Every original LR/freeze/evaluation manifest and file, including consumed
  marker and original PNG, reverified unchanged. HGB stays selected on validation.
- Parent visually inspected the four-curve PNG and scanned all13 candidate files
  against all174931 final identifiers, private home paths and credential markers:
  PASS. Only placeholders tracked under raw/processed; all private data/model/
  ranking/cache outputs ignored. Public JSON has101 sampled budgets, not every K.
- `git diff --check`: PASS. Public deliverables: v2 JSON/table/PNG, cache-only
  module/CLI/tests, updated README/progress/roadmap/models/results and attribution.
  Original CSVs, individual evidence, models and every-K arrays remain private.
- **Phase5 DONE on verified analytical/aggregate-publication acceptance** under
  the owner's limited authorization and documented conditions review, not an
  express derivative license. Push completion/SHA and clean-tree state cannot be
  embedded in their own commit and are confirmed in the final delivery report.
  Phase4 remains DONE; Phase6 NOT STARTED. No PR, merge, force-push or data removal.
- Risk: item2 (derived-outcome/public-export privacy boundary); independent
  verification passed. RDD remained globally disabled/unmanaged. No new review
  consent/transaction started. Engram persistence unavailable, local log retained.
- Next suggested action: human review before merge, especially post-hoc framing,
  frozen evidence lineage and aggregate-only publication. Do not begin Phase6.


## 2026-10-20 — Documentation consistency and results polish

- User authorized documentation-only maintenance and commit/push directly to
  `main`, with no new branch, PR, merge or Phase 6. Initial tree clean; fetched
  `origin`; local/remote main both `6ca1f4a33dbba05ce03c8bfe4b653215d7b04e59`,
  no divergence. This also records the earlier completed fast-forward/push of
  the four-strategy comparison; historical no-merge instructions remain scoped.
- Read AGENTS, project/roadmap/progress/README and all docs. Corrected current
  three-curve/Phase 5-pending/branch-before-merge statements; distinguish three
  families from four displayed strategies. Phase 1 restricted gate unchanged;
  Phases 1–5 complete, Phases 6–8 NOT STARTED. Phase 6 remains next, not implemented.
- Moved the original evaluation protocol verbatim into
  `docs/evaluation_history.md`, explicitly archived. Preserved its then-valid
  publication hold, one-shot command and outcome-access chronology. Current
  results lead with the question, four strategies, metrics, tables, complexity
  comparison and graph; both frozen JSON snapshots retain historical metadata.
- README retains its structure/graph with a shorter entry, clear 10% result,
  four-strategy names, phase table and technical links. No fresh legal review,
  license claim or publication-policy expansion; attribution retained.
- Public-only verification: JSON syntax, all 101 sampled metric/floor/effective
  capacity rows, five pp differences and 12 table rows agree. Initial wrapper
  mistakenly included the comparison-table header in its row filter; corrected
  wrapper passed. No experimental-result discrepancy or artifact edit occurred.
- PNG inspected visually: four specified curves/colors, expected-random dashed,
  5/10/20 markers, axes/endpoints and LR post-hoc label. Existing public artifact
  SHA-256 identities are unchanged; no original/processed data was opened.
- Fresh execution of the existing suite in an isolated temporary copy containing
  tracked files and the new historical document, but no private KKBOX data:
  `.venv/bin/python -m unittest discover -s tests -v`: **77/77 PASS**, 63.404s,
  exit 0. Synthetic model fitting in existing tests is not real KKBOX training or
  a repeated experiment. No production preparation/training/selection/evaluation
  command, private dataset, ranking reconstruction or Phase 6 probe was run.
- Structural checks: **75 relative Markdown file/heading links across 19 files
  PASS**; all public JSON parses; README/public tables and original LR diagnostic
  figures agree with versioned artifacts. All 101 budgets satisfy existing metric
  formulas, floor rounding, effective capacities and all five pp differences.
  Every tracked non-Markdown byte is unchanged, including all models/results
  publication artifacts, implementation and tests; no private file was read.
- The complete archived protocol is byte-identical to the moved historical body;
  the entire pre-existing chronological progress record is preserved. Only 11
  authorized Markdown files changed. Credential/private-path scan and tracked
  private-file exclusion checks passed. `git diff --check` passed.
- All 11 external destinations resolved through the browser. Kaggle pages exposed
  their titles/URLs but no readable body: destination reachability was checked,
  not fresh legal/host-content validation. Attribution and publication policy
  remain unchanged; no express derivative-license claim is added.
- Documentation-only change: runnable RED is not applicable; structural readback,
  aggregate formula checks and the existing data-free suite provide proportional
  verification. RDD remains globally off, unchanged. Final staged review and
  authorized push follow; exact completion SHA belongs in the delivery report.
- Next: Phase 6 remains NOT STARTED and requires separate authorization. Existing
  tests do not close that future robustness phase. No unresolved result defect
  or new methodological claim was found; known cohort/causal/temporal limits stay.

## 2026-10-21 — Phase 6 frozen-cohort audit

- Authorized full Phase 6 only, new branch from latest fetched `origin/main`,
  commit/push (no merge, PR or Phase 7). Base remains
  `da86448eb03b7950b8d6a08ea71dde9a23cd3c10`. Clean initial worktree.
- Read repository instructions, project/roadmap/progress/README and relevant docs;
  read-only mapping independently inspected code, tests and private evidence.
  CodeGraph sync/explore used before structural exploration. No new dependency.
- New `robustness.py`, fixed `audit_kkbox_robustness.py`, synthetic tests,
  robustness report, classified limitations and aggregate `robustness_v1.json`.
  Existing `audit_kkbox.py` and all frozen source files remain unchanged.
- Independent mapper ran existing post-hoc identity gate: full v2 JSON and Markdown
  table reproduced exactly from private cache (no raw CSV or model access).
- Fixed before results: N-user paired unstratified bootstrap, seed 20261021,
  2,000 replicates, 1,000 prefix sensitivity, 5/10/20% capacity. Frozen total orders,
  exact floor K, integer multiplicities and partial boundary copies; replicate
  positives are denominator. 95% pointwise percentile/linear quantiles. Zero
  positive replicates excluded/counted: 0/2,000 in real run.
- Real fixed private audit executed twice; both exit 0, second create-or-compare
  reproduces all 9,155 aggregate output bytes. SHA-256
  `f1a9d643daf74774916dc28895bf41ff1f054a8138580d7911565f9fd182ddb2`.
  Runtime CPython 3.12.3, NumPy 2.5.4, scikit-learn 1.7.2 (existing pins).
- Each real audit validates three outcome inversions and original sorted-key digest,
  historical commit ancestry/manifest anchors, model/ranking hashes, same keys,
  score-to-order mapping, all split hashes/coverage and permitted label alignment.
  43 historical private/public files unchanged before/after each run.
- All 101 public budgets independently checked: population, prevalence, decimal
  floor at integer capacities, Recall/Precision/Lift, expected random and pp
  differences. All public table rows match JSON/results document. Public-only
  command exit 0. PNG visually inspected; original four curves/markers remain.
- HGB−LR paired differences at 5/10/20%: 1.23 [0.73,1.63],
  1.29 [0.89,1.72], 6.48 [5.94,7.09] pp. HGB−rule:
  13.95 [12.98,14.85], 6.73 [5.91,7.50], 8.38 [7.78,9.08] pp.
  Full LR−rule/marginal intervals in report/JSON. Maximum prefix endpoint shift:
  0.0715 pp paired, 0.0605 pp marginal. No sign change; not temporal validation.
- New descriptive final-score AP/AUC: HGB .396124/.872788,
  LR .341869/.818756, rule .219303/.788627. Brier is descriptive, not proof
  of calibration; no recalibration or probability-bin optimization. Renewal-off
  N=21,006, prevalence 30.2009% vs renewal-on 2.0679%; explains rule slope near
  12% capacity, not a causal renewal effect. 10–20% band accounts for 494 of
  HGB's 617 extra detections over LR at 20%; no interaction attribution.
- RED: new focused suite failed with missing robustness module before implementation.
  GREEN: `.venv/bin/python -m unittest discover -s tests -p test_robustness.py -v`
  7/7 PASS. Covers expanded-copy oracle, identical/perfect/imperfect ranks, ties,
  multiplicity, K=0/N, zero outcomes/replicates, seed reproducibility, alignment,
  invalid input, hand AP/AUC and public tamper refusal. Existing metric tests reused.
- Parent byte comparison against base: all 41 original non-Markdown tracked files
  identical, including Phase 4/5 JSON/PNG/code/tests. `git diff --check` PASS.
- Publication review: only global intervals/three capacity bands/global score
  diagnostics/two large renewal groups (minimum N=21,006), no small slices,
  individual labels/scores, IDs, model bytes, ranks, draws or every-K arrays.
  Not differential privacy, not express derivative licensing. No fresh legal
  clearance asserted; existing documented aggregate-only conditions apply.
- Known limits: source authenticity, arrival/release timestamps and independent
  label adjudication not verified; historical Phase 1 global diagnostics cannot
  be undone; one retrospective cohort; iid/fixed-model/fixed-tie/pointwise bootstrap.
  No observed invalidating leakage. These limitations do not support broader claims.
- Native review mode checked: OFF (global), unchanged; no native review started.
  Risk: item 6 (statistical/alignment errors may escape ordinary regression tests);
  independent verifier/full isolated suite passed (details below). Engram unavailable; local task
  log used, mirror unavailable. No source/model normalization changes required.

- Independent verification PASS for S1–S7, with S8 delivery reserved for final
  commit/push readback: 5,373 expanded-copy oracle cases, independent common-draw
  quantile reconstruction, tied AP/AUC, interval/document agreement, tamper
  refusal with unchanged files, and baseline-compatible outputs/help for four
  existing CLIs. No change-caused blockers; no correction batch needed.
- Full suite in fresh isolated temporary baseline-plus-change copy:
  `/home/fjrc94/projects/retention-lab/.venv/bin/python -m unittest discover -s tests -v`
  **84/84 PASS**, 63.915 seconds, exit 0. This includes synthetic model fitting,
  not real KKBOX retraining. No real evaluator, preparation or selection executed.
- Parent spot-check reran focused 7/7 suite and public-only audit, exit 0.
  95 relative Markdown file destinations verified. No frontend build (Phase 7
  not started), no new temporal experiment, no raw-source cold rebuild or fresh
  authenticity/legal verification. All such limits remain explicit.
- Phase 6 acceptance gate satisfied for the restricted descriptive scope;
  Phases 1–6 DONE, Phases 7–8 NOT STARTED. No unresolved invalidating blocker.
  Human review of statistical assumptions, source/temporal limits and aggregate
  publication remains appropriate before any separately authorized merge.

- Verified Phase 6 implementation committed as `7e501d1b129664c0ec46ba365de96b2735eda7f9`
  (`feat(validation): audit churn ranking robustness and limitations`). Final
  task-record update is documentation-only; authorized branch push, exact local/remote
  SHA comparison and clean-tree result are reported in the final handoff.


## 2026-10-21 — Phase 7 interactive static demo

### Scope and implementation

- Explicitly authorized Phase 7 implementation, configured GitHub SSH use,
  commits and branch publication. No PR, main merge, Netlify deployment or Phase 8.
- Clean starting worktree; SSH fetch confirmed HEAD and origin/main both
  `787534281c9d53914bb72b17b1935f385db844cc`. Created
  `feat/retention-interactive-demo` directly from that reference.
- React 19.3.1, TypeScript, Vite 8.3.5 and Recharts 3.10.1 under `web/`.
  Vitest/Testing Library for focused tests; Playwright/axe for browser checks.
  Exact installed versions are in `web/package-lock.json`. No Python dependencies changed.
- Components: App, CapacityControl, CapacityChart, StrategyComparison and
  TechnicalEvidence. Reusable metric validation/lookup/formatting functions are
  separate from JSX. Local React state only; no backend, scoring or external assets.
- Neutral off-white/forest visual system, orange selected HGB, consistent
  gray/blue/green/orange curves with distinct dash styles. Responsive stacked
  table at mobile widths, visible focus, native slider/shortcuts/details,
  chart keyboard navigation and selected numeric table alternative.
- Two original public JSON imports only; no manual metric copies or public-data
  synchronization step. All 101 records validated, exact floor K, effective
  capacity distinguished, null precision/lift at zero preserved, random counts
  explicitly fractional expectations. Full precision differences precede display rounding.
- Bootstrap interval validation and display only at 5/10/20%, both Recall and
  paired differences. Fixed-cohort/frozen-ranking and post-hoc caveats preserved;
  no test-driven model reselection, causal retention or future-performance claim.

### Verification evidence

- Initial RED: both test modules failed before implementation because App/data
  modules did not exist. Then 26/26 Vitest tests passed, including 18 malformed
  aggregate cases and exact public records at 0/5/10/20/100%. A stray nonexistent
  Vitest project filter also failed during development; it was not used as proof.
- `npm ci --ignore-scripts` (initial reproducibility check): PASS; 149 packages,
  zero vulnerabilities reported by npm at that time. Final normal ci recorded below.
- `npm run typecheck`, `npm test`, `npm run build`: PASS; production `web/dist/`
  generated. Build creates static HTML/CSS/JS and separate original aggregate chunks.
- `npm run check:build`: PASS; both decoded shipped aggregates deep-equal source;
  comparison SHA-256 matches robustness provenance; dist filename allowlist and
  focused private-data/secret-marker scan passed. Historical artifacts unchanged.
- Chromium initially could not start (`libnspr4.so` missing). Resolved without
  system installation: downloaded/extracted libnspr4, libnss3 and libasound2t64
  into temporary storage and set LD_LIBRARY_PATH for the browser process only.
- Playwright: 4/4 PASS at 1440×1100, 768×1024 and 390×844. Four actual SVG curves
  and four markers, slider keyboard Home/End/arrows, published boundary metrics,
  conditional intervals, fail-closed missing aggregate, no console/page errors,
  local asset requests only, and no horizontal overflow verified.
- axe WCAG 2 A/AA + 2.1 AA scan: zero violations on all three layouts with
  evidence disclosures open. Parent visually inspected desktop and mobile
  screenshots. Not a full assistive-technology or cross-browser certification.
- Independent isolated Python suite: **84/84 PASS**, 79.494 seconds; public-only
  robustness audit PASS. No real KKBOX training/evaluation or private audit run.
- Independent Node **24.22.0** Vite production build and check:build: PASS.
  All 43 historical artifact/source/script/test files independently byte-compared
  unchanged. No Python/CLI changes; existing CLI differential test is N/A.
- Independent review found one blocker: formula-consistent but impossible
  captured counts at full population were accepted. Reproduced with a RED test
  (23 passed / 1 failed), enforced lower bound max(0,K+P−N), then parent full
  suite **27/27 PASS**. Independent narrow recheck: **24/24 data tests PASS**;
  original impossible-count probe rejected. No unresolved review blocker.
- Parent reran the public-only audit as handoff spot check: PASS.

### Delivery and remaining boundaries

- Root `netlify.toml`: base web; npm ci && npm run build; publish dist; Node 24.
  No SPA rewrite needed (single page/hash anchors), secrets or serverless functions.
- Host Node 26.11.1; deployment Node 24.22.0 build independently verified.
- README, PROJECT, ROADMAP and frontend guide describe actual state; this entry
  appends to historical progress rather than rewriting dated phase events.
- RDD remains globally OFF; no native review started. Risk: item 5 (frontend
  dependencies and Netlify configuration); independent verifier required.
- Implementation ready for separately approved Netlify deployment. Phase 7 is not fully DONE because
  deployment remains pending; Phase 8 NOT STARTED.
- Feature units/commit identities and remote readback are recorded below after
  actual creation. No remote success is inferred from an intended command.

### Final pre-commit checks

- Normal `npm ci` (without ignore-scripts): PASS; 149 installed packages,
  150 audited, zero reported vulnerabilities at verification time.
- Final typecheck, 27/27 unit/integration tests, production build and check:build:
  PASS. Final Chromium rerun: 4/4 PASS, including all three layouts/axe checks.
- 46 relative documentation destinations exist. `git diff --cached --check`
  passed; all 27 staged paths reviewed. No raw/processed/model/node_modules/dist
  paths or private-key/token markers staged. Package and lockfile agree.
- The cohesive implementation contains approximately 1,200 authored additions/deletions plus
  the generated lockfile (2,531 lines); no artificial code/test/doc split or PR
  was introduced to meet a line heuristic. `main` remains at the original base.


### Authorized GitHub delivery

- Implementation committed as `b486e01def31557d9d39b0ae3955967ec782dd69`
  (`feat(web): add interactive retention capacity dashboard`).
- `git push -u origin feat/retention-interactive-demo`: PASS over the authorized
  existing SSH connection. `git ls-remote --heads origin` returned the exact same
  SHA for the new branch, confirming its existence on GitHub.
- Both remote main and local main remain
  `787534281c9d53914bb72b17b1935f385db844cc`. Worktree was clean after implementation
  commit/push. This follow-up documentation commit records observed delivery;
  its final HEAD/remote equality and clean-tree readback are in the final handoff.
- No force-push, merge, PR, SSH reconfiguration, Netlify deployment or Phase 8.
  Required next action is separately authorized Netlify deployment and live-site
  acceptance checks. Existing single-cohort/methodological limits remain intact.


## 2026-10-21 — Phase 7 UI/UX and scientific-copy refinement

### Scope and implementation

- Authorized evolution, not a redesign; existing branch only, commit/push via
  configured GitHub SSH. Initial clean local/remote branch both
  `8bc545e4353bf45195b89da08e3b203af103d6ab`; remote main confirmed
  `787534281c9d53914bb72b17b1935f385db844cc`. No PR, merge, force-push or deployment.
- Preserved off-white/forest palette, strategy colors/dashes, original Recharts
  plot, linear connections, 101 original points and exact capacity selection.
- Raised secondary typography from 9–12px to a coherent 12–15px scale; body
  15–16px, readable legends/axes, KPI subtitles, tables, differences and footer.
  Increased slider interaction height to 44px; preserved focus/reduced motion.
- Three metric cards explain distinct denominators using dynamic HGB examples.
  Selector explains exact K/N, floor rounding and hypothetical selection; equal
  numbers do not imply identical subscribers. No real-contact/retention/ROI claim.
- Technical Evidence now starts with four robustness facts and three data-derived
  HGB−LR interval cards on one zero-based scale. Exact matching checkpoint is
  highlighted; no intervals invented/interpolated elsewhere. All marginal Recall
  and three pairwise differences remain in expandable detail. HGB remains selected
  on validation, LR post-hoc; fixed-cohort intervals are not future guarantees.
- Tooltip distinguishes hovered and selected capacity while preserving dashboard
  selection. Main numeric table remains the accessible four-strategy alternative.
- Central `web/src/lib/links.ts`: four identical documents use main; methodology
  differs and retains a single configurable branch fallback. Existing remote main
  matched the local main reference; all five linked targets exist there or on the
  branch as appropriate. Kaggle/KKBOX attribution and publication limits retained.
- Local tracking: `odd/tasks/phase7-ux-refinement.md`. No memory service available;
  documentation is the recovery record. No dependency/configuration changes.

### Verification evidence

- New copy/selection tests observed RED before implementation; chart/evidence
  workers also observed RED then GREEN. Final command results appended below.
- `npm ci --cache /tmp/retention-npm-cache`: PASS, 149 packages installed,
  150 audited, zero reported vulnerabilities. Sandbox network initially blocked
  installation and GitHub DNS; authorized escalated commands succeeded.
- Baseline production build/browser suite: 4/4 PASS after provisioning Chromium
  and three shared-library packages in temporary storage only. Initial attempts
  failed due to missing browser/libraries and restricted local-server startup;
  these were environment failures, not successful browser proof.
- Fresh tracked-only Python scratch: 84/84 tests PASS in 67.204s; public-only
  `scripts/audit_kkbox_robustness.py` PASS. No private data, real training, final
  label reopening or fresh KKBOX evaluation. A post-test shell wrapper used a
  reserved zsh variable; its error did not alter the successful unittest result,
  and the public audit was executed separately with exit 0.
- All 43 historical artifact/Python files byte-compared unchanged against initial
  commit. Production aggregate chunks deep-equal original JSON; comparison
  provenance SHA-256 and dist allowlist/privacy scan PASS.
- Intermediate browser checks exposed two test-timing/modality mistakes: links
  read before lazy-loaded app mounted; programmatic focus after mouse clicks was
  not keyboard `:focus-visible`. Tests now await loaded UI and press an arrow
  before asserting keyboard outline. No focus style was suppressed.
- Baseline screenshots: `/tmp/retention-ux-before/`; refined default/expanded,
  evidence/chart/table and hover captures: `/tmp/retention-ux-after/`. Desktop and
  mobile captures visually inspected; final review evidence follows below.
- Native review switch remains globally OFF, unchanged. Required writer-diff
  assessment returned unassessable due to explicit untracked-file scope; no
  inference of low risk or native review/consent was made. This presentation-only
  diff changes no data contract, shared calculation, dependencies or delivery
  configuration. Risk: none.

### Remaining boundary

Phase 7 stays **IMPLEMENTED — Netlify deployment and live checks pending**.
Phases 1–6 DONE; Phase 8 NOT STARTED. Next: human visual review at the three target
widths and separate deployment authorization. No claim that the website is online.

### Final local acceptance for this refinement

- `npm run typecheck`: PASS; `npm test`: **44/44 PASS** across five modules.
- `npm run build` and `npm run check:build`: PASS. Both original aggregate chunks
  match source exactly; no new dependencies, metric points or private exports.
- Final `npm run test:browser`: **10/10 PASS** in Chromium (14.1s). All three
  1440/768/390 layouts pass axe WCAG 2/2.1 A/AA with disclosures open, no document
  overflow or clipped table width, four curves/markers, exact metrics/differences,
  zero/full capacities, quick controls, arrows/Home/End and visible keyboard focus.
  Separate hover tests at all three widths confirm exact sampled values, tooltip
  horizontal containment and unchanged selected KPIs. Reduced motion, keyboard
  disclosure and skip-navigation behavior pass. No console/page errors or
  non-local app requests in layout tests.
- Visually inspected before/after desktop and mobile full-page captures, the
  default evidence panel, the 390px chart and 768px complete table. This is not
  a screen-reader usability study or Safari/Firefox certification. A dedicated
  browser test confirms skip navigation is hidden when unfocused and visible/
  functional on Tab; screenshot focus was not cosmetically removed.
- Parent reran public-only Python audit: PASS. Focused secret-marker scan over
  candidate text files and complete historical artifact/Python byte comparison:
  PASS. `git diff --check`: PASS. No changed historical JSON or raw/private files.
- Authorized commit/push and final remote/clean-tree readback follow these checks;
  their identities are recorded in the task log/final handoff, not inferred here.
- After explicitly staging the 16 intended files, native assessment completed:
  **medium**, `review_due=false`, `under_budget`; no named high-risk item applies.
  RDD is still globally OFF, so no review lifecycle or consent was invoked.
  Staged paths/stat and whitespace were reviewed; only UI, tests and docs included.

### Authorized refinement publication

- Implementation commit: `091430a084caae03d07974dc35463d2477a10e9e`
  (`feat(web): refine dashboard UX and technical evidence`). Authorized normal
  branch push succeeded; `git ls-remote` returned that exact SHA. Worktree clean
  after implementation delivery. Remote main remains
  `787534281c9d53914bb72b17b1935f385db844cc`.
- This documentation-only follow-up records completed tasks and observed push;
  its own final remote SHA/worktree readback belongs in the final handoff.
  No PR, merge, force-push, Netlify deployment, Phase 8 or historical JSON change.
