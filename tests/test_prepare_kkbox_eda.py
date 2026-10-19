"""Synthetic public-interface tests for isolated EDA preparation."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/prepare_kkbox_eda.py'
HEADER = ('msno,payment_method_id,payment_plan_days,plan_list_price,'
          'actual_amount_paid,is_auto_renew,transaction_date,'
          'membership_expire_date,is_cancel').split(',')


def event(user, day='20170131', expiry='20170228', auto='1', days='30', amount='100', cancel='0'):
    return [user, '1', days, '100', amount, auto, day, expiry, cancel]


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.raw = self.root / 'raw'
        self.raw.mkdir()
        self.users = [f'synthetic-{i}' for i in range(40)]
        self.rows = [event(u) for u in self.users]
        self.labels = [[u, str(i % 2)] for i, u in enumerate(self.users)]

    def write(self):
        for name, header, rows in [('transactions.csv', HEADER, self.rows),
                                   ('train.csv', ['msno', 'is_churn'], self.labels)]:
            with (self.raw / name).open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(header)
                writer.writerows(rows)

    def run_prepare(self, output='prepared', success=True):
        self.write()
        result = subprocess.run([sys.executable, str(SCRIPT), '--raw-dir', str(self.raw),
                                 '--output-dir', str(self.root / output)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        self.assertNotIn('synthetic-', result.stdout + result.stderr)
        return self.root / output

    def assignments(self, path):
        with (path / 'assignments.csv').open() as stream:
            return list(csv.DictReader(stream))

    def training(self, path):
        with (path / 'training.csv').open() as stream:
            return {r['msno']: r for r in csv.DictReader(stream)}

    def test_hash_coverage_disjunction_reordering_and_immutable_rerun(self):
        out = self.run_prepare()
        rows = self.assignments(out)
        self.assertEqual({r['msno'] for r in rows}, set(self.users))
        known = next(r for r in rows if r['msno'] == 'synthetic-0')
        self.assertEqual(known['digest'], '1cb25ab08e299ce25b9c297a2eb4a643af4d575b604bb250a81f213e25d933bc')
        for row in rows:
            digest = hashlib.sha256(('retention-lab-feb2017-v1|' + row['msno']).encode()).hexdigest()
            bucket = int(digest, 16) % 10
            self.assertEqual(row['digest'], digest)
            self.assertEqual(int(row['bucket']), bucket)
            self.assertEqual(row['partition'], 'train' if bucket < 6 else 'validation' if bucket < 8 else 'final')
        before = (out / 'manifest.json').read_bytes()
        self.run_prepare()
        self.assertEqual(before, (out / 'manifest.json').read_bytes())
        self.rows.reverse()
        self.labels.reverse()
        reordered = self.run_prepare('reordered')
        self.assertEqual((out / 'assignments.csv').read_bytes(), (reordered / 'assignments.csv').read_bytes())
        self.assertEqual((out / 'training.csv').read_bytes(), (reordered / 'training.csv').read_bytes())
        self.run_prepare(success=False)
        self.assertEqual(before, (out / 'manifest.json').read_bytes())

    def test_eligibility_conflicts_cutoff_and_exact_duplicates(self):
        train = next(u for u in self.users if int(hashlib.sha256(('retention-lab-feb2017-v1|' + u).encode()).hexdigest(), 16) % 10 < 6)
        self.rows += [event(train), event(train, days='60'), event(train, day='20170101', auto='0'),
                      event('conflict', auto='0'), event('conflict'),
                      event('cancelled', cancel='1'), event('march', expiry='20170301'),
                      event('missing-label')]
        self.labels += [['conflict', '0'], ['cancelled', '1'], ['march', '0']]
        out = self.run_prepare()
        assigned = {r['msno'] for r in self.assignments(out)}
        self.assertEqual(assigned, set(self.users))
        row = self.training(out)[train]
        self.assertEqual(row['latest_plan_days'], '')
        self.assertEqual(row['latest_amount'], '100')
        self.assertEqual(row['january_transactions'], '3')
        self.assertEqual(row['duplicate_rows'], '1')
        self.rows += [event(train, day='20170201', auto='0', cancel='1'),
                      event('new-future-user', day='20170301')]
        future = self.run_prepare('future')
        self.assertEqual((out / 'training.csv').read_bytes(), (future / 'training.csv').read_bytes())
        self.assertEqual((out / 'assignments.csv').read_bytes(), (future / 'assignments.csv').read_bytes())
        summary = json.loads((out / 'manifest.json').read_text())['population']
        self.assertEqual(summary['candidates'], 41)
        self.assertEqual(summary['unlabeled'], 1)

    def test_nontraining_labels_are_never_interpreted(self):
        out = self.run_prepare()
        train = set(self.training(out))
        for row in self.labels:
            if row[0] not in train:
                row[1] = 'THIS IS NOT A LABEL, including quotes \" and a newline\nignored'
        changed = self.run_prepare('changed')
        for name in ('training.csv', 'assignments.csv', 'quality.json'):
            self.assertEqual((out / name).read_bytes(), (changed / name).read_bytes())
        self.run_prepare()  # Same manifest: label values outside train are irrelevant.

    def test_latest_values_changes_and_missing_validation(self):
        u = next(u for u in self.users if int(hashlib.sha256(('retention-lab-feb2017-v1|' + u).encode()).hexdigest(), 16) % 10 < 6)
        self.rows += [event(u, day='20170101', auto='1'), event(u, day='20170115', auto='0')]
        out = self.run_prepare()
        row = self.training(out)[u]
        self.assertEqual(row['auto_on_to_off'], '1')
        self.assertEqual(row['observed_history_days'], '30')
        self.assertEqual(row['latest_plan_days'], '30')
        self.rows.append(event(u, day='20170132'))
        self.run_prepare('invalid', success=False)


    def test_ambiguous_day_breaks_transitions_and_rejections_preserve_bytes(self):
        user = next(u for u in self.users if int(hashlib.sha256(
            ('retention-lab-feb2017-v1|' + u).encode()).hexdigest(), 16) % 10 < 6)
        self.rows += [event(user, day='20170101', auto='1'),
                      event(user, day='20170102', auto='0'),
                      event(user, day='20170102', auto='1'),
                      event(user, day='20170103', auto='0')]
        out = self.run_prepare()
        row = self.training(out)[user]
        self.assertEqual(row['auto_on_to_off'], '0')
        self.assertEqual(row['ambiguous_auto_days'], '1')
        before = {p.name: p.read_bytes() for p in out.iterdir()}
        label = next(r for r in self.labels if r[0] == user)
        label[1] = str(1 - int(label[1]))
        self.run_prepare(success=False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})
        label[1] = str(1 - int(label[1]))
        self.rows += [event(user, day='20161231', expiry='20990228')]
        future = self.run_prepare('future-expiry')
        self.assertEqual(self.training(future)[user]['far_future_expiry'], '1')
        self.run_prepare(success=False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in out.iterdir()})


if __name__ == '__main__':
    unittest.main()
