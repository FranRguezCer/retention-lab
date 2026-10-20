"""Post-hoc public-interface probes use synthetic evidence, never real KKBOX data."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


class PosthocTests(unittest.TestCase):
    def setUp(self):
        from retention_lab.posthoc import extend_from_cache
        from retention_lab.data import fingerprint, write_json
        from retention_lab.final_evaluation import build_results
        self.extend = extend_from_cache
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.legacy, self.frozen, self.evaluation = [self.root / n for n in ('lr', 'freeze', 'eval')]
        self.repo = self.root / 'repo'
        for p in (self.legacy, self.frozen, self.evaluation, self.repo):
            p.mkdir(mode=0o700)
        self.git('init', '-q')
        self.keys = [f'fixture-{i:02d}' for i in range(20)]
        self.labels = np.array([1, 0, 1, 0, 0] * 4)
        self.orders = {'random': np.arange(20), 'business': np.arange(19, -1, -1),
                       'ml': np.argsort(-self.labels, kind='stable')}
        lr_orders = {**self.orders, 'ml': np.arange(20)}
        for folder, orders in ((self.legacy, lr_orders), (self.frozen, self.orders)):
            with (folder / 'final_keys.csv').open('w', newline='') as stream:
                writer = csv.writer(stream); writer.writerow(['msno'])
                writer.writerows([[k] for k in self.keys])
            for name in ('final_rankings.csv', 'final_scores.csv'):
                with (folder / name).open('w', newline='') as stream:
                    writer = csv.writer(stream); writer.writerow(['random', 'business', 'ml'])
                    writer.writerows(zip(*(orders[p] for p in ('random', 'business', 'ml'))))
        (self.legacy / 'pipeline.joblib').write_bytes(b'synthetic frozen LR, not a pickle')
        (self.frozen / 'logistic.joblib').write_bytes((self.legacy / 'pipeline.joblib').read_bytes())
        (self.frozen / 'hgb.joblib').write_bytes(b'synthetic frozen HGB, not a pickle')
        columns = ['auto_renew', 'observed_history_days', 'january_transactions',
                   'distinct_transactions', 'latest_plan_days', 'latest_amount', 'auto_on_to_off']
        legacy = {'version': 1, 'files': self.files(self.legacy), 'population': {'final': 20},
                  'configuration': {'feature_columns': columns}, 'feature_manifest': {'sha256': 'features'}}
        write_json(self.legacy / 'manifest.json', legacy)
        (self.repo / 'PROGRESS.md').write_text(fingerprint(self.legacy / 'manifest.json')['sha256'])
        self.lr_commit = self.commit('original LR before outcomes')
        frozen = {'version': 1, 'files': self.files(self.frozen), 'population': {'final': 20},
                  'feature_columns': columns, 'feature_manifest': legacy['feature_manifest'],
                  'legacy_manifest': fingerprint(self.legacy / 'manifest.json'), 'selected_model': 'hgb',
                  'legacy_model': fingerprint(self.legacy / 'pipeline.joblib'), 'sources': {}}
        write_json(self.frozen / 'manifest.json', frozen)
        (self.repo / 'artifacts').mkdir()
        write_json(self.repo / 'artifacts/model_freeze.json',
                   {'manifest': fingerprint(self.frozen / 'manifest.json'), 'selected_model': 'hgb'})
        self.freeze_commit = self.commit('freeze before outcomes')
        identity = {'freeze_commit': self.freeze_commit,
                    'freeze_manifest': fingerprint(self.frozen / 'manifest.json'), 'evaluator': {}}
        write_json(self.frozen / 'evaluation_started.json',
                   {**identity, 'started_utc': '2026-10-20T17:53:34+00:00'})
        result, counts = build_results(self.labels, self.orders, 'hgb')
        write_json(self.evaluation / 'results.json', result)
        np.savez_compressed(self.evaluation / 'curve_counts.npz', **counts)
        (self.evaluation / 'capacity_curve.png').write_bytes(b'original synthetic image')
        digest = hashlib.sha256()
        for key, value in zip(self.keys, self.labels):
            digest.update((json.dumps([key, int(value)]) + '\n').encode())
        manifest = {'version': 1, 'files': self.files(self.evaluation), 'identity': identity,
                    'start_record': fingerprint(self.frozen / 'evaluation_started.json'),
                    'selected_labels_sha256': digest.hexdigest()}
        write_json(self.evaluation / 'manifest.json', manifest)
        with (self.repo / 'PROGRESS.md').open('a') as stream:
            stream.write('\n' + fingerprint(self.evaluation / 'manifest.json')['sha256'])
        self.eval_commit = self.commit('original evaluation recorded')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.DEVNULL)

    def commit(self, message):
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', message)
        return self.git('rev-parse', 'HEAD').decode().strip()

    def files(self, folder):
        from retention_lab.data import fingerprint
        return {p.name: fingerprint(p) for p in folder.iterdir() if p.is_file()}

    def run_extension(self):
        return self.extend(self.legacy, self.frozen, self.evaluation, self.repo,
                           self.lr_commit, self.freeze_commit, self.eval_commit)

    def test_manual_metrics_random_floor_pp_and_original_equivalence(self):
        result, counts = self.run_extension()
        self.assertEqual(result['selected_model'], 'hgb')
        self.assertIn('Post-hoc descriptive extension', result['extension'])
        for row in result['table']:
            k = int(20 * row['requested_percent'] / 100)
            self.assertEqual(row['logistic']['k'], k)
            self.assertEqual(row['logistic']['captured'], int(self.labels[:k].sum()))
            self.assertEqual(row['logistic']['recall'], self.labels[:k].sum() / 8)
            self.assertEqual(row['logistic']['precision'], self.labels[:k].sum() / k)
            self.assertAlmostEqual(row['random_expected']['captured'], k * 8 / 20)
            self.assertAlmostEqual(row['random_expected']['recall'], k / 20)
            self.assertAlmostEqual(row['random_expected']['precision'], 8 / 20)
            self.assertAlmostEqual(row['random_expected']['lift'], 1)
            self.assertEqual(row['logistic']['capacity'], k / 20)
            self.assertEqual(row['hgb_minus_logistic_recall_pp'],
                             100 * (row['hgb']['recall'] - row['logistic']['recall']))
        original = json.loads((self.evaluation / 'results.json').read_text())
        for old, new in zip(original['curve'], result['curve']):
            for policy in ('business', 'random_expected'):
                self.assertEqual(old[policy], new[policy])
            self.assertEqual(old['ml'], new['hgb'])
        self.assertEqual(counts['logistic'][0], 0)
        self.assertEqual(counts['logistic'][-1], 8)
        self.assertTrue(all(k not in json.dumps(result) for k in self.keys))
        self.assertNotIn('counts', result)

    def test_frozen_inputs_immutable_no_raw_no_training_or_reselection(self):
        before = {p: p.read_bytes() for d in (self.legacy, self.frozen, self.evaluation)
                  for p in d.iterdir()}
        original_open = Path.open
        def guarded(path, *args, **kwargs):
            if path.name in ('train.csv', 'transactions.csv') or 'raw' in path.parts:
                raise AssertionError('Original CSV access forbidden')
            return original_open(path, *args, **kwargs)
        with patch.object(Path, 'open', guarded), \
             patch('retention_lab.train.fit_model', side_effect=AssertionError('training')), \
             patch('retention_lab.selection.compare_and_freeze', side_effect=AssertionError('selection')), \
             patch('retention_lab.selection.verify_freeze', side_effect=AssertionError('rescoring')):
            self.run_extension()
        self.assertEqual(before, {p: p.read_bytes() for p in before})

    def test_changed_ranking_model_baseline_keys_cache_and_marker_are_refused(self):
        for folder, name in ((self.legacy, 'final_rankings.csv'), (self.legacy, 'pipeline.joblib'),
                             (self.frozen, 'final_scores.csv'), (self.frozen, 'hgb.joblib'),
                             (self.frozen, 'final_keys.csv'), (self.evaluation, 'results.json'),
                             (self.evaluation, 'curve_counts.npz'),
                             (self.frozen, 'evaluation_started.json')):
            path = folder / name
            original = path.read_bytes()
            path.write_bytes(original + b'tampered')
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.run_extension()
            path.write_bytes(original)

    def test_refreshed_lr_manifest_cannot_replace_historical_identity(self):
        from retention_lab.data import fingerprint, write_json
        path = self.legacy / 'final_rankings.csv'
        path.write_bytes(path.read_bytes() + b'changed')
        manifest = json.loads((self.legacy / 'manifest.json').read_text())
        manifest['files'][path.name] = fingerprint(path)
        write_json(self.legacy / 'manifest.json', manifest)
        with self.assertRaises(ValueError):
            self.run_extension()

    def test_plot_is_byte_reproducible_and_markdown_has_only_aggregates(self):
        from retention_lab.posthoc import render_comparison, comparison_markdown
        result, counts = self.run_extension()
        a, b = self.root / 'a.png', self.root / 'b.png'
        render_comparison(counts, result['n'], result['positives'], a)
        render_comparison(counts, result['n'], result['positives'], b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        text = comparison_markdown(result)
        self.assertIn('Logistic Regression (post-hoc)', text)
        self.assertIn('percentage points', text)
        self.assertTrue(all(key not in text for key in self.keys))

    def test_cli_exports_only_three_aggregate_files_and_never_overwrites(self):
        import importlib.util
        from retention_lab.data import fingerprint
        spec = importlib.util.spec_from_file_location('posthoc_cli', ROOT / 'scripts/extend_kkbox_comparison.py')
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        result, counts = self.run_extension()
        output = self.root / 'public'
        args = ['extend_kkbox_comparison.py', '--legacy-dir', str(self.legacy),
                '--frozen-dir', str(self.frozen), '--evaluation-dir', str(self.evaluation),
                '--output-dir', str(output)]
        with patch.object(sys, 'argv', args), patch.object(cli, 'extend_from_cache', return_value=(result, counts)):
            self.assertEqual(cli.main(), 0)
            before = self.files(output)
            self.assertEqual(set(before), {'capacity_comparison_v2.json', 'capacity_comparison_v2.md',
                                           'capacity_comparison_v2.png'})
            self.assertEqual(cli.main(), 0)
            self.assertEqual(before, self.files(output))
            path = output / 'capacity_comparison_v2.json'
            path.write_text('preserve existing conflict')
            changed = fingerprint(path)
            self.assertEqual(cli.main(), 2)
            self.assertEqual(changed, fingerprint(path))
        args[-1] = str(self.frozen)
        with patch.object(sys, 'argv', args), patch.object(cli, 'extend_from_cache') as extension:
            self.assertEqual(cli.main(), 2)
            extension.assert_not_called()
