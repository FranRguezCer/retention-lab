"""Synthetic public-interface checks; no competition records."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/audit_kkbox.py'
HEADER = ('msno,payment_method_id,payment_plan_days,plan_list_price,actual_amount_paid,'
          'is_auto_renew,transaction_date,membership_expire_date,is_cancel\n')


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'train_v2.csv').write_text('msno,is_churn\nprivate-id,1\n')
        (self.root / 'transactions_v2.csv').write_text(
            HEADER + 'private-id,1,30,100,100,1,20170101,20170201,0\n')
        self.report = self.root / 'report.json'

    def run_audit(self):
        return subprocess.run([sys.executable, str(SCRIPT), '--raw-dir', str(self.root),
                               '--report', str(self.report)], capture_output=True, text=True)

    def test_identical_repeat_preserves_all_bytes(self):
        before = {p.name: p.read_bytes() for p in self.root.glob('*.csv')}
        self.assertEqual(self.run_audit().returncode, 0)
        first = self.report.read_bytes()
        self.assertEqual(self.run_audit().returncode, 0)
        self.assertEqual(first, self.report.read_bytes())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.glob('*.csv')})
        self.assertNotIn(b'private-id', first)
        report = json.loads(first)
        train = report['files']['train_v2.csv']
        self.assertEqual(train['rows'], 1)
        self.assertEqual(train['sha256'], hashlib.sha256(before['train_v2.csv']).hexdigest())
        self.assertEqual(train['labels'], {'0': 0, '1': 1, 'invalid': 0})
        self.assertEqual(report['files']['transactions_v2.csv']['dates']['transaction_date'],
                         {'invalid': 0, 'min': '20170101', 'max': '20170101'})

    def test_wrong_schema(self):
        (self.root / 'train_v2.csv').write_text('msno,target\nsecret,1\n')
        result = self.run_audit()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.report.exists())
        self.assertNotIn('secret', result.stderr)

    def test_invalid_labels_and_dates(self):
        (self.root / 'train_v2.csv').write_text('msno,is_churn\nsecret,2\nother,\n')
        (self.root / 'transactions_v2.csv').write_text(
            HEADER + 'secret,1,30,100,100,1,20170230,2017011,0\n')
        result = self.run_audit()
        self.assertNotEqual(result.returncode, 0)
        report = json.loads(self.report.read_text())
        self.assertFalse(report['valid'])
        self.assertEqual(report['files']['train_v2.csv']['labels']['invalid'], 2)
        for date in report['files']['transactions_v2.csv']['dates'].values():
            self.assertEqual(date, {'invalid': 1, 'min': None, 'max': None})

    def test_content_change_refuses_old_report(self):
        self.assertEqual(self.run_audit().returncode, 0)
        before = self.report.read_bytes()
        with (self.root / 'train_v2.csv').open('a') as stream:
            stream.write('another,0\n')
        self.assertNotEqual(self.run_audit().returncode, 0)
        self.assertEqual(self.report.read_bytes(), before)

    def test_missing_file(self):
        (self.root / 'train_v2.csv').unlink()
        self.assertNotEqual(self.run_audit().returncode, 0)
        self.assertFalse(self.report.exists())

    def test_malformed_row(self):
        (self.root / 'train_v2.csv').write_text('msno,is_churn\nsecret,1,extra\n')
        self.assertNotEqual(self.run_audit().returncode, 0)
        self.assertFalse(self.report.exists())

    def test_report_cannot_overwrite_source(self):
        self.report = self.root / 'train_v2.csv'
        before = self.report.read_bytes()
        self.assertNotEqual(self.run_audit().returncode, 0)
        self.assertEqual(self.report.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
