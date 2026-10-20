# Retention Lab

A retrospective subscription-churn study: how many observed future churners can
be identified when outreach capacity is limited? **Four frozen strategies are
now compared:** Random expected, Business Rule, Logistic Regression and
HistGradientBoosting. HGB was selected on validation before the original final
evaluation; LR is a **post-hoc descriptive addition**, not a new model selection
or an independent confirmatory test. No deployed application or Phase 6 work.

![Churn Captured vs. Outreach Capacity](artifacts/capacity_comparison_v2.png)

On the shared 174,931-subscriber final cohort (9,527 observed churners), at 10%
capacity HGB identifies 5,968 churners (62.64% recall), versus 5,845 (61.35%) for
LR and 5,327 (55.91%) for the rule. HGB's descriptive gain over LR is **1.29
percentage points**; at 5% and 20% it is 1.23 and 6.48 points. These results do
not show that contacts prevented churn, nor demonstrate temporal generalization.
See [full tables and limitations](docs/results.md) and
[versioned aggregate JSON](artifacts/capacity_comparison_v2.json).

Data: **WSDM 2018 — KKBOX Churn Prediction Challenge**
([source](https://www.kaggle.com/c/kkbox-churn-prediction-challenge),
[rules](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules),
[data](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/data)).
Independent educational project; not affiliated with or endorsed by KKBOX or
Kaggle. Acquire originals from the authorized source; never redistribute them.
See [attribution and limited aggregate-publication review](docs/data_attribution.md).
No express permission for derivative-data publication is asserted.

## Reproduce the descriptive extension (no raw CSV access)

With the intact private original LR, HGB freeze and consumed evaluation cache:

```sh
.venv/bin/python scripts/extend_kkbox_comparison.py
```

This verifies historical hashes, reuses outcomes from private cached counts in
memory, and exports only separate v2 aggregate JSON/table/PNG. Repeat runs compare
existing outputs rather than overwrite them. Do not rerun training, selection or
`evaluate_kkbox.py` for this extension. Original three-strategy evidence stays
private and byte-identical. Preparation/training commands below document the
historical workflow, not authorization to run it again on this consumed test.

## Start here

- [Methodology and reproduction](docs/methodology.md): environment, private data,
  commands, isolation boundaries and limitations.
- [Executed EDA notebook](notebooks/01_eda.ipynb) and
  [aggregate results](artifacts/eda_summary.json): readable without private data.
- [Progress and verification](PROGRESS.md), [project scope](PROJECT.md) and
  [roadmap](ROADMAP.md): observed state and separately authorized next phases.

## Install and test without KKBOX data

Run from the repository root. The verified target is **CPython 3.12.3 on Linux
x86_64**. A Python installation with `venv`/`ensurepip` support is required for
this quick path. Do not overwrite an existing environment used for other work.

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m unittest discover -s tests -v
```

The tests use synthetic fixtures and committed aggregate notebook outputs, not
private KKBOX files. No `pip install .` is required: this repository is not
packaged as an installable distribution; its CLIs load `src/` explicitly.
See [the pip-free environment fallback](docs/methodology.md#python-without-ensurepip)
if your Python installation cannot bootstrap pip.

[`requirements.txt`](requirements.txt) is the only dependency manifest and pins
the complete verified environment, including direct and transitive dependencies.
Use the single ignored `.venv` environment for analysis and feature preparation.
The manifest includes scikit-learn and its pinned numerical dependencies. No
interactive JupyterLab/Notebook server is needed; notebook execution uses nbclient
and an ipykernel in a fresh local process.

## Reproduce the private-data analysis

Obtain the original KKBOX `transactions.csv` and `train.csv` yourself under the
competition's access rules; place them under ignored `data/raw/`. Do not substitute
v2 files, rename other releases, commit private files or run global-label auditors
as part of EDA. Follow [the complete preparation and notebook commands](docs/methodology.md#prepare-and-execute)
only after setup. The published aggregates do not replace those private inputs.

The pinned environment was tested on the stated platform, not all operating
systems. Package version pins are not package-byte hashes; offline installation,
other-platform wheels and cross-machine PNG identity are not guaranteed.

## Reproduce Phase 3 features

With the verified private Phase 2 artifacts available, run:

```sh
.venv/bin/python scripts/prepare_kkbox_features.py --verify-real-population
```

The [feature contract](docs/features.md) documents the seven predictors, private
outputs, separate validation labels, unlabeled final features and cache checks.
No imputer/scaler/encoder or model is fitted by this command.

## Reproduce Phase 4 models and rankings

```sh
.venv/bin/python scripts/train_kkbox.py --verify-real-population
```

The [training guide](docs/models.md) explains train-only preprocessing, deterministic
policies, private outputs, checksums and limitations. The [public development
diagnostics](artifacts/model_validation.json) contain training/validation
aggregates only. The original Logistic Regression converged in 21 iterations;
validation AP is 0.335492 and ROC-AUC 0.812455. These are **not final evaluation
results** or proof of improvement at a particular outreach capacity. That original iteration froze final
scores without labels; the subsequently authorized Phase5 comparison is now
preserved privately; the separate post-hoc aggregate comparison is linked above.

## Model selection and original evaluation

The [model guide](docs/models.md#authorized-second-and-final-candidate-2026-10-20)
and [original protocol](docs/results.md#historical-original-evaluation-protocol)
document the validation-only HGB selection and committed pre-test freeze. One
original final evaluation compared Random, Business Rule and HGB. Its consumed
marker, outputs and plot are retained unchanged. The separately versioned LR
addition reuses the same already-observed outcomes; it cannot reopen selection.
The earlier aggregate-publication hold is superseded only by the owner's limited
authorization and the [documented conditions review](docs/data_attribution.md).
