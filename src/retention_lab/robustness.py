"""Conditional subscriber bootstrap over frozen total orders, never model fitting."""
from itertools import combinations
from numbers import Integral

import numpy as np

from retention_lab.evaluate import capacity_to_k, cumulative_captures, validate_ranking


def _weighted_recall(y, order, weights, k):
    """Fast internal path after validating a complete aligned population."""
    total = int(weights @ y)
    if not total:
        return None
    if not k:
        return 0.0
    ranked_weights = weights[order]
    cumulative = np.cumsum(ranked_weights)
    boundary = int(np.searchsorted(cumulative, k, side='left'))
    before = int(cumulative[boundary - 1]) if boundary else 0
    captured = int(ranked_weights[:boundary] @ y[order[:boundary]])
    captured += (k - before) * int(y[order[boundary]])
    return captured / total


def weighted_recall(labels, order, weights, k: int) -> float | None:
    """Recall among first K bootstrap copies, including a partial boundary user.

    Each user has a nonnegative integer multiplicity. Copies remain adjacent in
    their original frozen total order; selecting only some identical copies at
    the boundary cannot change their common outcome. Zero positives is undefined.
    """
    y = np.asarray(labels)
    cumulative_captures(y, order)
    ranks = validate_ranking(order, len(y))
    w = np.asarray(weights)
    if (w.shape != y.shape or w.dtype.kind not in 'iu' or np.any(w < 0)
            or not w.sum() or not isinstance(k, Integral) or isinstance(k, bool)
            or not 0 <= k <= w.sum()):
        raise ValueError('Invalid bootstrap weights or capacity')
    return _weighted_recall(y.astype(np.int64), ranks, w, k)


def paired_bootstrap(labels, orders: dict, capacities=(5, 10, 20),
                     replicates: int = 2000, seed: int = 20261021,
                     sensitivity: int = 1000) -> dict:
    """Pointwise percentile intervals conditional on frozen models and cohort.

    Sample N user indices uniformly with replacement, using ONE multiplicity
    vector for every policy. Top-K is reconstructed separately within each
    resampled policy by that policy's original total order. K=floor(N*p/100).
    No IDs, outcomes, scores or replicate-level arrays are returned. Undefined
    zero-positive replicates are excluded and counted, including in the prefix.
    """
    if (not isinstance(replicates, Integral) or isinstance(replicates, bool)
            or not isinstance(sensitivity, Integral) or isinstance(sensitivity, bool)
            or not 2 <= sensitivity < replicates or len(orders) < 2):
        raise ValueError('Invalid replicate configuration or policy set')
    y = np.asarray(labels)
    for order in orders.values():
        cumulative_captures(y, order)
    y = y.astype(np.int64)
    if not y.sum():
        raise ValueError('Recall undefined: no positive outcomes')
    n = len(y)
    ks = [capacity_to_k(n, p) for p in capacities]
    if not ks or len(set(capacities)) != len(ks):
        raise ValueError('Empty or duplicate capacities')
    names = list(orders)
    ranks = [validate_ranking(orders[p], n) for p in names]
    draws = np.full((replicates, len(names), len(ks)), np.nan)
    rng = np.random.default_rng(seed)
    for b in range(replicates):
        weights = np.bincount(rng.integers(0, n, size=n), minlength=n)
        if not weights @ y:
            continue
        for j, order in enumerate(ranks):
            for c, k in enumerate(ks):
                draws[b, j, c] = _weighted_recall(y, order, weights, k)
    valid = np.isfinite(draws[:, 0, 0])
    if valid.sum() < 2 or valid[:sensitivity].sum() < 2:
        raise ValueError('Too few defined bootstrap replicates')

    def summary(estimate, samples):
        interval = np.quantile(samples[np.isfinite(samples)], [.025, .975], method='linear')
        prefix = samples[:sensitivity]
        short = np.quantile(prefix[np.isfinite(prefix)], [.025, .975], method='linear')
        return {'estimate': float(estimate), 'interval_95': interval.tolist(),
                'prefix_interval_95': short.tolist(),
                'max_endpoint_shift': float(np.max(np.abs(interval - short)))}

    rows = []
    for c, (percent, k) in enumerate(zip(capacities, ks)):
        point = [_weighted_recall(y, order, np.ones(n, dtype=np.int64), k) for order in ranks]
        rows.append({'requested_percent': percent, 'k': k,
                     'recall': {name: summary(point[j], draws[:, j, c])
                                for j, name in enumerate(names)},
                     'differences_pp': {
                         f'{names[a]}_minus_{names[b]}':
                         summary(100 * (point[a] - point[b]),
                                 100 * (draws[:, a, c] - draws[:, b, c]))
                         for a, b in combinations(range(len(names)), 2)}})
    return {'seed': seed, 'replicates': replicates, 'sensitivity_prefix': sensitivity,
            'undefined_replicates': int((~valid).sum()),
            'undefined_prefix_replicates': int((~valid[:sensitivity]).sum()),
            'interval': '95% pointwise percentile; numpy linear quantile',
            'estimand': 'iid subscriber resampling conditional on this cohort and frozen total orders',
            'capacities': rows}
