"""Training-only aggregate behavior, using synthetic inputs."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.eda import summarize
import pandas as pd


class EdaTests(unittest.TestCase):
    def frame(self):
        return pd.DataFrame({
            'is_churn': [0, 1, 0, 1], 'auto_renew': [1, 0, 1, 0],
            'observed_history_days': [0, 1, 10, 20], 'january_transactions': [1, 1, 2, 2],
            'latest_plan_days': [30, None, 30, 30], 'latest_amount': [100, 100, 0, None],
            'auto_on_to_off': [0, 1, 0, 1], 'always_auto_on': [1, 0, 1, 0],
            'distinct_transactions': [1, 2, 3, 4], 'duplicate_rows': [0, 1, 0, 0],
            'ambiguous_auto_days': [0, 0, 1, 0], 'expiry_before_event': [0, 0, 0, 1],
            'far_future_expiry': [0, 0, 1, 0], 'missing_numeric_fields': [0, 0, 0, 1],
            'latest_list_price': [100, 100, 0, None], 'latest_payment_method': [1, 1, 2, 2]})

    def test_aggregates_denominators_unknowns_and_order_invariance(self):
        frame = self.frame()
        report = summarize(frame)
        self.assertEqual(report, summarize(frame.iloc[::-1]))
        self.assertEqual(report['training_users'], 4)
        self.assertEqual(report['churners'], 2)
        self.assertEqual(len(report['charts']), 5)
        for table in report['charts'].values():
            self.assertEqual(sum(r['users'] for r in table), 4)
            self.assertEqual(sum(r['churners'] for r in table), 2)
        unknown = next(r for r in report['charts']['latest_plan_days'] if r['group'] == 'Unknown')
        self.assertEqual(unknown['users'], 1)
        self.assertEqual(unknown['churn_rate'], 1)
        self.assertEqual(report['hypothesis_transition'][0]['group'], 'Always on')
        self.assertEqual(report['hypothesis_transition'][0]['users'], 2)

    def test_single_value_and_invalid_training_labels(self):
        frame = self.frame()
        frame['latest_plan_days'] = 30
        table = summarize(frame)['charts']['latest_plan_days']
        self.assertEqual(table, [{'group': '30', 'users': 4, 'churners': 2, 'churn_rate': 0.5}])
        frame.loc[0, 'is_churn'] = 2
        with self.assertRaises(ValueError):
            summarize(frame)


if __name__ == '__main__':
    unittest.main()
