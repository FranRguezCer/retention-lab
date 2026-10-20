"""Pure capacity metrics shared by development and the one final evaluation."""
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from numbers import Integral, Real

import numpy as np


def capacity_to_k(n: int, percent: float) -> int:
    """Floor the decimal percentage budget; never exceed the contact allowance."""
    if (not isinstance(n, Integral) or isinstance(n, bool) or n <= 0
            or not isinstance(percent, (Real, Decimal)) or isinstance(percent, bool)):
        raise ValueError('Invalid population or percentage')
    try:
        value = Decimal(str(percent))
        if not value.is_finite() or not 0 <= value <= 100:
            raise ValueError('Percentage outside [0, 100]')
        return int((Decimal(int(n)) * value / 100).to_integral_value(rounding=ROUND_FLOOR))
    except InvalidOperation as error:
        raise ValueError('Invalid percentage') from error


def validate_ranking(order, n: int) -> np.ndarray:
    """Require a complete permutation of integer row offsets, not partial ranks."""
    ranks = np.asarray(order)
    if (ranks.ndim != 1 or ranks.dtype.kind not in 'iu' or len(ranks) != n
            or not np.array_equal(np.sort(ranks), np.arange(n))):
        raise ValueError('Ranking is not a complete permutation')
    return ranks


def cumulative_captures(labels, order) -> np.ndarray:
    """Validate binary outcomes and return captures at every K from zero to N."""
    y = np.asarray(labels)
    if (y.ndim != 1 or not len(y) or y.dtype.kind not in 'iufb'
            or not np.isin(y, [0, 1]).all()):
        raise ValueError('Invalid binary outcomes')
    ranks = validate_ranking(order, len(y))
    return np.concatenate(([0], np.cumsum(y[ranks], dtype=np.int64)))


def summarize(n: int, positives: int, k: int, captured: float) -> dict:
    """Undefined ratios are None (JSON null), never fictitious zeros."""
    precision = float(captured / k) if k else None
    return {'n': int(n), 'positives': int(positives), 'k': int(k),
            'captured': captured, 'capacity': k / n,
            'recall': float(captured / positives) if positives else None,
            'precision': precision,
            'lift': float(precision / (positives / n)) if k and positives else None}


def capacity_metrics(labels, order, percent: float) -> dict:
    """Recall=TP/P; Precision=TP/K; Lift=Precision/(P/N); actual capacity=K/N."""
    cumulative = cumulative_captures(labels, order)
    n = len(cumulative) - 1
    k = capacity_to_k(n, percent)
    return summarize(n, int(cumulative[-1]), k, int(cumulative[k]))


def expected_random(n: int, positives: int, percent: float) -> dict:
    """Uniform subset expectation, not a realized random permutation result."""
    k = capacity_to_k(n, percent)
    if not isinstance(positives, Integral) or not 0 <= positives <= n:
        raise ValueError('Invalid positive count')
    return summarize(n, positives, k, positives * k / n)
