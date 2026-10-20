"""Label-free policy priorities and deterministic, purpose-separated ranking."""
import hashlib
import math
from collections.abc import Sequence

POLICIES = ('random', 'business', 'ml')


def random_scores(keys: Sequence[str]) -> list[float]:
    """Assign equal priority; the independent hash tie-break supplies the draw."""
    return [0.0] * len(keys)


def business_scores(auto_renew: Sequence[float]) -> list[float]:
    """Prioritize renewal off; unknown categories fail closed, never imputed."""
    if any(value not in (0, 1) for value in auto_renew):
        raise ValueError('Invalid renewal category')
    return [1.0 - value for value in auto_renew]


def rank_users(keys: Sequence[str], scores: Sequence[float], policy: str,
               seed: int) -> list[int]:
    """Return zero-based row offsets, score descending then purpose hash and ID.

    Hashes use neither labels/features nor the frozen partition digest. They
    simulate one reproducible random ordering, not expected random performance.
    """
    if (policy not in POLICIES or len(keys) != len(scores)
            or len(set(keys)) != len(keys) or any(not key for key in keys)
            or any(not math.isfinite(value) for value in scores)):
        raise ValueError('Invalid ranking inputs')
    prefix = f'retention-lab-ranking-v1|{policy}|{seed}|'
    ties = [hashlib.sha256((prefix + key).encode('utf-8')).hexdigest() for key in keys]
    return sorted(range(len(keys)), key=lambda i: (-scores[i], ties[i], keys[i]))
