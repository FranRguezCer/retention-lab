"""Synthetic CLI regression tests for the four-source feasibility audit."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_audit_kkbox import HEADER

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/audit_kkbox_history.py'


def event(user, day, expiry, cancel='0'):
    return [user, '1', '30', '100', '100', '1', day, expiry, cancel]


class HistoryAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.raw = Path(self.temp.name) / 'raw'
        self.raw.mkdir()
        self.report = Path(self.temp.name) / 'history.json'
        self.write('train.csv', [['private-a', '1'], ['private-b', '0']])
        self.write('train_v2.csv', [['private-a', '0'], ['private-c', '1']])
        shared = event('private-a', '20170101', '20170201')
        self.write('transactions.csv', [shared, shared,
                   event('private-b', '20170131', '20170228')])
        march = event('private-c', '20170228', '20170331')
        self.write('transactions_v2.csv', [shared, march, march,
                   event('private-c', '20170301', '20170401')])

    def write(self, name, rows):
        header = ['msno', 'is_churn'] if name.startswith('train') else HEADER.strip().split(',')
        with (self.raw / name).open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)

    def run_audit(self):
        return subprocess.run([sys.executable, str(SCRIPT), '--raw-dir', str(self.raw),
                               '--report', str(self.report)], capture_output=True, text=True)

    def test_overlap_duplicates_labels_and_cutoffs(self):
        result = self.run_audit()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(self.report.read_text())
        self.assertEqual(report['transaction_overlap'], {
            'shared_distinct_row_hashes': 1, 'v2_rows_matching_history': 1,
            'union_distinct_row_hashes': 4})
        self.assertEqual(report['files']['transactions.csv']['duplicate_rows'], 1)
        self.assertEqual(report['files']['transactions_v2.csv']['duplicate_rows'], 1)
        self.assertEqual(report['cohort_overlap']['shared_ids'], 1)
        self.assertEqual(report['cohort_overlap']['label_pairs'], {'1->0': 1})
        self.assertEqual(report['cutoffs']['20170131']['cohorts']['train.csv']['with_history'], 2)
        cohort = report['cutoffs']['20170228']['cohorts']['train_v2.csv']
        self.assertEqual(cohort['with_history'], 2)
        original = report['original_cutoffs']['20170228']['cohorts']['train_v2.csv']
        self.assertEqual(original['with_history'], 1)
        self.assertEqual(cohort['unambiguous_expiry_in_next_month'], 1)
        self.assertNotIn('private-', self.report.read_text())

    def test_rerun_and_changed_source(self):
        before = {p.name: p.read_bytes() for p in self.raw.iterdir()}
        self.assertEqual(self.run_audit().returncode, 0)
        payload = self.report.read_bytes()
        self.assertEqual(self.run_audit().returncode, 0)
        self.assertEqual(self.report.read_bytes(), payload)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.raw.iterdir()})
        self.write('train.csv', [['changed', '0']])
        self.assertEqual(self.run_audit().returncode, 2)
        self.assertEqual(self.report.read_bytes(), payload)

    def test_same_day_ambiguity_is_not_arbitrary_last_row(self):
        self.write('transactions_v2.csv', [
            event('private-c', '20170228', '20170331'),
            event('private-c', '20170228', '20170430', '1')])
        self.assertEqual(self.run_audit().returncode, 0)
        cutoffs = json.loads(self.report.read_text())['cutoffs']
        cohort = cutoffs['20170228']['cohorts']['train_v2.csv']
        self.assertEqual(cohort['ambiguous_latest_day'], 1)
        self.assertEqual(cohort['unambiguous_expiry_in_next_month'], 0)

    def test_cancellation_flag_is_an_explicit_subset_filter(self):
        self.write('transactions_v2.csv', [
            event('private-c', '20170228', '20170331', '1')])
        self.assertEqual(self.run_audit().returncode, 0)
        cutoffs = json.loads(self.report.read_text())['cutoffs']
        cohort = cutoffs['20170228']['cohorts']['train_v2.csv']
        self.assertEqual(cohort['unambiguous_expiry_in_next_month'], 1)
        self.assertEqual(cohort['non_cancelled_expiry_in_next_month'], 0)

    def test_population_only_mode_checks_both_target_classes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--raw-dir', str(self.raw),
             '--report', str(self.report), '--population-only'],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(self.report.read_text())
        self.assertEqual(report['candidate_users'], 2)
        self.assertEqual(report['labels'], {'0': 1, '1': 1})
        self.assertEqual(report['missing_labels'], 0)
        self.assertNotIn('private-', self.report.read_text())

    def test_invalid_fields_are_aggregated_not_exposed(self):
        self.write('train.csv', [['private-a', '2']])
        self.write('transactions.csv', [event('private-a', '20170230', '2017031', '2')])
        result = self.run_audit()
        self.assertEqual(result.returncode, 1)
        report = json.loads(self.report.read_text())
        self.assertFalse(report['valid'])
        self.assertEqual(report['files']['train.csv']['labels']['invalid'], 1)
        dates = report['files']['transactions.csv']['dates']
        self.assertEqual(dates['transaction_date']['invalid'], 1)
        self.assertEqual(report['files']['transactions.csv']['invalid_flags'], 1)
        self.assertNotIn('private-', result.stdout + result.stderr + self.report.read_text())

    def test_missing_schema_and_source_report_collision(self):
        self.report = self.raw / 'train.csv'
        before = self.report.read_bytes()
        self.assertEqual(self.run_audit().returncode, 2)
        self.assertEqual(self.report.read_bytes(), before)
        self.report = Path(self.temp.name) / 'history.json'
        (self.raw / 'train.csv').write_text('wrong,header\nprivate,1\n')
        self.assertEqual(self.run_audit().returncode, 2)
        self.assertFalse(self.report.exists())
        (self.raw / 'train.csv').unlink()
        self.assertEqual(self.run_audit().returncode, 2)
        self.assertFalse(self.report.exists())


if __name__ == '__main__':
    unittest.main()
