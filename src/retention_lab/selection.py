"""Development-only second candidate and artifact-bound model freeze."""
import csv
from decimal import Decimal
import hashlib
import re
import subprocess
from importlib.metadata import version
import json
from pathlib import Path
import shutil
import tempfile

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from threadpoolctl import threadpool_limits

from retention_lab.baselines import business_scores, random_scores, rank_users
from retention_lab.data import fingerprint, publish_private, read_rows, write_json
from retention_lab.evaluate import capacity_metrics, expected_random
from retention_lab.features import FEATURE_COLUMNS
from retention_lab.train import load_inputs, score_model, validate_frame

ROOT = Path(__file__).resolve().parents[2]
HGB_PARAMS = dict(learning_rate=0.1, max_iter=200, max_leaf_nodes=15,
                  min_samples_leaf=50, l2_regularization=1.0,
                  early_stopping=False, random_state=42,
                  categorical_features=['auto_renew'])
RULE = {'primary': 'validation Recall@10%', 'minimum_absolute_gain': 0.01,
        'secondary': 'no decrease in validation Recall@5% or Recall@20%',
        'otherwise': 'logistic', 'rounding': 'floor(N * decimal_percentage / 100)',
        'significance': 'practical threshold, not statistical significance'}
SOURCES = ['src/retention_lab/' + name for name in
           ('selection.py', 'evaluate.py', 'train.py', 'baselines.py', 'features.py', 'data.py')]
SOURCES += ['scripts/select_kkbox_model.py', 'requirements.txt']
OUTPUTS = ['logistic.joblib', 'hgb.joblib', 'validation.json',
           'validation_keys.csv', 'validation_scores.csv',
           'final_keys.csv', 'final_scores.csv', 'final_rankings.csv']


def fit_hgb(frame, labels) -> Pipeline:
    """Fit native NaN/categorical trees on training only; no scaling or holdout."""
    validate_frame(frame)
    model = Pipeline([
        ('schema', FunctionTransformer(validate_frame, feature_names_out='one-to-one')),
        ('classifier', HistGradientBoostingClassifier(**HGB_PARAMS)),
    ])
    with threadpool_limits(limits=1):
        model.fit(frame, labels)
    return model


def choose_model(report: dict) -> str:
    """Apply the practical selection rule declared before observing any scores."""
    lr, hgb = (report[name]['capacity'] for name in ('logistic', 'hgb'))
    gain = Decimal(str(hgb['10']['recall'])) - Decimal(str(lr['10']['recall']))
    consistent = all(hgb[str(p)]['recall'] >= lr[str(p)]['recall'] for p in (5, 20))
    return 'hgb' if gain >= Decimal(str(RULE['minimum_absolute_gain'])) and consistent else 'logistic'


def validation_report(keys: list[str], labels, scores: dict) -> dict:
    """Score diagnostics plus actual permutations and separate random expectation."""
    report = {}
    for name, values in scores.items():
        policy = name if name in ('random', 'business') else 'ml'
        order = rank_users(keys, values, policy, 42)
        diagnostic = np.asarray(values)
        if name == 'random':
            # Continuous arbitrary priorities encode this realized permutation;
            # its AP/ROC are not the theoretical expectation of random ranking.
            diagnostic = np.empty(len(keys))
            diagnostic[order] = np.arange(len(keys), 0, -1)
        report[name] = {
            'average_precision': float(average_precision_score(labels, diagnostic)),
            'roc_auc': float(roc_auc_score(labels, diagnostic)),
            'capacity': {str(p): capacity_metrics(labels, order, p) for p in (5, 10, 20)},
        }
    report['random_expected'] = {
        str(p): expected_random(len(keys), int(np.sum(labels)), p) for p in (5, 10, 20)}
    return report


def read_scores(path: Path, columns: list[str]) -> dict:
    """Read numeric scores with Python's round-trip float parser."""
    rows = list(read_rows(path, columns))
    result = {name: [float(row[i]) for row in rows] for i, name in enumerate(columns)}
    if any(not np.isfinite(v).all() or np.any(np.asarray(v) < 0)
           or np.any(np.asarray(v) > 1) for v in result.values()):
        raise ValueError('Invalid frozen scores')
    return result


def write_columns(path: Path, columns: dict) -> None:
    """Keep aligned predictor-free numeric outputs in explicit column order."""
    with path.open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(columns)
        writer.writerows(zip(*columns.values()))


def verify_freeze(frozen: Path, features: Path, eda: Path) -> dict:
    """Verify bytes AND model/feature/score/ranking/selection relationships.

    This checks trusted locally generated joblib bytes before deserializing them;
    it is not safe ingestion of arbitrary external serialized models.
    """
    manifest = json.loads((frozen / 'manifest.json').read_text())
    if (manifest['version'] != 1 or manifest['rule'] != RULE
            or manifest['feature_columns'] != FEATURE_COLUMNS
            or manifest['hgb_parameters'] != HGB_PARAMS
            or manifest['selected_model'] not in ('logistic', 'hgb')
            or manifest['fitted_partition'] != 'train'
            or manifest['selection_partition'] != 'validation'
            or manifest['final_labels'] != 'not accepted or opened'
            or set(manifest['files']) != set(OUTPUTS)
            or set(manifest['sources']) != set(SOURCES)):
        raise ValueError('Incompatible selection freeze')
    for name, expected in manifest['files'].items():
        if fingerprint(frozen / name) != expected:
            raise ValueError('Frozen model artifact changed')
    for name, expected in manifest['sources'].items():
        if fingerprint(ROOT / name) != expected:
            raise ValueError('Frozen implementation changed')
    if fingerprint(features / 'manifest.json') != manifest['feature_manifest']:
        raise ValueError('Frozen feature provenance changed')
    for name, expected in manifest['packages'].items():
        if version(name) != expected:
            raise ValueError('Frozen environment changed')
    data, _ = load_inputs(features, eda)
    if manifest['population'] != {p: len(d['keys']) for p, d in data.items()}:
        raise ValueError('Frozen population changed')
    models = {name: joblib.load(frozen / f'{name}.joblib') for name in ('logistic', 'hgb')}
    classifier = models['hgb'].named_steps['classifier']
    if (not isinstance(classifier, HistGradientBoostingClassifier)
            or any(classifier.get_params()[k] != v for k, v in HGB_PARAMS.items())
            or list(models['hgb'].named_steps) != ['schema', 'classifier']):
        raise ValueError('HGB preprocessing or parameters differ')
    if (manifest['files']['logistic.joblib'] != manifest['legacy_model']
            or models['hgb'].named_steps['classifier'].get_params() != manifest['hgb_full_parameters']):
        raise ValueError('Candidate model identity differs')
    val = data['validation']
    keys = [r[0] for r in read_rows(frozen / 'validation_keys.csv', ['msno'])]
    if keys != val['keys']:
        raise ValueError('Validation key alignment differs')
    scores = read_scores(frozen / 'validation_scores.csv', ['random','business','logistic','hgb'])
    expected = {'random': random_scores(keys), 'business': business_scores(val['X']['auto_renew'])}
    expected.update({name: score_model(model, val['X']).tolist() for name, model in models.items()})
    if scores != expected:
        raise ValueError('Validation scores differ from models')
    report = validation_report(keys, val['y'], scores)
    if report != json.loads((frozen / 'validation.json').read_text()):
        raise ValueError('Validation report differs')
    if choose_model(report) != manifest['selected_model']:
        raise ValueError('Selection differs from predeclared rule')
    final = data['final']
    keys = [r[0] for r in read_rows(frozen / 'final_keys.csv', ['msno'])]
    if keys != final['keys']:
        raise ValueError('Final key alignment differs')
    scores = read_scores(frozen / 'final_scores.csv', ['random','business','ml'])
    expected = {'random': random_scores(keys), 'business': business_scores(final['X']['auto_renew']),
                'ml': score_model(models[manifest['selected_model']], final['X']).tolist()}
    if scores != expected:
        raise ValueError('Final scores differ from frozen policies')
    rows = list(read_rows(frozen / 'final_rankings.csv', ['random','business','ml']))
    for i, policy in enumerate(scores):
        if [int(r[i]) for r in rows] != rank_users(keys, scores[policy], policy, 42):
            raise ValueError('Final policy ranking differs')
    return manifest


def compare_and_freeze(features: Path, eda: Path, legacy: Path, output: Path,
                       verify_real: bool = False) -> dict:
    """Compare exactly two candidates; never receive raw or final outcome inputs."""
    roots = [p.resolve() for p in (features, eda, legacy, output)]
    if any(a == b or a in b.parents or b in a.parents
           for i, a in enumerate(roots) for b in roots[i+1:]):
        raise ValueError('Input/output overlap')
    if ((output / 'evaluation_started.json').exists()
            or output.exists() and output.stat().st_mode & 0o077):
        raise ValueError('Selection closed or output not private')
    data, _ = load_inputs(features, eda, verify_real)
    old = json.loads((legacy / 'manifest.json').read_text())
    if old['feature_manifest'] != fingerprint(features / 'manifest.json'):
        raise ValueError('Legacy feature identity differs')
    for name, expected in old['files'].items():
        if fingerprint(legacy / name) != expected:
            raise ValueError('Legacy artifact changed')
    if (old['fitted_partition'] != 'train'
            or old['population'] != {p: len(d['keys']) for p, d in data.items()}
            or old['configuration']['seed'] != 42):
        raise ValueError('Original model fit/configuration differs')
    for name, expected in old['implementation'].items():
        if fingerprint(ROOT / 'src/retention_lab' / name) != expected:
            raise ValueError('Original implementation changed')
    models = {'logistic': joblib.load(legacy / 'pipeline.joblib'),
              'hgb': fit_hgb(data['train']['X'], data['train']['y'])}
    for partition in ('validation', 'final'):
        prior = read_scores(legacy / f'{partition}_scores.csv', ['random', 'business', 'ml'])
        if score_model(models['logistic'], data[partition]['X']).tolist() != prior['ml']:
            raise ValueError('Original model predictions differ')
    with tempfile.TemporaryDirectory(prefix='retention-selection-') as directory:
        scratch = Path(directory)
        # Preserve original serialization exactly: re-pickling an equivalent
        # model can encode different Python object aliasing without changing it.
        shutil.copyfile(legacy / 'pipeline.joblib', scratch / 'logistic.joblib')
        joblib.dump(models['hgb'], scratch / 'hgb.joblib', compress=0, protocol=5)
        val = data['validation']
        scores = {'random': random_scores(val['keys']),
                  'business': business_scores(val['X']['auto_renew'])}
        scores.update({name: score_model(model, val['X']).tolist() for name, model in models.items()})
        report = validation_report(val['keys'], val['y'], scores)
        selected = choose_model(report)
        write_json(scratch / 'validation.json', report)
        write_columns(scratch / 'validation_scores.csv', scores)
        shutil.copyfile(features / 'validation_keys.csv', scratch / 'validation_keys.csv')
        final = data['final']
        scores = {'random': random_scores(final['keys']),
                  'business': business_scores(final['X']['auto_renew']),
                  'ml': score_model(models[selected], final['X']).tolist()}
        write_columns(scratch / 'final_scores.csv', scores)
        write_columns(scratch / 'final_rankings.csv',
                      {p: rank_users(final['keys'], s, p, 42) for p, s in scores.items()})
        shutil.copyfile(features / 'final_keys.csv', scratch / 'final_keys.csv')
        manifest = {'version': 1, 'selected_model': selected, 'rule': RULE,
                    'feature_columns': FEATURE_COLUMNS, 'hgb_parameters': HGB_PARAMS,
                    'hgb_full_parameters': models['hgb'].named_steps['classifier'].get_params(),
                    'feature_manifest': fingerprint(features / 'manifest.json'),
                    'legacy_model': old['files']['pipeline.joblib'],
                    'legacy_manifest': fingerprint(legacy / 'manifest.json'),
                    'population': {p: len(d['keys']) for p, d in data.items()},
                    'fitted_partition': 'train', 'selection_partition': 'validation',
                    'final_labels': 'not accepted or opened',
                    'packages': old['configuration']['packages'],
                    'sources': {name: fingerprint(ROOT / name) for name in SOURCES},
                    'files': {name: fingerprint(scratch / name) for name in OUTPUTS}}
        write_json(scratch / 'manifest.json', manifest)
        verify_freeze(scratch, features, eda)
        for name in OUTPUTS + ['manifest.json']:
            if (output / name).exists() and fingerprint(output / name) != fingerprint(scratch / name):
                raise ValueError('Existing frozen comparison differs')
        output.mkdir(parents=True, exist_ok=True, mode=0o700)
        for name in OUTPUTS + ['manifest.json']:
            publish_private(output / name, scratch / name)
    return {'selected_model': selected, 'validation': report,
            'manifest': fingerprint(output / 'manifest.json')}


def verify_committed_freeze(frozen: Path, features: Path, eda: Path, commit: str) -> dict:
    """Require an ancestor commit binding the exact manifest and implementation.

    The commit is the chronological evidence before final-label access, while
    verify_freeze checks actual artifacts and their relationships on disk.
    """
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('An explicit full freeze commit is required')
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'],
                   cwd=ROOT, check=True, capture_output=True)
    anchor = json.loads(subprocess.check_output(
        ['git', 'show', commit + ':artifacts/model_freeze.json'], cwd=ROOT))
    if anchor['version'] != 1 or anchor['manifest'] != fingerprint(frozen / 'manifest.json'):
        raise ValueError('Committed freeze anchor differs')
    manifest = verify_freeze(frozen, features, eda)
    if anchor['selected_model'] != manifest['selected_model'] or anchor['rule'] != RULE:
        raise ValueError('Committed model decision differs')
    for name, expected in manifest['sources'].items():
        blob = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)
        if {'sha256': hashlib.sha256(blob).hexdigest(), 'size_bytes': len(blob)} != expected:
            raise ValueError('Committed implementation differs')
    return manifest
