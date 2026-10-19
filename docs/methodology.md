# Training-only KKBOX exploratory analysis

Phase 2 uses original-source records available by January 31, 2017 and supplied
February outcomes in an explicitly retrospective, single-cohort benchmark.
No operational campaign simulation, causal retention claim or model is implied.

## Reproduce

Use Python **3.12.3**. The existing unrelated `.venv` is not reused: it runs Python
3.15. The dedicated ignored `.venv-eda` contains verified pandas 2.2.3,
matplotlib 3.9.4, nbformat 5.10.4, nbclient 0.10.2 and ipykernel 6.29.5.
`requirements-eda.lock` pins the full observed environment, including transitive
packages; `requirements-eda.txt` records the five direct dependencies. No
modeling library is installed. Install only from an authorized package source.

```sh
python3.12 -m venv .venv-eda
.venv-eda/bin/python -m pip install -r requirements-eda.lock
.venv-eda/bin/python scripts/prepare_kkbox_eda.py --verify-real-population
.venv-eda/bin/python scripts/prepare_kkbox_eda.py --verify-real-population
.venv-eda/bin/python -m unittest discover -s tests -v
.venv-eda/bin/python scripts/run_eda_notebook.py
.venv-eda/bin/python scripts/run_eda_notebook.py --check
```

On a Python installation without `ensurepip`, create the environment with
`--without-pip`, then use an already installed pip's `--python .venv-eda`
option to install the lock. Do not overwrite an existing unrelated environment.
The notebook runner creates its kernel specification and matplotlib/IPython
caches in system temporary storage, executes two fresh kernels, compares
aggregate text and image bytes and removes its temporary directory. The
`--check` mode additionally compares both executions to published outputs.
Failure to start a kernel is missing proof, not a successful EDA run.

## Freeze first, extract labels second

1. Read identifiers from `train.csv` without interpreting outcome values.
2. Stream `transactions.csv`; accept only `transaction_date <= 20170131`.
   Dates and flags are validated. Missing optional numeric fields stay unknown.
3. Deduplicate **all nine CSV fields exactly** in temporary SQLite; retain copy
   counts separately. Multiple distinct rows for a subscriber/day are not duplicates.
4. On the latest observed day require agreement in recorded expiry, cancellation
   and auto-renew. Retain expiry February 1–28 and `is_cancel=0`.
5. Intersect with supplied label identifiers. Require **874,581 candidates**,
   **874,580 labeled identifiers**, and therefore **one excluded unlabeled candidate**
   when `--verify-real-population` is supplied.
6. Hash UTF-8 `retention-lab-feb2017-v1|` + identifier with SHA-256, convert the
   complete digest to an integer and take modulo 10. Buckets 0–5: train; 6–7:
   validation; 8–9: final. The primary key ensures one assignment per eligible ID;
   the total and distinct count must match. No sampled or seed-based replacement.
7. Persist and byte-verify private assignments and manifest **before** interpreting
   training labels. Only then reread `train.csv`, interpreting a value only if its
   identifier belongs to training. No labeled validation/final table is written.

Private files reside under ignored `data/processed/kkbox-eda-v1/`:
`assignments.csv`, `manifest.json`, `training.csv`, `quality.json`. The manifest
stores configuration, transaction byte fingerprint, a sorted-identifier fingerprint
for the label source, population counts and the assignment fingerprint. The
label-source fingerprint deliberately excludes outcome bytes: changing a
non-training label must not alter preparation. `quality.json` separately binds
the exact training artifact, including its extracted labels. No claim is made
that this is a whole-file fingerprint of `train.csv`.

A repeat run compares existing artifacts and refuses differences without replacing
them. Source-order changes preserve assignments/training but change the transaction
byte fingerprint, so rerunning into the same frozen manifest refuses them.
Post-cutoff events do not affect assignments/training; changed source bytes still
invalidate the source fingerprint. Use a separate private output directory to
investigate intentional source revisions, never silently overwrite frozen evidence.
An interruption may leave only a verified manifest/assignment pair; rerun the same
sources to finish extraction. Those files alone are not proof of a completed EDA.

## Isolation boundary and analytical fields

The notebook loads only `training.csv` and its integrity metadata, drops identifiers
immediately and exposes no partition selector or original-label input. This is
pipeline/data-flow isolation, **not OS-enforced filesystem denial**. Kernels retain
the invoking user's filesystem privileges. Phase 1 global audits are historical
exposure that cannot be undone; they are not inputs to this EDA and are not rerun.

Training history covers all original-source pre-cutoff events for selected training
users. The first observed transaction defines **observed history**, not actual tenure.
Counts represent distinct records, not successful payments. Each additional latest
field requires independent agreement across all rows of the selected latest day;
otherwise it is unknown. We do not fall back to a convenient earlier date.

| Field | Conservative use and limitation |
|---|---|
| `msno` | Private subscriber key; never published |
| `transaction_date`, `membership_expire_date` | Recorded calendar dates, not verified arrival timestamps or adjudicated events |
| `is_auto_renew` | Recorded binary renewal configuration; operational meaning and intervention effects are not independently established |
| `is_cancel` | Recorded cancellation flag; not equivalent to churn |
| `payment_plan_days` | Recorded plan duration; not remaining days or actual usage |
| `plan_list_price`, `actual_amount_paid` | Recorded amounts; not verified realized revenue, net value or payment success |
| `payment_method_id` | Categorical recorded code; no invented channel descriptions |
| `is_churn` | Supplied original February outcome; official 30-day concept accepted, labeler not independently replayed |

The canonical field-description reference is the
[official KKBOX data page](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data).
During this run its dataset-description body was not readable through the browser;
field-level business semantics cannot be certified from that retrieval. We therefore
use conservative recorded-field descriptions and do not add unverified units or
payment interpretations. Existing official-host cohort/target evidence and its
limits are recorded in [the problem definition](problem_definition.md).

## Charts, quality and hypotheses

All prevalence, missingness, frequencies, distributions and churn tables use
**training only**. Every chart publishes group denominators and churner counts;
unknown values remain explicit. Numeric groups use training-only marginal quartiles
with repeated boundaries removed, never churn-optimized thresholds. Constant fields
become a single group. Missing raw optional numeric values and same-day disagreements
are not imputed. Entire malformed inputs fail closed, without private diagnostics.

The five questions compare churn against recorded renewal state, observed-history
length, distinct January transaction count, agreed latest plan duration and agreed
latest amount. Aggregate distributions include list-price and payment-method counts;
quality totals include exact duplicate copies, ambiguous daily renewal states,
missing numeric fields, expiry before event, and recorded expiry after February 1,
2018. The latter is only an explicit descriptive exception threshold, not a rule to
remove valid future expiries. A future expiry recorded by the cutoff is permitted.

Exploratory hypotheses (not causal or confirmatory tests):
1. Recorded auto-renew off is associated with greater churn.
2. Shorter observed history is associated with greater churn.
3. An observed unambiguous on-to-off transition is associated with greater churn
   than every observed day being unambiguously on.

For hypothesis 3, consecutive **observed** days need not be adjacent calendar days;
an ambiguous day breaks the chain. The transition group can include later switches
back on. Other histories remain a separate group. This compares selected histories,
not the effect of changing renewal configuration. No significance or generalization
claim is made from these descriptive training comparisons.

**Candidate rule, documented only:** prioritize auto-renew off, then ascending split
SHA-256 digest, then identifier. No ranking implementation, capacity metric, threshold
tuning or validation/final outcome inspection occurs in this phase.

## Publication and next step

Only aggregate `artifacts/eda_summary.json`, notebook text and five figures may be
published. Raw files, private assignments and subscriber-level training records stay
ignored. The runner rejects source identifiers, private absolute paths and error
outputs and strips volatile cell metadata. Two clean kernels must produce identical
aggregate outputs and figures. The independent check covers holdout isolation and
dependency configuration; source-level tests are synthetic, not global real audits.

Results and exact verification evidence are recorded in `PROGRESS.md`. No Phase 3
feature-engineering, model, three-strategy curves, frontend, PR or deployment is
authorized by this phase. Review the aggregate findings and limitations before any
separate authorization to advance.
