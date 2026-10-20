"""Hand-checkable capacity definitions, before real model comparison."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.evaluate import capacity_to_k, capacity_metrics, expected_random


class CapacityTests(unittest.TestCase):
    def test_floor_exact_boundaries_and_invalid_inputs(self):
        self.assertEqual(capacity_to_k(174931, 10), 17493)
        self.assertEqual(capacity_to_k(20, 5), 1)
        self.assertEqual(capacity_to_k(3, 100), 3)
        self.assertEqual(capacity_to_k(3, 0), 0)
        for p in (-1, 101, float('nan'), float('inf'), '10', True):
            with self.assertRaises(ValueError):
                capacity_to_k(10, p)
        for n in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                capacity_to_k(n, 10)

    def test_manual_metrics_and_null_undefined_ratios(self):
        y, order = [1, 0, 1, 0], [0, 2, 1, 3]
        row = capacity_metrics(y, order, 50)
        self.assertEqual(row, {'k': 2, 'n': 4, 'positives': 2, 'captured': 2,
                              'capacity': .5, 'recall': 1., 'precision': 1., 'lift': 2.})
        zero = capacity_metrics(y, order, 0)
        self.assertEqual(zero['recall'], 0)
        self.assertIsNone(zero['precision'])
        self.assertIsNone(zero['lift'])
        full = capacity_metrics(y, order, 100)
        self.assertEqual((full['recall'], full['precision'], full['lift']), (1, .5, 1))
        none = capacity_metrics([0]*4, order, 50)
        self.assertIsNone(none['recall'])
        self.assertEqual(none['precision'], 0)
        self.assertIsNone(none['lift'])
        random = expected_random(4, 2, 50)
        self.assertEqual((random['captured'], random['recall'], random['precision'], random['lift']),
                         (1., .5, .5, 1.))
        self.assertIsNone(expected_random(4, 0, 50)['recall'])
        self.assertIsNone(expected_random(4, 2, 0)['precision'])

    def test_incomplete_duplicate_invalid_rankings_and_labels_are_refused(self):
        for y, order in [([1,0], [0]), ([1,0], [0,0]), ([1,0], [0,2]),
                         ([1,0], [0.,1.]), ([1,2], [0,1]), (['1','0'], [0,1]),
                         ([float('nan'),0], [0,1]), ([], [])]:
            with self.assertRaises(ValueError):
                capacity_metrics(y, order, 50)
