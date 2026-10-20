# Retention Lab

A retrospective subscription-churn study: how many future churners can be
identified when outreach capacity is limited? **Phase 3 is complete:** seven
reproducible cutoff-safe predictors, frozen user partitions, isolated outcomes
and five interpreted training-only EDA charts. No model, capacity-comparison curves or deployed application yet.
Identifying churn is not evidence that an intervention saves customers.

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
No modeling library or interactive JupyterLab/Notebook server is needed; execution
uses nbclient and an ipykernel in a fresh local process.

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
