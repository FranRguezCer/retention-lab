# Training-only KKBOX exploratory analysis

Phase 2 uses original-source records available by January 31, 2017 and supplied
February outcomes in an explicitly retrospective, single-cohort benchmark.
No operational campaign simulation, causal retention claim or model is implied.

> **Historical Phase 2 procedure.** Phases 1–5 are now DONE; the current
> [four-strategy results](results.md) preserve the original final evaluation and
> identify LR as a post-hoc addition. Phase 6 is documented in [the robustness audit](robustness.md). Data preparation
> and notebook commands below describe earlier reproduction, not maintenance
> steps to rerun on the consumed experiment.

## Reproduce

Run every command from the repository root. The verified target is **CPython
3.12.3 / Linux x86_64**; do not assume Windows/macOS or another Python version is
covered by this lock. Python must include SQLite and virtual-environment support.
Use one ignored `.venv` environment for this project. Do not overwrite an
environment used by another project. The repository is not a pip-installable package:
its scripts explicitly add `src/` to the import path.

### Install and test without private data

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v
```

All tests use synthetic fixtures or committed aggregate notebook content; no raw
KKBOX data is required. The original Phase 2 subset used pandas 2.2.3,
matplotlib 3.9.4, matplotlib-inline 0.2.2, nbformat 5.10.4, nbclient 0.10.2,
ipykernel 6.29.5 and jupyter-client 8.10.0. The last two launch and manage local
kernels; matplotlib-inline supplies the explicitly selected figure backend.
Phase 2 itself does not fit a model or require an interactive Jupyter server.
The current manifest also includes NumPy, scikit-learn, joblib and threadpoolctl
as direct dependencies, plus explicitly pinned SciPy; it serves the completed
ML phases as well. The manifest, not the historical Phase 2 subset, is the
authoritative environment definition.

`requirements.txt` is the only dependency manifest. It pins the complete
environment, including direct and transitive packages, and lists the direct
dependencies in its header. It uses version pins, not distribution-file hashes:
it is not a hermetic/offline bundle or a cross-platform guarantee. Installing
requires an available authorized package index and compatible distributions.
The test suite checks imported packages against exact pins and verifies that
the manifest is self-contained; changing dependencies requires a fresh installation, `pip check`,
tests and notebook reconstruction, not just editing the direct pins.

### Python without ensurepip

If `python3.12 -m venv` cannot bootstrap pip, use an **already available pip
22.3 or newer** via its explicit target-interpreter option, as documented by
[pip](https://pip.pypa.io/en/stable/topics/python-option/):

```sh
python3.12 -m venv --without-pip .venv
python3 -m pip --python .venv install -r requirements.txt
python3 -m pip --python .venv check
.venv/bin/python -m unittest discover -s tests -v
```

Here `python3 -m pip` is the installer already available on the host, not a
requirement that it use the analysis interpreter. The `--python` argument selects
the analysis environment. If neither ensurepip nor a recent external pip is
available, install your operating system's Python 3.12 venv/pip support first;
do not install dependencies into system Python.
The analysis environment intentionally lacks pip under this fallback, so its
`python -m pip check` is unavailable: use the external-pip command above.

### Prepare and execute

Prerequisites beyond the environment:
- Legally acquired **original** `data/raw/transactions.csv` and `data/raw/train.csv`.
  Acquire them through the [official competition](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data)
  under its access/rules; no download credential or data is included here.
- Writable `data/processed/` and system temporary storage, with several GB free
  for exact SQLite deduplication. Observed preparation time: about four minutes
  per run on the development machine, not a performance guarantee.
- Permission to start local Jupyter kernels and open their localhost sockets.
  A sandbox denying sockets cannot provide notebook-execution proof.

```sh
.venv/bin/python scripts/prepare_kkbox_eda.py --verify-real-population
.venv/bin/python scripts/prepare_kkbox_eda.py --verify-real-population
.venv/bin/python scripts/run_eda_notebook.py --check
```

Do not run the real Phase 1 auditors for this workflow: they inspect global label
values. Expected preparation counts are 874,581 candidates and 874,580 assigned
users: 523,998 training, 175,651 validation, 174,931 final; one unlabeled candidate
is excluded. Source byte identity is recorded in the private manifest. The
fingerprint/conflict rules below intentionally refuse incompatible existing
artifacts; do not delete or overwrite evidence to make a rerun pass.

The notebook runner uses the invoking interpreter, creates its own temporary kernel
specification and matplotlib/IPython caches, executes two fresh kernels and removes
temporary state. `--check` is read-only for published artifacts and compares both
runs to the committed notebook and `artifacts/eda_summary.json`. To intentionally
regenerate outputs after an authorized analysis change, run the command **without**
`--check`, review its notebook/JSON diff and rerun `--check` before publishing.

Same-machine clean executions must have identical aggregate text and figure
bytes. Cross-machine PNG bytes may differ with fonts/rendering/system libraries
that this Python package lock does not capture; compare aggregate results and
investigate rendering differences rather than silently replacing accepted outputs.
A failed install, kernel start or output comparison is missing proof, not success.

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

**Historical Phase 2 candidate rule, documented only at that stage:** prioritize auto-renew off, then ascending split
SHA-256 digest, then identifier. No ranking implementation, capacity metric, threshold
tuning or validation/final outcome inspection occurs in this phase.

The implemented Phase 4 rankings subsequently used purpose-specific hash ties,
not the split digest; see the [frozen policy families](models.md#three-fixed-policy-families).

## Phase 2 publication and next-step boundary — historical

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

## Subsequent authorized Phase 3

The Phase 2 next-step boundary above is historical. Phase 3 was separately
authorized and reuses the same deterministic preparation and frozen population.
See [feature schema and reproduction](features.md) for the seven predictors,
separate keys/labels, conservative missingness, cached source-bound regeneration
and train-only preprocessing contract. Phase 3 itself fits no model. The
subsequently authorized [Phase 4 model pipeline](models.md) implements that
contract with training/validation diagnostics and label-free final rankings.
No cross-cohort/operational claim or final-outcome evaluation is introduced.

## Current completed comparison

Phases 3–5 were separately authorized and completed after the Phase 2 record.
Both LR and HGB use the seven approved features; HGB was selected on validation
and frozen before the original final evaluation. LR's original ranking was
subsequently added through descriptive post-hoc reuse, not a new confirmation
or model selection. See [current results](results.md),
[archived original evaluation](evaluation_history.md) and
[publication boundary](data_attribution.md). Final-label access is consumed;
no current reproduction instruction authorizes retraining, reselection or a
new final-label read. The subsequent Phase 6 audit is documented in [robustness](robustness.md);
Phase 7 remains NOT STARTED.
