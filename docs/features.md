# Reproduce the February 2017 feature tables

Phase 3 produces **seven deterministic predictors**, not a fitted preprocessing
pipeline or a model. The approved experiment remains a single-cohort,
**RESTRICTED GO retrospective benchmark**, not historical deployment or
cross-month temporal generalization. Event dates are proxies for availability;
arrival times and label adjudication remain unverified.

## Run

Use the existing [locked Phase 2 environment](methodology.md#reproduce) and legally
acquired original `transactions.csv` and `train.csv`. No new dependencies,
`members`, `user_logs`, v2 releases or notebook are needed.

```sh
.venv-eda/bin/python -m unittest discover -s tests -v
.venv-eda/bin/python scripts/prepare_kkbox_features.py --verify-real-population
.venv-eda/bin/python scripts/prepare_kkbox_features.py --verify-real-population
.venv-eda/bin/python scripts/run_eda_notebook.py --check
```

Prerequisite: verified private `data/processed/kkbox-eda-v1/` artifacts from
[Phase 2 preparation](methodology.md#prepare-and-execute). The default output is
ignored `data/processed/kkbox-features-v1/`; `--raw-dir`, `--eda-dir` and
`--output-dir` select alternate nonoverlapping directories. Outputs must remain
private: the process creates the feature directory owner-only (0700) and refuses
an existing directory accessible to other users. Files inherit local umask, but
cannot be traversed through this directory by other users. This is not protection
against the owner, privileged processes, backups or a malicious local program.

The first build needs several GB temporary SQLite disk and a full original-source
pass (roughly four minutes for Phase 2 on this machine; not a guarantee). Existing
EDA tables contain no validation/final histories, so they cannot replace that
pass. `data.py` now owns the exact same schema/date validation, nine-field textual
deduplication, independent daily field agreement, latest state, eligibility,
SHA-256 assignment and history/transition calculation used by both commands.

Later runs validate source/configuration, EDA and all output byte fingerprints,
re-extract only permitted labels, check keys/coverage/training parity, and reuse
the verified feature cache. They still read transaction bytes for SHA-256 but do
not parse/deduplicate 21 million events. For an independent cold reconstruction,
use a **new private** output directory and compare table hashes; never remove
frozen evidence to make a changed source pass. After an algorithm/schema change,
bump the feature manifest version and use a new output identity.

## Files and model input contract

| Private file | Schema and use |
|---|---|
| `{train,validation,final}_features.csv` | Exactly the seven columns below, one row per eligible subscriber; no ID, partition, digest or target |
| `{train,validation,final}_keys.csv` | Only `msno`, sorted ascending; row i identifies row i of the corresponding feature table |
| `train_labels.csv` | `msno,is_churn`, same sorted training keys; permitted for development |
| `validation_labels.csv` | `msno,is_churn`, separate controlled artifact; prepare only in Phase 3, do not analyze or use for feature decisions |
| `manifest.json` | Version, ordered predictor whitelist, cutoff, frozen EDA fingerprints, population and every output file hash/byte size; no outcome statistics |

There is **no final-label artifact**. Row alignment is explicit, not a relational
join through the predictor matrix: retain keys separately, verify their order
and hashes, and join labels only by the corresponding keys when later authorized.
Never send `msno`, hash, bucket, partition or `is_churn` to an estimator. CSVs can
be read by existing pandas and later passed to scikit-learn after train-only
preprocessing; this phase does not install or train scikit-learn.

Population is exactly the frozen labeled eligible cohort: **874,580**, with
**523,998 train**, **175,651 validation**, **174,931 final**. One of 874,581
transaction-defined candidates has no supplied label and remains excluded.
Buckets remain SHA-256 of UTF-8 `retention-lab-feb2017-v1|` + `msno`, entire digest
integer modulo ten: 0–5 / 6–7 / 8–9. No new split or eligibility rule is introduced.

## Predictor provenance

Every row uses only **original events with `transaction_date <= 20170131`**.
History begins at the first observed event, not account creation. January means
2017-01-01 through 2017-01-31 inclusive. Counts follow exact nine-field
textual deduplication, not successful payments or independently verified events.

| Predictor | Definition / source columns | Possible value for ranking; risk |
|---|---|---|
| `auto_renew` | Agreed `is_auto_renew` on latest observed day | Recorded renewal configuration; not guaranteed future renewal or an intervention effect |
| `observed_history_days` | Calendar days: cutoff minus minimum `transaction_date` | Observed relationship length; left truncation means this is not true tenure |
| `january_transactions` | Number of distinct records dated in January | Recent recorded activity, not listening or successful payments |
| `distinct_transactions` | Number of distinct records across observed history | Historical frequency proxy; exposure-dependent count, not an exposure-normalized rate |
| `latest_plan_days` | Independently agreed `payment_plan_days` on latest observed day | Plan-duration signal; not remaining entitlement or actual use |
| `latest_amount` | Independently agreed `actual_amount_paid` on latest observed day | Recorded payment signal; no verified currency, realized revenue or successful-payment semantics |
| `auto_on_to_off` | Count of `is_auto_renew` transitions 1→0 across consecutive observed daily states | Renewal instability signal; an ambiguous day breaks the chain; no inferred transition across it |

The first five signals and renewal transitions were justified in the
[training-only EDA](methodology.md#charts-quality-and-hypotheses). Historical count
adds a simple frequency proxy without many windows or ratios. No validation or
final outcomes informed this fixed list. No claim of incremental predictive
value exists before Phase 4. Redundant `always_auto_on`, list price, payment
method and quality diagnostics remain outside the predictor whitelist.

## Missingness, types and exceptional records

- `auto_renew` is a required categorical binary code (CSV `0`/`1`), not a continuous
  magnitude. Eligibility already excludes ambiguous latest renewal states.
- Other columns are integer-valued recorded numerics/counts/days. Latest plan and
  amount may be empty (unknown); pandas can read these as nullable `Int64` or
  float/NaN. Never turn unknown into zero. Counts/history/transition values are
  defined for every eligible user, including history zero for a first cutoff-day
  event and zero transitions when none is observed.
- Latest-day field values require independent textual agreement across all
  distinct rows. A missing value or disagreement yields unknown for that field;
  no arbitrary last row, earlier-day fallback or mean. Missing versus recorded
  zero remains distinct. An ambiguous historical renewal day breaks a transition
  chain, but does not remove otherwise eligible history.
- Optional numeric source cells accept empty or `int()`-parseable values. Signed
  or unusual but parseable recorded amounts/durations are retained, not silently
  repaired/clipped or used to redefine eligibility. No unverified business-range
  constraints are invented. Nonnumeric values fail closed. Textual `01` and `1`
  remain distinct during deduplication/agreement, preserving Phase 2 behavior.
- Dates must be real ASCII `YYYYMMDD`; malformed dates/flags, schemas, row widths
  or duplicate label IDs fail closed with generic, non-identifying CLI errors.
  A recorded expiry before its event or a distant valid expiry is not repaired.
  Future expiry recorded by cutoff is not a future transaction; only February
  expiry on the unambiguous latest state is eligible under the existing contract.
- Exact duplicate copies do not increase counts or transitions. Indistinguishable
  genuine events may be collapsed: there is no reliable event ID to resolve this.

**Phase 4 contract (not executed):** fit statistical imputation, scaling and
categorical encoding on training only within the eventual pipeline. Choose any
missing indicators/encoding behavior using development data only. Apply frozen
training parameters to validation and, after selection, final features. Never
fit on concatenated train/validation or final features. No imputer, quantile,
scaler or vocabulary is learned in Phase 3.

## Leakage, integrity and reproducibility

1. Freeze and verify Phase 2 identifiers/partitions first. Require exact rebuilt
   manifest/assignment identity for a cold feature build, not merely equal counts.
2. Transport `train.csv` rows through CSV parsing, but test partition membership
   **before evaluating** an outcome. Only train/validation values are validated
   or exported. Final values are not converted, validated, hashed or summarized.
   Parsing necessarily transports the second field: this is data-flow isolation,
   not a claim that raw bytes were never read from disk or OS access is denied.
3. Label-source provenance hashes sorted identifiers only, never whole label-file
   bytes. Final-label poisoning with quoted/multiline nonlabels must leave all
   feature artifacts and manifests identical. Validation-label changes can only
   change its separate label artifact and its integrity hash, not features.
4. Check exact partition keys, uniqueness, coverage, feature schema/counts and
   equality of every training feature/label with frozen EDA. Do not calculate
   final prevalence, metrics, distributions or label summaries.
5. Preserve artifacts create-or-compare. Preflight every existing output conflict
   before publishing; manifest is written last as the completion marker. A crash
   between complete file writes can leave a subset; same-source rerun completes
   and verifies that subset. A truncated file is refused, not repaired: retain
   the failed evidence and use a new private output directory. This is not an
   atomic multi-file transaction or concurrent-writer service.
6. Identical sources/configuration produce identical table bytes. Reordering
   source rows or appending future events leaves feature values unchanged, but
   intentionally changes transaction-source byte identity: use a new frozen EDA
   directory to investigate it. Do not confuse value invariance with provenance.

Synthetic tests exercise these invariants through the CLI, including malformed
inputs, immutable rejection and EDA equivalence. Real checks and timings are
recorded in [progress](../PROGRESS.md); historical Phase 1 global-label exposure
cannot be undone and those auditors are not rerun. Private data/IDs, intermediate
SQLite and per-user outputs are never publication artifacts. This document is
schema/configuration only; no new individual data or outcome analysis is public.

## Review before merge

Review shared-state extraction first, then outcome gating, key/row alignment and
manifest/cache validation. Reproduce tests and private counts, verify EDA parity,
and confirm no data files are staged. Defend these distinctions in interviews:
**event time vs arrival time**, **observed history vs tenure**, **ambiguous vs
missing vs zero**, **deterministic features vs learned preprocessing**, and
**retrospective held-out detection vs deployable or causal retention claims**.
Do not begin Phase 4 without separate authorization.
