"""One final outcome pass after a committed, relationship-verified model freeze."""
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from retention_lab.data import fingerprint, read_rows, write_json
from retention_lab.evaluate import capacity_to_k, cumulative_captures, expected_random, summarize
from retention_lab.selection import verify_committed_freeze

ROOT = Path(__file__).resolve().parents[2]
FILES = ['results.json', 'curve_counts.npz', 'capacity_curve.png']


def final_outcomes(source: Path, keys: list[str], expected_identifiers: str) -> tuple[np.ndarray, str]:
    """Interpret ONLY selected final outcomes, after the caller's freeze gate.

    CSV parsing transports nonfinal fields, but never validates/converts/hashes
    their outcome values. This is data-flow isolation, not OS-level isolation.
    """
    wanted, identifiers, values = set(keys), set(), {}
    for user, value in read_rows(source, ['msno', 'is_churn']):
        if user in identifiers:
            raise ValueError('Duplicate original label identifier')
        identifiers.add(user)
        if user in wanted:
            if value not in ('0', '1'):
                raise ValueError('Invalid selected final outcome')
            values[user] = int(value)
    digest = hashlib.sha256()
    for user in sorted(identifiers):
        digest.update((json.dumps(user) + '\n').encode())
    if digest.hexdigest() != expected_identifiers or set(values) != wanted:
        raise ValueError('Original identifiers or final outcome coverage differ')
    selected = hashlib.sha256()
    for key in keys:
        selected.update((json.dumps([key, values[key]]) + '\n').encode())
    return np.array([values[key] for key in keys], dtype=np.int64), selected.hexdigest()


def render_curve(counts: dict, n: int, positives: int, path: Path) -> None:
    """Plot every empirical K as steps, not smoothed or resampled measurements."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    x = np.arange(n + 1) * 100 / n
    fig, ax = plt.subplots(figsize=(9, 6))
    if positives:
        ax.plot(x, x, '--', color='gray', label='Random (expected)')
        for policy, label in (('business', 'Business Rule'), ('ml', 'Selected ML')):
            ax.step(x, counts[policy] * 100 / positives, where='post', label=label)
        for percent in (5, 10, 20):
            k = capacity_to_k(n, percent)
            ax.scatter([x[k]], [counts['ml'][k] * 100 / positives], s=25, color='black')
            ax.axvline(x[k], color='gray', linewidth=.6, alpha=.4)
    else:
        ax.text(.5, .5, 'Recall undefined: no observed positives', ha='center', transform=ax.transAxes)
    ax.set(title='Churn Captured vs. Outreach Capacity',
           xlabel='Subscribers selected (%)', ylabel='Observed churners identified (Recall, %)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    if positives:
        ax.legend()
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=120, metadata={'Software': 'Retention Lab'})
    plt.close(fig)


def build_results(labels: np.ndarray, orders: dict, selected_model: str) -> tuple[dict, dict]:
    """Compute one set of cumulative captures, then all requested budgets."""
    counts = {policy: cumulative_captures(labels, order) for policy, order in orders.items()}
    n, positives = len(labels), int(labels.sum())
    curve = []
    for percent in range(101):
        k = capacity_to_k(n, percent)
        row = {'requested_percent': percent,
               'random_expected': expected_random(n, positives, percent)}
        for policy in ('random', 'business', 'ml'):
            name = 'random_permutation' if policy == 'random' else policy
            row[name] = summarize(n, positives, k, int(counts[policy][k]))
        for reference in ('business', 'random_expected'):
            row[f'ml_minus_{reference}_recall_pp'] = (
                100 * (row['ml']['recall'] - row[reference]['recall']) if positives else None)
        curve.append(row)
    return {'version': 1, 'selected_model': selected_model, 'n': n, 'positives': positives,
            'prevalence': positives / n, 'rounding': 'floor(N * decimal_percentage / 100)',
            'interpretation': 'Retrospective churn identified, not prevented; no causal or ROI estimate',
            'publication': 'PRIVATE: KKBOX aggregate-publication clearance unresolved',
            'curve': curve, 'table': [curve[p] for p in (5, 10, 20)]}, counts


def evaluate_once(frozen: Path, features: Path, eda: Path, source: Path,
                  output: Path, freeze_commit: str, verify_real: bool = False) -> dict:
    """Consume one durable final-label attempt; later runs only verify/read cache.

    An interrupted or rejected attempt never silently reopens outcomes. The owner
    can bypass files manually; this is a local protocol, not a security sandbox.
    """
    roots = [p.resolve() for p in (frozen, features, eda, source.parent, output)]
    if source.name != 'train.csv' or any(a == b or a in b.parents or b in a.parents
                                       for i, a in enumerate(roots) for b in roots[i+1:]):
        raise ValueError('Original label source or directory separation differs')
    if output.exists() and output.stat().st_mode & 0o077:
        raise ValueError('Evaluation output must be owner-only')
    # This entire relationship/commit gate runs BEFORE any raw outcome I/O.
    manifest = verify_committed_freeze(frozen, features, eda, freeze_commit)
    if verify_real and manifest['population'] != {'train': 523998, 'validation': 175651, 'final': 174931}:
        raise ValueError('Unexpected final population')
    keys = [r[0] for r in read_rows(frozen / 'final_keys.csv', ['msno'])]
    if len(set(keys)) != len(keys) or len(keys) != manifest['population']['final']:
        raise ValueError('Final key coverage differs')
    rows = list(read_rows(frozen / 'final_rankings.csv', ['random', 'business', 'ml']))
    orders = {policy: [int(row[i]) for row in rows] for i, policy in enumerate(('random','business','ml'))}
    identity = {'freeze_commit': freeze_commit, 'freeze_manifest': fingerprint(frozen / 'manifest.json'),
                'output': str(output.resolve()),
                'evaluator': {name: fingerprint(ROOT / name) for name in
                              ('src/retention_lab/final_evaluation.py', 'scripts/evaluate_kkbox.py')}}
    state_path = frozen / 'evaluation_started.json'
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if {k: state[k] for k in identity} != identity:
            raise ValueError('Final evaluation already consumed for another identity')
        completed = json.loads((output / 'manifest.json').read_text())
        if (completed['version'] != 1 or completed['identity'] != identity
                or completed['start_record'] != fingerprint(state_path)
                or set(completed['files']) != set(FILES)):
            raise ValueError('Final evaluation incomplete or changed')
        for name, expected in completed['files'].items():
            if fingerprint(output / name) != expected:
                raise ValueError('Cached final artifact changed')
        return json.loads((output / 'results.json').read_text())
    if (output.exists() and any(output.iterdir())) or not source.is_file():
        raise ValueError('Evaluation destination is not empty or source missing')
    # Structural/configuration checks above cannot consume outcomes. From here on,
    # ANY failure preserves this marker and prevents an automatic second pass.
    with state_path.open('x') as stream:
        json.dump({**identity, 'started_utc': datetime.now(timezone.utc).isoformat()}, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    original = json.loads((eda / 'manifest.json').read_text())
    labels, selected_hash = final_outcomes(
        source, keys, original['sources']['train.csv']['sorted_identifier_sha256'])
    results, counts = build_results(labels, orders, manifest['selected_model'])
    write_json(output / 'results.json', results)
    # Counts at every K can reveal ordered outcomes; private-only, never export.
    np.savez_compressed(output / 'curve_counts.npz', **counts)
    render_curve(counts, len(keys), int(labels.sum()), output / 'capacity_curve.png')
    write_json(output / 'manifest.json', {
        'version': 1, 'identity': identity, 'start_record': fingerprint(state_path),
        'completed_utc': datetime.now(timezone.utc).isoformat(),
        'source_scope': 'original identifiers verified; only selected final outcome values interpreted/hashed',
        'selected_labels_sha256': selected_hash,
        'files': {name: fingerprint(output / name) for name in FILES},
        'publication': 'private until KKBOX derived-aggregate clearance is established'})
    return results
