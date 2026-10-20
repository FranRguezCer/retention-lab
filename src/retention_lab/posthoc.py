"""Descriptive extension from immutable historical evidence, never a new test pass."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from retention_lab.data import fingerprint, read_rows
from retention_lab.evaluate import capacity_to_k, cumulative_captures, summarize, validate_ranking
from retention_lab.final_evaluation import build_results

EXTENSION = 'Post-hoc descriptive extension using the previously frozen Logistic Regression ranking.'
POLICIES = ('random', 'business', 'ml')
FEATURES = ['auto_renew', 'observed_history_days', 'january_transactions',
            'distinct_transactions', 'latest_plan_days', 'latest_amount', 'auto_on_to_off']


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _git(repository: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(repository), *args],
                                   stderr=subprocess.DEVNULL).decode()


def _verified_files(folder: Path, manifest: dict, snapshot: dict) -> None:
    for name, expected in manifest['files'].items():
        _require(Path(name).name == name, 'Artifact name is not a basename')
        path = folder / name
        _require(fingerprint(path) == expected, 'Historical artifact changed')
        snapshot[path] = expected


def _orders(folder: Path, n: int) -> dict:
    rows = list(read_rows(folder / 'final_rankings.csv', list(POLICIES)))
    return {p: validate_ranking(np.array([int(r[i]) for r in rows]), n)
            for i, p in enumerate(POLICIES)}


def extend_from_cache(legacy: Path, frozen: Path, evaluation: Path, repository: Path,
                      lr_commit: str, freeze_commit: str, evaluation_commit: str,
                      expected_population: tuple[int, int] | None = None) -> tuple[dict, dict]:
    """Audit first; recover private outcomes in memory; return sampled aggregates.

    No model deserialization, predictions, selection, source CSV or outcome-file
    parameter exists. Full cumulative counts in the second return value are
    PRIVATE rendering inputs and must never be serialized for public delivery.
    Checksums/Git evidence establish local identity, not external timestamps or
    resistance to a malicious owner rewriting all evidence.
    """
    snapshot = {}
    manifests = []
    for folder in (legacy, frozen, evaluation):
        path = folder / 'manifest.json'
        snapshot[path] = fingerprint(path)
        manifests.append(json.loads(path.read_text()))
    original_lr, freeze, completed = manifests
    for commit in (lr_commit, freeze_commit, evaluation_commit):
        _require(len(commit) == 40 and all(c in '0123456789abcdef' for c in commit),
                 'Full historical commit required')
        _git(repository, 'merge-base', '--is-ancestor', commit, 'HEAD')
    _git(repository, 'merge-base', '--is-ancestor', lr_commit, freeze_commit)
    _git(repository, 'merge-base', '--is-ancestor', freeze_commit, evaluation_commit)
    _require(snapshot[legacy / 'manifest.json']['sha256'] in
             _git(repository, 'show', f'{lr_commit}:PROGRESS.md'), 'LR manifest lacks historical anchor')
    anchor = json.loads(_git(repository, 'show', f'{freeze_commit}:artifacts/model_freeze.json'))
    _require(anchor['manifest'] == snapshot[frozen / 'manifest.json']
             and anchor['selected_model'] == freeze['selected_model'] == 'hgb', 'HGB freeze differs')
    _require(snapshot[evaluation / 'manifest.json']['sha256'] in
             _git(repository, 'show', f'{evaluation_commit}:PROGRESS.md'),
             'Original evaluation lacks historical anchor')
    for folder, manifest in zip((legacy, frozen, evaluation), manifests):
        _require(manifest['version'] == 1, 'Unexpected historical version')
        _verified_files(folder, manifest, snapshot)
    _require(freeze['legacy_manifest'] == snapshot[legacy / 'manifest.json']
             and freeze['legacy_model'] == original_lr['files']['pipeline.joblib']
             == freeze['files']['logistic.joblib'], 'Original LR relationship differs')
    _require(original_lr['configuration']['feature_columns'] == freeze['feature_columns'] == FEATURES
             and original_lr['feature_manifest'] == freeze['feature_manifest'], 'Seven features differ')
    for name, expected in freeze['sources'].items():
        path = repository / name
        _require(not Path(name).is_absolute() and '..' not in Path(name).parts,
                 'Invalid source path')
        _require(fingerprint(path) == expected, 'Frozen implementation changed')
        snapshot[path] = expected
    identity = completed['identity']
    _require(identity['freeze_commit'] == freeze_commit
             and identity['freeze_manifest'] == snapshot[frozen / 'manifest.json'],
             'Original evaluation identity differs')
    for name, expected in identity['evaluator'].items():
        _require(not Path(name).is_absolute() and '..' not in Path(name).parts,
                 'Invalid evaluator path')
        path = repository / name
        _require(fingerprint(path) == expected, 'Original evaluator changed')
        snapshot[path] = expected
    marker = frozen / 'evaluation_started.json'
    _require(fingerprint(marker) == completed['start_record'], 'Consumed marker changed')
    snapshot[marker] = completed['start_record']
    start = json.loads(marker.read_text())
    _require(all(start[k] == v for k, v in identity.items()), 'Consumed identity differs')
    keys = [r[0] for r in read_rows(frozen / 'final_keys.csv', ['msno'])]
    n = len(keys)
    _require(n > 0 and len(set(keys)) == n and keys == sorted(keys), 'Invalid final keys')
    _require(original_lr['population']['final'] == freeze['population']['final'] == n
             and original_lr['files']['final_keys.csv'] == freeze['files']['final_keys.csv'],
             'Different final population')
    lr_orders, orders = _orders(legacy, n), _orders(frozen, n)
    for p in ('random', 'business'):
        _require(np.array_equal(lr_orders[p], orders[p]), 'Frozen baseline order differs')
    old_scores = list(read_rows(legacy / 'final_scores.csv', list(POLICIES)))
    new_scores = list(read_rows(frozen / 'final_scores.csv', list(POLICIES)))
    _require(len(old_scores) == len(new_scores) == n
             and all(a[:2] == b[:2] for a, b in zip(old_scores, new_scores)),
             'Frozen baseline scores differ')
    # All identities are verified before deriving any per-key outcome.
    labels = None
    with np.load(evaluation / 'curve_counts.npz', allow_pickle=False) as archive:
        _require(set(archive.files) == set(POLICIES), 'Cached policy set differs')
        for p in POLICIES:
            counts = archive[p]
            _require(counts.shape == (n + 1,) and counts.dtype.kind in 'iu'
                     and counts[0] == 0 and np.isin(np.diff(counts), [0, 1]).all(),
                     'Invalid cumulative evidence')
            recovered = np.empty(n, dtype=np.int64)
            recovered[orders[p]] = np.diff(counts)
            _require(labels is None or np.array_equal(labels, recovered),
                     'Independent outcome reconstructions disagree')
            labels = recovered
    digest = hashlib.sha256()
    for key, value in zip(keys, labels):
        digest.update((json.dumps([key, int(value)]) + '\n').encode())
    _require(digest.hexdigest() == completed['selected_labels_sha256'], 'Reused outcome digest differs')
    positives = int(labels.sum())
    _require(expected_population is None or (n, positives) == expected_population,
             'Unexpected real population/outcome count')
    original = json.loads((evaluation / 'results.json').read_text())
    rebuilt, counts = build_results(labels, orders, 'hgb')
    _require(rebuilt == original, 'Original three-strategy results differ')
    counts['logistic'] = cumulative_captures(labels, lr_orders['ml'])
    curve = []
    pairs = [('logistic', 'random_expected'), ('logistic', 'business'),
             ('hgb', 'random_expected'), ('hgb', 'business'), ('hgb', 'logistic')]
    for old in original['curve']:
        percent = old['requested_percent']
        k = capacity_to_k(n, percent)
        row = {'requested_percent': percent, 'random_expected': old['random_expected'],
               'business': old['business'], 'hgb': old['ml'],
               'logistic': summarize(n, positives, k, int(counts['logistic'][k]))}
        for left, right in pairs:
            row[f'{left}_minus_{right}_recall_pp'] = (
                100 * (row[left]['recall'] - row[right]['recall']) if positives else None)
        curve.append(row)
    # Read back every audited artifact after computation; never repair originals.
    _require(all(fingerprint(path) == expected for path, expected in snapshot.items()),
             'Original evidence changed during extension')
    result = {'version': 2, 'extension': EXTENSION, 'selected_model': 'hgb',
              'n': n, 'positives': positives, 'prevalence': positives / n,
              'rounding': original['rounding'], 'cutoff': '20170131',
              'interpretation': 'Descriptive reuse, not independent confirmation; churn identified, not prevented',
              'publication': 'Owner-authorized aggregates; no express derivative-data license asserted',
              'outcome_reuse': 'Private v1 counts inverted through frozen orders in memory; original digest verified; no raw CSV access',
              'provenance': {'lr_commit': lr_commit, 'freeze_commit': freeze_commit,
                             'evaluation_commit': evaluation_commit,
                             'lr_manifest': snapshot[legacy / 'manifest.json'],
                             'lr_rankings': original_lr['files']['final_rankings.csv'],
                             'evaluation_manifest': snapshot[evaluation / 'manifest.json'],
                             'consumed_marker': snapshot[marker]},
              'curve': curve, 'table': [curve[p] for p in (5, 10, 20)]}
    return result, counts


def render_comparison(counts: dict, n: int, positives: int, path: Path) -> None:
    """Render empirical unsmoothed every-K steps; do not export their arrays."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    x = np.arange(n + 1) * 100 / n
    fig, ax = plt.subplots(figsize=(10, 6.5))
    if positives:
        ax.plot(x, x, '--', color='gray', label='Random expected (theoretical)')
        for policy, label, color in (
                ('business', 'Business Rule', 'tab:blue'),
                ('logistic', 'Logistic Regression (post-hoc)', 'tab:green'),
                ('ml', 'HistGradientBoosting (selected on validation)', 'tab:orange')):
            ax.step(x, counts[policy] * 100 / positives, where='post', color=color, label=label)
            ks = [capacity_to_k(n, p) for p in (5, 10, 20)]
            ax.scatter(x[ks], counts[policy][ks] * 100 / positives, color=color, s=22, zorder=4)
        ks = [capacity_to_k(n, p) for p in (5, 10, 20)]
        ax.scatter(x[ks], x[ks], color='gray', s=22, zorder=4)
        for k in ks:
            ax.axvline(x[k], color='gray', linewidth=.6, alpha=.4)
        ax.legend(loc='lower right', fontsize=9)
    else:
        ax.text(.5, .5, 'Recall undefined: no observed positives', ha='center', transform=ax.transAxes)
    ax.set(title='Churn Captured vs. Outreach Capacity', xlabel='Subscribers selected (%)',
           ylabel='Observed churners identified (Recall, %)', xlim=(0, 100), ylim=(0, 100))
    ax.grid(alpha=.2)
    fig.text(.5, .015, f'Same retrospective cohort: N={n:,}, observed churners={positives:,}. '
             'LR added descriptively after test use; no model reselection.', ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .035, 1, 1))
    fig.savefig(path, dpi=120, metadata={'Software': 'Retention Lab'})
    plt.close(fig)


def comparison_markdown(result: dict) -> str:
    """Format display values only; all arithmetic uses unrounded stored metrics."""
    def percentage(value):
        return 'undefined' if value is None else f'{value * 100:.2f}%'

    lines = ['| Strategy | Capacity | Subscribers contacted | Churners identified | Recall@K | Precision@K | Lift@K |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for row in result['table']:
        for policy, label in [('random_expected', 'Random expected'), ('business', 'Business Rule'),
                              ('logistic', 'Logistic Regression (post-hoc)'), ('hgb', 'HistGradientBoosting')]:
            m = row[policy]
            captured = f"{m['captured']:.2f} expected" if policy == 'random_expected' else str(m['captured'])
            lift = 'undefined' if m['lift'] is None else f"{m['lift']:.3f}"
            lines.append(f"| {label} | {row['requested_percent']}% | {m['k']:,} | {captured} | "
                         f"{percentage(m['recall'])} | {percentage(m['precision'])} | {lift} |")
    lines += ['', 'Recall differences in percentage points (not relative percentages).', '',
              '| Capacity | Logistic vs Rule | HGB vs Rule | HGB vs Logistic |', '|---|---:|---:|---:|']
    for row in result['table']:
        values = [row[f'{a}_minus_{b}_recall_pp'] for a, b in
                  [('logistic', 'business'), ('hgb', 'business'), ('hgb', 'logistic')]]
        formatted = ['undefined' if v is None else f'{v:+.2f} pp' for v in values]
        lines.append(f"| {row['requested_percent']}% | " + ' | '.join(formatted) + ' |')
    return '\n'.join(lines) + '\n'
