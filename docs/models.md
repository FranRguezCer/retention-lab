# Reproduce Phase 4 rankings

Phase 4 freezes **random, business-rule and Logistic Regression rankings**. It
prepares the later comparison; **Recall@K curves belong to Phase 5**, and no final
outcomes or final predictive metrics are used here. This remains the approved
RESTRICTED GO retrospective original-February-2017 benchmark, not a deployment
simulation or a claim of customers saved.

## Run

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

## Three fixed policies

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

## One train-only pipeline

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

## Observed execution and review

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
[`model_validation.json`](../artifacts/model_validation.json). Logistic Regression
is retained: convergence, finite oriented probabilities and useful validation
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
