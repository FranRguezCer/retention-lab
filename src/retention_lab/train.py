"""Train one frozen logistic candidate; score all partitions without final labels."""
import csv
from importlib.metadata import version
import json
from pathlib import Path
import platform
import shutil
import tempfile
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from threadpoolctl import threadpool_limits

from retention_lab.baselines import business_scores, random_scores, rank_users
from retention_lab.data import COLUMNS, CUTOFF, SALT, fingerprint, publish_private, read_rows, split_user, write_json
from retention_lab.features import EXPECTED, FEATURE_COLUMNS, FILES, PARTITIONS

SEED = 42
MAX_ITER = 1000


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Require exactly the frozen predictors, never silently discard extra fields."""
    if not isinstance(frame, pd.DataFrame) or list(frame) != FEATURE_COLUMNS or frame.empty:
        raise ValueError('Incompatible predictor schema')
    values = frame.to_numpy(dtype=float)
    if np.isinf(values).any() or not frame['auto_renew'].isin([0, 1]).all():
        raise ValueError('Invalid predictor values')
    required = [c for c in FEATURE_COLUMNS if c not in ('latest_plan_days', 'latest_amount')]
    if frame[required].isna().any().any():
        raise ValueError('Missing required predictor')
    if not np.equal(values[~np.isnan(values)], np.floor(values[~np.isnan(values)])).all():
        raise ValueError('Predictors must be integer-valued')
    return frame


def load_inputs(features: Path, eda: Path, verify_real: bool = False) -> tuple[dict, dict]:
    """Verify frozen provenance and positional alignment; open only allowed files.

    No raw-source directory or final-label path is accepted. Provenance is a
    checksum chain, not a signature or proof of original source authenticity.
    """
    manifest = json.loads((features / 'manifest.json').read_text())
    if (manifest['version'] != 1 or manifest['cutoff'] != CUTOFF
            or manifest['feature_columns'] != FEATURE_COLUMNS
            or manifest['final_outcomes'] != 'never evaluated or exported'
            or set(manifest['files']) != set(FILES)
            or set(manifest['eda']) != {'manifest.json', 'assignments.csv', 'training.csv', 'quality.json'}):
        raise ValueError('Incompatible feature contract')
    for name, expected in manifest['eda'].items():
        if fingerprint(eda / name) != expected:
            raise ValueError('Frozen EDA provenance differs')
    original = json.loads((eda / 'manifest.json').read_text())
    configuration = original['configuration']
    if (original['version'] != 1 or configuration != {
            'cutoff': CUTOFF, 'salt': SALT, 'schema': COLUMNS,
            'buckets': {'train': [0, 5], 'validation': [6, 7], 'final': [8, 9]},
            'deduplication': 'exact all CSV fields'}
            or set(original['sources']) != {'transactions.csv', 'train.csv'}
            or original['population'] != manifest['population']
            or original['assignments'] != manifest['eda']['assignments.csv']):
        raise ValueError('Incompatible original source configuration')
    quality = json.loads((eda / 'quality.json').read_text())
    if quality['training_artifact'] != manifest['eda']['training.csv']:
        raise ValueError('Frozen EDA training identity differs')
    if verify_real and (manifest['population']['partitions'] != EXPECTED
                        or manifest['population']['labeled'] != sum(EXPECTED.values())
                        or manifest['population']['candidates'] != 874581
                        or manifest['population']['unlabeled'] != 1):
        raise ValueError('Unexpected real population')
    for name in FILES:
        if fingerprint(features / name) != manifest['files'][name]:
            raise ValueError('Frozen feature artifact differs')
    expected_keys = {p: [] for p in PARTITIONS}
    previous = None
    for user, digest, bucket, partition in read_rows(
            eda / 'assignments.csv', ['msno', 'digest', 'bucket', 'partition']):
        if ((digest, int(bucket), partition) != split_user(user)
                or previous is not None and user <= previous):
            raise ValueError('Invalid frozen assignment')
        expected_keys[partition].append(user)
        previous = user
    data = {}
    for partition in PARTITIONS:
        keys = [r[0] for r in read_rows(features / f'{partition}_keys.csv', ['msno'])]
        if (not keys or keys != expected_keys[partition]
                or len(keys) != manifest['population']['partitions'][partition]):
            raise ValueError('Keys or population differ')
        rows = [[int(v) if v else np.nan for v in row] for row in
                read_rows(features / f'{partition}_features.csv', FEATURE_COLUMNS)]
        frame = validate_frame(pd.DataFrame(rows, columns=FEATURE_COLUMNS, dtype=float))
        if len(frame) != len(keys):
            raise ValueError('Feature/key alignment differs')
        data[partition] = {'keys': keys, 'X': frame}
        if partition != 'final':
            labels = list(read_rows(features / f'{partition}_labels.csv', ['msno', 'is_churn']))
            if [r[0] for r in labels] != keys or any(r[1] not in ('0', '1') for r in labels):
                raise ValueError('Permitted label alignment or values differ')
            y = np.array([int(r[1]) for r in labels])
            if set(y) != {0, 1}:
                raise ValueError('Both classes required for fit/diagnostics')
            data[partition]['y'] = y
    return data, manifest


def fit_model(frame: pd.DataFrame, labels: np.ndarray, seed: int = SEED,
              max_iter: int = MAX_ITER) -> Pipeline:
    """Fit only supplied training rows; refuse nonconvergence before publication."""
    validate_frame(frame)
    if len(labels) != len(frame) or set(labels) != {0, 1} or max_iter < 1:
        raise ValueError('Invalid training configuration')
    numeric = Pipeline([
        ('impute', SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True)),
        ('scale', StandardScaler()),
    ])
    preprocess = ColumnTransformer([
        ('binary', 'passthrough', ['auto_renew']),
        ('numeric', numeric, FEATURE_COLUMNS[1:]),
    ], remainder='drop')
    model = Pipeline([
        ('schema', FunctionTransformer(validate_frame, feature_names_out='one-to-one')),
        ('preprocess', preprocess),
        ('classifier', LogisticRegression(C=1.0, solver='lbfgs', max_iter=max_iter,
                                          tol=1e-4, random_state=seed, class_weight=None)),
    ])
    with warnings.catch_warnings(), threadpool_limits(limits=1):
        warnings.simplefilter('error', ConvergenceWarning)
        model.fit(frame, labels)
    classifier = model.named_steps['classifier']
    if (classifier.n_iter_.max() >= max_iter or not np.isfinite(classifier.coef_).all()
            or not np.isfinite(classifier.intercept_).all()):
        raise ValueError('Model did not converge to finite parameters')
    return model


def score_model(model: Pipeline, frame: pd.DataFrame) -> np.ndarray:
    """Positive class is explicitly 1 (churn); greater scores imply greater risk."""
    validate_frame(frame)
    if (not isinstance(model, Pipeline)
            or list(model.feature_names_in_) != FEATURE_COLUMNS
            or list(model.classes_) != [0, 1]):
        raise ValueError('Incompatible fitted model')
    with threadpool_limits(limits=1):
        scores = model.predict_proba(frame)[:, 1]
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError('Invalid risk scores')
    return scores


def diagnostics(labels: np.ndarray, scores: np.ndarray) -> dict:
    """Development-only diagnostics, never the project's capacity result."""
    return {'average_precision': float(average_precision_score(labels, scores)),
            'roc_auc': float(roc_auc_score(labels, scores)),
            'log_loss': float(log_loss(labels, scores, labels=[0, 1])),
            'score_min': float(scores.min()), 'score_max': float(scores.max()),
            'score_mean': float(scores.mean())}


def train_and_score(features: Path, eda: Path, output: Path, seed: int = SEED,
                    max_iter: int = MAX_ITER, verify_real: bool = False) -> dict:
    """Retrain and create-or-compare all private artifacts, manifest last.

    No external serialized model is loaded. An incompatible existing model or
    run is refused by exact byte comparison, without deserializing it.
    """
    roots = [p.resolve() for p in (features, eda, output)]
    if any(a == b or a in b.parents or b in a.parents
           for i, a in enumerate(roots) for b in roots[i + 1:]):
        raise ValueError('Input/output directories overlap')
    if output.exists() and output.stat().st_mode & 0o077:
        raise ValueError('Model directory must be owner-only')
    data, feature_manifest = load_inputs(features, eda, verify_real)
    model = fit_model(data['train']['X'], data['train']['y'], seed, max_iter)
    versions = {name: version(name) for name in
                ('numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'threadpoolctl')}
    config = {'version': 1, 'seed': seed, 'feature_columns': FEATURE_COLUMNS,
              'classifier': model.named_steps['classifier'].get_params(),
              'numeric': {'imputation': 'train median', 'add_indicator': True,
                          'keep_empty_features': True, 'scaling': 'train StandardScaler'},
              'binary': 'validated 0/1 passthrough', 'threads': 1,
              'ranking': 'score descending; SHA256(retention-lab-ranking-v1|policy|seed|ID); ID',
              'model_selection': 'single logistic candidate; development diagnostics only',
              'python': platform.python_version(), 'platform': platform.platform(),
              'packages': versions}
    metrics = {}
    with tempfile.TemporaryDirectory(prefix='retention-models-') as directory:
        scratch = Path(directory)
        joblib.dump(model, scratch / 'pipeline.joblib', compress=0, protocol=5)
        write_json(scratch / 'configuration.json', config)
        for partition, table in data.items():
            keys, frame = table['keys'], table['X']
            scores = {'random': random_scores(keys),
                      'business': business_scores(frame['auto_renew'].tolist()),
                      'ml': score_model(model, frame).tolist()}
            if partition != 'final':
                # A constant 0.5 reference and the uncalibrated binary rule are
                # ranking diagnostics, not calibrated probability competitors.
                metrics[partition] = {p: diagnostics(table['y'], np.array(s))
                                      for p, s in scores.items() if p != 'random'}
                # The business score is a priority, not a probability: omit log loss.
                metrics[partition]['business'].pop('log_loss')
                metrics[partition]['random_reference'] = {
                    'average_precision': float(table['y'].mean()), 'roc_auc': 0.5}
            shutil.copyfile(features / f'{partition}_keys.csv', scratch / f'{partition}_keys.csv')
            orders = {p: rank_users(keys, s, p, seed) for p, s in scores.items()}
            for kind, values in (('scores', scores), ('rankings', orders)):
                with (scratch / f'{partition}_{kind}.csv').open('w', newline='') as stream:
                    writer = csv.writer(stream)
                    writer.writerow(list(scores))
                    writer.writerows(zip(*values.values()))
        write_json(scratch / 'metrics.json', metrics)
        files = sorted(p.name for p in scratch.iterdir())
        manifest = {
            'version': 1, 'feature_manifest': fingerprint(features / 'manifest.json'),
            'feature_provenance': feature_manifest, 'configuration': config,
            'implementation': {name: fingerprint(Path(__file__).parent / name)
                               for name in ('train.py', 'baselines.py', 'features.py', 'data.py')},
            'runner': fingerprint(Path(__file__).resolve().parents[2] / 'scripts/train_kkbox.py'),
            'requirements': fingerprint(Path(__file__).resolve().parents[2] / 'requirements.txt'),
            'population': {p: len(table['keys']) for p, table in data.items()},
            'fitted_partition': 'train', 'diagnostic_partitions': ['train', 'validation'],
            'final_labels': 'not accepted, opened, hashed or evaluated',
            'ranking_offsets': 'zero-based row indices into separate partition keys; top K = first K rows',
            'convergence': {'n_iter': model.named_steps['classifier'].n_iter_.tolist(),
                            'max_iter': max_iter, 'warning': False},
            'files': {name: fingerprint(scratch / name) for name in files},
        }
        write_json(scratch / 'manifest.json', manifest)
        for name in files + ['manifest.json']:
            if (output / name).exists() and fingerprint(output / name) != fingerprint(scratch / name):
                raise ValueError('Existing model run differs')
        output.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in files + ['manifest.json']:
            publish_private(output / name, scratch / name)
    return {'population': manifest['population'], 'convergence': manifest['convergence'],
            'metrics': metrics, 'manifest': fingerprint(output / 'manifest.json')}
