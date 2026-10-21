"""Audit public metrics; optionally bootstrap the verified consumed private cache.

Default is data-free. --private performs the fixed Phase 6 analysis without raw
CSV access, model loading, fitting, scoring, reselection or evaluator execution.
Only global aggregates are exported, create-or-compare, never overwritten.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from retention_lab.baselines import rank_users
from retention_lab.data import fingerprint, publish_private, read_rows, write_json
from retention_lab.posthoc import comparison_markdown, extend_from_cache
from retention_lab.robustness import paired_bootstrap
from retention_lab.train import load_inputs

LR_COMMIT = '471525b34afdef2783350a734c4c2cfdd8366749'
FREEZE_COMMIT = '7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8'
EVALUATION_COMMIT = 'ec3e58ebf8f0312ab353ab1f854ba058d7c9d669'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def audit_public(root: Path) -> dict:
    """Independently check every stored formula and the published display table."""
    result = json.loads((root / 'artifacts/capacity_comparison_v2.json').read_text())
    n, positives = result['n'], result['positives']
    require(n == 174931 and positives == 9527, 'Public population changed')
    require(result['prevalence'] == positives / n, 'Prevalence differs')
    require([r['requested_percent'] for r in result['curve']] == list(range(101)),
            'Capacity coverage differs')
    policies = ('random_expected', 'business', 'logistic', 'hgb')
    for row in result['curve']:
        k = n * row['requested_percent'] // 100
        for policy in policies:
            m = row[policy]
            tp = m['captured']
            require(m['n'] == n and m['positives'] == positives and m['k'] == k,
                    'Stored population or K differs')
            expected = {'capacity': k / n, 'recall': tp / positives,
                        'precision': tp / k if k else None,
                        'lift': (tp / k) / (positives / n) if k else None}
            require(all(m[field] == value for field, value in expected.items()),
                    'Stored metric formula differs')
            require(0 <= tp <= min(k, positives), 'Impossible capture count')
            if policy == 'random_expected':
                require(tp == positives * k / n, 'Expected random differs')
        for field, value in row.items():
            if field.endswith('_recall_pp'):
                left, right = field.removesuffix('_recall_pp').split('_minus_')
                require(value == 100 * (row[left]['recall'] - row[right]['recall']),
                        'Percentage-point difference differs')
    require(result['table'] == [result['curve'][p] for p in (5, 10, 20)],
            'Sampled table differs')
    table = comparison_markdown(result)
    require(table == (root / 'artifacts/capacity_comparison_v2.md').read_text(),
            'Published table differs')
    documentation = (root / 'docs/results.md').read_text()
    require(all(line in documentation for line in table.splitlines() if line.startswith('|')),
            'Results document table differs')
    for policy in policies:
        captures = [r[policy]['captured'] for r in result['curve']]
        require(captures == sorted(captures) and captures[0] == 0 and captures[-1] == positives,
                'Nonmonotone or incomplete public curve')
    return result


def private_audit(root: Path) -> dict:
    """Verify identity before outcomes; recover only in memory; export summaries."""
    folders = {name: root / 'data/processed' / f'kkbox-{name}-v1'
               for name in ('eda', 'features', 'models', 'selection', 'evaluation')}
    snapshot = {p: fingerprint(p) for folder in folders.values()
                for p in folder.iterdir() if p.is_file()}
    public_paths = list((root / 'artifacts').glob('capacity_comparison_v2.*'))
    snapshot.update({p: fingerprint(p) for p in public_paths})
    public = audit_public(root)
    rebuilt, counts = extend_from_cache(
        folders['models'], folders['selection'], folders['evaluation'], root,
        LR_COMMIT, FREEZE_COMMIT, EVALUATION_COMMIT, (174931, 9527))
    require(public == rebuilt, 'Historical reconstruction differs from published results')
    # Validates assignments, every split digest, coverage and allowed label alignment.
    data, _ = load_inputs(folders['features'], folders['eda'], verify_real=True)
    keys = data['final']['keys']
    n = len(keys)
    ranks, scores = {}, {}
    for name, folder, column, policy in (
            ('hgb', folders['selection'], 'ml', 'ml'),
            ('logistic', folders['models'], 'ml', 'ml'),
            ('business', folders['selection'], 'business', 'business')):
        rows = list(read_rows(folder / 'final_rankings.csv', ['random', 'business', 'ml']))
        index = ['random', 'business', 'ml'].index(column)
        ranks[name] = np.array([int(r[index]) for r in rows])
        rows = list(read_rows(folder / 'final_scores.csv', ['random', 'business', 'ml']))
        scores[name] = np.array([float(r[index]) for r in rows])
        historical_keys = [r[0] for r in read_rows(folder / 'final_keys.csv', ['msno'])]
        require(historical_keys == keys, 'Historical feature/key alignment differs')
        require(np.array_equal(rank_users(keys, scores[name], policy, 42), ranks[name]),
                'Frozen scores and total order disagree')
    labels = np.empty(n, dtype=np.int64)
    labels[ranks['hgb']] = np.diff(counts['ml'])
    # Already verified via independent reconstructions and original digest above.
    require(np.array_equal(labels[ranks['logistic']], np.diff(counts['logistic'])),
            'LR outcome alignment differs')
    bootstrap = paired_bootstrap(labels, ranks)
    for row in bootstrap['capacities']:
        original = public['curve'][row['requested_percent']]
        require(all(row['recall'][p]['estimate'] == original[p]['recall'] for p in ranks),
                'Bootstrap estimand differs from original point metrics')
    diagnostics = {}
    for name, values in scores.items():
        diagnostics[name] = {
            'average_precision': float(average_precision_score(labels, values)),
            'roc_auc': float(roc_auc_score(labels, values)),
            'unique_scores': int(len(np.unique(values))),
            'brier_score': float(np.mean((values - labels) ** 2)) if name != 'business' else None}
    renewal_off = scores['business'] == 1
    require(np.array_equal(renewal_off, data['final']['X']['auto_renew'].to_numpy() == 0),
            'Rule priority and frozen features disagree')
    groups = {name: {'n': int(mask.sum()), 'positives': int(labels[mask].sum()),
                     'prevalence': float(labels[mask].mean())}
              for name, mask in [('renewal_off', renewal_off), ('renewal_on', ~renewal_off)]}
    bands = []
    for low, high in ((0, 5), (5, 10), (10, 20)):
        lower, upper = public['curve'][low], public['curve'][high]
        bands.append({'from_percent': low, 'to_percent': high,
                      'captures': {name: upper[name]['captured'] - lower[name]['captured']
                                   for name in ranks}})
    require(all(fingerprint(p) == value for p, value in snapshot.items()),
            'Original evidence changed during audit; publication blocked')
    return {'version': 1, 'analysis': 'Phase 6 descriptive post-hoc frozen-cohort audit',
            'n': n, 'positives': int(labels.sum()), 'cutoff': '20170131',
            'public_comparison': fingerprint(root / 'artifacts/capacity_comparison_v2.json'),
            'historical_files_verified_unchanged': len(snapshot),
            'bootstrap': bootstrap, 'frozen_score_diagnostics': diagnostics,
            'renewal_groups': groups, 'capacity_bands': bands,
            'interpretation': 'Conditional sampling uncertainty, not temporal or causal evidence; no reselection'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private', action='store_true', help='Run fixed 2000-replicate private-cache audit')
    args = parser.parse_args()
    try:
        audit_public(ROOT)
        if args.private:
            result = private_audit(ROOT)
            target = ROOT / 'artifacts/robustness_v1.json'
            # Public output is fixed; never accept an arbitrary private destination.
            import tempfile
            with tempfile.TemporaryDirectory(prefix='retention-robustness-') as directory:
                candidate = Path(directory) / target.name
                write_json(candidate, result)
                require(not target.exists() or fingerprint(target) == fingerprint(candidate),
                        'Existing robustness artifact differs; preserve it')
                publish_private(target, candidate)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Audit blocked ({type(error).__name__}); preserve evidence and inspect locally.', file=sys.stderr)
        return 2
    print('Public metrics verified.' + (' Fixed private audit reproduced/exported; originals unchanged.'
                                      if args.private else ' Private analysis not requested.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
