# Reproduce Phase 4 rankings

**Phase 4 DONE:** Logistic Regression (LR) and HistGradientBoostingClassifier
(HGB) both used the same seven approved features, with fitting restricted to
training data. HGB was selected exclusively on validation by the predeclared
Recall@10% rule and frozen before final-label access. It remains the selected
model. The original final evaluation compared Random, Business Rule and HGB;
LR was added later from its original ranking as a descriptive post-hoc
comparison, with no retraining or final-based reselection.

See [current results](results.md) and [publication boundary](data_attribution.md).
The original [LR diagnostic JSON](../artifacts/model_validation.json) and
[HGB freeze JSON](../artifacts/model_freeze.json) are immutable historical
snapshots, not current status reports. Their earlier selection/publication and
unopened-test statements must be read at their respective points in time.

## Original LR iteration — historical implementation record

The following documents the first Phase 4 increment, before the HGB extension
and Phase 5. Its train-only fitting and label isolation guarantees remain
relevant; its then-current authorization boundaries are historical. The
approved benchmark remains retrospective, not deployment or causal retention.

## Run — archived reproduction commands

These commands retrain and were used during the original implementation. They
are not steps to rerun on the current consumed experiment. Use published
results for reading and synthetic tests for code checks.

Install the single pinned `requirements.txt` in `.venv` as described in the
[environment guide](methodology.md#reproduce), then use the already verified
[Phase 3 feature artifacts](features.md). Training accepts no raw data path and
never invokes the global-label auditors or feature preparation.

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/train_kkbox.py --verify-real-population
.venv/bin/python scripts/train_kkbox.py --verify-real-population
.venv/bin/python scripts/run_eda_notebook.py --check
```

`--feature-dir`, `--eda-dir` and `--output-dir` support alternate nonoverlapping
private directories. Default output: ignored `data/processed/kkbox-models-v1/`.
`--seed` defaults to 42; `--max-iter` defaults to 1000. Changed source bytes,
configuration, environment or model outputs require a **new output directory**;
existing evidence is create-or-compare, never silently replaced. An identical
rerun retrains; it does not just trust a cached serialized model. No external
model loading is supported: never deserialize an untrusted joblib/pickle file.

## Three fixed policy families

| Policy | Priority | Ties |
|---|---|---|
| Random | Everyone has score 0 | Purpose-specific SHA-256 of seed and ID |
| Business | `auto_renew=0` scores 1; `auto_renew=1` scores 0 | Separate business-purpose hash |
| ML | `predict_proba` for class `1` (churn) | Separate ML-purpose hash |

Sort descending by score, then ascending by full hash, then ID. Hash input is
UTF-8 `retention-lab-ranking-v1|{policy}|{seed}|{ID}`. No policy uses the split
digest for ties. IDs are technical alignment/tie keys only, never predictors.
The random policy is **one reproducible realized ordering**, not an estimate of
risk. Its diagnostic reference is the constant-priority classifier (AP equals
partition prevalence, ROC-AUC 0.5), not measured performance of its realized
permutation or a capacity curve. Choosing a different seed is not model tuning.

The business policy means “review subscribers whose automatic renewal is off
first.” There are no added conditions or label-tuned thresholds. Unknown renewal
status **refuses scoring** rather than inventing priority: eligibility requires
0/1 today; a future unknown bucket would need a new explicitly approved policy.
The rule's binary priority is not a calibrated churn probability; its AP/ROC-AUC
are descriptive score diagnostics and it has no reported log loss.

## Original LR train-only pipeline

Seven source columns only, in frozen order. A schema guard rejects extra ID,
label, digest or partition fields, changed order, invalid renewal categories,
infinite values and missing required inputs, including on direct pipeline use.

- `auto_renew`: validated binary 0/1 passthrough; no numeric standardization or
  learned category vocabulary is needed for this two-level category.
- Six numeric predictors: `SimpleImputer(strategy='median', add_indicator=True,
  keep_empty_features=True)`, then `StandardScaler`. Medians, missing-indicator
  presence, means and scales are fitted on **training rows only**. Missing is not
  silently treated as zero; an entirely missing training column is retained with
  scikit-learn's zero fallback and a missingness indicator. No vocabulary or
  transformation is refitted on validation or final features.
- `LogisticRegression`: L2 regularization, `C=1`, `solver='lbfgs'`, `tol=1e-4`,
  `max_iter=1000`, `random_state=42`, intercept enabled, no class weights. Numerical
  kernels use one thread. Any convergence warning, exhausted iteration limit or
  nonfinite coefficients refuses publication; no automatic parameter search.

Logistic regression provides a simple interpretable first candidate. No second
model is warranted merely to add complexity. Candidate selection uses technical
validity and train/validation diagnostics only; **ML need not beat the rule**.
Probability estimates need not be calibrated, and linear log odds cannot express
arbitrary nonlinearities or interactions. These metrics are not the main budgeted
contact result and cannot establish superiority at a particular capacity.

References: [LogisticRegression](https://scikit-learn.org/1.7/modules/generated/sklearn.linear_model.LogisticRegression.html),
[imputation and retained empty features](https://scikit-learn.org/1.7/modules/impute.html).

## Private output contract

| File | Meaning |
|---|---|
| `pipeline.joblib` | Fitted schema guard, preprocessing and classifier; private, never published |
| `configuration.json` | Parameters, seeds, preprocessing, platform/Python and six numerical-library versions |
| `{partition}_keys.csv` | Exact copy of Phase 3 sorted keys, one `msno` column |
| `{partition}_scores.csv` | Aligned `random,business,ml` priorities, no identifiers or labels |
| `{partition}_rankings.csv` | Same three columns containing zero-based row offsets into keys/scores, in priority order |
| `metrics.json` | Training and validation diagnostics only; no final entry |
| `manifest.json` | Completion marker: frozen feature provenance, source/runner/dependency hashes, config, convergence, coverage and every output hash/size |

Rankings are complete permutations: take the first K rows of a policy's column
and resolve offsets through its separate keys. Phase 4 leaves K/rounding/metrics
implementation to Phase 5. Every policy covers exactly the same frozen users:
523,998 train, 175,651 validation and 174,931 final. Eligibility, cutoff
2017-01-31 and original `train.csv`/`transactions.csv` provenance remain unchanged;
there is no v2 input or cross-month split.

Before fitting, the loader verifies all fixed feature-file checksums, EDA
provenance, original-source configuration, exact assignment hashes and ordered
keys, feature whitelist/values/counts and permitted label alignment. It reads
only train/validation labels. A stray final-label file is ignored, not opened or
hashed. Synthetic guarded-I/O and poisoned-input checks exercise this boundary.
This is **data-flow isolation**, not an OS sandbox; the owner can manually open
raw labels. Historical Phase 1 label exposure cannot be undone.

Outputs are inside a 0700 owner-only directory (files inherit umask). All existing
file conflicts are checked before publishing any file; the manifest is last.
This is not atomic multi-file publication or a concurrent-writer service. A crash
may leave a subset, which an identical rerun completes; truncated or incompatible
evidence is refused. Checksums are integrity checks, not signatures or proof of
Kaggle source authenticity. Pickle bytes and last-bit predictions are guaranteed
only by the observed same-platform reproducibility checks, not across platforms,
Python/BLAS versions or numerical-library upgrades.

## Original LR execution and review — historical

Real training ran on all frozen rows, converged in **21 iterations** without a
warning, and reproduced all 13 private files byte-for-byte across three runs,
including one separate output directory. Verified Linux x86_64 / CPython 3.12.3;
scikit-learn 1.7.2, SciPy 1.17.0, NumPy 2.5.4, pandas 2.2.3, joblib 1.5.2,
threadpoolctl 3.6.0. All 52 installed distributions match the pins.

| Development diagnostic | Training | Validation |
|---|---:|---:|
| Logistic AP | 0.347491 | 0.335492 |
| Business AP | 0.221123 | 0.212767 |
| Constant-priority AP reference | 0.055372 | 0.054910 |
| Logistic ROC-AUC | 0.820125 | 0.812455 |
| Business ROC-AUC | 0.787996 | 0.780569 |
| Logistic log loss | 0.159503 | 0.160784 |

Full permitted diagnostics and configuration are in the public aggregate
[`model_validation.json`](../artifacts/model_validation.json). In that first increment, Logistic Regression
was retained: convergence, finite oriented probabilities and useful validation
discrimination justify the simple first candidate. No validation search or second
model was needed. Better validation AP/ROC-AUC does **not** establish final
performance, superiority at every contact budget, calibration or causal impact.
No final prevalence, final diagnostic or Recall@K curve was calculated.

Real execution, independent checks and limitations are recorded in
[progress](../PROGRESS.md). Only aggregate training/validation
results may be copied to Git; no individual keys, scores, model or raw records.
Review schema/provenance first, then train-only fitting, positive-class scoring,
label-free rankings and publication privacy. Existing source-arrival/labeler,
left-truncated history, record-based eligibility and single-cohort limitations
remain unchanged. No final-label access, Phase 5 work, PR or merge is authorized
by this implementation.

## Authorized second and final candidate (2026-10-20)

This section records the subsequently completed HGB comparison and pre-test
freeze. Its command is historical: do not rerun selection on this consumed
experiment. HGB remains selected; the four-curve result is in [results](results.md).

The extension keeps `train.py`, the original CLI and `kkbox-models-v1` immutable.
It adds `selection.py` and a separate private `kkbox-selection-v1` identity:

```sh
.venv/bin/python scripts/select_kkbox_model.py --verify-real-population
```

Exactly one HGB configuration is compared with the byte-reproduced original LR.
HGB uses the same seven predictors and training rows, native missing-value routing
and categorical `auto_renew`, no imputer/scaler, learning rate 0.1, 200 boosting
rounds, at most 15 leaves per tree, at least 50 rows per leaf, L2=1 and seed42.
Early stopping is disabled: neither the external validation cohort nor an internal
holdout determines training length. One numerical thread is used. No search,
extra features, third model or final outcomes enter this comparison.

Before measuring results, the practical rule is fixed: select HGB only if
validation Recall@10% improves by at least **one percentage point** and Recall@5%
and Recall@20% do not decrease; otherwise retain LR. This is a simplicity
preference, **not a significance test**. AP and ROC-AUC are secondary score
diagnostics. Realized random AP/ROC use its hash permutation as an arbitrary
continuous ordering; expected random capacity results are reported separately.

Contact budget is `K=floor(N*percentage/100)`, computed with decimal arithmetic.
Actual capacity is `K/N`; rounding never exceeds the requested allowance.
`evaluate.py` implements Recall=TP/P, Precision=TP/K, Lift=Precision/(P/N).
At K=0, precision/lift are null; recall is zero if P>0. At P=0, recall/lift are
null, precision is zero for K>0. At K=N with P>0, recall/lift are one.
Invalid percentages, labels, incomplete/duplicated permutations and duplicate
alignment keys fail closed. Existing purpose-specific hash tie policies remain.

The private freeze records both serialized candidates, permitted validation
scores/report, final keys/scores/rankings, parameters, feature/source/environment
hashes and selection rule. Verification recomputes validation diagnostics and
final predictions from the frozen models and features, checks exact permutations,
then confirms the decision. An explicit ancestor Git commit must contain the
matching `artifacts/model_freeze.json` and exact implementation bytes before the
separate final evaluator can open outcomes. A manifest's mere existence is not
sufficient. The freeze closes permanently when final evaluation starts.

### Historical publication hold — pre-release snapshot

This was the local publication boundary at freezing time. The later limited
aggregate authorization is documented in [attribution](data_attribution.md);
the original private files and frozen metadata remain unchanged.


The [official KKBOX rules, sections 7–8](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules)
were checked again on 2026-10-20 using indexed official text. They describe
educational/research use and restrict redistribution of competition data, without
explicit clearance for this project's new derived aggregates. No such clearance
is inferred here. **New real validation/final aggregates and figures remain
private**; the public anchor contains only configuration, decision and checksums,
not new measured metrics. This is a documented publication blocker, not legal
advice, not evidence of prohibition of every aggregate, and not permission to
publish. Previously committed Phase 2/4 artifacts are unchanged; their existence
does not establish permission for further outputs.

The real comparison selected **HGB** using the fixed rule; full validation
measurements are in private `data/processed/kkbox-selection-v1/validation.json`.
Both model and final-ranking hashes are anchored in public
[`model_freeze.json`](../artifacts/model_freeze.json), without publishing new
empirical aggregates. All nine private files reproduced byte-for-byte in three
CLI runs, including independent output reconstruction. Exact original LR bytes
are preserved; its scores are verified against the original run. Cross-process
serialization is not a general guarantee for arbitrary equivalent pickle object
graphs. Known NumPy/joblib deserialization deprecation warnings are nonfatal; no
new package versions were introduced to silence them.

The pre-test freeze was committed as
`7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8` before the separately authorized
single final evaluation. The final pass is now consumed: no retraining, model
reselection or new final experiment is permitted. See [current results](results.md) and [original evaluation history](evaluation_history.md). Reproduction across identical configurations
is not evidence of statistical uncertainty bounds or cross-cohort stability.
