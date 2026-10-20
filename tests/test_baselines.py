"""Label-free deterministic policy checks using synthetic identifiers."""
import hashlib
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.baselines import rank_users, random_scores, business_scores


class BaselineTests(unittest.TestCase):
    def test_random_is_equal_priority_deterministic_and_not_split_digest(self):
        keys = [f'synthetic-{i}' for i in range(100)]
        scores = random_scores(keys)
        self.assertEqual(scores, [0.0] * len(keys))
        order = rank_users(keys, scores, 'random', 42)
        self.assertEqual(order, rank_users(keys, scores, 'random', 42))
        reversed_keys = list(reversed(keys))
        self.assertEqual([keys[i] for i in order],
                         [reversed_keys[i] for i in rank_users(reversed_keys, scores, 'random', 42)])
        split = sorted(range(len(keys)), key=lambda i: hashlib.sha256(
            ('retention-lab-feb2017-v1|' + keys[i]).encode()).hexdigest())
        self.assertNotEqual(order, split)
        self.assertNotEqual(order, rank_users(keys, scores, 'random', 43))

    def test_business_off_first_with_independent_reproducible_ties(self):
        keys = [f'synthetic-{i}' for i in range(20)]
        renewal = [i % 2 for i in range(20)]
        scores = business_scores(renewal)
        order = rank_users(keys, scores, 'business', 42)
        self.assertEqual([scores[i] for i in order], [1.0] * 10 + [0.0] * 10)
        self.assertEqual(order, rank_users(keys, scores, 'business', 42))
        self.assertNotEqual(order[:10], rank_users(keys, scores, 'ml', 42)[:10])
        for invalid in (None, 2, float('nan'), '0'):
            with self.assertRaises(ValueError):
                business_scores([invalid])

    def test_invalid_alignment_scores_keys_and_policy_are_rejected(self):
        for keys, scores, policy in [(['a'], [], 'random'), (['a','a'], [0,0], 'ml'),
                                    (['a'], [float('inf')], 'ml'), (['a'], [0], 'split')]:
            with self.assertRaises(ValueError):
                rank_users(keys, scores, policy, 42)
