"""Development-only comparison and integrity gate, using synthetic data."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import numpy as np
import test_train as training

ROOT = training.ROOT
sys.path.insert(0, str(ROOT / 'src'))


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = training.ModelTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.run_cli()
        self.features, self.eda = self.fixture.features, self.fixture.eda
        self.output = self.features.parent / 'selection'

    def cli(self, success=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/select_kkbox_model.py'),
                                 '--feature-dir', str(self.features), '--eda-dir', str(self.eda),
                                 '--legacy-dir', str(self.fixture.output),
                                 '--output-dir', str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return result

    def test_selection_reproduces_without_final_outcome_or_raw_access(self):
        from retention_lab.selection import compare_and_freeze, verify_freeze
        original = Path.open
        def guarded(path, *args, **kwargs):
            if path.name in ('train.csv', 'final_labels.csv', 'transactions.csv'):
                raise AssertionError('Forbidden label/source access')
            return original(path, *args, **kwargs)
        self.cli()
        before = {p.name: p.read_bytes() for p in self.output.iterdir()}
        self.cli()
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.output.iterdir()})
        independent = self.output.parent / 'guarded-selection'
        with patch.object(Path, 'open', guarded):
            compare_and_freeze(self.features, self.eda, self.fixture.output, independent)
            verify_freeze(independent, self.features, self.eda)
        # Numerical reproducibility across API/subprocess contexts; pickle
        # object aliasing is not itself learned model state.
        for name in ('validation.json', 'final_scores.csv', 'final_rankings.csv'):
            self.assertEqual((self.output / name).read_bytes(), (independent / name).read_bytes())
        self.assertEqual((self.output / 'logistic.joblib').read_bytes(),
                         (self.fixture.output / 'pipeline.joblib').read_bytes())
        with (self.output / 'final_rankings.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        for policy in ('random', 'business', 'ml'):
            self.assertEqual(sorted(int(r[policy]) for r in rows), list(range(len(rows))))

    def test_hgb_is_train_only_native_missing_and_reproducible(self):
        from retention_lab.selection import fit_hgb
        from retention_lab.train import load_inputs, score_model
        data, _ = load_inputs(self.features, self.eda)
        first = fit_hgb(data['train']['X'], data['train']['y'])
        second = fit_hgb(data['train']['X'], data['train']['y'])
        self.assertEqual(first.feature_names_in_.tolist(), list(data['train']['X']))
        self.assertEqual(list(first.named_steps), ['schema', 'classifier'])
        self.assertFalse(first.named_steps['classifier'].early_stopping)
        np.testing.assert_array_equal(score_model(first, data['validation']['X']),
                                      score_model(second, data['validation']['X']))
        changed = data['validation']['X'].copy()
        changed[['latest_plan_days','latest_amount']] = np.nan
        self.assertTrue(np.isfinite(score_model(first, changed)).all())

    def test_predeclared_selection_prefers_simplicity_on_small_or_inconsistent_gain(self):
        from retention_lab.selection import choose_model
        def report(r5, r10, r20):
            return {'capacity': {str(p): {'recall': r} for p, r in zip((5,10,20),(r5,r10,r20))}}
        lr = report(.2,.4,.6)
        for hgb in (report(.2,.405,.6), report(.19,.5,.7), report(.3,.5,.59)):
            self.assertEqual(choose_model({'logistic':lr,'hgb':hgb}), 'logistic')
        self.assertEqual(choose_model({'logistic':lr,'hgb':report(.3,.5,.7)}), 'hgb')
        self.assertEqual(choose_model({'logistic':lr,'hgb':report(.2,.41,.6)}), 'hgb')

    def test_gate_refuses_tampering_and_selection_is_closed_after_test_start(self):
        from retention_lab.selection import verify_freeze
        self.cli()
        path = self.output / 'final_rankings.csv'
        original = path.read_bytes()
        path.write_bytes(original + b'bad\n')
        with self.assertRaises(ValueError):
            verify_freeze(self.output, self.features, self.eda)
        path.write_bytes(original)
        path = self.output / 'manifest.json'
        manifest = json.loads(path.read_text())
        manifest['selected_model'] = 'unknown'
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            verify_freeze(self.output, self.features, self.eda)
        (self.output / 'evaluation_started.json').write_text('{}')
        self.cli(success=False)

    def test_commit_anchor_is_required_and_binds_code_and_artifacts(self):
        import shutil
        from retention_lab import selection
        from retention_lab.data import fingerprint
        self.cli()
        repository = self.features.parent / 'freeze-repository'
        repository.mkdir()
        for name in selection.SOURCES:
            target = repository / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        anchor = repository / 'artifacts/model_freeze.json'
        anchor.parent.mkdir()
        manifest = json.loads((self.output / 'manifest.json').read_text())
        anchor.write_text(json.dumps({'version': 1, 'manifest': fingerprint(self.output / 'manifest.json'),
                                      'selected_model': manifest['selected_model'], 'rule': selection.RULE}))
        def git(*args):
            return subprocess.check_output(['git', '-C', str(repository), *args], stderr=subprocess.DEVNULL)
        git('init', '-q')
        git('add', '.')
        git('-c', 'user.name=Synthetic Test', '-c', 'user.email=test@example.invalid',
            'commit', '-qm', 'test: bind synthetic freeze')
        commit = git('rev-parse', 'HEAD').decode().strip()
        with patch.object(selection, 'ROOT', repository):
            with self.assertRaises(ValueError):
                selection.verify_committed_freeze(self.output, self.features, self.eda, '')
            selection.verify_committed_freeze(self.output, self.features, self.eda, commit)
            anchor.write_text('{}')  # Live edits cannot replace the committed anchor.
            selection.verify_committed_freeze(self.output, self.features, self.eda, commit)
            path = repository / selection.SOURCES[0]
            path.write_bytes(path.read_bytes() + b'\n# changed\n')
            with self.assertRaises(ValueError):
                selection.verify_committed_freeze(self.output, self.features, self.eda, commit)
