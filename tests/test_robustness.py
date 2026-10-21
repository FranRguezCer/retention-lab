"""Hand-checkable subscriber resampling; no private data required."""
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.robustness import paired_bootstrap, weighted_recall


class RobustnessTests(unittest.TestCase):
    def test_repeated_copies_and_partial_boundary(self):
        # Expanded ranked sample: positive, positive, positive, negative.
        self.assertEqual(weighted_recall([1, 0, 1], [0, 1, 2], [3, 1, 0], 2), 2 / 3)
        self.assertEqual(weighted_recall([1, 0, 1], [0, 1, 2], [3, 1, 0], 0), 0)
        self.assertEqual(weighted_recall([1, 0, 1], [0, 1, 2], [3, 1, 0], 4), 1)
        self.assertIsNone(weighted_recall([0, 0], [0, 1], [2, 0], 1))

    def test_identical_rankings_reproducibility_and_edges(self):
        orders = {'a': [0, 2, 1, 3], 'b': [0, 2, 1, 3]}
        args = ([1, 0, 1, 0], orders)
        result = paired_bootstrap(*args, capacities=(0, 50, 100), replicates=100, seed=8,
                                  sensitivity=50)
        self.assertEqual(result, paired_bootstrap(*args, capacities=(0, 50, 100),
                                                 replicates=100, seed=8, sensitivity=50))
        for row in result['capacities']:
            self.assertEqual(row['differences_pp']['a_minus_b']['estimate'], 0)
            self.assertEqual(row['differences_pp']['a_minus_b']['interval_95'], [0, 0])
        self.assertEqual(result['capacities'][0]['recall']['a']['interval_95'], [0, 0])
        self.assertEqual(result['capacities'][-1]['recall']['a']['interval_95'], [1, 1])

    def test_perfect_imperfect_and_alignment(self):
        y = [1, 0, 1, 0]
        orders = {'perfect': [0, 2, 1, 3], 'imperfect': [1, 3, 0, 2]}
        result = paired_bootstrap(y, orders, capacities=(50,), replicates=100, seed=9,
                                  sensitivity=50)
        row = result['capacities'][0]
        self.assertEqual(row['differences_pp']['perfect_minus_imperfect']['estimate'], 100)
        self.assertGreaterEqual(row['differences_pp']['perfect_minus_imperfect']['interval_95'][0], 0)
        # A common reindexing of users/outcomes/orders preserves the estimand.
        permutation = np.array([2, 0, 3, 1])
        inverse = np.argsort(permutation)
        moved = {p: inverse[o] for p, o in orders.items()}
        other = paired_bootstrap(np.array(y)[permutation], moved, capacities=(50,),
                                 replicates=100, seed=9, sensitivity=50)
        self.assertEqual(row['recall']['perfect']['estimate'],
                         other['capacities'][0]['recall']['perfect']['estimate'])
        # Tied scores are represented by their previously frozen total order.
        self.assertEqual(weighted_recall([1, 0], [1, 0], [1, 1], 1), 0)
        self.assertEqual(weighted_recall([1, 0], [0, 1], [1, 1], 1), 1)

    def test_invalid_and_no_positive_samples(self):
        for y, orders in [([0, 0], {'a': [0, 1], 'b': [1, 0]}),
                          ([1, 0], {'a': [0, 0], 'b': [0, 1]}),
                          ([1, 0], {'a': [0], 'b': [0, 1]}),
                          ([1, 2], {'a': [0, 1], 'b': [0, 1]})]:
            with self.assertRaises(ValueError):
                paired_bootstrap(y, orders, replicates=10, sensitivity=5)
        for capacity in (-1, 101, float('nan'), True):
            with self.assertRaises(ValueError):
                paired_bootstrap([1, 0], {'a': [0, 1], 'b': [1, 0]},
                                 capacities=(capacity,), replicates=10, sensitivity=5)
        # Zero-positive replicates are explicitly excluded, never made zero recall.
        result = paired_bootstrap([1, 0], {'a': [0, 1], 'b': [1, 0]},
                                  replicates=100, seed=1, sensitivity=50)
        self.assertGreater(result['undefined_replicates'], 0)

    def test_explicit_expansion_oracle(self):
        y = np.array([1, 0, 1, 0, 1])
        orders = ([3, 0, 2, 4, 1], [4, 3, 1, 0, 2])
        for weights in ([2, 0, 1, 3, 0], [0, 4, 0, 0, 2], [1, 1, 1, 1, 1]):
            for order in orders:
                expanded = np.repeat(y[order], np.array(weights)[order])
                for k in range(len(expanded) + 1):
                    expected = expanded[:k].sum() / expanded.sum()
                    self.assertEqual(weighted_recall(y, order, weights, k), expected)

    def test_existing_diagnostic_formulas_and_ties(self):
        from retention_lab.train import diagnostics
        result = diagnostics(np.array([1, 0, 1, 0]), np.array([1., .5, .5, 0.]))
        # AP=(1 + 2/3)/2; ROC=(3 strict wins + half a tie)/4.
        self.assertAlmostEqual(result['average_precision'], 5 / 6)
        self.assertEqual(result['roc_auc'], .875)

    def test_public_only_audit_and_tamper_rejection(self):
        import importlib.util
        import json
        import shutil
        import tempfile
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('phase6_audit',
                                                      root / 'scripts/audit_kkbox_robustness.py')
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)
        with tempfile.TemporaryDirectory(prefix='retention-audit-test-') as tmp:
            copy = Path(tmp)
            (copy / 'artifacts').mkdir()
            (copy / 'docs').mkdir()
            for name in ('capacity_comparison_v2.json', 'capacity_comparison_v2.md'):
                shutil.copyfile(root / 'artifacts' / name, copy / 'artifacts' / name)
            shutil.copyfile(root / 'docs/results.md', copy / 'docs/results.md')
            audit.audit_public(copy)
            path = copy / 'artifacts/capacity_comparison_v2.json'
            value = json.loads(path.read_text())
            value['curve'][10]['hgb']['recall'] = .99
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):
                audit.audit_public(copy)
