"""Synthetic public-CLI checks; never open real data or final outcomes."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import numpy as np

import test_prepare_kkbox_eda as preparation

ROOT = preparation.ROOT
event = preparation.event

SCRIPT = ROOT / 'scripts/train_kkbox.py'
sys.path.insert(0, str(ROOT / 'src'))


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.fixture = preparation.PreparationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        f.users = [f'synthetic-{i}' for i in range(120)]
        f.rows = [event(u, auto=str(i % 2), amount='' if i % 7 == 0 else str(100 + i),
                        days='' if i % 9 == 0 else '30') for i, u in enumerate(f.users)]
        f.labels = [[u, str(int(i % 2 == 0))] for i, u in enumerate(f.users)]
        f.run_prepare()
        self.features = f.root / 'features'
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/prepare_kkbox_features.py'),
                                 '--raw-dir', str(f.raw), '--eda-dir', str(f.root / 'prepared'),
                                 '--output-dir', str(self.features)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.eda = f.root / 'prepared'
        self.output = f.root / 'models'

    def run_cli(self, output=None, success=True, extra=()):
        result = subprocess.run([sys.executable, str(SCRIPT), '--feature-dir', str(self.features),
                                 '--eda-dir', str(self.eda), '--output-dir', str(output or self.output),
                                 *extra], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        self.assertNotIn('synthetic-', result.stdout + result.stderr)
        return result

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.output.iterdir()}

    def rehash(self, name):
        from retention_lab.data import fingerprint
        path = self.features / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['files'][name] = fingerprint(self.features / name)
        path.write_text(json.dumps(manifest))

    def test_same_population_alignment_finite_scores_rankings_and_reproduction(self):
        self.run_cli()
        before = self.snapshot()
        self.run_cli()
        self.assertEqual(before, self.snapshot())
        other = self.output.parent / 'independent'
        self.run_cli(other)
        self.assertEqual(before, {p.name: p.read_bytes() for p in other.iterdir()})
        from retention_lab.data import fingerprint
        manifest = json.loads((self.output / 'manifest.json').read_text())
        for name, digest in manifest['files'].items():
            self.assertEqual(fingerprint(self.output / name), digest)
        for partition in ('train', 'validation', 'final'):
            self.assertEqual((self.features / f'{partition}_keys.csv').read_bytes(),
                             (self.output / f'{partition}_keys.csv').read_bytes())
            with (self.output / f'{partition}_scores.csv').open() as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(list(rows[0]), ['random', 'business', 'ml'])
            for row in rows:
                self.assertTrue(all(np.isfinite(float(v)) and 0 <= float(v) <= 1
                                    for v in row.values()))
            with (self.output / f'{partition}_rankings.csv').open() as stream:
                rankings = list(csv.DictReader(stream))
            for policy in ('random', 'business', 'ml'):
                order = [int(r[policy]) for r in rankings]
                self.assertEqual(sorted(order), list(range(len(rows))))
                with (self.output / f'{partition}_keys.csv').open() as stream:
                    keys = [r['msno'] for r in csv.DictReader(stream)]
                expected = sorted(range(len(rows)), key=lambda i: (
                    -float(rows[i][policy]), hashlib.sha256(
                        f'retention-lab-ranking-v1|{policy}|42|{keys[i]}'.encode()).hexdigest(), keys[i]))
                self.assertEqual(order, expected)
                self.assertEqual([float(rows[i][policy]) for i in order],
                                 sorted((float(r[policy]) for r in rows), reverse=True))
        self.assertEqual(self.output.stat().st_mode & 0o077, 0)
        self.assertFalse((self.output / 'final_labels.csv').exists())

    def test_train_only_fit_positive_class_and_strict_pipeline_schema(self):
        from retention_lab.train import load_inputs, fit_model, score_model
        data, _ = load_inputs(self.features, self.eda)
        model = fit_model(data['train']['X'], data['train']['y'])
        prep = model.named_steps['preprocess']
        numeric = prep.named_transformers_['numeric']
        expected = np.nanmedian(data['train']['X'].iloc[:, 1:].to_numpy(), axis=0)
        np.testing.assert_allclose(numeric.named_steps['impute'].statistics_, expected)
        self.assertEqual(model.feature_names_in_.tolist(), list(data['train']['X']))
        self.assertEqual(numeric.named_steps['scale'].n_samples_seen_, len(data['train']['X']))
        imputed = numeric.named_steps['impute'].transform(data['train']['X'].iloc[:, 1:])
        np.testing.assert_allclose(numeric.named_steps['scale'].mean_, imputed.mean(axis=0))
        np.testing.assert_allclose(numeric.named_steps['scale'].var_, imputed.var(axis=0))
        old = numeric.named_steps['scale'].mean_.copy()
        changed = data['validation']['X'].copy()
        changed.iloc[:, 1:] = changed.iloc[:, 1:] * 10000
        score_model(model, changed)
        np.testing.assert_array_equal(old, numeric.named_steps['scale'].mean_)
        scores = score_model(model, data['validation']['X'])
        np.testing.assert_array_equal(scores, model.predict_proba(data['validation']['X'])[:, 1])
        self.assertGreater(scores[data['validation']['y'] == 1].mean(),
                           scores[data['validation']['y'] == 0].mean())
        for name in ('msno', 'is_churn', 'digest', 'partition'):
            with self.assertRaises(ValueError):
                model.predict_proba(changed.assign(**{name: 0}))
        with self.assertRaises(ValueError):
            score_model(object(), changed)

    def test_fully_missing_training_optional_columns_are_retained(self):
        from retention_lab.train import load_inputs, fit_model, score_model
        data, _ = load_inputs(self.features, self.eda)
        frame = data['train']['X'].copy()
        frame[['latest_plan_days', 'latest_amount']] = np.nan
        model = fit_model(frame, data['train']['y'])
        imputer = model.named_steps['preprocess'].named_transformers_['numeric'].named_steps['impute']
        self.assertEqual(len(imputer.statistics_), 6)
        self.assertTrue(np.isfinite(score_model(model, data['validation']['X'])).all())

    def test_final_labels_and_raw_sources_are_never_opened(self):
        from retention_lab.train import train_and_score
        original = Path.open
        def guarded(path, *args, **kwargs):
            if path.name in ('final_labels.csv', 'train.csv', 'transactions.csv'):
                raise AssertionError('Forbidden input accessed')
            return original(path, *args, **kwargs)
        (self.features / 'final_labels.csv').write_text('not a label,\npoison')
        with patch.object(Path, 'open', guarded):
            train_and_score(self.features, self.eda, self.output)
        self.assertEqual(set(json.loads((self.output / 'metrics.json').read_text())),
                         {'train', 'validation'})

    def test_validation_features_and_outcomes_do_not_change_model_or_final_scores(self):
        self.run_cli()
        for name in ('validation_labels.csv',):
            path = self.features / name
            with path.open() as stream:
                rows = list(csv.reader(stream))
            for row in rows[1:]:
                row[1] = str(1 - int(row[1]))
            with path.open('w', newline='') as stream:
                csv.writer(stream).writerows(rows)
            self.rehash(name)
        path = self.features / 'validation_features.csv'
        with path.open() as stream:
            rows = list(csv.reader(stream))
        for row in rows[1:]:
            row[1] = str(int(row[1]) + 10000)
        with path.open('w', newline='') as stream:
            csv.writer(stream).writerows(rows)
        self.rehash(path.name)
        other = self.output.parent / 'changed-validation'
        self.run_cli(other)
        for name in ('pipeline.joblib', 'train_scores.csv', 'final_scores.csv', 'final_rankings.csv'):
            self.assertEqual((self.output / name).read_bytes(), (other / name).read_bytes())
        self.assertNotEqual((self.output / 'metrics.json').read_bytes(),
                            (other / 'metrics.json').read_bytes())

    def test_reject_invalid_or_changed_inputs_without_overwriting(self):
        self.run_cli()
        before = self.snapshot()
        path = self.features / 'train_features.csv'
        good = path.read_bytes()
        for bad in (good.replace(b'auto_renew', b'msno', 1), good + b'bad\n'):
            path.write_bytes(bad)
            self.run_cli(success=False)
            self.assertEqual(before, self.snapshot())
        path.write_bytes(good)
        for name, change in [('final_keys.csv', lambda text: text.replace('synthetic-', 'other-', 1)),
                             ('validation_labels.csv', lambda text: text.replace(',0', ',2', 1))]:
            path = self.features / name
            original = path.read_text()
            path.write_text(change(original))
            self.rehash(name)
            self.run_cli(success=False)
            self.assertEqual(before, self.snapshot())
            path.write_text(original)
            self.rehash(name)
        self.run_cli(success=False, extra=('--verify-real-population',))
        self.assertEqual(before, self.snapshot())

    def test_reject_incompatible_manifest_source_and_existing_model(self):
        self.run_cli()
        for root, name in ((self.features, 'manifest.json'), (self.eda, 'manifest.json'),
                           (self.output, 'pipeline.joblib')):
            path = root / name
            good = path.read_bytes()
            path.write_bytes(good + b'broken')
            before = self.snapshot()
            self.run_cli(success=False)
            self.assertEqual(before, self.snapshot())
            path.write_bytes(good)

    def test_convergence_failure_is_not_published(self):
        self.run_cli(success=False, extra=('--max-iter', '1'))
        self.assertFalse(self.output.exists())

    def test_semantic_rejections_with_refreshed_integrity_hashes(self):
        # Independent verifier probes pinned as realistic CLI regressions.
        from retention_lab.data import fingerprint
        self.run_cli()
        before = self.snapshot()
        original = {p.name: p.read_bytes() for p in self.features.iterdir()}
        original_eda = {p.name: p.read_bytes() for p in self.eda.iterdir()}

        def restore():
            for root, files in ((self.features, original), (self.eda, original_eda)):
                for name, content in files.items():
                    (root / name).write_bytes(content)

        def reject():
            self.run_cli(success=False)
            self.assertEqual(before, self.snapshot())

        for field in ('msno', 'is_churn', 'digest', 'partition'):
            restore()
            path = self.features / 'train_features.csv'
            with path.open() as stream:
                rows = list(csv.reader(stream))
            rows[0].append(field)
            for row in rows[1:]:
                row.append('0')
            with path.open('w', newline='') as stream:
                csv.writer(stream).writerows(rows)
            self.rehash(path.name)
            reject()
        for value, column in (('2', 0), ('', 0), ('', 1)):
            restore()
            path = self.features / 'train_features.csv'
            with path.open() as stream:
                rows = list(csv.reader(stream))
            rows[1][column] = value
            with path.open('w', newline='') as stream:
                csv.writer(stream).writerows(rows)
            self.rehash(path.name)
            reject()
        for name in ('final_features.csv', 'train_keys.csv', 'validation_labels.csv'):
            restore()
            path = self.features / name
            with path.open() as stream:
                rows = list(csv.reader(stream))
            if name.endswith('features.csv'):
                rows.pop()
            else:
                rows[1], rows[2] = rows[2], rows[1]
            with path.open('w', newline='') as stream:
                csv.writer(stream).writerows(rows)
            self.rehash(name)
            reject()
        for mutation in ('source', 'salt', 'version', 'final-label-entry'):
            restore()
            path = self.features / 'manifest.json'
            manifest = json.loads(path.read_text())
            if mutation in ('source', 'salt'):
                eda_path = self.eda / 'manifest.json'
                eda = json.loads(eda_path.read_text())
                if mutation == 'source':
                    eda['sources']['train_v2.csv'] = eda['sources'].pop('train.csv')
                else:
                    eda['configuration']['salt'] = 'incompatible|'
                eda_path.write_text(json.dumps(eda))
                manifest['eda']['manifest.json'] = fingerprint(eda_path)
            elif mutation == 'version':
                manifest['version'] = 2
            else:
                manifest['files']['final_labels.csv'] = {}
            path.write_text(json.dumps(manifest))
            reject()
        restore()
