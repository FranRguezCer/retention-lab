"""Synthetic public-interface checks; never read real subscriber outcomes."""
import csv
from pathlib import Path
import subprocess
import sys

from test_prepare_kkbox_eda import PreparationTests, event

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/prepare_kkbox_features.py'
FEATURES = ['auto_renew', 'observed_history_days', 'january_transactions',
            'distinct_transactions', 'latest_plan_days', 'latest_amount', 'auto_on_to_off']


class FeatureTests(PreparationTests):
    def features(self, output='features', eda='prepared', success=True, extra=()):
        self.write()
        result = subprocess.run([sys.executable, str(SCRIPT), '--raw-dir', str(self.raw),
                                 '--eda-dir', str(self.root / eda),
                                 '--output-dir', str(self.root / output), *extra],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        self.assertNotIn('synthetic-', result.stdout + result.stderr)
        return self.root / output

    def table(self, out, name):
        with (out / name).open() as stream:
            return list(csv.DictReader(stream))

    def test_feature_schema_coverage_eda_equivalence_and_rerun(self):
        eda = self.run_prepare()
        out = self.features()
        observed = set()
        train = self.training(eda)
        for partition in ('train', 'validation', 'final'):
            keys = self.table(out, f'{partition}_keys.csv')
            rows = self.table(out, f'{partition}_features.csv')
            self.assertEqual(list(rows[0]), FEATURES)
            ids = [r['msno'] for r in keys]
            self.assertEqual(len(ids), len(set(ids)))
            self.assertFalse(observed.intersection(ids))
            observed.update(ids)
            self.assertEqual(len(keys), len(rows))
            if partition == 'train':
                for user, row in zip(ids, rows):
                    self.assertEqual(row, {c: train[user][c] for c in FEATURES})
                self.assertEqual({r['msno']: r['is_churn'] for r in self.table(out, 'train_labels.csv')},
                                 {u: r['is_churn'] for u, r in train.items()})
        self.assertEqual(observed, set(self.users))
        self.assertFalse((out / 'final_labels.csv').exists())
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        self.features()
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})

    def test_final_label_poisoning_and_validation_separation(self):
        eda = self.run_prepare()
        out = self.features()
        assigned = {r['msno']: r['partition'] for r in self.assignments(eda)}
        for row in self.labels:
            if assigned[row[0]] == 'final':
                row[1] = 'NOT A LABEL, "quoted"\nignored'
        changed = self.features('poisoned')
        self.assertEqual({p.name: p.read_bytes() for p in out.iterdir()},
                         {p.name: p.read_bytes() for p in changed.iterdir()})
        for row in self.labels:
            if assigned[row[0]] == 'validation':
                row[1] = str(1 - int(row[1]))
        changed = self.features('validation-change')
        for partition in ('train', 'validation', 'final'):
            for kind in ('keys', 'features'):
                name = f'{partition}_{kind}.csv'
                self.assertEqual((out / name).read_bytes(), (changed / name).read_bytes())
        self.assertNotEqual((out / 'validation_labels.csv').read_bytes(),
                            (changed / 'validation_labels.csv').read_bytes())

    def test_cutoff_order_duplicates_ambiguity_and_missing(self):
        u = self.users[0]
        self.rows += [event(u), event(u, days='60', amount=''),
                      event(u, day='20170101'), event(u, day='20170102', auto='0'),
                      event(u, day='20170102'), event(u, day='20170103', auto='0')]
        self.run_prepare()
        out = self.features()
        assigned = {r['msno']: r['partition'] for r in self.assignments(self.root / 'prepared')}
        def row(directory):
            part = assigned[u]
            keys = self.table(directory, f'{part}_keys.csv')
            return self.table(directory, f'{part}_features.csv')[[r['msno'] for r in keys].index(u)]
        self.assertEqual(row(out)['latest_plan_days'], '')
        self.assertEqual(row(out)['latest_amount'], '')
        self.assertEqual(row(out)['auto_on_to_off'], '0')
        self.assertEqual(row(out)['january_transactions'], '6')
        self.rows += [event(u, day='20170201', auto='0', cancel='1')]
        self.rows.reverse()
        self.labels.reverse()
        self.run_prepare('reordered-eda')
        reordered = self.features('reordered', 'reordered-eda')
        for name in [p.name for p in out.glob('*.csv')]:
            self.assertEqual((out / name).read_bytes(), (reordered / name).read_bytes())

    def test_invalid_inputs_and_rejected_artifacts_are_immutable(self):
        self.run_prepare()
        out = self.features()
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        self.rows.append(event(self.users[0], day='20170132'))
        self.features(success=False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
        self.rows.pop()
        self.rows.append(event(self.users[0], amount='not-a-number'))
        self.features('invalid-numeric', success=False)
        self.rows.pop()
        self.features(success=False, extra=('--verify-real-population',))
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})

    def test_changed_cache_fails_without_replacing_evidence(self):
        self.run_prepare()
        out = self.features()
        path = out / 'train_features.csv'
        path.write_bytes(path.read_bytes() + b'bad\n')
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        self.features(success=False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})

    def test_owner_only_output_and_invalid_validation_label(self):
        eda = self.run_prepare()
        out = self.features()
        self.assertEqual(out.stat().st_mode & 0o077, 0)
        assigned = {r['msno']: r['partition'] for r in self.assignments(eda)}
        for row in self.labels:
            if assigned[row[0]] == 'validation':
                row[1] = 'invalid'
                break
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        self.features(success=False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
