# Retention Lab

How much more observed churn can a model identify when a subscription team can
contact only 10% of subscribers? Retention Lab compares **Random expected,
Business Rule, Logistic Regression and HistGradientBoostingClassifier (HGB)**
on the WSDM 2018 — KKBOX Churn Prediction Challenge cohort.

![Churn Captured vs. Outreach Capacity](artifacts/capacity_comparison_v2.png)

At 10% capacity (17,493 of 174,931 subscribers), HGB identifies **5,968 of 9,527
observed churners: 62.64% recall**. LR identifies 5,845 (61.35%), the rule 5,327
(55.91%), and random selection expects about 952.69 (10.00%). HGB adds **1.29
recall percentage points** over the simpler LR at this budget.

HGB was selected on validation before the original final evaluation; LR was
added later from its original frozen ranking as a **descriptive post-hoc
comparison**, not independent confirmation or model reselection. This is one
retrospective cohort: no temporal generalization, causal retention effect or
churn prevented is demonstrated. [Results and limitations](docs/results.md) ·
[Aggregate JSON](artifacts/capacity_comparison_v2.json).

Data: [WSDM 2018 — KKBOX Churn Prediction Challenge](https://www.kaggle.com/c/kkbox-churn-prediction-challenge)
([rules](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules),
[data](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/data)).
Independent educational project, not affiliated with or endorsed by KKBOX or
Kaggle. Obtain original CSVs from the authorized source; they are never
redistributed here. Published metrics/visualizations are derived aggregates;
no express license to redistribute data or all derivatives is asserted.
[Attribution and publication boundary](docs/data_attribution.md).

## Project status

| Phase | Status |
|---|---|
| 1 — Dataset feasibility | DONE — RESTRICTED GO |
| 2 — EDA | DONE |
| 3 — Feature engineering | DONE |
| 4 — Baselines and ML models | DONE |
| 5 — Capacity evaluation | DONE |
| 6 — Reliability and robustness | DONE |
| 7 — Interactive web demo | IMPLEMENTED — Netlify deployment pending |
| 8 — Portfolio and storytelling | NOT STARTED |

**Next: separately approve and verify the Phase 7 Netlify deployment.** The static
demo is implemented and locally verified, not deployed. Phase 8 remains NOT STARTED.

## Interactive React demo

The [static capacity explorer](web/README.md) compares all four strategies using
only the original public aggregate JSON. A 0–100% slider updates the curves,
selected-K metrics and paired differences; conditional bootstrap intervals appear
only at 5/10/20%. LR's post-hoc status and detection-versus-prevention limits are
explicit. Refined typography, source-derived metric examples and visual paired
intervals make the evidence easier to read. No subscriber data, model execution
or backend is included.

```sh
cd web
npm ci
npm run dev
# Production verification
npm run typecheck
npm test
npm run build
npm run check:build
```

Node 24 is the deployment target. The root `netlify.toml` publishes `web/dist`,
not the repository. **Netlify is prepared but has not been deployed.** See
[frontend instructions](web/README.md) for browser checks and deployment approval.

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

## Reliability audit

The [post-hoc robustness audit](docs/robustness.md) verifies the frozen results
and reports conditional subscriber-bootstrap uncertainty. See also the
[classified limitations](docs/limitations.md). No temporal or causal guarantee
is implied; the original metrics and models are unchanged.

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

## Historical reproduction: data preparation and models

The following commands document the original staged workflow. Do not rerun data
preparation, training or selection to refresh this already-consumed experiment.
For current results, use the published artifacts and technical documentation.

### Reproduce the private-data analysis

Obtain the original KKBOX `transactions.csv` and `train.csv` yourself under the
competition's access rules; place them under ignored `data/raw/`. Do not substitute
v2 files, rename other releases, commit private files or run global-label auditors
as part of EDA. Follow [the complete preparation and notebook commands](docs/methodology.md#prepare-and-execute)
only after setup. The published aggregates do not replace those private inputs.

The pinned environment was tested on the stated platform, not all operating
systems. Package version pins are not package-byte hashes; offline installation,
other-platform wheels and cross-machine PNG identity are not guaranteed.

### Reproduce Phase 3 features

With the verified private Phase 2 artifacts available, run:

```sh
.venv/bin/python scripts/prepare_kkbox_features.py --verify-real-population
```

The [feature contract](docs/features.md) documents the seven predictors, private
outputs, separate validation labels, unlabeled final features and cache checks.
No imputer/scaler/encoder or model is fitted by this command.

### Reproduce Phase 4 models and rankings

```sh
.venv/bin/python scripts/train_kkbox.py --verify-real-population
```

The [training guide](docs/models.md) explains train-only preprocessing, deterministic
policies, private outputs, checksums and limitations. The [public development
diagnostics](artifacts/model_validation.json) contain training/validation
aggregates only. The original Logistic Regression converged in 21 iterations;
validation AP is 0.335492 and ROC-AUC 0.812455. These are **not final evaluation
results** or proof of improvement at a particular outreach capacity. The JSON is the original LR development snapshot, not the later HGB selection
or the final four-strategy result. Its historical metadata remains unchanged.

## Model selection and original evaluation

The [model guide](docs/models.md#authorized-second-and-final-candidate-2026-10-20)
and [archived original protocol](docs/evaluation_history.md)
document the validation-only HGB selection and committed pre-test freeze. One
original final evaluation compared Random, Business Rule and HGB. Its consumed
marker, outputs and plot are retained unchanged. The separately versioned LR
addition reuses the same already-observed outcomes; it cannot reopen selection.
The earlier aggregate-publication hold is superseded only by the owner's limited
authorization and the [documented conditions review](docs/data_attribution.md).
