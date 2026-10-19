# KKBOX feasibility: minimal local audit

**Status: local audit verified; Phase 1 is not approved.**
Both target CSVs are now available locally and passed two audit runs. Official
provenance, terms and temporal label semantics remain unverified.

## Acquisition and provenance

Official source: [Kaggle competition data](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/data).
On 2026-10-19, the unauthenticated browser returned no readable catalog content.
Official filenames, archive sizes, terms and redistribution rights remain unverified.
No credentials were accessed and no agreements were accepted.

The developer must review the rules and supply the official catalog (names and
sizes) before downloading only the confirmed targets. Expected targets are
`train_v2.csv` and `transactions_v2.csv`; these are provisional, not verified
availability claims. Extract original CSVs into ignored `data/raw/`. Do not
acquire activity, profiles or the full dataset. A missing target blocks the audit;
there is no fallback to another cohort/file. Preserve catalog evidence and source
archive names/sizes separately: CSV byte sizes are not archive download sizes.

## Reproduce locally

After confirming the catalog and completing manual acquisition:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/audit_kkbox.py --raw-dir data/raw --report data/audit/kkbox.json
sha256sum data/raw/train_v2.csv data/raw/transactions_v2.csv data/audit/kkbox.json
python3 scripts/audit_kkbox.py --raw-dir data/raw --report data/audit/kkbox.json
sha256sum data/raw/train_v2.csv data/raw/transactions_v2.csv data/audit/kkbox.json
```

Both hash listings must match. Real two-run verification passed on 2026-10-19; synthetic
repeatability alone is not empirical dataset evidence. Reports remain local and ignored.
Do not publish records or subscriber identifiers.

## Audit contract

The standalone standard-library script reads CSVs sequentially with bounded
memory. It hashes each source before and after inspection, reports byte sizes,
SHA-256, fixed configuration, row counts, per-column missingness, binary label
counts, and valid min/max dates with invalid-date counts. Source records and
identifiers are never included in output or errors.

Expected schemas are strict, including order, and provisional until checked
against the catalog and actual files:

- `train_v2.csv`: `msno,is_churn`.
- `transactions_v2.csv`: `msno,payment_method_id,payment_plan_days,plan_list_price,actual_amount_paid,is_auto_renew,transaction_date,membership_expire_date,is_cancel`.

Labels must be literal `0` or `1`; dates must be real calendar dates in strict
ASCII `YYYYMMDD` format. Empty fields are counted as missing. Empty datasets,
missing values, invalid labels or dates produce an aggregate invalid report and
exit 1. Missing files, schema/row-width errors, malformed CSV and differing
existing reports exit 2 without replacing an existing report. Exit 0 means only
that these narrow structural checks passed, not that the data are scientifically
usable. Non-date transaction fields are not type-validated in this increment.

Identical inputs and configuration yield identical JSON without timestamps or
absolute paths. Existing report bytes must match exactly; changed inputs require
a new report path, never automatic overwriting or appending. Hash checks detect
ordinary concurrent changes, not adversarial modifications; keep sources stable
during execution. Runtime requires multiple sequential source passes, trading
extra I/O for bounded memory and integrity checks.

## Temporal meaning and limits

| Concept | Evidence needed | Current status |
|---|---|---|
| Transaction date | Event time and when the record became available | Range measurable; availability unverified |
| Membership expiry | Contractual subscription end, not necessarily churn | Semantics unverified |
| Churn window | Official renewal grace period and exceptions after expiry | Unverified; do not assume 30 days |
| Label availability | End of outcome observation plus publication/processing delay | Not inferable from CSV date extrema |

For example, if an expiry is February 28 and an eventual verified outcome
window is 30 days, a March 1 prediction cannot already know that outcome.
This is an illustration, not a verified KKBOX labeling rule. Even the latest
observed transaction date cannot prove complete follow-up or mature labels.

Historical eligibility, cancellations/renewals, duplicate subscribers, cohort
overlap, full historical coverage, permitted redistribution and an operational
backtest remain unresolved. No cohort comparison or evaluation protocol is
approved. No models, feature package, frontend or deployment are included.

## Observed verification

On 2026-10-19, seven synthetic CLI tests passed: schema rejection, invalid labels
and dates, identical rerun/source preservation, content-change refusal, missing
file, malformed row and source/report collision. The initial RED run failed
because the script did not yet exist; after implementation all seven passed.
The default real invocation exited 2 because the target files are absent.

## Local evidence — 2026-10-19

| File | Bytes | Rows |
|---|---:|---:|
| `train_v2.csv` | 45,635,134 | 970,960 |
| `transactions_v2.csv` | 115,394,513 | 1,431,009 |

Observed schemas match the script configuration. No missing fields, invalid
binary labels or invalid calendar dates were found by the implemented checks.
Labels: 883,630 zeros and 87,330 ones. Transaction dates span 2015-01-01 to
2017-03-31; expiry dates span 2016-04-19 to 2036-10-15. The 2036 expiry is
calendar-valid but needs semantic investigation; it does not prove follow-up
through 2036 or label maturity.

Both real runs exited 0. Source hashes matched before, between and after runs;
the report hash matched between and after runs:

- Train: `1f7590a3467174f5a147db3fb85dd1393074b6c13da0fd6e70af31bf37dee5cc`.
- Transactions: `1d3015e32ed1661e9cfe813a9779b1b33e9d1d0829f1203633440045d4c6ea36`.
- Report: `d1d3787e9dc35210f329bd451bcd08ceeebdcc00d5fe28b86291ff3c942d0711`.

The earlier absent-file result above is historical. `git check-ignore -v`
confirmed both CSVs are excluded by `data/raw/**`; neither is tracked.

**Next step:** verify official provenance/conditions and investigate date and
label semantics before proposing eligibility or approving a backtest.
